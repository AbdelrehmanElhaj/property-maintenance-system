# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceStage(models.Model):
    _name = 'maintenance.stage'
    _description = 'Maintenance Stage'
    _order = 'sequence, name'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    fold = fields.Boolean(string='Folded in Kanban', default=False)
    done = fields.Boolean(string='Is Done Stage', default=False)
    cancelled = fields.Boolean(string='Is Cancelled Stage', default=False)
    code = fields.Selection([
        ('new', 'New'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='Stage Code', required=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Stage code must be unique!')
    ]
