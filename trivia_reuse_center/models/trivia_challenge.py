from odoo import models

from odoo.addons.trivia_hackathon.models.trivia_challenge import name_matches, require

from ..hooks import LOST_SERIAL

# the names asked by the statement: the players may type them in English or in French
CLOTHING = ["Clothing", "Vêtements"]
FURNITURE = ["Furniture", "Meubles"]
APPLIANCES = ["Appliances", "Électro"]
SOCIAL_RATE = ["Social Rate", "Tarif social"]
ANONYMOUS_DONOR = ["Anonymous Donor", "Donateur anonyme"]
REPAIR_WORKSHOP = ["Repair Workshop", "Atelier réparation"]


class TriviaChallenge(models.Model):
    _inherit = "trivia.challenge"

    # ----------------------------------------------------------------------------
    # Checker of the challenge "Second Life": DO NOT MODIFY
    # ----------------------------------------------------------------------------

    def _check_reuse_center(self):
        _ = self._get_report_env()._
        env = self.env

        def find(model, name, message):
            records = env[model].search([]).filtered(lambda record: name_matches(record.name, name))
            require(records, message)
            return records

        # the 3 categories of the articles: (name displayed in the language of the player, accepted names)
        categories = [(_("Clothing"), CLOTHING), (_("Furniture"), FURNITURE), (_("Appliances"), APPLIANCES)]

        def get_articles():
            records = env["product.category"]
            for label, names in categories:
                records |= find("product.category", names, _("There is no product category %(name)s (mission 1).", name=label))
            return env["product.template"].search([("is_storable", "=", True), ("categ_id", "in", records.ids)])

        def get_pricelist():
            return find("product.pricelist", SOCIAL_RATE, _("There is no pricelist Social Rate (mission 2)."))

        def get_orders():
            return env["pos.order"].search([("state", "in", ("paid", "done"))])

        def check_articles():
            articles = get_articles()
            require(len(articles) >= 8, _(
                "%(count)s article(s) whose stock is tracked in the categories Clothing, Furniture and Appliances: "
                "create 8 of them (mission 1).", count=len(articles),
            ))
            used = [names for _label, names in categories
                    if any(name_matches(article.categ_id.name, names) for article in articles)]
            require(len(used) == len(categories), _("The articles must use the 3 categories Clothing, Furniture and Appliances."))
            require(all(article.list_price > 0 for article in articles), _("Each article must have a sales price."))

        def check_pricelist():
            articles = get_articles().filtered("list_price")
            require(articles, _("Create the articles first (mission 1)."))
            discounted = [
                article for article in articles
                for pricelist in get_pricelist()
                if abs(pricelist._get_product_price(article.product_variant_id, 1.0) - article.list_price / 2) < 0.01
            ]
            require(discounted, _("The Social Rate does not give 50 % off any article."))

        def check_donation():
            receipts = env["stock.picking"].search([("picking_type_code", "=", "incoming"), ("state", "=", "done")])
            require(receipts.filtered(lambda receipt: name_matches(receipt.partner_id.name, ANONYMOUS_DONOR)),
                    _("No validated receipt from the contact Anonymous Donor yet (mission 3)."))

        def check_sales():
            orders = get_orders()
            require(len(orders) >= 3, _(
                "%(count)s paid sale(s) at the till: make 3 sales (mission 4).", count=len(orders),
            ))
            require(orders.filtered(lambda order: name_matches(order.pricelist_id.name, SOCIAL_RATE)),
                    _("No sale at the Social Rate yet (mission 4)."))

        def check_closed():
            # the sales may have been made in several sessions, all of them closed
            require(len(get_orders().filtered(lambda order: order.session_id.state == "closed")) >= 3,
                    _("No closed session of the till with your sales yet: close the session (mission 5)."))

        def check_chest():
            lot = env["stock.lot"].search([("name", "=", LOST_SERIAL)], limit=1)
            quants = env["stock.quant"].search([("lot_id", "=", lot.id), ("quantity", ">", 0)])
            in_workshop = quants.filtered(lambda quant: name_matches(quant.location_id.name, REPAIR_WORKSHOP))
            if not in_workshop:
                others = env["stock.quant"].search([
                    ("product_id", "=", lot.product_id.id), ("quantity", ">", 0),
                ]).filtered(lambda quant: name_matches(quant.location_id.name, REPAIR_WORKSHOP))
                require(not others, _(
                    "There is a chest of drawers in the Repair Workshop, but not the one Josiane Feller brought back: "
                    "check its serial number (mission 6).",
                ))
            require(in_workshop, _("The chest of drawers of Josiane Feller is not in a location Repair Workshop yet (mission 6)."))
            require(in_workshop.location_id.usage == "internal", _("The Repair Workshop must be an internal location."))

        def check_descriptions():
            articles = get_articles()
            require(articles and all(article.description_sale for article in articles),
                    _("Some articles have no sales description."))

        def check_category_rule():
            items = get_pricelist().item_ids
            require(items.filtered(lambda item: item.applied_on == "2_product_category"),
                    _("The rules of the Social Rate are not limited to a product category."))

        def check_customer():
            require(get_orders().filtered("partner_id"), _("No sale at the till has a customer."))

        def check_analysis():
            filters = env["ir.filters"].search([("model_id", "in", ["report.pos.order", "pos.order", "pos.order.line"])])
            require(any("categ" in (favorite.context or "") for favorite in filters),
                    _("No favorite of the sales is grouped by product category."))

        return [self._run_step(label, step, bonus=bonus) for label, step, bonus in [
            (_("1. The articles"), check_articles, False),
            (_("2. The social pricelist"), check_pricelist, False),
            (_("3. A donation is received"), check_donation, False),
            (_("4. Sales at the till"), check_sales, False),
            (_("5. The session is closed"), check_closed, False),
            (_("6. The lost chest of drawers is in the workshop"), check_chest, False),
            (_("Sales descriptions of the articles"), check_descriptions, True),
            (_("Social pricelist limited to a category"), check_category_rule, True),
            (_("A customer on a ticket"), check_customer, True),
            (_("Analysis of the sales by category"), check_analysis, True),
        ]]
