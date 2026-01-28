# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Unit(models.Model):
    _name = 'property.unit'
    _description = 'Property Unit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Unit Name', required=True, tracking=True)
    code = fields.Char(string='Unit Code', required=True, tracking=True)
    property_id = fields.Many2one('property.property', string='Property', required=True, ondelete='cascade', tracking=True)
    building_id = fields.Many2one('property.building', string='Building', required=True, ondelete='cascade', tracking=True)
    
    floor = fields.Integer(string='Floor')
    unit_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('office', 'Office'),
        ('shop', 'Shop'),
        ('warehouse', 'Warehouse'),
        ('villa', 'Villa'),
        ('other', 'Other'),
    ], string='Unit Type', default='apartment', tracking=True)
    
    area = fields.Float(string='Area (sq m)')
    bedrooms = fields.Integer(string='Bedrooms')
    bathrooms = fields.Integer(string='Bathrooms')
    
    status = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    ], string='Status', default='available', tracking=True)
    
    tenant_id = fields.Many2one('res.partner', string='Current Tenant', domain=[('is_tenant', '=', True)])
    owner_id = fields.Many2one('res.partner', string='Owner', domain=[('is_property_owner', '=', True)])
    
    asset_ids = fields.One2many('property.asset', 'unit_id', string='Assets')
    asset_count = fields.Integer(string='Asset Count', compute='_compute_asset_count')
    
    maintenance_request_ids = fields.One2many('maintenance.request', 'unit_id', string='Maintenance Requests')
    maintenance_count = fields.Integer(string='Maintenance Count', compute='_compute_maintenance_count')
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', related='property_id.company_id', store=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code, building_id)', 'Unit code must be unique per building!')
    ]
    
    @api.depends('asset_ids')
    def _compute_asset_count(self):
        for record in self:
            record.asset_count = len(record.asset_ids)
    
    @api.depends('maintenance_request_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_request_ids)
    
    @api.onchange('building_id')
    def _onchange_building_id(self):
        if self.building_id:
            self.property_id = self.building_id.property_id
    
    def action_view_assets(self):
        self.ensure_one()
        return {
            'name': 'Assets',
            'type': 'ir.actions.act_window',
            'res_model': 'property.asset',
            'view_mode': 'tree,form',
            'domain': [('unit_id', '=', self.id)],
            'context': {'default_unit_id': self.id, 'default_building_id': self.building_id.id, 'default_property_id': self.property_id.id},
        }
    
    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'name': 'Maintenance Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form,kanban',
            'domain': [('unit_id', '=', self.id)],
            'context': {'default_unit_id': self.id, 'default_building_id': self.building_id.id, 'default_property_id': self.property_id.id},
        }
