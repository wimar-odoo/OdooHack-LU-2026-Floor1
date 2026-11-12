from odoo import fields, models


class GardenMembershipFee(models.Model):
    _name = "garden.membership.fee"
    _description = "Membership Fee"
    _order = "year desc, partner_id"

    partner_id = fields.Many2one("res.partner", string="Member", required=True, index=True, ondelete="cascade")
    year = fields.Integer(required=True)
    amount = fields.Float()
    state = fields.Selection([("draft", "Draft"), ("paid", "Paid")], string="Status", required=True, default="draft")
    payment_date = fields.Date()

    # on the member and the year only: a draft and a paid fee of the same year are a duplicate too
    _unique_partner_year = models.Constraint(
        "UNIQUE(partner_id, year)",
        "A member pays at most one fee per year.",
    )

    def action_mark_paid(self):
        self.write({"state": "paid", "payment_date": fields.Date.context_today(self)})
