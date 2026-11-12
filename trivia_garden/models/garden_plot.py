from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GardenPlot(models.Model):
    _name = "garden.plot"
    _description = "Garden Plot"
    _order = "site_id, name"

    name = fields.Char(required=True)
    site_id = fields.Many2one("garden.site", string="Site", required=True, ondelete="cascade")
    area = fields.Float(string="Area (m²)")
    tenant_id = fields.Many2one("res.partner", string="Tenant", index=True)

    @api.constrains("tenant_id")
    def _check_tenant(self):
        this_year = fields.Date.context_today(self).year
        for plot in self.filtered("tenant_id"):
            tenant = plot.tenant_id
            if tenant.last_paid_year < this_year:
                raise ValidationError(self.env._(
                    "%(member)s did not pay the membership fee of %(year)s: they cannot rent the plot %(plot)s.",
                    member=tenant.display_name, year=this_year, plot=plot.name,
                ))
            other_plots = self.search([("tenant_id", "=", tenant.id), ("id", "!=", plot.id)])
            if other_plots:
                raise ValidationError(self.env._(
                    "%(member)s already rents the plot %(other)s: a member rents one plot at most.",
                    member=tenant.display_name, other=", ".join(other_plots.mapped("name")),
                ))
