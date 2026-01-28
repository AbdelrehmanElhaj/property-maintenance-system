# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceTechnician(models.Model):
    _name = 'maintenance.technician'
    _description = 'Maintenance Technician'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Technician Name', required=True, tracking=True)
    code = fields.Char(string='Employee Code', tracking=True)
    
    user_id = fields.Many2one('res.users', string='User', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    
    team_id = fields.Many2one('maintenance.team', string='Team', tracking=True)
    
    category_ids = fields.Many2many('maintenance.category', 'technician_category_rel', 
                                    'technician_id', 'category_id', string='Specializations')
    
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    
    hourly_rate = fields.Float(string='Hourly Rate', tracking=True)
    
    work_order_ids = fields.Many2many('work.order', 'work_order_technician_rel', 
                                      'technician_id', 'work_order_id', string='Work Orders')
    work_order_count = fields.Integer(string='Work Orders', compute='_compute_work_order_count')
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'Employee code must be unique per company!')
    ]
    
    @api.depends('work_order_ids')
    def _compute_work_order_count(self):
        for record in self:
            record.work_order_count = len(record.work_order_ids)
    
    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.email = self.user_id.email
            if not self.name:
                self.name = self.user_id.name
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            if not self.name:
                self.name = self.employee_id.name
            self.email = self.employee_id.work_email
            self.phone = self.employee_id.work_phone
            self.mobile = self.employee_id.mobile_phone
