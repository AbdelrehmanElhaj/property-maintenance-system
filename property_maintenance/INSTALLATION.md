# Installation Guide - Property Maintenance Management Module

## Prerequisites

- Odoo 15 Enterprise Edition installed
- Python 3.7 or higher
- PostgreSQL database
- Admin access to Odoo instance

## Installation Steps

### 1. Upload Module

Copy the `property_maintenance` folder to your Odoo addons directory:

```bash
# For standard installation
cp -r property_maintenance /opt/odoo/addons/

# For custom addons path
cp -r property_maintenance /path/to/your/custom/addons/
```

### 2. Update Odoo Configuration

Edit your `odoo.conf` file to include the addons path:

```ini
[options]
addons_path = /opt/odoo/addons,/path/to/your/custom/addons
```

### 3. Restart Odoo Service

```bash
sudo systemctl restart odoo
# or
sudo service odoo restart
```

### 4. Update Apps List

1. Log in to Odoo as Administrator
2. Enable Developer Mode:
   - Settings → Activate Developer Mode
3. Go to Apps menu
4. Click "Update Apps List" button
5. Click "Update" in the confirmation dialog

### 5. Install the Module

1. In Apps menu, remove the "Apps" filter
2. Search for "Property Maintenance Management"
3. Click the "Install" button
4. Wait for installation to complete

## Post-Installation Configuration

### 1. Set Up Partner Types

Add custom fields to partners for tenant and owner identification:

1. Go to Settings → Technical → Database Structure → Models
2. Find model "res.partner"
3. Add two boolean fields:
   - `is_tenant` (Label: "Is a Tenant")
   - `is_property_owner` (Label: "Is Property Owner")

Or run this SQL in database:

```sql
ALTER TABLE res_partner ADD COLUMN is_tenant BOOLEAN DEFAULT FALSE;
ALTER TABLE res_partner ADD COLUMN is_property_owner BOOLEAN DEFAULT FALSE;
```

### 2. Configure Users and Access Rights

1. Go to Settings → Users & Companies → Users
2. For each user, assign appropriate groups:
   - Maintenance Manager
   - Maintenance Technician
   - Maintenance User

### 3. Set Up Portal Access

For Tenants:
```
Settings → Users & Companies → Users
Create new user → Portal Access
Technical Settings → Add to group "Portal - Tenant"
```

For Owners:
```
Settings → Users & Companies → Users
Create new user → Portal Access
Technical Settings → Add to group "Portal - Owner"
```

### 4. Configure Email Templates

1. Navigate to Settings → Technical → Email → Templates
2. Find templates starting with "Property Maintenance"
3. Customize as needed for your organization

### 5. Set Up Scheduled Actions

The module includes a cron job for preventive maintenance. Verify it's active:

1. Go to Settings → Technical → Automation → Scheduled Actions
2. Find "Auto-Generate Preventive Maintenance"
3. Ensure it's active and scheduled correctly (recommended: daily)

## Initial Data Setup

### 1. Create Maintenance Teams

```
Maintenance → Configuration → Teams
```

Create teams like:
- Electrical Team
- Plumbing Team
- HVAC Team
- General Maintenance

### 2. Add Technicians

```
Maintenance → Configuration → Technicians
```

Link technicians to:
- User accounts
- HR employees (if HR module is installed)
- Teams
- Specializations

### 3. Register Contractors

```
Maintenance → Configuration → Contractors
```

Add external contractors with:
- Company details
- Contact information
- Service categories
- License and insurance details

### 4. Set Up Properties

```
Maintenance → Configuration → Properties
```

Create property hierarchy:
1. Create Properties
2. Add Buildings to each property
3. Add Units to each building

### 5. Register Assets

```
Maintenance → Configuration → Assets
```

Add assets to units:
- HVAC systems
- Electrical equipment
- Plumbing systems
- Appliances
- Security systems

### 6. Create Preventive Maintenance Plans

```
Maintenance → Preventive Maintenance
```

Set up recurring maintenance:
- Select asset or unit
- Choose frequency
- Assign team/technicians
- Enable auto-generation

## Verification Steps

### 1. Test Maintenance Request Creation

1. Go to Maintenance → Requests
2. Create a new request
3. Fill in all required fields
4. Submit and verify workflow

### 2. Test Work Order Conversion

1. Open a maintenance request
2. Click "Convert to Work Order"
3. Verify work order creation
4. Check cost line functionality

### 3. Test Portal Access

1. Log in as a portal user (tenant)
2. Navigate to /my/maintenance
3. Create a new request
4. Verify visibility restrictions

### 4. Test Preventive Maintenance

1. Create a PM plan
2. Activate the plan
3. Set next execution to today
4. Run the cron job manually or wait for scheduled run
5. Verify work order generation

### 5. Test Cost Tracking

1. Create a work order
2. Add cost lines (labor, materials, contractor)
3. Verify total cost calculation
4. Test invoice generation for billable work

## Troubleshooting

### Module Not Appearing in Apps

- Verify the module is in the correct addons path
- Check Odoo logs for errors: `tail -f /var/log/odoo/odoo.log`
- Ensure all dependencies are installed
- Restart Odoo service

### Permission Errors

- Verify user has correct access rights
- Check security groups assignment
- Review ir.rules in security file

### Portal Users Cannot Access

- Ensure users are in correct portal groups
- Verify URL: yourdomain.com/my/maintenance
- Check that maintenance requests have correct tenant/owner links

### Cron Job Not Running

- Check scheduled actions are active
- Verify Odoo workers are running: `ps aux | grep odoo`
- Check cron logs for errors

### Database Errors

- Ensure PostgreSQL is running
- Check database connection in odoo.conf
- Verify database user has correct permissions

## Upgrading

To upgrade the module:

1. Backup your database
2. Replace the module files
3. Restart Odoo
4. Go to Apps → Find module → Click "Upgrade"
5. Test all functionality after upgrade

## Uninstallation

⚠️ **Warning:** Uninstalling will remove all maintenance data!

1. Backup your database first
2. Go to Apps
3. Find "Property Maintenance Management"
4. Click "Uninstall"
5. Confirm the action

## Support

For installation issues:

**DevIntelle Consulting Services Pvt. Ltd.**
- Technical Support: support@devintelle.com
- Website: https://www.devintelle.com
- Phone: [Contact Information]

---

Last Updated: January 28, 2026
