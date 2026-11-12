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

    # NULL values are distinct for UNIQUE: any number of plots can stay free
    _unique_tenant = models.Constraint(
        "UNIQUE(tenant_id)",
        "A member rents one plot at most.",
    )

    @api.constrains("tenant_id")
    def _check_tenant_paid_current_year(self):
        current_year = fields.Date.context_today(self).year
        late_plots = self.filtered(lambda plot: plot.tenant_id and plot.tenant_id.last_paid_year < current_year)
        if late_plots:
            raise ValidationError(self.env._(
                "Only a member who paid the fee of %(year)s can rent a plot: %(members)s did not.",
                year=current_year,
                members=", ".join(late_plots.tenant_id.mapped("display_name")),
            ))
