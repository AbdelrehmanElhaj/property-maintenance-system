# Property Maintenance Module Structure

## Directory Structure

```
property_maintenance/
├── __init__.py                          # Module initialization
├── __manifest__.py                      # Module manifest with metadata
├── README.md                            # Comprehensive documentation
├── INSTALLATION.md                      # Installation guide
├── MODULE_STRUCTURE.md                  # This file
│
├── models/                              # Python models (business logic)
│   ├── __init__.py
│   ├── res_partner.py                   # Partner extension (tenant/owner flags)
│   ├── maintenance_category.py          # Maintenance categories
│   ├── maintenance_stage.py             # Workflow stages
│   ├── property.py                      # Property model
│   ├── building.py                      # Building model
│   ├── unit.py                          # Unit model
│   ├── asset.py                         # Asset model
│   ├── maintenance_request.py           # Maintenance request (ticket) model
│   ├── work_order.py                    # Work order model
│   ├── maintenance_cost_line.py         # Cost tracking lines
│   ├── preventive_maintenance.py        # Preventive maintenance plans
│   ├── maintenance_team.py              # Maintenance teams
│   ├── technician.py                    # Technician records
│   └── contractor.py                    # Contractor records
│
├── security/                            # Access control
│   ├── maintenance_security.xml         # Security groups and rules
│   └── ir.model.access.csv             # Model access rights (CRUD permissions)
│
├── data/                                # Default data
│   ├── maintenance_sequence.xml         # Number sequences
│   ├── maintenance_category_data.xml    # Default categories
│   └── maintenance_stage_data.xml       # Default workflow stages
│
├── views/                               # XML views (UI definitions)
│   ├── maintenance_menu.xml             # Menu structure
│   ├── maintenance_category_views.xml   # Category views
│   ├── maintenance_stage_views.xml      # Stage views
│   ├── property_views.xml               # Property views
│   ├── building_views.xml               # Building views
│   ├── unit_views.xml                   # Unit views
│   ├── asset_views.xml                  # Asset views
│   ├── maintenance_request_views.xml    # Request views (tree, form, kanban)
│   ├── work_order_views.xml            # Work order views
│   ├── preventive_maintenance_views.xml # PM plan views
│   ├── maintenance_team_views.xml       # Team views
│   ├── technician_views.xml            # Technician views
│   ├── contractor_views.xml            # Contractor views
│   └── portal_templates.xml            # Portal templates
│
├── wizard/                              # Transient models (wizards)
│   ├── __init__.py
│   ├── convert_to_work_order.py        # Convert request to work order
│   ├── convert_to_work_order_views.xml
│   ├── maintenance_cost_analysis.py     # Cost analysis wizard
│   └── maintenance_cost_analysis_views.xml
│
├── reports/                             # Report definitions
│   ├── maintenance_report_views.xml     # Report menu items
│   ├── maintenance_request_report.xml   # Request report template
│   └── work_order_report.xml           # Work order report template
│
└── static/                              # Static assets
    └── description/
        ├── icon.png                     # Module icon
        └── banner.png                   # Module banner
```

## Model Relationships

### Core Models

1. **property.property** (Properties)
   - One2Many: property.building
   - One2Many: maintenance.request
   - Many2One: res.partner (owner)

2. **property.building** (Buildings)
   - Many2One: property.property
   - One2Many: property.unit
   - One2Many: maintenance.request

3. **property.unit** (Units)
   - Many2One: property.property
   - Many2One: property.building
   - One2Many: property.asset
   - One2Many: maintenance.request
   - Many2One: res.partner (tenant)
   - Many2One: res.partner (owner)

4. **property.asset** (Assets)
   - Many2One: property.property
   - Many2One: property.building
   - Many2One: property.unit
   - One2Many: maintenance.request
   - One2Many: preventive.maintenance

5. **maintenance.request** (Tickets)
   - Many2One: property.property
   - Many2One: property.building
   - Many2One: property.unit
   - Many2One: property.asset
   - Many2One: maintenance.category
   - Many2One: maintenance.stage
   - Many2One: maintenance.team
   - Many2One: res.partner (tenant)
   - Many2One: res.partner (owner)
   - One2Many: work.order

6. **work.order** (Work Orders)
   - Many2One: maintenance.request
   - Many2One: property.property
   - Many2One: property.building
   - Many2One: property.unit
   - Many2One: property.asset
   - Many2One: maintenance.category
   - Many2One: maintenance.team
   - Many2Many: maintenance.technician
   - Many2One: maintenance.contractor
   - One2Many: maintenance.cost.line
   - Many2One: account.move (invoice)

7. **maintenance.cost.line** (Cost Lines)
   - Many2One: work.order
   - Many2One: maintenance.technician
   - Many2One: maintenance.contractor
   - Many2One: product.product

8. **preventive.maintenance** (PM Plans)
   - Many2One: property.property
   - Many2One: property.building
   - Many2One: property.unit
   - Many2One: property.asset
   - Many2One: maintenance.category
   - Many2One: maintenance.team
   - Many2Many: maintenance.technician
   - One2Many: work.order

## Key Features Implementation

### 1. Workflow Management
- Implemented via `maintenance.stage` model
- Stages: New → Submitted → Approved → In Progress → On Hold → Completed → Closed → Cancelled
- Action buttons on maintenance requests and work orders

### 2. SLA Management
- Computed fields on `maintenance.request`
- Priority-based SLA hours (Urgent: 4h, High: 24h, Normal: 48h, Low: 72h)
- SLA status indicators (On Time, Warning, Overdue)

### 3. Portal Access
- Inherits from `portal.mixin`
- Separate access rules for tenants and owners
- Custom portal templates in `views/portal_templates.xml`

### 4. Cost Tracking
- `maintenance.cost.line` model for detailed cost tracking
- Categories: Labor, Material, Contractor, Other
- Automatic subtotal calculation
- Integration with accounting module

### 5. Preventive Maintenance
- Frequency options: Daily, Weekly, Monthly, Quarterly, Semi-Annual, Annual, Custom
- Auto-generation of work orders via cron job
- Calendar view for scheduling

### 6. Multi-company Support
- Company field on all major models
- Multi-company rules in security

### 7. Audit Trail
- All major models inherit from `mail.thread` and `mail.activity.mixin`
- Tracking enabled on key fields
- Message posting on state changes

## View Types Implemented

1. **Tree Views** - List view of records
2. **Form Views** - Detailed record editing
3. **Kanban Views** - Card-based workflow view
4. **Calendar Views** - For preventive maintenance scheduling
5. **Pivot Views** - For reporting and analysis
6. **Graph Views** - For visual reporting
7. **Search Views** - With filters and group by options

## Security Implementation

### Access Groups

1. **Maintenance User** - Basic access
2. **Maintenance Technician** - Can update work orders
3. **Maintenance Manager** - Full access
4. **Portal - Tenant** - Limited portal access
5. **Portal - Owner** - Limited portal access

### Access Rules

- Multi-company rules for data isolation
- Portal rules restrict access to own records
- CRUD permissions defined in ir.model.access.csv

## Integration Points

### With Odoo Core Modules

1. **Accounting (`account`)**
   - Customer invoices for billable work
   - Vendor bills from contractors
   - Cost tracking

2. **Inventory (`stock`)**
   - Material/spare parts tracking
   - Product integration for cost lines

3. **HR (`hr`)**
   - Technician linkage to employees
   - Hourly rate from employee records

4. **Calendar (`calendar`)**
   - Work order scheduling
   - Preventive maintenance planning

5. **Portal (`portal`)**
   - Tenant self-service
   - Owner self-service

## Customization Points

### Easy to Extend

1. Add new maintenance categories
2. Create custom workflow stages
3. Add custom fields to models
4. Create custom reports
5. Extend portal functionality
6. Add email templates
7. Create custom dashboards

### Recommended Extensions

1. Mobile app integration
2. QR code asset tagging
3. Photo attachments with GPS
4. SMS notifications
5. WhatsApp integration
6. IoT sensor integration
7. Predictive maintenance AI

## Database Tables Created

Core tables:
- `maintenance_category`
- `maintenance_stage`
- `property_property`
- `property_building`
- `property_unit`
- `property_asset`
- `maintenance_request`
- `work_order`
- `maintenance_cost_line`
- `preventive_maintenance`
- `maintenance_team`
- `maintenance_technician`
- `maintenance_contractor`

Relation tables (Many2Many):
- `maintenance_request_attachment_rel`
- `work_order_attachment_rel`
- `work_order_technician_rel`
- `preventive_maintenance_technician_rel`
- `maintenance_team_member_rel`
- `team_category_rel`
- `technician_category_rel`
- `contractor_category_rel`

## Sequences

- `maintenance.request` → MR00001, MR00002, ...
- `work.order` → WO00001, WO00002, ...

## Cron Jobs

1. **Auto-Generate Preventive Maintenance**
   - Model: `preventive.maintenance`
   - Method: `cron_generate_preventive_maintenance`
   - Interval: Daily
   - Function: Creates work orders for due preventive maintenance

## Technical Specifications

- **Odoo Version:** 15.0 Enterprise
- **Python Version:** 3.7+
- **Database:** PostgreSQL
- **License:** OPL-1
- **Dependencies:**
  - base
  - mail
  - portal
  - account
  - stock
  - hr
  - calendar
  - web

## Performance Considerations

1. Indexed fields:
   - name (on all major models)
   - create_date
   - write_date
   - company_id

2. Computed fields with store=True:
   - Cost calculations
   - Counts
   - SLA status

3. SQL constraints for data integrity:
   - Unique codes per company
   - Required fields enforcement

## Testing Checklist

- [ ] Create property hierarchy
- [ ] Create maintenance request
- [ ] Convert request to work order
- [ ] Add cost lines
- [ ] Complete work order
- [ ] Create preventive maintenance plan
- [ ] Test auto-generation
- [ ] Test portal access (tenant)
- [ ] Test portal access (owner)
- [ ] Create and post invoice
- [ ] Test multi-company isolation
- [ ] Test permissions for each role
- [ ] Test workflow state transitions
- [ ] Test SLA calculations
- [ ] Generate reports

---

**Module Version:** 15.0.1.0.0  
**Last Updated:** January 28, 2026  
**Developed by:** DevIntelle Consulting Services Pvt. Ltd.
