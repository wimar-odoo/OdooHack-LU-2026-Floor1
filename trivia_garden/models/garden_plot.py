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
        current_year = fields.Date.context_today(self).year
        for plot in self.filtered("tenant_id"):
            tenant = plot.tenant_id
            # rule 1: the tenant must have paid the fee of this year
            if tenant.last_paid_year < current_year:
                raise ValidationError(self.env._(
                    "%(member)s did not pay the membership fee of %(year)s: they cannot rent a plot.",
                    member=tenant.display_name, year=current_year,
                ))
            # rule 2: the tenant must not rent another plot already
            other = self.search([("tenant_id", "=", tenant.id), ("id", "!=", plot.id)], limit=1)
            if other:
                raise ValidationError(self.env._(
                    "%(member)s already rents the plot %(plot)s: a member rents one plot at most.",
                    member=tenant.display_name, plot=other.display_name,
                ))
