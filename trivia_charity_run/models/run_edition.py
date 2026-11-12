from odoo import api, fields, models


class RunEdition(models.Model):
    _name = "run.edition"
    _description = "Race Edition"
    _order = "year desc"

    name = fields.Char(required=True)
    year = fields.Integer(required=True)
    date = fields.Date()
    runner_ids = fields.One2many("run.runner", "edition_id", string="Runners")
    runner_count = fields.Integer(string="Number of Runners", compute="_compute_runner_count")

    @api.depends("runner_ids")
    def _compute_runner_count(self):
        for edition in self:
            edition.runner_count = len(edition.runner_ids)
