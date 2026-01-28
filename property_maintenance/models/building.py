# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Building(models.Model):
    _name = 'property.building'
    _description = 'Building'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Building Name', required=True, tracking=True)
    code = fields.Char(string='Building Code', required=True, tracking=True)
    property_id = fields.Many2one('property.property', string='Property', required=True, ondelete='cascade', tracking=True)
    
    floors = fields.Integer(string='Number of Floors', default=1)
    year_built = fields.Integer(string='Year Built')
    total_area = fields.Float(string='Total Area (sq m)')
    
    unit_ids = fields.One2many('property.unit', 'building_id', string='Units')
    unit_count = fields.Integer(string='Unit Count', compute='_compute_unit_count')
    
    maintenance_request_ids = fields.One2many('maintenance.request', 'building_id', string='Maintenance Requests')
    maintenance_count = fields.Integer(string='Maintenance Count', compute='_compute_maintenance_count')
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', related='property_id.company_id', store=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code, property_id)', 'Building code must be unique per property!')
    ]
    
    @api.depends('unit_ids')
    def _compute_unit_count(self):
        for record in self:
            record.unit_count = len(record.unit_ids)
    
    @api.depends('maintenance_request_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_request_ids)
    
    def action_view_units(self):
        self.ensure_one()
        return {
            'name': 'Units',
            'type': 'ir.actions.act_window',
            'res_model': 'property.unit',
            'view_mode': 'tree,form',
            'domain': [('building_id', '=', self.id)],
            'context': {'default_building_id': self.id, 'default_property_id': self.property_id.id},
        }
    
    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'name': 'Maintenance Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form,kanban',
            'domain': [('building_id', '=', self.id)],
            'context': {'default_building_id': self.id, 'default_property_id': self.property_id.id},
        }
