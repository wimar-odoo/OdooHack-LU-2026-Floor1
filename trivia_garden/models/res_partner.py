from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_type = fields.Selection(
        [("individual", "Individual"), ("family", "Family"), ("patron", "Patron")],
        string="Membership Type",
    )
    member_since = fields.Date(string="Member Since")
    fee_ids = fields.One2many("garden.membership.fee", "partner_id", string="Membership Fees")
    fee_count = fields.Integer(string="Fees", compute="_compute_fee_count")
    last_paid_year = fields.Integer(
        string="Last Paid Year", compute="_compute_last_paid_year", store=True,
    )

    @api.depends("fee_ids.state", "fee_ids.year")
    def _compute_last_paid_year(self):
        for partner in self:
            paid_years = partner.fee_ids.filtered(lambda fee: fee.state == "paid").mapped("year")
            partner.last_paid_year = max(paid_years, default=0)

    @api.depends("fee_ids")
    def _compute_fee_count(self):
        for partner in self:
            partner.fee_count = len(partner.fee_ids)

    def action_view_fees(self):
        """ Opened by the "Fees" smart button: the fees of this member only. """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Membership Fees"),
            "res_model": "garden.membership.fee",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }
