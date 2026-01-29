# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta


class PreventiveMaintenance(models.Model):
    _name = 'preventive.maintenance'
    _description = 'Preventive Maintenance Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'next_execution_date'

    name = fields.Char(string='Plan Name', required=True, tracking=True)
    code = fields.Char(string='Plan Code', required=True, tracking=True)
    description = fields.Text(string='Description')
    
    property_id = fields.Many2one('property.property', string='Property', required=True, tracking=True)
    building_id = fields.Many2one('property.building', string='Building', tracking=True)
    unit_id = fields.Many2one('property.unit', string='Unit', tracking=True)
    asset_id = fields.Many2one('property.asset', string='Asset', tracking=True)
    
    category_id = fields.Many2one('maintenance.category', string='Category', required=True, tracking=True)
    
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
        ('custom', 'Custom'),
    ], string='Frequency', required=True, default='monthly', tracking=True)
    
    interval = fields.Integer(string='Interval', default=1, help='Interval for custom frequency (in days)')
    
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today, tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    next_execution_date = fields.Date(string='Next Execution Date', compute='_compute_next_execution_date', store=True, tracking=True)
    last_execution_date = fields.Date(string='Last Execution Date', readonly=True)
    
    team_id = fields.Many2one('maintenance.team', string='Maintenance Team', tracking=True)
    technician_ids = fields.Many2many('maintenance.technician', 'preventive_maintenance_technician_rel', 
                                      'plan_id', 'technician_id', string='Assigned Technicians')
    
    auto_generate = fields.Boolean(string='Auto Generate Work Orders', default=True, tracking=True)
    advance_days = fields.Integer(string='Generate in Advance (Days)', default=7, 
                                   help='How many days in advance to generate work orders')
    
    work_order_ids = fields.One2many('work.order', 'preventive_maintenance_id', string='Generated Work Orders')
    work_order_count = fields.Integer(string='Work Orders', compute='_compute_work_order_count')
    
    estimated_duration = fields.Float(string='Estimated Duration (Hours)', default=1.0)
    estimated_cost = fields.Float(string='Estimated Cost')
    
    checklist = fields.Text(string='Maintenance Checklist', help='Tasks to be performed during maintenance')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'Plan code must be unique per company!')
    ]
    
    @api.depends('start_date', 'last_execution_date', 'frequency', 'interval', 'state')
    def _compute_next_execution_date(self):
        for record in self:
            if record.state != 'active':
                record.next_execution_date = False
                continue
            
            base_date = record.last_execution_date or record.start_date
            if not base_date:
                record.next_execution_date = False
                continue
            
            if record.frequency == 'daily':
                record.next_execution_date = base_date + timedelta(days=1)
            elif record.frequency == 'weekly':
                record.next_execution_date = base_date + timedelta(weeks=1)
            elif record.frequency == 'monthly':
                record.next_execution_date = base_date + relativedelta(months=1)
            elif record.frequency == 'quarterly':
                record.next_execution_date = base_date + relativedelta(months=3)
            elif record.frequency == 'semi_annual':
                record.next_execution_date = base_date + relativedelta(months=6)
            elif record.frequency == 'annual':
                record.next_execution_date = base_date + relativedelta(years=1)
            elif record.frequency == 'custom':
                record.next_execution_date = base_date + timedelta(days=record.interval)
            else:
                record.next_execution_date = False
            
            # Check if end date has passed
            if record.end_date and record.next_execution_date > record.end_date:
                record.next_execution_date = False
    
    @api.depends('work_order_ids')
    def _compute_work_order_count(self):
        for record in self:
            record.work_order_count = len(record.work_order_ids)
    
    def action_activate(self):
        self.write({'state': 'active'})
        self.message_post(body=_('Preventive maintenance plan activated'))
        return True
    
    def action_suspend(self):
        self.write({'state': 'suspended'})
        self.message_post(body=_('Preventive maintenance plan suspended'))
        return True
    
    def action_generate_work_order(self):
        self.ensure_one()
        
        if not self.next_execution_date:
            raise ValidationError(_('Next execution date is required to generate work order.'))
        
        if not self.property_id:
            raise ValidationError(_('Property is required to generate work order.'))
        
        # Check if work order already exists for this execution date
        existing_wo = self.env['work.order'].search([
            ('preventive_maintenance_id', '=', self.id),
            ('scheduled_date', '>=', datetime.combine(self.next_execution_date, time.min)),
            ('scheduled_date', '<=', datetime.combine(self.next_execution_date, time.max)),
        ], limit=1)
        
        if existing_wo:
            return existing_wo
        
        # Create work order
        wo_vals = {
            'title': f'{self.name} - {self.next_execution_date}',
            'description': self.description or '',
            'preventive_maintenance_id': self.id,
            'property_id': self.property_id.id if self.property_id else False,
            'building_id': self.building_id.id if self.building_id else False,
            'unit_id': self.unit_id.id if self.unit_id else False,
            'asset_id': self.asset_id.id if self.asset_id else False,
            'category_id': self.category_id.id,
            'work_type': 'internal',
            'team_id': self.team_id.id if self.team_id else False,
            'scheduled_date': datetime.combine(self.next_execution_date, time.min),
            'state': 'scheduled',
        }
        
        work_order = self.env['work.order'].create(wo_vals)
        
        # Add technicians
        if self.technician_ids:
            work_order.technician_ids = [(6, 0, self.technician_ids.ids)]
        
        # Update last execution date
        self.write({'last_execution_date': self.next_execution_date})
        
        self.message_post(body=_('Work order %s generated for %s') % (work_order.name, self.next_execution_date))
        
        return work_order
    
    @api.model
    def cron_generate_preventive_maintenance(self):
        """Cron job to auto-generate work orders for active preventive maintenance plans"""
        today = fields.Date.today()
        
        # Find plans that need work orders generated
        plans = self.search([
            ('state', '=', 'active'),
            ('auto_generate', '=', True),
            ('next_execution_date', '!=', False),
        ])
        
        for plan in plans:
            # Check if we should generate in advance
            generate_date = today + timedelta(days=plan.advance_days)
            
            if plan.next_execution_date <= generate_date:
                plan.action_generate_work_order()
        
        return True
    
    def action_view_work_orders(self):
        self.ensure_one()
        return {
            'name': _('Work Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'work.order',
            'view_mode': 'tree,form,calendar',
            'domain': [('preventive_maintenance_id', '=', self.id)],
            'context': {'default_preventive_maintenance_id': self.id},
        }


class WorkOrder(models.Model):
    _inherit = 'work.order'
    
    preventive_maintenance_id = fields.Many2one('preventive.maintenance', string='Preventive Maintenance Plan', readonly=True)
