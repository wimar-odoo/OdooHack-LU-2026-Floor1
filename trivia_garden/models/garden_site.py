from odoo import api, fields, models


class GardenSite(models.Model):
    _name = "garden.site"
    _description = "Garden Site"
    _order = "name"

    name = fields.Char(required=True)
    city = fields.Char()
    plot_ids = fields.One2many("garden.plot", "site_id", string="Plots")
    plot_count = fields.Integer(string="Number of Plots", compute="_compute_plot_count")

    @api.depends("plot_ids")
    def _compute_plot_count(self):
        for site in self:
            site.plot_count = len(site.plot_ids)
