# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _description = 'Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(string='Request Number', required=True, readonly=True, copy=False, default='New')
    title = fields.Char(string='Request Title', required=True, tracking=True)
    description = fields.Html(string='Description', required=True)
    
    property_id = fields.Many2one('property.property', string='Property', required=True, tracking=True)
    building_id = fields.Many2one('property.building', string='Building', required=True, tracking=True)
    unit_id = fields.Many2one('property.unit', string='Unit', tracking=True)
    asset_id = fields.Many2one('property.asset', string='Asset', tracking=True)
    
    category_id = fields.Many2one('maintenance.category', string='Category', required=True, tracking=True)
    stage_id = fields.Many2one('maintenance.stage', string='Stage', required=True, tracking=True, group_expand='_read_group_stage_ids')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1', required=True, tracking=True)
    
    request_type = fields.Selection([
        ('reactive', 'Reactive'),
        ('preventive', 'Preventive'),
        ('improvement', 'Improvement'),
    ], string='Request Type', default='reactive', required=True, tracking=True)
    
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, tracking=True)
    requester_partner_id = fields.Many2one('res.partner', string='Requester (Partner)', tracking=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant', domain=[('is_tenant', '=', True)], tracking=True)
    owner_id = fields.Many2one('res.partner', string='Owner', domain=[('is_property_owner', '=', True)], tracking=True)
    
    team_id = fields.Many2one('maintenance.team', string='Maintenance Team', tracking=True)
    assigned_to = fields.Many2one('res.users', string='Assigned To', tracking=True)
    
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now, required=True, tracking=True)
    scheduled_date = fields.Datetime(string='Scheduled Date', tracking=True)
    completion_date = fields.Datetime(string='Completion Date', readonly=True, tracking=True)
    
    # SLA
    sla_hours = fields.Float(string='SLA (Hours)', compute='_compute_sla_hours', store=True)
    sla_deadline = fields.Datetime(string='SLA Deadline', compute='_compute_sla_deadline', store=True)
    sla_status = fields.Selection([
        ('on_time', 'On Time'),
        ('warning', 'Warning'),
        ('overdue', 'Overdue'),
    ], string='SLA Status', compute='_compute_sla_status', store=True)
    
    # Work Order
    work_order_id = fields.Many2one('work.order', string='Work Order', readonly=True, tracking=True)
    work_order_count = fields.Integer(string='Work Orders', compute='_compute_work_order_count')
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', 'maintenance_request_attachment_rel', 
                                      'request_id', 'attachment_id', string='Attachments')
    attachment_count = fields.Integer(string='Attachments', compute='_compute_attachment_count')
    
    # Cost
    estimated_cost = fields.Float(string='Estimated Cost', tracking=True)
    actual_cost = fields.Float(string='Actual Cost', compute='_compute_actual_cost', store=True)
    
    billable = fields.Boolean(string='Billable', default=False, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    
    # Internal Notes
    internal_notes = fields.Text(string='Internal Notes')
    solution = fields.Html(string='Solution/Resolution')
    
    # Status
    state = fields.Selection(related='stage_id.code', string='State', store=True)
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Ready'),
    ], string='Kanban State', default='normal', tracking=True)
    
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.request') or 'New'
        return super(MaintenanceRequest, self).create(vals)
    
    @api.depends('category_id', 'priority')
    def _compute_sla_hours(self):
        # Define SLA based on category and priority
        sla_matrix = {
            '0': 72,  # Low: 72 hours
            '1': 48,  # Normal: 48 hours
            '2': 24,  # High: 24 hours
            '3': 4,   # Urgent: 4 hours
        }
        for record in self:
            record.sla_hours = sla_matrix.get(record.priority, 48)
    
    @api.depends('request_date', 'sla_hours')
    def _compute_sla_deadline(self):
        for record in self:
            if record.request_date and record.sla_hours:
                record.sla_deadline = record.request_date + timedelta(hours=record.sla_hours)
            else:
                record.sla_deadline = False
    
    @api.depends('sla_deadline', 'completion_date', 'stage_id.done')
    def _compute_sla_status(self):
        now = fields.Datetime.now()
        for record in self:
            if record.stage_id.done:
                if record.completion_date and record.sla_deadline:
                    record.sla_status = 'on_time' if record.completion_date <= record.sla_deadline else 'overdue'
                else:
                    record.sla_status = 'on_time'
            elif record.sla_deadline:
                hours_remaining = (record.sla_deadline - now).total_seconds() / 3600
                if hours_remaining < 0:
                    record.sla_status = 'overdue'
                elif hours_remaining < record.sla_hours * 0.2:  # Less than 20% time remaining
                    record.sla_status = 'warning'
                else:
                    record.sla_status = 'on_time'
            else:
                record.sla_status = 'on_time'
    
    @api.depends('work_order_id')
    def _compute_work_order_count(self):
        for record in self:
            record.work_order_count = 1 if record.work_order_id else 0
    
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)
    
    @api.depends('work_order_id.total_cost')
    def _compute_actual_cost(self):
        for record in self:
            record.actual_cost = record.work_order_id.total_cost if record.work_order_id else 0.0
    
    @api.onchange('unit_id')
    def _onchange_unit_id(self):
        if self.unit_id:
            self.building_id = self.unit_id.building_id
            self.property_id = self.unit_id.property_id
            self.tenant_id = self.unit_id.tenant_id
            self.owner_id = self.unit_id.owner_id
    
    @api.onchange('building_id')
    def _onchange_building_id(self):
        if self.building_id and not self.unit_id:
            self.property_id = self.building_id.property_id
    
    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        if self.asset_id:
            self.unit_id = self.asset_id.unit_id
            self.building_id = self.asset_id.building_id
            self.property_id = self.asset_id.property_id
            if self.asset_id.category_id:
                self.category_id = self.asset_id.category_id
    
    def action_submit(self):
        submitted_stage = self.env['maintenance.stage'].search([('code', '=', 'submitted')], limit=1)
        if submitted_stage:
            self.write({'stage_id': submitted_stage.id})
            self.message_post(body=_('Request submitted for approval'))
        return True
    
    def action_approve(self):
        approved_stage = self.env['maintenance.stage'].search([('code', '=', 'approved')], limit=1)
        if approved_stage:
            self.write({'stage_id': approved_stage.id})
            self.message_post(body=_('Request approved'))
        return True
    
    def action_start(self):
        in_progress_stage = self.env['maintenance.stage'].search([('code', '=', 'in_progress')], limit=1)
        if in_progress_stage:
            self.write({'stage_id': in_progress_stage.id})
            self.message_post(body=_('Request started'))
        return True
    
    def action_complete(self):
        completed_stage = self.env['maintenance.stage'].search([('code', '=', 'completed')], limit=1)
        if completed_stage:
            self.write({
                'stage_id': completed_stage.id,
                'completion_date': fields.Datetime.now()
            })
            self.message_post(body=_('Request completed'))
        return True
    
    def action_close(self):
        closed_stage = self.env['maintenance.stage'].search([('code', '=', 'closed')], limit=1)
        if closed_stage:
            self.write({'stage_id': closed_stage.id})
            self.message_post(body=_('Request closed'))
        return True
    
    def action_cancel(self):
        cancelled_stage = self.env['maintenance.stage'].search([('code', '=', 'cancelled')], limit=1)
        if cancelled_stage:
            self.write({'stage_id': cancelled_stage.id})
            self.message_post(body=_('Request cancelled'))
        return True
    
    def action_convert_to_work_order(self):
        self.ensure_one()
        if self.work_order_id:
            raise UserError(_('A work order already exists for this request.'))
        
        return {
            'name': _('Convert to Work Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'convert.to.work.order.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_maintenance_request_id': self.id,
                'default_property_id': self.property_id.id,
                'default_building_id': self.building_id.id,
                'default_unit_id': self.unit_id.id,
                'default_asset_id': self.asset_id.id,
            }
        }
    
    def action_view_work_order(self):
        self.ensure_one()
        return {
            'name': _('Work Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'work.order',
            'res_id': self.work_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['maintenance.stage'].search([])
    
    def _compute_access_url(self):
        super(MaintenanceRequest, self)._compute_access_url()
        for request in self:
            request.access_url = '/my/maintenance/%s' % request.id
