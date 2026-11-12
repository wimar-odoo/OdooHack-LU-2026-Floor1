# ----------------------------------------------------------------------------
# TODO 1 - The membership fees
#
# Create the model garden.membership.fee ("Membership Fee"), with the fields:
#   * partner_id     Many2one to res.partner, required     "Member"
#   * year           Integer, required                      "Year"
#   * amount         Float (or Monetary)                    "Amount"
#   * state          Selection draft / paid, required,      "Status"
#                    "draft" by default
#   * payment_date   Date                                   "Payment Date"
#
# A member pays at most one fee per year: add a constraint.
# Add the method action_mark_paid(), which marks the fees as paid today.
# ----------------------------------------------------------------------------

from odoo import fields, models


class GardenMembershipFee(models.Model):
    _name = "garden.membership.fee"
    _description = "Membership Fee"
    _order = "year desc, partner_id"

    partner_id = fields.Many2one(
        "res.partner", string="Member", required=True,
        index=True, ondelete="cascade",
    )
    year = fields.Integer(string="Year", required=True)
    amount = fields.Float(string="Amount")
    state = fields.Selection(
        [("draft", "Draft"), ("paid", "Paid")],
        string="Status", required=True, default="draft",
    )
    payment_date = fields.Date(string="Payment Date")

    # A member pays at most one fee per year (Odoo 20: models.Constraint)
    _partner_year_unique = models.Constraint(
        "UNIQUE(partner_id, year)",
        "A member can only have one membership fee per year.",
    )

    def action_mark_paid(self):
        self.write({
            "state": "paid",
            "payment_date": fields.Date.context_today(self),
        })
        return True