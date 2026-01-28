# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Work Order Number', required=True, readonly=True, copy=False, default='New')
    title = fields.Char(string='Work Order Title', required=True, tracking=True)
    description = fields.Html(string='Description')
    
    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request', tracking=True)
    
    property_id = fields.Many2one('property.property', string='Property', required=True, tracking=True)
    building_id = fields.Many2one('property.building', string='Building', required=True, tracking=True)
    unit_id = fields.Many2one('property.unit', string='Unit', tracking=True)
    asset_id = fields.Many2one('property.asset', string='Asset', tracking=True)
    
    category_id = fields.Many2one('maintenance.category', string='Category', required=True, tracking=True)
    
    work_type = fields.Selection([
        ('internal', 'Internal Team'),
        ('contractor', 'External Contractor'),
        ('mixed', 'Mixed'),
    ], string='Work Type', default='internal', required=True, tracking=True)
    
    team_id = fields.Many2one('maintenance.team', string='Maintenance Team', tracking=True)
    technician_ids = fields.Many2many('maintenance.technician', 'work_order_technician_rel', 
                                      'work_order_id', 'technician_id', string='Technicians')
    contractor_id = fields.Many2one('maintenance.contractor', string='Contractor', tracking=True)
    
    scheduled_date = fields.Datetime(string='Scheduled Date', required=True, tracking=True)
    start_date = fields.Datetime(string='Start Date', tracking=True)
    end_date = fields.Datetime(string='End Date', tracking=True)
    
    duration_hours = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Cost Lines
    cost_line_ids = fields.One2many('maintenance.cost.line', 'work_order_id', string='Cost Lines')
    
    # Cost Summary
    labor_cost = fields.Float(string='Labor Cost', compute='_compute_costs', store=True)
    material_cost = fields.Float(string='Material Cost', compute='_compute_costs', store=True)
    contractor_cost = fields.Float(string='Contractor Cost', compute='_compute_costs', store=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_costs', store=True, tracking=True)
    
    # Billing
    billable = fields.Boolean(string='Billable', default=False, tracking=True)
    bill_to = fields.Selection([
        ('tenant', 'Tenant'),
        ('owner', 'Owner'),
        ('company', 'Company'),
    ], string='Bill To', tracking=True)
    
    tenant_id = fields.Many2one('res.partner', string='Tenant', domain=[('is_tenant', '=', True)])
    owner_id = fields.Many2one('res.partner', string='Owner', domain=[('is_property_owner', '=', True)])
    
    invoice_id = fields.Many2one('account.move', string='Customer Invoice', readonly=True)
    vendor_bill_ids = fields.One2many('account.move', 'work_order_id', string='Vendor Bills', 
                                      domain=[('move_type', '=', 'in_invoice')])
    
    # Notes and Solution
    internal_notes = fields.Text(string='Internal Notes')
    work_performed = fields.Html(string='Work Performed')
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', 'work_order_attachment_rel', 
                                      'work_order_id', 'attachment_id', string='Attachments')
    
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('work.order') or 'New'
        return super(WorkOrder, self).create(vals)
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                duration = record.end_date - record.start_date
                record.duration_hours = duration.total_seconds() / 3600
            else:
                record.duration_hours = 0.0
    
    @api.depends('cost_line_ids', 'cost_line_ids.subtotal')
    def _compute_costs(self):
        for record in self:
            labor_cost = sum(record.cost_line_ids.filtered(lambda l: l.cost_type == 'labor').mapped('subtotal'))
            material_cost = sum(record.cost_line_ids.filtered(lambda l: l.cost_type == 'material').mapped('subtotal'))
            contractor_cost = sum(record.cost_line_ids.filtered(lambda l: l.cost_type == 'contractor').mapped('subtotal'))
            
            record.labor_cost = labor_cost
            record.material_cost = material_cost
            record.contractor_cost = contractor_cost
            record.total_cost = labor_cost + material_cost + contractor_cost
    
    def action_schedule(self):
        self.write({'state': 'scheduled'})
        self.message_post(body=_('Work order scheduled'))
        return True
    
    def action_start(self):
        self.write({
            'state': 'in_progress',
            'start_date': fields.Datetime.now()
        })
        self.message_post(body=_('Work order started'))
        
        # Update asset status if linked
        if self.asset_id:
            self.asset_id.write({'status': 'maintenance'})
        
        # Update maintenance request
        if self.maintenance_request_id:
            in_progress_stage = self.env['maintenance.stage'].search([('code', '=', 'in_progress')], limit=1)
            if in_progress_stage:
                self.maintenance_request_id.write({'stage_id': in_progress_stage.id})
        
        return True
    
    def action_complete(self):
        if not self.work_performed:
            raise UserError(_('Please describe the work performed before completing.'))
        
        self.write({
            'state': 'completed',
            'end_date': fields.Datetime.now()
        })
        self.message_post(body=_('Work order completed'))
        
        # Update asset status if linked
        if self.asset_id:
            self.asset_id.write({'status': 'operational'})
        
        # Update maintenance request
        if self.maintenance_request_id:
            completed_stage = self.env['maintenance.stage'].search([('code', '=', 'completed')], limit=1)
            if completed_stage:
                self.maintenance_request_id.write({
                    'stage_id': completed_stage.id,
                    'completion_date': fields.Datetime.now(),
                    'solution': self.work_performed
                })
        
        return True
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
        self.message_post(body=_('Work order cancelled'))
        
        # Reset asset status if linked
        if self.asset_id and self.asset_id.status == 'maintenance':
            self.asset_id.write({'status': 'operational'})
        
        return True
    
    def action_create_invoice(self):
        self.ensure_one()
        
        if not self.billable:
            raise UserError(_('This work order is not billable.'))
        
        if self.invoice_id:
            raise UserError(_('An invoice already exists for this work order.'))
        
        if not self.bill_to:
            raise UserError(_('Please specify who to bill.'))
        
        # Determine the customer
        if self.bill_to == 'tenant':
            if not self.tenant_id:
                raise UserError(_('No tenant specified for billing.'))
            customer = self.tenant_id
        elif self.bill_to == 'owner':
            if not self.owner_id:
                raise UserError(_('No owner specified for billing.'))
            customer = self.owner_id
        else:
            raise UserError(_('Cannot create invoice for company billing.'))
        
        # Create invoice
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': customer.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Work Order: {self.name} - {self.title}',
                'quantity': 1,
                'price_unit': self.total_cost,
            })],
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.write({'invoice_id': invoice.id})
        
        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_invoice(self):
        self.ensure_one()
        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    work_order_id = fields.Many2one('work.order', string='Work Order', readonly=True)
