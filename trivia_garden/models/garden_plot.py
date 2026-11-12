from odoo import fields, models


class GardenPlot(models.Model):
    _name = "garden.plot"
    _description = "Garden Plot"
    _order = "site_id, name"

    name = fields.Char(required=True)
    site_id = fields.Many2one("garden.site", string="Site", required=True, ondelete="cascade")
    area = fields.Float(string="Area (m²)")
    tenant_id = fields.Many2one("res.partner", string="Tenant", index=True)

    # ----------------------------------------------------------------------------
    # TODO 6 - The rules of the plots
    #
    # A plot can only be rented (tenant_id) by a member who paid the fee of the
    # current year (see last_paid_year, TODO 4), and a member rents one plot at most.
    # Refuse the other cases with a clear message.
    # ----------------------------------------------------------------------------
