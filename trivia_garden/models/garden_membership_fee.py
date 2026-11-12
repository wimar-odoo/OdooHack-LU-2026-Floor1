from odoo import api, fields, models


class GardenMembershipFee(models.Model):
    _name = "garden.membership.fee"
    _description = "Membership Fee"
    _order = "year desc, partner_id"

    partner_id = fields.Many2one("res.partner", string="Member", required=True, ondelete="cascade", index=True)
    year = fields.Integer(string="Year", required=True, default=lambda self: fields.Date.context_today(self).year)
    amount = fields.Float(string="Amount")
    state = fields.Selection(
        [("draft", "Draft"), ("paid", "Paid")],
        string="Status",
        required=True,
        default="draft",
    )
    payment_date = fields.Date(string="Payment Date")

    # a member pays at most one fee per year, whatever its status 
    _partner_year_unique = models.Constraint(
        "unique(partner_id, year)",
        "A member pays at most one fee per year.",
    )

    @api.depends("partner_id", "year")
    def _compute_display_name(self):
        for fee in self:
            fee.display_name = f"{fee.partner_id.name or ''} - {fee.year or ''}"

    def action_mark_paid(self):
        self.write({
            "state": "paid",
            "payment_date": fields.Date.context_today(self),
        })
