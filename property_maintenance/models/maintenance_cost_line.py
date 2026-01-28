# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceCostLine(models.Model):
    _name = 'maintenance.cost.line'
    _description = 'Maintenance Cost Line'
    _order = 'create_date'

    work_order_id = fields.Many2one('work.order', string='Work Order', required=True, ondelete='cascade')
    
    cost_type = fields.Selection([
        ('labor', 'Labor'),
        ('material', 'Material/Spare Parts'),
        ('contractor', 'Contractor Service'),
        ('other', 'Other'),
    ], string='Cost Type', required=True, default='labor')
    
    description = fields.Char(string='Description', required=True)
    
    # For Labor
    technician_id = fields.Many2one('maintenance.technician', string='Technician')
    hours = fields.Float(string='Hours')
    hourly_rate = fields.Float(string='Hourly Rate')
    
    # For Materials
    product_id = fields.Many2one('product.product', string='Product/Material')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    
    # For Contractor
    contractor_id = fields.Many2one('maintenance.contractor', string='Contractor')
    
    # Common
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', related='work_order_id.company_id', store=True)
    
    @api.depends('cost_type', 'hours', 'hourly_rate', 'quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            if record.cost_type == 'labor':
                record.subtotal = record.hours * record.hourly_rate
            elif record.cost_type in ['material', 'contractor', 'other']:
                record.subtotal = record.quantity * record.unit_price
            else:
                record.subtotal = 0.0
    
    @api.onchange('technician_id')
    def _onchange_technician_id(self):
        if self.technician_id and self.technician_id.hourly_rate:
            self.hourly_rate = self.technician_id.hourly_rate
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.standard_price
            self.description = self.product_id.name
    
    @api.onchange('contractor_id')
    def _onchange_contractor_id(self):
        if self.contractor_id:
            self.description = self.contractor_id.name
