# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MaintenanceCostAnalysisWizard(models.TransientModel):
    _name = 'maintenance.cost.analysis.wizard'
    _description = 'Maintenance Cost Analysis'

    date_from = fields.Date(string='Date From', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.context_today)
    
    property_ids = fields.Many2many('property.property', string='Properties')
    building_ids = fields.Many2many('property.building', string='Buildings')
    unit_ids = fields.Many2many('property.unit', string='Units')
    asset_ids = fields.Many2many('property.asset', string='Assets')
    
    category_ids = fields.Many2many('maintenance.category', string='Categories')
    
    group_by = fields.Selection([
        ('property', 'Property'),
        ('building', 'Building'),
        ('unit', 'Unit'),
        ('asset', 'Asset'),
        ('category', 'Category'),
        ('month', 'Month'),
    ], string='Group By', default='property', required=True)
    
    def action_generate_report(self):
        self.ensure_one()
        
        # Build domain
        domain = [
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to),
            ('state', '=', 'completed'),
        ]
        
        if self.property_ids:
            domain.append(('property_id', 'in', self.property_ids.ids))
        
        if self.building_ids:
            domain.append(('building_id', 'in', self.building_ids.ids))
        
        if self.unit_ids:
            domain.append(('unit_id', 'in', self.unit_ids.ids))
        
        if self.asset_ids:
            domain.append(('asset_id', 'in', self.asset_ids.ids))
        
        if self.category_ids:
            domain.append(('category_id', 'in', self.category_ids.ids))
        
        # Find work orders
        work_orders = self.env['work.order'].search(domain)
        
        # Generate analysis data
        analysis_data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'total_cost': sum(work_orders.mapped('total_cost')),
            'labor_cost': sum(work_orders.mapped('labor_cost')),
            'material_cost': sum(work_orders.mapped('material_cost')),
            'contractor_cost': sum(work_orders.mapped('contractor_cost')),
            'work_order_count': len(work_orders),
        }
        
        return {
            'name': _('Maintenance Cost Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'work.order',
            'view_mode': 'tree,pivot,graph',
            'domain': domain,
            'context': {
                'search_default_group_by_%s' % self.group_by: 1,
            },
        }
