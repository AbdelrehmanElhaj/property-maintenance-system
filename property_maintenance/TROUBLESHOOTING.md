# Troubleshooting Guide - Property Maintenance Module

## Common Issues and Solutions

### Issue 1: KeyError: 'maintenance.request'

**Error Message:**
```
KeyError: 'maintenance.request'
```

**Cause:** The module isn't fully loaded or needs to be upgraded.

**Solution:**
1. **Uninstall the module completely**
   - Apps → Search "property" → Uninstall
   - Confirm uninstallation

2. **Restart Odoo**
   ```bash
   sudo systemctl restart odoo
   ```

3. **Update Apps List**
   - Apps → Update Apps List

4. **Reinstall the module**
   - Apps → Search "Property Maintenance" → Install

5. **Assign user groups**
   - Settings → Users → Your User → Access Rights
   - Check "Maintenance Manager"

6. **Refresh browser** (Ctrl+R or F5)

### Issue 2: Menu Not Showing

**Solution:** See MENU_NOT_SHOWING.md or:
- Settings → Users → Your User
- Access Rights tab → Property Maintenance → Check "Manager"
- Save and refresh

### Issue 3: "Is Property Owner" Checkbox Not Visible

**Solution:**
1. **Run SQL to add fields:**
   ```sql
   ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS is_property_owner BOOLEAN DEFAULT FALSE;
   ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS is_tenant BOOLEAN DEFAULT FALSE;
   ```

2. **Upgrade the module:**
   - Apps → Search "property" → Upgrade

3. **Refresh browser**

### Issue 4: AttributeError in Preventive Maintenance

**Error:**
```
AttributeError: type object 'Datetime' has no attribute 'combine'
```

**Solution:** This is fixed in version 15.0.1.0.1 and later. Upgrade the module.

### Issue 5: Cannot Create Maintenance Request

**Possible Causes:**
1. No properties exist
2. No categories exist
3. No stages exist
4. User doesn't have permission

**Solution:**
1. **Check if master data exists:**
   - Maintenance → Configuration → Properties (create at least one)
   - Check if categories loaded (should be 10 default categories)
   - Check if stages loaded (should be 8 default stages)

2. **Verify user has access:**
   - Settings → Users → Check groups

3. **Check Odoo logs:**
   ```bash
   tail -f /var/log/odoo/odoo.log
   ```

### Issue 6: Access Denied Errors

**Solution:**
Assign proper groups to users:
- Maintenance Manager - Full access
- Maintenance Technician - Work order access
- Maintenance User - Basic access

### Issue 7: Views Not Loading

**Solution:**
1. **Clear browser cache**
2. **Restart Odoo**
3. **Upgrade module**
4. **Check for XML errors in logs**

### Issue 8: Data Not Saving

**Possible Causes:**
1. Required fields missing
2. Database constraints
3. Validation errors

**Solution:**
1. Check which fields are required (marked with *)
2. Look at error message in browser console (F12)
3. Check Odoo logs for detailed error

### Issue 9: Cost Calculations Not Working

**Solution:**
1. Ensure quantity and unit_price are filled
2. Check that cost_type is selected
3. Verify computed field dependencies

### Issue 10: Module Installation Fails

**Common Errors and Fixes:**

**Error: "Model not found"**
- Ensure all Python files are present
- Check __init__.py imports
- Restart Odoo

**Error: "XML Syntax Error"**
- Check all XML files for proper syntax
- Ensure all tags are closed
- Verify XML encoding is UTF-8

**Error: "Dependency missing"**
- Install: base, mail, portal, account, stock, hr, calendar
- These should be in Odoo by default

## Complete Reinstallation Process

If nothing works, follow this clean installation:

### Step 1: Complete Removal
```bash
# Stop Odoo
sudo systemctl stop odoo

# Remove module folder
sudo rm -rf /opt/odoo/addons/property_maintenance
sudo rm -rf /var/lib/odoo/.local/share/Odoo/addons/*/property_maintenance

# Drop database (WARNING: This deletes all data!)
# Only do this on test systems
sudo -u postgres psql
DROP DATABASE your_database_name;
CREATE DATABASE your_database_name OWNER odoo;
\q
```

### Step 2: Fresh Install
```bash
# Extract new module
unzip property_maintenance_odoo15_COMPLETE.zip

# Copy to addons
sudo cp -r property_maintenance /opt/odoo/addons/

# Set permissions
sudo chown -R odoo:odoo /opt/odoo/addons/property_maintenance
sudo chmod -R 755 /opt/odoo/addons/property_maintenance

# Start Odoo
sudo systemctl start odoo

# Check logs
tail -f /var/log/odoo/odoo.log
```

### Step 3: Install in Odoo
1. Log in as admin
2. Apps → Update Apps List
3. Search "property"
4. Install
5. Wait for completion
6. Assign user to groups
7. Refresh browser

## Verification Checklist

After installation, verify:

- [ ] Module appears in Apps as "Installed"
- [ ] "Maintenance" menu appears in top navigation
- [ ] Can access Maintenance → Configuration → Properties
- [ ] Can create a property
- [ ] Can create a building
- [ ] Can create a unit
- [ ] Can access Maintenance → Requests
- [ ] Can create a maintenance request
- [ ] 10 categories exist
- [ ] 8 stages exist
- [ ] No errors in Odoo log

## Getting Help

### Check Logs
```bash
# View live log
tail -f /var/log/odoo/odoo.log

# Search for errors
grep -i error /var/log/odoo/odoo.log

# Search for property maintenance errors
grep -i "property_maintenance" /var/log/odoo/odoo.log
```

### Database Checks

```sql
-- Check if models are registered
SELECT * FROM ir_model 
WHERE model LIKE 'maintenance.%' 
   OR model LIKE 'property.%';

-- Check if views exist
SELECT * FROM ir_ui_view 
WHERE model LIKE 'maintenance.%' 
   OR model LIKE 'property.%';

-- Check if menus exist
SELECT * FROM ir_ui_menu 
WHERE name LIKE '%Maintenance%';

-- Check if actions exist
SELECT * FROM ir_act_window 
WHERE res_model LIKE 'maintenance.%' 
   OR res_model LIKE 'property.%';
```

### Module Status

```sql
-- Check module state
SELECT name, state, latest_version 
FROM ir_module_module 
WHERE name = 'property_maintenance';

-- Should show: state = 'installed'
```

## Support

For persistent issues:
- Email: support@devintelle.com
- Check README.md for full documentation
- Review MODULE_STRUCTURE.md for technical details

## Known Limitations

1. Portal access (for tenants/owners) is foundation only - needs customization
2. Reports are placeholders - need to be developed
3. Email templates need to be configured
4. SMS notifications not included
5. Mobile app not included

These can be added as customizations.

---

© 2026 DevIntelle Consulting Services Pvt. Ltd.
