# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Property(models.Model):
    _name = 'property.property'
    _description = 'Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Property Name', required=True, tracking=True)
    code = fields.Char(string='Property Code', required=True, tracking=True)
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP Code')
    country_id = fields.Many2one('res.country', string='Country')
    
    property_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('mixed', 'Mixed Use'),
    ], string='Property Type', required=True, default='residential', tracking=True)
    
    owner_id = fields.Many2one('res.partner', string='Owner', domain=[('is_property_owner', '=', True)])
    manager_id = fields.Many2one('res.users', string='Property Manager', tracking=True)
    
    building_ids = fields.One2many('property.building', 'property_id', string='Buildings')
    building_count = fields.Integer(string='Building Count', compute='_compute_building_count')
    
    maintenance_request_ids = fields.One2many('maintenance.request', 'property_id', string='Maintenance Requests')
    maintenance_count = fields.Integer(string='Maintenance Count', compute='_compute_maintenance_count')
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'Property code must be unique per company!')
    ]
    
    @api.depends('building_ids')
    def _compute_building_count(self):
        for record in self:
            record.building_count = len(record.building_ids)
    
    @api.depends('maintenance_request_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_request_ids)
    
    def action_view_buildings(self):
        self.ensure_one()
        return {
            'name': 'Buildings',
            'type': 'ir.actions.act_window',
            'res_model': 'property.building',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
    
    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'name': 'Maintenance Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form,kanban',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
