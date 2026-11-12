from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Required fields for the members
    membership_type = fields.Selection([
        ('individual', 'Individual'),
        ('family', 'Family'),
        ('patron', 'Patron')
    ], string='Membership Type')
    
    member_since = fields.Date(string='Member Since')
    
    # Fees and computations
    fee_ids = fields.One2many('garden.membership.fee', 'partner_id', string='Membership Fees')
    last_paid_year = fields.Integer(string='Last Paid Year', compute='_compute_last_paid_year', store=True)
    fee_count = fields.Integer(compute='_compute_fee_count', string='Fees')

    @api.depends('fee_ids.state', 'fee_ids.year')
    def _compute_last_paid_year(self):
        for partner in self:
            paid_fees = partner.fee_ids.filtered(lambda f: f.state == 'paid')
            partner.last_paid_year = max(paid_fees.mapped('year')) if paid_fees else 0

    @api.depends('fee_ids')
    def _compute_fee_count(self):
        for partner in self:
            partner.fee_count = len(partner.fee_ids)