from odoo import fields, models


class RunPledge(models.Model):
    """ A sponsor gives an amount for each kilometre covered by a runner. """
    _name = "run.pledge"
    _description = "Pledge"
    _order = "runner_id, id"

    sponsor = fields.Char(required=True)
    runner_id = fields.Many2one("run.runner", string="Runner", required=True, ondelete="cascade", index=True)
    amount_per_km = fields.Float(string="Amount per km")
