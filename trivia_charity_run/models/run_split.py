from odoo import fields, models


class RunSplit(models.Model):
    """ The time of a runner at a checkpoint: km 0 (start), km 5 and km 10 (finish). """
    _name = "run.split"
    _description = "Split Time"
    _order = "runner_id, checkpoint_km"

    runner_id = fields.Many2one("run.runner", string="Runner", required=True, ondelete="cascade")
    checkpoint_km = fields.Integer(string="Checkpoint (km)", required=True)
    time = fields.Datetime(required=True)
