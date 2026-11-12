# Food Bank (trivia_food_bank): the functional challenge, done through the ORM.
# Runs inside "odoo-bin shell" (Odoo.sh shell):   cd ~/src/user && odoo-bin shell < food_bank_shell.py
# Safe to run several times: everything is searched before being created.
import csv
import io
import os

# the shell runs as the system user (uid 1): act as the administrator (uid 2)
env = env(user=2)
print("db:", env.cr.dbname, "uid:", env.uid)

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd(), "trivia_food_bank", "static", "data", "donors.csv")
if not os.path.exists(CSV_FILE):
    for candidate in ("trivia_food_bank/static/data/donors.csv", "/mnt/extra-addons/trivia_food_bank/static/data/donors.csv",
                      os.path.expanduser("~/src/user/trivia_food_bank/static/data/donors.csv")):
        if os.path.exists(candidate):
            CSV_FILE = candidate
            break
print("donors file:", CSV_FILE)


def step(title):
    print(f"\n### {title}")


def get_or_create(model, domain, vals, label):
    record = env[model].search(domain, limit=1)
    if record:
        print(f"  = {label} exists")
        return record
    record = env[model].create(vals)
    print(f"  + {label} created")
    return record


# ------------------------------------------------------------------ 1. the donors
step("1. The donors")
Partner = env["res.partner"]
Tag = env["res.partner.category"]
tags = {name: get_or_create("res.partner.category", [("name", "=ilike", name)], {"name": name}, f"tag {name}")
        for name in ("Donor", "Volunteer", "Company")}
rows = list(csv.DictReader(io.open(CSV_FILE, encoding="utf-8-sig")))
partners = {}
for row in rows:
    partner = Partner.search([("email", "=ilike", row["Email"])], limit=1)
    vals = {"name": row["Name"], "email": row["Email"], "phone": row["Phone"], "city": row["City"]}
    if row["Tax ID"]:
        vals["vat"] = row["Tax ID"]
    if not partner:
        try:
            partner = Partner.with_context(no_vat_validation=True).create(vals)
        except Exception as e:  # noqa: BLE001
            print("  (vat refused, creating without:", str(e).splitlines()[-1][:100], ")")
            env.cr.rollback() if False else None
            vals.pop("vat", None)
            partner = Partner.create(vals)
        print("  + contact", row["Name"])
    else:
        print("  = contact", row["Name"], "exists")
    partners[row["Email"]] = (partner, row)
company = partners["contact@boulangerie-kremer.example.lu"][0]
for email, (partner, row) in partners.items():
    if row["Related Company"]:
        parent = Partner.search([("name", "=ilike", row["Related Company"]), ("parent_id", "=", False)], limit=1) or company
        if partner.parent_id != parent:
            partner.parent_id = parent
for email, (partner, row) in partners.items():
    wanted = tags["Donor"]
    if email in ("elise.bernard@example.lu", "marc.kieffer@example.lu"):
        wanted |= tags["Volunteer"]
    if email == "contact@boulangerie-kremer.example.lu":
        wanted |= tags["Company"]
    partner.category_id = [(4, tag.id) for tag in wanted]
if not company.is_company:
    company.is_company = True
print("  company is_company:", company.is_company, "| employees:", company.child_ids.mapped("name"))

# ------------------------------------------------------------------ 2. the products
step("2. The products")
donations = get_or_create("product.category", [("name", "=ilike", "Donations")], {"name": "Donations"}, "category Donations")
zero_tax = env["account.tax"].search([("type_tax_use", "=", "sale"), ("amount", "=", 0), ("amount_type", "=", "percent")], limit=1)
if not zero_tax:
    try:
        zero_tax = env["account.tax"].create({"name": "0%", "amount": 0, "amount_type": "percent", "type_tax_use": "sale"})
        print("  + tax 0% created")
    except Exception as e:  # noqa: BLE001
        print("  (no 0% tax:", str(e).splitlines()[-1][:120], ")")
products = {}
for name, price in (("Free Donation", 0.0), ("Membership Fee", 25.0)):
    product = get_or_create("product.template", [("name", "=ilike", name)],
                            {"name": name, "type": "service", "list_price": price, "categ_id": donations.id}, f"product {name}")
    vals = {"type": "service", "categ_id": donations.id, "list_price": price}
    if zero_tax:
        vals["taxes_id"] = [(6, 0, zero_tax.ids)]
    product.write(vals)
    products[name] = product

# ------------------------------------------------------------------ 3. the patrons (CRM)
step("3. The patrons")
team = get_or_create("crm.team", [("name", "=ilike", "Patronage")], {"name": "Patronage"}, "team Patronage")
stages = {}
for sequence, name in enumerate(("Identified", "Contacted", "Proposal Sent", "Signed"), start=1):
    stage = env["crm.stage"].search([("name", "=ilike", name), ("team_ids", "in", team.ids)], limit=1)
    if not stage:
        stage = env["crm.stage"].create({"name": name, "sequence": sequence, "team_ids": [(6, 0, team.ids)]})
        print("  + stage", name)
    stages[name] = stage
if "is_won" in env["crm.stage"]._fields:
    stages["Signed"].is_won = True
Lead = env["crm.lead"].with_context(active_test=False)
leads = Lead.search([("team_id", "=", team.id), ("type", "=", "opportunity")])
patrons = [("Boulangerie Kremer sponsorship", "Identified", 5000), ("Garage Weber partnership", "Contacted", 3000), ("Café Am Eck gift", "Proposal Sent", 1500)]
for lead_name, stage_name, revenue in patrons:
    if not Lead.search([("name", "=", lead_name)]):
        Lead.create({"name": lead_name, "type": "opportunity", "team_id": team.id, "stage_id": stages[stage_name].id,
                     "expected_revenue": revenue, "partner_id": company.id if "Kremer" in lead_name else False})
        print("  + opportunity", lead_name)
leads = Lead.search([("team_id", "=", team.id), ("type", "=", "opportunity")])
if not any(lead.won_status == "won" for lead in leads):
    leads[0].action_set_won()
    print("  + opportunity won:", leads[0].name)
try:
    if not env["mail.activity"].search_count([("res_model", "=", "crm.lead"), ("res_id", "in", leads.ids)]):
        leads[-1].activity_schedule("mail.mail_activity_data_todo", summary="Call the patron")
        print("  + activity planned")
except Exception as e:  # noqa: BLE001
    print("  (activity skipped:", str(e).splitlines()[-1][:120], ")")

# ------------------------------------------------------------------ 4. the thank-you mailing
step("4. The mailing")
mailing_list = get_or_create("mailing.list", [("name", "=ilike", "Donors")], {"name": "Donors"}, "mailing list Donors")
existing = {(c.email or "").lower() for c in mailing_list.contact_ids}
for email, (partner, row) in partners.items():
    if email.lower() not in existing:
        env["mailing.contact"].create({"name": partner.name, "email": email, "list_ids": [(6, 0, mailing_list.ids)]})
print("  list Donors has", len(mailing_list.contact_ids), "contacts")
mailing = env["mailing.mailing"].search([("contact_list_ids", "in", mailing_list.ids)], limit=1)
if not mailing:
    mailing = env["mailing.mailing"].create({
        "subject": "Thank you for your donation!",
        "contact_list_ids": [(6, 0, mailing_list.ids)],
        "mailing_model_id": env.ref("mass_mailing.model_mailing_list").id,
        "body_html": "<p>Dear donor,</p><p>Thank you for your generosity: thanks to you, our food bank keeps its doors open.</p>",
    })
    print("  + mailing created")
if mailing.state == "draft":
    mailing.action_launch()
    print("  + mailing launched, state:", mailing.state)
try:
    env["mailing.mailing"]._process_mass_mailing_queue()
    print("  queue processed, traces:", env["mailing.trace"].search_count([("mass_mailing_id", "=", mailing.id)]))
except Exception as e:  # noqa: BLE001
    print("  (queue not processed:", str(e).splitlines()[-1][:160], ")")

# ------------------------------------------------------------------ 5. the donations (invoices)
step("5. The donation invoices")
donor_partners = [partner for partner, row in partners.values()]
product_variants = {name: tmpl.product_variant_id for name, tmpl in products.items()}
posted = env["account.move"].search([("move_type", "=", "out_invoice"), ("state", "=", "posted"),
                                     ("partner_id", "in", [p.id for p in donor_partners]),
                                     ("invoice_line_ids.product_id", "in", [v.id for v in product_variants.values()])])
plan = [("sofia.martins@example.lu", "Membership Fee", 25.0), ("patrick.steffen@example.lu", "Free Donation", 50.0), ("nora.wirtz@example.lu", "Free Donation", 20.0)]
created = env["account.move"]
for email, product_name, amount in plan:
    if len(posted) + len(created) >= 3:
        break
    invoice = env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": partners[email][0].id,
        "invoice_line_ids": [(0, 0, {"product_id": product_variants[product_name].id, "quantity": 1, "price_unit": amount,
                                     "name": product_name})],
    })
    invoice.action_post()
    created |= invoice
    print(f"  + invoice {invoice.name} for {partners[email][0].name}: {product_name} {amount}, state={invoice.state}")
all_posted = posted | created
try:
    paid = all_posted.filtered(lambda m: m.payment_state in ("paid", "in_payment"))
    if all_posted and not paid:
        wizard = env["account.payment.register"].with_context(active_model="account.move", active_ids=all_posted[0].ids).create({})
        wizard.action_create_payments()
        print("  + a donation was paid:", all_posted[0].payment_state)
except Exception as e:  # noqa: BLE001
    print("  (payment skipped:", str(e).splitlines()[-1][:160], ")")
get_or_create("ir.filters", [("model_id", "=", "account.invoice.report"), ("name", "=", "Invoices by donor")], {
    "name": "Invoices by donor",
    "model_id": "account.invoice.report",
    "domain": "[]",
    "context": "{'group_by': ['partner_id'], 'pivot_measures': ['price_subtotal']}",
}, "favorite Invoices by donor")

# ------------------------------------------------------------------ bonus: Company Number on the contacts
step("Bonus: Company Number")
if not env["ir.model.fields"].search_count([("model", "=", "res.partner"), ("state", "=", "manual")]):
    env["ir.model.fields"].create({
        "name": "x_company_number", "field_description": "Company Number", "ttype": "char",
        "model_id": env["ir.model"]._get("res.partner").id, "state": "manual",
    })
    print("  + field x_company_number created")
else:
    print("  = a custom field exists on the contacts")

# ------------------------------------------------------------------ the checker
step("Check")
challenge = env["trivia.challenge"].search([("code", "=", "food_bank")], limit=1)
challenge.action_run_checker()
for result in challenge.check_results or []:
    print(f"  [{'PASS' if result.get('passed') else 'FAIL'}] {result.get('label')}{' (bonus)' if result.get('bonus') else ''}"
          f"{'' if result.get('passed') else ' -> ' + str(result.get('message'))}")
print(f"  => {challenge.requirement_count}/{challenge.requirement_total} requirements, stars {challenge.star_count}/{challenge.star_total}, state={challenge.state}")
env.cr.commit()
print("committed")
