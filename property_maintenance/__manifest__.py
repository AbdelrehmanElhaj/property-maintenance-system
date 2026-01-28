# -*- coding: utf-8 -*-
{
    'name': 'Property Maintenance Management',
    'version': '15.0.1.0.0',
    'category': 'Property Management',
    'summary': 'Complete Property Maintenance Management System with Reactive and Preventive Maintenance',
    'description': """
        Property Maintenance Management Module
        =======================================
        
        Features:
        ---------
        * Maintenance Request Management (Tickets)
        * Work Order Management
        * Preventive Maintenance Planning
        * Asset & Property Integration
        * Cost Tracking & Accounting Integration
        * Multi-user Portal (Tenants & Owners)
        * Technician & Contractor Management
        * SLA & Priority Management
        * Full Audit Trail
        
        Developed by: DevIntelle Consulting Services Pvt. Ltd.
        Date: January 28, 2026
        For: PropTech - Abdelrehman Elhaj
    """,
    'author': 'DevIntelle Consulting Services Pvt. Ltd.',
    'website': 'https://www.devintelle.com',
    'license': 'OPL-1',
    'depends': [
        'base',
        'mail',
        'portal',
        'account',
        'stock',
        'hr',
        'calendar',
        'web',
    ],
    'data': [
        # Security
        'security/maintenance_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/maintenance_sequence.xml',
        'data/maintenance_category_data.xml',
        'data/maintenance_stage_data.xml',
        'data/default_user_groups.xml',
        'data/module_installation_message.xml',
        
        # Views - Master Data
        'views/res_partner_views.xml',
        'views/maintenance_category_views.xml',
        'views/maintenance_stage_views.xml',
        'views/property_views.xml',
        'views/building_views.xml',
        'views/unit_views.xml',
        'views/asset_views.xml',
        
        # Views - Main Modules
        'views/maintenance_request_views.xml',
        'views/work_order_views.xml',
        'views/preventive_maintenance_views.xml',
        
        # Views - Supporting
        'views/maintenance_team_views.xml',
        'views/technician_views.xml',
        'views/contractor_views.xml',
        
        # Actions (must come before menu)
        'views/maintenance_actions.xml',
        
        # Portal
        'views/portal_templates.xml',
        
        # Reports
        'reports/maintenance_report_views.xml',
        'reports/maintenance_request_report.xml',
        'reports/work_order_report.xml',
        
        # Wizards
        'wizard/convert_to_work_order_views.xml',
        'wizard/maintenance_cost_analysis_views.xml',
        
        # Menu
        'views/maintenance_menu.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 900.00,
    'currency': 'USD',
}
