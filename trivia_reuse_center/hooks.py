from datetime import timedelta

from markupsafe import Markup

from odoo import Command, fields

LOST_SERIAL = "CAD-1924-02"  # the chest of drawers brought back by Josiane Feller (mission 6)


def post_init_hook(env):
    # no till here: the chart of accounts, needed by a till, is only installed at the end of the
    # installation. The participants create it (missions 2 and 4), with the "Retail" tile of the Point of Sale.
    _enable_inventory_features(env)
    _setup_lost_chest_of_drawers(env)


def _enable_inventory_features(env):
    """ The serial numbers and the storage locations are needed to follow the lost chest of drawers. """
    env["res.config.settings"].create({
        "group_stock_production_lot": True,
        "group_stock_multi_locations": True,
    }).execute()


def _setup_lost_chest_of_drawers(env):
    """ Mission 6: three Art Deco chests of drawers were donated. One is still for sale, one was sold to
    Marco Bettendorf, and the one sold to Josiane Feller was brought back and put aside in a forgotten
    location, outside of the stock for sale. """
    warehouse = env.ref("stock.warehouse0")
    lost_and_found = env["stock.location"].create({
        "name": "Lost & Found",
        "usage": "internal",
        "location_id": warehouse.view_location_id.id,
    })
    # "Antiques": a name which does not match the categories of the articles (Furniture, Meubles), see the checker
    category = env["product.category"].create({"name": "Antiques"})
    chest = env["product.product"].create({
        "name": "Art Deco Chest of Drawers",
        "is_storable": True,
        "tracking": "serial",
        "list_price": 180,
        "categ_id": category.id,
    })
    if "fr_FR" in dict(env["res.lang"].get_installed()):
        category.update_field_translations("name", {"fr_FR": "Mobilier ancien"})
        chest.product_tmpl_id.update_field_translations("name", {"fr_FR": "Commode Art déco"})
    lots = env["stock.lot"].create([
        {"name": f"CAD-1924-0{index}", "product_id": chest.id} for index in (1, 2, 3)
    ])
    for lot in lots:
        env["stock.quant"].with_context(inventory_mode=True).create({
            "product_id": chest.id,
            "location_id": warehouse.lot_stock_id.id,
            "lot_id": lot.id,
            "inventory_quantity": 1,
        })._apply_inventory()

    Partner = env["res.partner"]
    josiane = Partner.create({"name": "Josiane Feller", "city": "Esch-sur-Alzette", "email": "josiane.feller@example.com"})
    marco = Partner.create({"name": "Marco Bettendorf", "city": "Luxembourg", "email": "marco.bettendorf@example.com"})
    now = fields.Datetime.now()
    _deliver(env, chest, lots[2], marco, now - timedelta(days=52))
    delivery = _deliver(env, chest, lots[1], josiane, now - timedelta(days=41))
    _bring_back(env, delivery, lots[1], lost_and_found, now - timedelta(days=12))


def _deliver(env, product, lot, customer, date):
    warehouse = env.ref("stock.warehouse0")
    picking = env["stock.picking"].create({
        "picking_type_id": warehouse.out_type_id.id,
        "partner_id": customer.id,
        "location_id": warehouse.lot_stock_id.id,
        "location_dest_id": env.ref("stock.stock_location_customers").id,
        "move_ids": [Command.create({
            "product_id": product.id,
            "product_uom_qty": 1,
            "location_id": warehouse.lot_stock_id.id,
            "location_dest_id": env.ref("stock.stock_location_customers").id,
        })],
    })
    _validate(picking, lot, date)
    return picking


def _bring_back(env, delivery, lot, location, date):
    # Odoo 20: the return is created from the delivery itself (no more stock.return.picking wizard).
    # Like _create_return(), without its chatter message (its template logs a warning in Odoo 20).
    return_picking = delivery.copy({
        **delivery._prepare_return_picking_default_values(),
        "location_dest_id": location.id,
        "note": Markup(
            "<p>🇬🇧 Brought back by the customer: a drawer is broken. Put aside in the <i>Lost &amp; Found</i>, "
            "until somebody takes it to the repair workshop.</p>"
            "<p>🇫🇷 Rapportée par la cliente : un tiroir est cassé. Mise de côté dans le <i>Lost &amp; Found</i>, "
            "en attendant que quelqu'un l'emmène à l'atelier de réparation.</p>"
        ),
    })
    env["stock.move"].create([
        move.copy_data(return_picking._prepare_return_move_default_values(move))[0] for move in delivery.move_ids
    ])
    return_picking.action_return_all()
    _validate(return_picking, lot, date)


def _validate(picking, lot, date):
    """ Validate ``picking`` with the serial number ``lot``, as if it had been done on ``date``. """
    picking.action_confirm()
    picking.action_assign()
    picking.move_line_ids.lot_id = lot
    picking.move_ids.picked = True
    picking._action_done()
    picking.date_done = date
