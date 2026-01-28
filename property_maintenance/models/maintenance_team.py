# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceTeam(models.Model):
    _name = 'maintenance.team'
    _description = 'Maintenance Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Team Name', required=True, tracking=True)
    code = fields.Char(string='Team Code', required=True, tracking=True)
    description = fields.Text(string='Description')
    
    leader_id = fields.Many2one('res.users', string='Team Leader', tracking=True)
    member_ids = fields.Many2many('res.users', 'maintenance_team_member_rel', 
                                   'team_id', 'user_id', string='Team Members')
    
    technician_ids = fields.One2many('maintenance.technician', 'team_id', string='Technicians')
    technician_count = fields.Integer(string='Technicians', compute='_compute_technician_count')
    
    category_ids = fields.Many2many('maintenance.category', 'team_category_rel', 
                                    'team_id', 'category_id', string='Specializations')
    
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'Team code must be unique per company!')
    ]
    
    @api.depends('technician_ids')
    def _compute_technician_count(self):
        for record in self:
            record.technician_count = len(record.technician_ids)
