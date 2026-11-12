from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class GardenPlot(models.Model):
    _name = 'garden.plot'
    _description = 'Garden Plot'

    name = fields.Char(string='Plot Name', required=True)
    site_id = fields.Many2one('garden.site', string='Garden Site', required=True)
    area = fields.Integer(string='Area') # Added to prevent server crashes!
    tenant_id = fields.Many2one('res.partner', string='Tenant')

    @api.constrains('tenant_id')
    def _check_tenant_rental(self):
        current_year = datetime.now().year
        for plot in self:
            if plot.tenant_id:
                if plot.tenant_id.last_paid_year != current_year:
                    raise ValidationError("Only a member who paid the fee of the current year can rent a plot.")
                
                other_plots = self.search([
                    ('tenant_id', '=', plot.tenant_id.id),
                    ('id', '!=', plot.id)
                ])
                if other_plots:
                    raise ValidationError("A member can rent one plot at most.")