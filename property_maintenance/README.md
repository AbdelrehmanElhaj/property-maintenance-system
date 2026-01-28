# Property Maintenance Management Module for Odoo 15

## Overview
Complete Property Maintenance Management System for Odoo 15 Enterprise Edition, developed based on the RFP specifications for PropTech.

**Developer:** DevIntelle Consulting Services Pvt. Ltd.  
**Date:** January 28, 2026  
**Client:** PropTech - Abdelrehman Elhaj  
**Version:** 15.0.1.0.0  
**Price:** $900

## Features

### Core Modules

1. **Maintenance Requests (Tickets)**
   - Create requests from Admin users, Tenant portal, and Owner portal
   - Attach photos and documents
   - Categories (Electrical, Plumbing, HVAC, etc.)
   - Priority & SLA management
   - Complete workflow: New → Submitted → Approved → In Progress → On Hold → Completed → Closed → Cancelled
   - Internal notes and communication log
   - Full audit trail

2. **Work Orders**
   - Convert ticket to work order
   - Assign to internal technicians or external contractors
   - Schedule date & time
   - Track labor hours, materials/spare parts, and external services
   - Automatic cost calculation per work order

3. **Preventive Maintenance**
   - Preventive maintenance plans by asset type, property, building, or unit
   - Frequencies: Daily / Weekly / Monthly / Quarterly / Yearly
   - Auto-generate work orders
   - Calendar view
   - Alerts for overdue or missed maintenance

4. **Asset & Property Integration**
   - Each maintenance request/work order linked to Property, Building, Unit, and Asset
   - Maintain full maintenance history per Asset, Unit, Property, and Tenant

5. **Costing & Accounting Integration**
   - Track maintenance cost: labor, materials, contractor services
   - Support billable and non-billable maintenance
   - Create vendor bills and customer invoices (tenant/owner)
   - Cost analysis per Property, Unit, Owner, and Asset

## Technical Specifications

- **Platform:** Odoo 15 Enterprise
- **Environment:** Multi-company, SaaS/multi-tenant architecture
- **Languages:** English & Arabic UI (bilingual support)
- **Development:** Follows Odoo best practices, modular, upgrade-safe, and configurable

## User Roles & Access Rights

The system supports the following roles with proper access control:

1. **Maintenance Manager / Admin** - Full access to all features
2. **Technician** - Access to assigned work orders and maintenance requests
3. **Contractor** - Access to contractor-assigned work orders
4. **Tenant (Portal)** - Create and view own maintenance requests
5. **Owner (Portal)** - Create and view property-related requests
6. **Accounting User** - Access to cost tracking and invoicing

## Installation

1. Copy the module to your Odoo addons directory:
   ```bash
   cp -r property_maintenance /path/to/odoo/addons/
   ```

2. Update the addons list:
   - Go to Apps menu
   - Click "Update Apps List"

3. Install the module:
   - Search for "Property Maintenance Management"
   - Click Install

## Configuration

### Initial Setup

1. **Create Maintenance Teams**
   - Navigate to Maintenance → Configuration → Teams
   - Create teams and assign team leaders

2. **Add Technicians**
   - Navigate to Maintenance → Configuration → Technicians
   - Link to HR employees if available

3. **Register Contractors**
   - Navigate to Maintenance → Configuration → Contractors
   - Link to vendor partners

4. **Set up Properties**
   - Navigate to Maintenance → Configuration → Properties
   - Create property hierarchy (Property → Building → Unit)

5. **Register Assets**
   - Navigate to Maintenance → Configuration → Assets
   - Link assets to units

6. **Configure Preventive Maintenance**
   - Navigate to Maintenance → Preventive Maintenance
   - Create maintenance plans
   - Set frequencies and schedules

### Portal Access

#### For Tenants:
1. Create a portal user for the tenant
2. Link the user to the tenant partner
3. Assign "Portal - Tenant" group
4. Tenant can access via: yourdomain.com/my/maintenance

#### For Owners:
1. Create a portal user for the owner
2. Link the user to the owner partner
3. Assign "Portal - Owner" group
4. Owner can access via: yourdomain.com/my/maintenance

## Usage

### Creating a Maintenance Request

1. Navigate to Maintenance → Requests
2. Click "Create"
3. Fill in:
   - Title and description
   - Property, Building, Unit, Asset
   - Category and priority
   - Attach photos/documents
4. Submit for approval

### Converting to Work Order

1. Open a maintenance request
2. Click "Convert to Work Order"
3. Select:
   - Work type (Internal/Contractor/Mixed)
   - Assign technicians or contractor
   - Schedule date and time
4. Confirm creation

### Managing Work Orders

1. Navigate to Maintenance → Work Orders
2. View work orders in list, form, or calendar view
3. Start work order when ready
4. Add cost lines for:
   - Labor (hours × hourly rate)
   - Materials (quantity × unit price)
   - Contractor services
5. Complete work order when finished

### Preventive Maintenance

1. Create preventive maintenance plan
2. Set frequency and schedule
3. System auto-generates work orders based on schedule
4. Cron job runs daily to check for due maintenance

### Cost Analysis

1. Navigate to Maintenance → Reports → Cost Analysis
2. Select date range and filters
3. Group by Property, Unit, Asset, or Category
4. View pivot tables and charts

## Database Structure

### Main Models

- `maintenance.category` - Maintenance categories
- `maintenance.stage` - Workflow stages
- `property.property` - Properties
- `property.building` - Buildings
- `property.unit` - Units
- `property.asset` - Assets
- `maintenance.request` - Maintenance tickets
- `work.order` - Work orders
- `maintenance.cost.line` - Cost tracking
- `preventive.maintenance` - PM plans
- `maintenance.team` - Maintenance teams
- `maintenance.technician` - Technicians
- `maintenance.contractor` - Contractors

## API Integration

The module inherits from `mail.thread` and `mail.activity.mixin` for:
- Email notifications
- Activity tracking
- Follower management

Portal integration via `portal.mixin` enables:
- Tenant and owner self-service
- Online request submission
- Request tracking

## Scheduled Actions

### Auto-Generate Preventive Maintenance
- **Model:** `preventive.maintenance`
- **Method:** `cron_generate_preventive_maintenance`
- **Interval:** Daily
- **Purpose:** Automatically creates work orders for preventive maintenance plans

## Reports

### Available Reports

1. **Maintenance Request Report** - PDF report for maintenance requests
2. **Work Order Report** - PDF report for work orders
3. **Cost Analysis Report** - Pivot and graph views for cost analysis
4. **Maintenance History** - Complete history per property/unit/asset

## Customization

The module is designed to be easily customizable:

- Add custom fields to models
- Extend workflow stages
- Add new maintenance categories
- Customize reports and views
- Integrate with other modules

## Support & Maintenance

For support, customization, or questions:

**DevIntelle Consulting Services Pvt. Ltd.**
- Website: https://www.devintelle.com
- Email: support@devintelle.com

## License

This module is licensed under OPL-1 (Odoo Proprietary License v1.0)

## Changelog

### Version 15.0.1.0.0 (January 28, 2026)
- Initial release
- Full implementation of RFP requirements
- Multi-language support (English & Arabic)
- Portal integration for tenants and owners
- Preventive maintenance automation
- Complete cost tracking and accounting integration

## Credits

**Developed by:** DevIntelle Consulting Services Pvt. Ltd.  
**For:** PropTech - Abdelrehman Elhaj  
**Based on:** RFP - Property Maintenance Management Module

---

© 2026 DevIntelle Consulting Services Pvt. Ltd. All rights reserved.
