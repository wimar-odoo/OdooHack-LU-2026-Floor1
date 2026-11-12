"""Second Life (trivia_reuse_center): do the functional challenge through the Odoo API.

Usage (inside the odoo container):
    python3 /mnt/extra-addons/second_life.py                 -> local Odoo (http://127.0.0.1:8069, db trivia)
    python3 /mnt/extra-addons/second_life.py <URL>           -> the Odoo.sh build of the team
It is safe to run several times: everything is searched before being created.
"""
# Runs inside "odoo-bin shell" (the Odoo.sh shell): no password, no RPC.
#   curl -sL <raw url> | odoo-bin shell
from odoo.service.model import call_kw

# the shell runs as the system user (uid 1), who cannot open a POS session: act as the administrator (uid 2)
env = env(user=2)
print("db:", env.cr.dbname, "uid:", env.uid)
UID = env.uid


def call(model, method, *args, **kw):
    result = call_kw(env[model], method, list(args), kw)
    if hasattr(result, "_name"):  # a recordset: behave like RPC
        return result.ids
    return result


def search(model, domain, **kw):
    return call(model, "search", domain, **kw)


def read(model, ids, fields):
    return call(model, "read", ids, fields=fields)


def sread(model, domain, fields, **kw):
    return call(model, "search_read", domain, fields=fields, **kw)


def get_or_create(model, domain, vals, label):
    ids = search(model, domain, limit=1)
    if ids:
        print(f"  = {label} exists ({model} {ids[0]})")
        return ids[0]
    rid = call(model, "create", vals)
    print(f"  + {label} created ({model} {rid})")
    return rid


def step(title):
    print(f"\n### {title}")


company_id = read("res.users", [UID], ["company_id"])[0]["company_id"][0]
warehouse = sread("stock.warehouse", [["company_id", "=", company_id]], ["id", "name", "lot_stock_id", "in_type_id", "int_type_id", "view_location_id"], limit=1)[0]

# ---------------------------------------------------------------- 1. the articles
step("1. The articles")
categories = {}
for name in ("Clothing", "Furniture", "Appliances"):
    categories[name] = get_or_create("product.category", [["name", "=ilike", name]], {"name": name}, f"category {name}")

ARTICLES = [
    ("Winter Coat", "Clothing", 12.0, "A warm wool coat, perfect for Luxembourg winters. Freshly cleaned."),
    ("Denim Jacket", "Clothing", 8.0, "Classic denim jacket in great condition, size M."),
    ("Summer Dress", "Clothing", 6.0, "Light flowery dress, ideal for sunny days."),
    ("Oak Dining Table", "Furniture", 60.0, "Solid oak table for six, a few charming marks of life."),
    ("Bookshelf", "Furniture", 25.0, "Five-shelf pine bookcase, sturdy and ready for your books."),
    ("Armchair", "Furniture", 35.0, "Comfortable velvet armchair, perfect for reading."),
    ("Toaster", "Appliances", 7.0, "Two-slot toaster, tested and working perfectly."),
    ("Microwave Oven", "Appliances", 30.0, "800 W microwave, cleaned and tested by our volunteers."),
]
article_ids = {}
for name, categ, price, description in ARTICLES:
    article_ids[name] = get_or_create("product.template", [["name", "=ilike", name]], {
        "name": name,
        "type": "consu",
        "is_storable": True,
        "available_in_pos": True,
        "sale_ok": True,
        "list_price": price,
        "categ_id": categories[categ],
        "description_sale": description,
        "taxes_id": [(5, 0, 0)],
    }, f"article {name}")
# make sure the existing ones have everything the checker wants
call("product.template", "write", list(article_ids.values()), {
    "is_storable": True, "available_in_pos": True, "sale_ok": True, "taxes_id": [(5, 0, 0)],
})
for tmpl_id, (name, categ, price, description) in zip(article_ids.values(), ARTICLES):
    call("product.template", "write", [tmpl_id], {"list_price": price, "categ_id": categories[categ], "description_sale": description})
variants = {t["id"]: t["product_variant_id"][0] for t in read("product.template", list(article_ids.values()), ["product_variant_id"])}

# ---------------------------------------------------------------- 2. the shop and the social pricelist
step("2. The shop and the social pricelist")
pos_config_id = search("pos.config", [["company_id", "=", company_id]], limit=1)
if pos_config_id:
    pos_config_id = pos_config_id[0]
    print("  = shop exists (pos.config", pos_config_id, ")")
else:
    pos_config_id = call("pos.config", "create", {"name": "Charity Shop"})
    print("  + shop created (pos.config", pos_config_id, ")")
pricelist_id = get_or_create("product.pricelist", [["name", "=ilike", "Social Rate"]], {
    "name": "Social Rate",
    "item_ids": [(0, 0, {
        "applied_on": "2_product_category",
        "categ_id": categories["Clothing"],
        "compute_price": "discount",
        "price_discount": 50,
    })],
}, "pricelist Social Rate")
config = read("pos.config", [pos_config_id], ["pricelist_id", "available_pricelist_ids", "payment_method_ids", "current_session_id", "use_pricelist"])[0]
available = set(config["available_pricelist_ids"]) | {pricelist_id}
if config["pricelist_id"]:
    available.add(config["pricelist_id"][0])
vals = {"use_pricelist": True, "available_pricelist_ids": [(6, 0, list(available))]}
if not config["pricelist_id"]:
    vals["pricelist_id"] = pricelist_id
call("pos.config", "write", [pos_config_id], vals)
print("  = pricelists enabled on the shop, Social Rate available")

# ---------------------------------------------------------------- 3. the donation
step("3. The donation")
donor_id = get_or_create("res.partner", [["name", "=ilike", "Anonymous Donor"]], {"name": "Anonymous Donor"}, "contact Anonymous Donor")
supplier_loc = search("stock.location", [["usage", "=", "supplier"]], limit=1)[0]
done_receipt = search("stock.picking", [["partner_id", "=", donor_id], ["picking_type_code", "=", "incoming"], ["state", "=", "done"]], limit=1)
if done_receipt:
    print("  = validated receipt exists (stock.picking", done_receipt[0], ")")
else:
    picking_id = call("stock.picking", "create", {
        "partner_id": donor_id,
        "picking_type_id": warehouse["in_type_id"][0],
        "location_id": supplier_loc,
        "location_dest_id": warehouse["lot_stock_id"][0],
        "move_ids": [(0, 0, {
            "product_id": variants[article_ids[name]],
            "product_uom_qty": qty,
            "location_id": supplier_loc,
            "location_dest_id": warehouse["lot_stock_id"][0],
        }) for name, qty in (("Winter Coat", 3), ("Denim Jacket", 2), ("Summer Dress", 4), ("Toaster", 2), ("Bookshelf", 1), ("Armchair", 1), ("Oak Dining Table", 1), ("Microwave Oven", 1))],
    })
    call("stock.picking", "action_confirm", [picking_id])
    moves = sread("stock.move", [["picking_id", "=", picking_id]], ["id", "product_uom_qty"])
    for move in moves:
        call("stock.move", "write", [move["id"]], {"quantity": move["product_uom_qty"], "picked": True})
    result = call("stock.picking", "button_validate", [picking_id])
    if isinstance(result, dict) and result.get("res_model"):
        # a confirmation wizard: confirm it
        wizard_model = result["res_model"]
        ctx = result.get("context") or {}
        wiz = call(wizard_model, "create", {}, context=ctx)
        method = "process" if wizard_model != "stock.backorder.confirmation" else "process_cancel_backorder"
        call(wizard_model, method, [wiz], context=ctx)
    state = read("stock.picking", [picking_id], ["state"])[0]["state"]
    print(f"  + receipt {picking_id} validated: state={state}")
    assert state == "done", "receipt not done"

# ---------------------------------------------------------------- 4. the till: 3 sales
step("4. The till")
config = read("pos.config", [pos_config_id], ["payment_method_ids", "current_session_id", "name", "pricelist_id"])[0]
payment_methods = sread("pos.payment.method", [["id", "in", config["payment_method_ids"]]], ["id", "name", "type"])
if not payment_methods:
    cash_journal = search("account.journal", [["type", "=", "cash"], ["company_id", "=", company_id]], limit=1)
    pm_id = call("pos.payment.method", "create", {"name": "Cash", "type": "cash", "journal_id": cash_journal[0] if cash_journal else False, "company_id": company_id})
    call("pos.config", "write", [pos_config_id], {"payment_method_ids": [(4, pm_id)]})
    payment_methods = [{"id": pm_id, "name": "Cash", "type": "cash"}]
cash_methods = [pm for pm in payment_methods if pm["type"] == "cash"] or [pm for pm in payment_methods if pm["type"] == "bank"] or payment_methods
payment_method_id = cash_methods[0]["id"]
print("  = payment method:", cash_methods[0]["name"])

paid_orders = sread("pos.order", [["state", "in", ["paid", "done", "invoiced"]], ["session_id.state", "=", "closed"]], ["id", "pricelist_id"])
social_closed = [o for o in paid_orders if o["pricelist_id"] and o["pricelist_id"][0] == pricelist_id]
if len(paid_orders) >= 3 and social_closed:
    print(f"  = {len(paid_orders)} paid orders in closed sessions already, one at the Social Rate: nothing to do")
else:
    # open a session
    session_id = config["current_session_id"] and config["current_session_id"][0]
    if not session_id:
        call("pos.config", "open_ui", [pos_config_id])
        session_id = read("pos.config", [pos_config_id], ["current_session_id"])[0]["current_session_id"][0]
        print("  + session opened (pos.session", session_id, ")")
    else:
        print("  = session already open (pos.session", session_id, ")")
    session = read("pos.session", [session_id], ["state"])[0]
    if session["state"] == "opening_control":
        call("pos.session", "set_opening_control", [session_id], 0.0, "")
        print("  = opening control done")

    customer_id = search("res.partner", [["name", "ilike", "Josiane Feller"]], limit=1)
    customer_id = customer_id[0] if customer_id else donor_id
    default_pricelist = config["pricelist_id"] and config["pricelist_id"][0] or pricelist_id

    def make_sale(lines, pricelist, partner=False):
        order_lines, total = [], 0.0
        for name, qty in lines:
            tmpl = read("product.template", [article_ids[name]], ["list_price", "categ_id"])[0]
            price = tmpl["list_price"]
            if pricelist == pricelist_id and tmpl["categ_id"][0] == categories["Clothing"]:
                price = price / 2
            order_lines.append((0, 0, {
                "product_id": variants[article_ids[name]],
                "qty": qty,
                "price_unit": price,
                "price_subtotal": price * qty,
                "price_subtotal_incl": price * qty,
                "tax_ids": [(5, 0, 0)],
                "full_product_name": name,
            }))
            total += price * qty
        order_id = call("pos.order", "create", {
            "session_id": session_id,
            "partner_id": partner,
            "pricelist_id": pricelist,
            "lines": order_lines,
            "amount_tax": 0.0,
            "amount_total": total,
            "amount_paid": 0.0,
            "amount_return": 0.0,
        })
        call("pos.order", "add_payment", [order_id], {
            "pos_order_id": order_id,
            "payment_method_id": payment_method_id,
            "amount": total,
        })
        call("pos.order", "action_pos_order_paid", [order_id])
        state = read("pos.order", [order_id], ["state", "amount_total"])[0]
        print(f"  + sale {order_id}: {total:.2f}, pricelist {pricelist}, state={state['state']}")
        return order_id

    existing_open = sread("pos.order", [["session_id", "=", session_id], ["state", "in", ["paid", "done", "invoiced"]]], ["id", "pricelist_id"])
    needed = max(0, 3 - len(existing_open))
    has_social = any(o["pricelist_id"] and o["pricelist_id"][0] == pricelist_id for o in existing_open)
    if needed or not has_social:
        make_sale([("Winter Coat", 1), ("Toaster", 1)], pricelist_id, customer_id)   # Social Rate + a customer
        make_sale([("Bookshelf", 1)], default_pricelist)
        make_sale([("Summer Dress", 2), ("Denim Jacket", 1)], default_pricelist)

    # -------------------------------------------------------------- 5. close the session
    step("5. Closing time")
    # Odoo 20: the till closes with close_session_from_ui (no difference to declare: counted = expected)
    try:
        result = call("pos.session", "close_session_from_ui", [session_id], {})
    except Exception as e:  # noqa: BLE001
        result = "error: " + str(e).splitlines()[-1][:300]
    state = read("pos.session", [session_id], ["state"])[0]["state"]
    if state != "closed":
        print("  close_session_from_ui returned:", str(result)[:400])
        for method in ("action_pos_session_closing_control", "action_pos_session_validate"):
            try:
                call("pos.session", method, [session_id])
            except Exception as e:  # noqa: BLE001
                print(f"  {method} failed:", str(e).splitlines()[-1][:200])
            state = read("pos.session", [session_id], ["state"])[0]["state"]
            if state == "closed":
                break
    print("  session state:", state)

# ---------------------------------------------------------------- 6. the lost chest of drawers
step("6. The lost chest of drawers")
lot = sread("stock.lot", [["name", "=", "CAD-1924-02"]], ["id", "product_id"], limit=1)[0]
workshop_id = get_or_create("stock.location", [["name", "=ilike", "Repair Workshop"]], {
    "name": "Repair Workshop", "usage": "internal", "location_id": warehouse["view_location_id"][0],
}, "location Repair Workshop")
call("stock.location", "write", [workshop_id], {"usage": "internal"})
quants = sread("stock.quant", [["lot_id", "=", lot["id"]], ["quantity", ">", 0]], ["id", "location_id", "quantity"])
print("  chest CAD-1924-02 is in:", [(q["location_id"][1], q["quantity"]) for q in quants])
if any(q["location_id"][0] == workshop_id for q in quants):
    print("  = already in the Repair Workshop")
else:
    src = quants[0]["location_id"][0]
    picking_id = call("stock.picking", "create", {
        "picking_type_id": warehouse["int_type_id"][0],
        "location_id": src,
        "location_dest_id": workshop_id,
        "move_ids": [(0, 0, {
            "product_id": lot["product_id"][0],
            "product_uom_qty": 1,
            "location_id": src,
            "location_dest_id": workshop_id,
        })],
    })
    call("stock.picking", "action_confirm", [picking_id])
    call("stock.picking", "action_assign", [picking_id])
    move_id = search("stock.move", [["picking_id", "=", picking_id]])[0]
    lines = sread("stock.move.line", [["move_id", "=", move_id]], ["id", "lot_id", "quantity"])
    print("  reserved lines:", [(l["lot_id"] and l["lot_id"][1], l["quantity"]) for l in lines])
    if not lines:
        call("stock.move.line", "create", {
            "move_id": move_id, "picking_id": picking_id, "product_id": lot["product_id"][0], "lot_id": lot["id"],
            "quantity": 1, "location_id": src, "location_dest_id": workshop_id,
        })
    else:
        for line in lines:
            vals = {"quantity": 1}
            if not line["lot_id"] or line["lot_id"][0] != lot["id"]:
                vals["lot_id"] = lot["id"]
            call("stock.move.line", "write", [line["id"]], vals)
    call("stock.move", "write", [move_id], {"picked": True})
    result = call("stock.picking", "button_validate", [picking_id])
    state = read("stock.picking", [picking_id], ["state"])[0]["state"]
    print(f"  + internal transfer {picking_id}: state={state}")
    quants = sread("stock.quant", [["lot_id", "=", lot["id"]], ["quantity", ">", 0]], ["location_id", "quantity"])
    print("  chest CAD-1924-02 is now in:", [(q["location_id"][1], q["quantity"]) for q in quants])

# ---------------------------------------------------------------- bonus: the analysis by category
step("Bonus: sales analysis by category")
get_or_create("ir.filters", [["model_id", "=", "report.pos.order"], ["name", "=", "Sales by product category"]], {
    "name": "Sales by product category",
    "model_id": "report.pos.order",
    "domain": "[]",
    "context": "{'group_by': ['product_categ_id'], 'pivot_measures': ['price_total']}",
}, "favorite Sales by product category")

# ---------------------------------------------------------------- the checker
step("Check")
challenge = sread("trivia.challenge", [["code", "=", "reuse_center"]], ["id", "name"])[0]
try:
    call("trivia.challenge", "action_run_checker", [challenge["id"]])
except Exception as e:  # noqa: BLE001
    print("  CHECKER CRASHED:", str(e)[:800])
rec = read("trivia.challenge", [challenge["id"]], ["check_results", "requirement_count", "requirement_total", "star_count", "star_total", "state"])[0]
for s in rec["check_results"] or []:
    mark = "PASS" if s.get("passed") else "FAIL"
    print(f"  [{mark}] {s.get('label')}{' (bonus)' if s.get('bonus') else ''}{'' if s.get('passed') else ' -> ' + str(s.get('message'))}")
print(f"  => {rec['requirement_count']}/{rec['requirement_total']} requirements, stars {rec['star_count']}/{rec['star_total']}, state={rec['state']}")

env.cr.commit()
print('committed')
