# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConvertToWorkOrderWizard(models.TransientModel):
    _name = 'convert.to.work.order.wizard'
    _description = 'Convert Maintenance Request to Work Order'

    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request', required=True)
    
    title = fields.Char(string='Work Order Title', required=True)
    description = fields.Html(string='Description')
    
    property_id = fields.Many2one('property.property', string='Property', required=True)
    building_id = fields.Many2one('property.building', string='Building', required=True)
    unit_id = fields.Many2one('property.unit', string='Unit')
    asset_id = fields.Many2one('property.asset', string='Asset')
    
    category_id = fields.Many2one('maintenance.category', string='Category', required=True)
    
    work_type = fields.Selection([
        ('internal', 'Internal Team'),
        ('contractor', 'External Contractor'),
        ('mixed', 'Mixed'),
    ], string='Work Type', default='internal', required=True)
    
    team_id = fields.Many2one('maintenance.team', string='Maintenance Team')
    technician_ids = fields.Many2many('maintenance.technician', string='Technicians')
    contractor_id = fields.Many2one('maintenance.contractor', string='Contractor')
    
    scheduled_date = fields.Datetime(string='Scheduled Date', required=True, default=fields.Datetime.now)
    
    estimated_duration = fields.Float(string='Estimated Duration (Hours)', default=1.0)
    estimated_cost = fields.Float(string='Estimated Cost')
    
    billable = fields.Boolean(string='Billable', default=False)
    bill_to = fields.Selection([
        ('tenant', 'Tenant'),
        ('owner', 'Owner'),
        ('company', 'Company'),
    ], string='Bill To')
    
    @api.onchange('maintenance_request_id')
    def _onchange_maintenance_request(self):
        if self.maintenance_request_id:
            self.title = self.maintenance_request_id.title
            self.description = self.maintenance_request_id.description
            self.property_id = self.maintenance_request_id.property_id
            self.building_id = self.maintenance_request_id.building_id
            self.unit_id = self.maintenance_request_id.unit_id
            self.asset_id = self.maintenance_request_id.asset_id
            self.category_id = self.maintenance_request_id.category_id
            self.team_id = self.maintenance_request_id.team_id
            self.scheduled_date = self.maintenance_request_id.scheduled_date or fields.Datetime.now()
            self.estimated_cost = self.maintenance_request_id.estimated_cost
            self.billable = self.maintenance_request_id.billable
    
    def action_convert(self):
        self.ensure_one()
        
        if self.maintenance_request_id.work_order_id:
            raise UserError(_('A work order already exists for this maintenance request.'))
        
        # Create work order
        wo_vals = {
            'title': self.title,
            'description': self.description,
            'maintenance_request_id': self.maintenance_request_id.id,
            'property_id': self.property_id.id,
            'building_id': self.building_id.id,
            'unit_id': self.unit_id.id if self.unit_id else False,
            'asset_id': self.asset_id.id if self.asset_id else False,
            'category_id': self.category_id.id,
            'work_type': self.work_type,
            'team_id': self.team_id.id if self.team_id else False,
            'contractor_id': self.contractor_id.id if self.contractor_id else False,
            'scheduled_date': self.scheduled_date,
            'billable': self.billable,
            'bill_to': self.bill_to,
            'tenant_id': self.maintenance_request_id.tenant_id.id if self.maintenance_request_id.tenant_id else False,
            'owner_id': self.maintenance_request_id.owner_id.id if self.maintenance_request_id.owner_id else False,
            'state': 'scheduled',
        }
        
        work_order = self.env['work.order'].create(wo_vals)
        
        # Add technicians
        if self.technician_ids:
            work_order.technician_ids = [(6, 0, self.technician_ids.ids)]
        
        # Link work order to maintenance request
        self.maintenance_request_id.write({'work_order_id': work_order.id})
        
        # Update maintenance request stage
        approved_stage = self.env['maintenance.stage'].search([('code', '=', 'approved')], limit=1)
        if approved_stage:
            self.maintenance_request_id.write({'stage_id': approved_stage.id})
        
        # Post message
        self.maintenance_request_id.message_post(
            body=_('Work order %s created from this maintenance request.') % work_order.name
        )
        
        return {
            'name': _('Work Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'work.order',
            'res_id': work_order.id,
            'view_mode': 'form',
            'target': 'current',
        }
