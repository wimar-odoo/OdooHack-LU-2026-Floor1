from odoo import _, api, fields, models
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
        current_year = fields.Date.context_today(self).year
        for plot in self.filtered("tenant_id"):
            tenant = plot.tenant_id
            if tenant.last_paid_year < current_year:
                raise ValidationError(_(
                    "%(member)s cannot rent the plot %(plot)s: the membership fee of %(year)s is not paid.",
                    member=tenant.display_name, plot=plot.name, year=current_year,
                ))
            other = self.search_count([("tenant_id", "=", tenant.id), ("id", "!=", plot.id)])
            if other:
                raise ValidationError(_(
                    "%(member)s already rents a plot: a member rents one plot at most.",
                    member=tenant.display_name,
                ))
