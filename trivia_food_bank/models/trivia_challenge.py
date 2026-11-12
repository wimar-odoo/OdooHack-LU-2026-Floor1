from odoo import models

from odoo.addons.trivia_hackathon.models.trivia_challenge import name_matches, normalize, require

# the donors of static/data/donors.csv: {email: name}
DONORS = {
    "contact@boulangerie-kremer.example.lu": "Boulangerie Kremer",
    "paul@boulangerie-kremer.example.lu": "Paul Kremer",
    "anne@boulangerie-kremer.example.lu": "Anne Kremer",
    "elise.bernard@example.lu": "Élise Bernard",
    "marc.kieffer@example.lu": "Marc Kieffer",
    "sofia.martins@example.lu": "Sofia Martins",
    "patrick.steffen@example.lu": "Patrick Steffen",
    "nora.wirtz@example.lu": "Nora Wirtz",
    "hugo.reding@example.lu": "Hugo Reding",
    "chloe.lentz@example.lu": "Chloé Lentz",
}
COMPANY = "contact@boulangerie-kremer.example.lu"
EMPLOYEES = ("paul@boulangerie-kremer.example.lu", "anne@boulangerie-kremer.example.lu")
VOLUNTEERS = ("elise.bernard@example.lu", "marc.kieffer@example.lu")
# the names asked by the statement: the players may type them in English or in French
DONOR = ["Donor", "Donateur"]
VOLUNTEER = ["Volunteer", "Bénévole"]
COMPANY_TAG = ["Company", "Entreprise"]
DONATIONS = ["Donations", "Dons"]
FREE_DONATION = ["Free Donation", "Don libre"]
MEMBERSHIP_FEE = ["Membership Fee", "Cotisation membre"]
PATRONAGE = ["Patronage", "Mécénat"]
DONORS_LIST = ["Donors", "Donateurs"]  # "Donor" or "Donateur", like the tag, is accepted too


class TriviaChallenge(models.Model):
    _inherit = "trivia.challenge"

    # ----------------------------------------------------------------------------
    # Checker of the challenge "Donors and Patrons": DO NOT MODIFY
    # ----------------------------------------------------------------------------

    def _check_food_bank(self):
        _ = self._get_report_env()._
        env = self.env

        def get_donors():
            partners = env["res.partner"].search([("email", "in", list(DONORS))])
            return {normalize(partner.email): partner for partner in partners}

        def require_donors():
            donors = get_donors()
            require(len(donors) == len(DONORS), _("Import the donors first (mission 1)."))
            return donors

        def has_tag(partner, name):
            return any(name_matches(tag.name, name) for tag in partner.category_id)

        def find(model, name, message):
            records = env[model].search([]).filtered(lambda record: name_matches(record.name, name))
            require(records, message)
            return records[0]

        # (name displayed in the language of the player, accepted names, sales price)
        products = [(_("Free Donation"), FREE_DONATION, None), (_("Membership Fee"), MEMBERSHIP_FEE, 25)]
        # the stages of the pipeline: (name displayed in the language of the player, accepted names)
        stages = [
            (_("Identified"), ["Identified", "Identifié"]),
            (_("Contacted"), ["Contacted", "Contacté"]),
            (_("Proposal Sent"), ["Proposal Sent", "Dossier envoyé"]),
            (_("Signed"), ["Signed", "Signé"]),
        ]

        def get_products():
            return [find("product.template", names, _("There is no product %(name)s (mission 2).", name=label))
                    for label, names, _price in products]

        def get_team():
            return find("crm.team", PATRONAGE, _("There is no sales team Patronage (mission 3)."))

        def get_list():
            # all the matching lists
            lists = env["mailing.list"].search([]).filtered(lambda record: name_matches(record.name, DONORS_LIST))
            require(lists, _("There is no mailing list Donors (mission 4)."))
            return lists

        def get_invoices():
            products = env["product.product"].search([
                ("product_tmpl_id", "in", [product.id for product in get_products()]),
            ])
            return env["account.move"].search([
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("partner_id", "in", [partner.id for partner in get_donors().values()]),
                ("invoice_line_ids.product_id", "in", products.ids),
            ])

        def check_import():
            donors = get_donors()
            missing = [name for email, name in DONORS.items() if email not in donors]
            require(not missing, _(
                "These donors are not in the contacts yet: %(names)s. Import the file donors.csv (mission 1).",
                names=", ".join(missing),
            ))
            require(donors[COMPANY].is_company, _(
                "Boulangerie Kremer must be a company: in Odoo 20, a contact without parent company and with a Tax ID.",
            ))
            require(all(donors[email].parent_id == donors[COMPANY] for email in EMPLOYEES),
                    _("Paul Kremer and Anne Kremer must be contacts of the company Boulangerie Kremer."))

        def check_tags():
            donors = require_donors()
            untagged = [partner.name for partner in donors.values() if not has_tag(partner, DONOR)]
            require(not untagged, _("These contacts have no tag Donor: %(names)s.", names=", ".join(untagged)))
            require(all(has_tag(donors[email], VOLUNTEER) for email in VOLUNTEERS),
                    _("Élise Bernard and Marc Kieffer must have the tag Volunteer."))
            require(has_tag(donors[COMPANY], COMPANY_TAG), _("Boulangerie Kremer must have the tag Company."))

        def check_products():
            for product, (_label, _names, price) in zip(get_products(), products):
                require(product.type == "service", _("%(product)s must be a service.", product=product.name))
                require(name_matches(product.categ_id.name, DONATIONS),
                        _("%(product)s must be in the product category Donations.", product=product.name))
                if price is not None:
                    require(abs(product.list_price - price) < 0.001, _(
                        "%(product)s must be sold %(price)s.", product=product.name, price=price,
                    ))

        def check_pipeline():
            team = get_team()
            records = env["crm.stage"].search(["|", ("team_ids", "in", team.ids), ("team_ids", "=", False)])
            missing = [label for label, names in stages if not any(name_matches(stage.name, names) for stage in records)]
            require(not missing, _("The pipeline has no stage %(stages)s.", stages=", ".join(missing)))
            opportunities = env["crm.lead"].with_context(active_test=False).search([
                ("team_id", "=", team.id), ("type", "=", "opportunity"),
            ])
            require(len(opportunities) >= 3, _(
                "The team Patronage has %(count)s opportunity(ies): create 3 of them.", count=len(opportunities),
            ))
            require(any(lead.won_status == "won" for lead in opportunities),
                    _("No opportunity of the team Patronage is won yet."))

        def check_mailing():
            mailing_list = get_list()
            emails = {normalize(contact.email) for contact in mailing_list.contact_ids}
            count = len(emails & set(DONORS))
            require(count == len(DONORS), _(
                "The mailing list Donors contains %(count)s donor(s) out of 10.", count=count,
            ))
            mailings = env["mailing.mailing"].search([("contact_list_ids", "in", mailing_list.ids)])
            require(mailings, _("No mailing is addressed to the list Donors yet."))
            require(mailings.filtered(lambda mailing: mailing.state != "draft"),
                    _("The mailing to the list Donors is still a draft: send it."))

        def check_invoices():
            invoices = get_invoices()
            require(len(invoices) >= 3, _(
                "%(count)s donation invoice(s) confirmed: confirm 3 invoices of Free Donation or Membership Fee "
                "to donors (mission 5).", count=len(invoices),
            ))

        def check_analysis():
            filters = env["ir.filters"].search([
                ("model_id", "in", ["account.invoice.report", "account.move", "account.move.line"]),
            ])
            require(any("partner_id" in (favorite.context or "") for favorite in filters), _(
                "No favorite of the invoices is grouped by customer: save your pivot analysis by donor "
                "in your favorites (mission 5).",
            ))

        def check_company_number():
            require(env["ir.model.fields"].search_count([("model", "=", "res.partner"), ("state", "=", "manual")]),
                    _("The contacts have no custom field yet."))

        def check_taxes():
            missing = [product.name for product in get_products()
                       if not (product.taxes_id and all(tax.amount == 0 for tax in product.taxes_id))]
            require(not missing, _(
                "The sales taxes of both donation products must be a 0 %% tax. Still to fix: %(products)s.",
                products=", ".join(missing),
            ))

        def check_activity():
            leads = env["crm.lead"].with_context(active_test=False).search([("team_id", "=", get_team().id)])
            require(env["mail.activity"].search_count([("res_model", "=", "crm.lead"), ("res_id", "in", leads.ids)]),
                    _("No activity is planned on an opportunity of the team Patronage."))

        def check_traces():
            mailings = env["mailing.mailing"].search([("contact_list_ids", "in", get_list().ids)])
            require(env["mailing.trace"].search_count([("mass_mailing_id", "in", mailings.ids)]) >= len(DONORS),
                    _("The mailing has not been processed yet: run the scheduled action Mail Marketing: Process queue."))

        def check_paid():
            require(get_invoices().filtered(lambda invoice: invoice.payment_state in ("paid", "in_payment")),
                    _("No donation invoice is paid yet."))

        return [self._run_step(label, step, bonus=bonus) for label, step, bonus in [
            (_("1. The donors are imported"), check_import, False),
            (_("1. The donors are tagged"), check_tags, False),
            (_("2. The donation products"), check_products, False),
            (_("3. The pipeline of the patrons"), check_pipeline, False),
            (_("4. The thank-you mailing"), check_mailing, False),
            (_("5. The donations are invoiced"), check_invoices, False),
            (_("5. The analysis by donor"), check_analysis, False),
            (_("Company number on the contacts"), check_company_number, True),
            (_("0 % tax on the donation products"), check_taxes, True),
            (_("An activity on a patron opportunity"), check_activity, True),
            (_("The mailing has been processed"), check_traces, True),
            (_("A donation is paid"), check_paid, True),
        ]]
