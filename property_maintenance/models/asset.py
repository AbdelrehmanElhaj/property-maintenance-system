# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Asset(models.Model):
    _name = 'property.asset'
    _description = 'Property Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    code = fields.Char(string='Asset Code', required=True, tracking=True)
    property_id = fields.Many2one('property.property', string='Property', required=True, ondelete='cascade', tracking=True)
    building_id = fields.Many2one('property.building', string='Building', required=True, ondelete='cascade', tracking=True)
    unit_id = fields.Many2one('property.unit', string='Unit', ondelete='cascade', tracking=True)
    
    asset_type = fields.Selection([
        ('hvac', 'HVAC System'),
        ('electrical', 'Electrical Equipment'),
        ('plumbing', 'Plumbing System'),
        ('elevator', 'Elevator'),
        ('generator', 'Generator'),
        ('fire_safety', 'Fire Safety Equipment'),
        ('security', 'Security System'),
        ('appliance', 'Appliance'),
        ('furniture', 'Furniture'),
        ('other', 'Other'),
    ], string='Asset Type', required=True, tracking=True)
    
    category_id = fields.Many2one('maintenance.category', string='Maintenance Category')
    manufacturer = fields.Char(string='Manufacturer')
    model = fields.Char(string='Model')
    serial_number = fields.Char(string='Serial Number')
    
    purchase_date = fields.Date(string='Purchase Date')
    installation_date = fields.Date(string='Installation Date')
    warranty_expiry_date = fields.Date(string='Warranty Expiry Date')
    
    status = fields.Selection([
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('broken', 'Broken'),
        ('retired', 'Retired'),
    ], string='Status', default='operational', tracking=True)
    
    maintenance_request_ids = fields.One2many('maintenance.request', 'asset_id', string='Maintenance Requests')
    maintenance_count = fields.Integer(string='Maintenance Count', compute='_compute_maintenance_count')
    
    preventive_maintenance_ids = fields.One2many('preventive.maintenance', 'asset_id', string='Preventive Maintenance Plans')
    preventive_maintenance_count = fields.Integer(string='PM Plans Count', compute='_compute_pm_count')
    
    last_maintenance_date = fields.Date(string='Last Maintenance Date', compute='_compute_last_maintenance_date', store=True)
    next_maintenance_date = fields.Date(string='Next Maintenance Date')
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', related='property_id.company_id', store=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'Asset code must be unique per company!')
    ]
    
    @api.depends('maintenance_request_ids', 'maintenance_request_ids.completion_date')
    def _compute_last_maintenance_date(self):
        for record in self:
            completed_requests = record.maintenance_request_ids.filtered(
                lambda r: r.completion_date and r.stage_id.done
            )
            if completed_requests:
                record.last_maintenance_date = max(completed_requests.mapped('completion_date'))
            else:
                record.last_maintenance_date = False
    
    @api.depends('maintenance_request_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_request_ids)
    
    @api.depends('preventive_maintenance_ids')
    def _compute_pm_count(self):
        for record in self:
            record.preventive_maintenance_count = len(record.preventive_maintenance_ids)
    
    @api.onchange('unit_id')
    def _onchange_unit_id(self):
        if self.unit_id:
            self.building_id = self.unit_id.building_id
            self.property_id = self.unit_id.property_id
    
    @api.onchange('building_id')
    def _onchange_building_id(self):
        if self.building_id and not self.unit_id:
            self.property_id = self.building_id.property_id
    
    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'name': 'Maintenance Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form,kanban',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id, 'default_unit_id': self.unit_id.id, 'default_building_id': self.building_id.id, 'default_property_id': self.property_id.id},
        }
    
    def action_view_preventive_maintenance(self):
        self.ensure_one()
        return {
            'name': 'Preventive Maintenance Plans',
            'type': 'ir.actions.act_window',
            'res_model': 'preventive.maintenance',
            'view_mode': 'tree,form,calendar',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }
