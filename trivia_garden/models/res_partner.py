from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_type = fields.Selection([
        ("individual", "Individual"),
        ("family", "Family"),
        ("patron", "Patron"),
    ])
    member_since = fields.Date()
    fee_ids = fields.One2many("garden.membership.fee", "partner_id", string="Membership Fees")
    fee_count = fields.Integer(compute="_compute_fee_count")
    last_paid_year = fields.Integer(compute="_compute_last_paid_year", store=True)

    @api.depends("fee_ids")
    def _compute_fee_count(self):
        for partner in self:
            partner.fee_count = len(partner.fee_ids)

    # the state and the year of the fees matter, not only the list of fees: paying a fee or changing its year
    # must recompute the stored value
    @api.depends("fee_ids.state", "fee_ids.year")
    def _compute_last_paid_year(self):
        for partner in self:
            partner.last_paid_year = max(partner.fee_ids.filtered(lambda fee: fee.state == "paid").mapped("year"), default=0)

    def action_open_fees(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Membership Fees"),
            "res_model": "garden.membership.fee",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }
