# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceContractor(models.Model):
    _name = 'maintenance.contractor'
    _description = 'Maintenance Contractor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Contractor Name', required=True, tracking=True)
    code = fields.Char(string='Contractor Code', tracking=True)
    
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, tracking=True)
    
    category_ids = fields.Many2many('maintenance.category', 'contractor_category_rel', 
                                    'contractor_id', 'category_id', string='Services Provided')
    
    contact_person = fields.Char(string='Contact Person')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    
    rating = fields.Selection([
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ], string='Rating', tracking=True)
    
    license_number = fields.Char(string='License Number')
    license_expiry = fields.Date(string='License Expiry Date')
    insurance_number = fields.Char(string='Insurance Number')
    insurance_expiry = fields.Date(string='Insurance Expiry Date')
    
    work_order_ids = fields.One2many('work.order', 'contractor_id', string='Work Orders')
    work_order_count = fields.Integer(string='Work Orders', compute='_compute_work_order_count')
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'Contractor code must be unique per company!')
    ]
    
    @api.depends('work_order_ids')
    def _compute_work_order_count(self):
        for record in self:
            record.work_order_count = len(record.work_order_ids)
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            if not self.name:
                self.name = self.partner_id.name
            self.email = self.partner_id.email
            self.phone = self.partner_id.phone
            self.mobile = self.partner_id.mobile
