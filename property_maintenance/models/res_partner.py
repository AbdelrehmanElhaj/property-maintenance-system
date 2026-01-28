# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_tenant = fields.Boolean(string='Is a Tenant', default=False)
    is_property_owner = fields.Boolean(string='Is Property Owner', default=False)
    
    # Related maintenance data
    tenant_maintenance_request_ids = fields.One2many(
        'maintenance.request', 
        'tenant_id', 
        string='Tenant Maintenance Requests'
    )
    owner_maintenance_request_ids = fields.One2many(
        'maintenance.request', 
        'owner_id', 
        string='Owner Maintenance Requests'
    )
    
    tenant_unit_ids = fields.One2many(
        'property.unit', 
        'tenant_id', 
        string='Rented Units'
    )
    owner_unit_ids = fields.One2many(
        'property.unit', 
        'owner_id', 
        string='Owned Units'
    )
    owner_property_ids = fields.One2many(
        'property.property', 
        'owner_id', 
        string='Owned Properties'
    )
