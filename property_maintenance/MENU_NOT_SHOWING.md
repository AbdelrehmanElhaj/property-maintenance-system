# Menu Not Showing? Quick Fix Guide

## Problem
After installing the Property Maintenance module, the "Maintenance" menu doesn't appear in the navigation bar.

## Solution

### Method 1: Assign User Group (Recommended)

1. **Go to Settings**
   - Click on Settings in the top menu

2. **Navigate to Users & Companies**
   - Settings → Users & Companies → Users

3. **Edit Your User**
   - Find your user in the list
   - Click to open

4. **Add Maintenance Manager Group**
   - Go to the "Access Rights" tab
   - Look for "Property Maintenance" section
   - Check the "Manager" checkbox
   - Save

5. **Refresh Browser**
   - Press F5 or Ctrl+R
   - The "Maintenance" menu should now appear!

### Method 2: Developer Mode (Alternative)

1. **Enable Developer Mode**
   - Settings → Activate Developer Mode

2. **Go to Users**
   - Settings → Users & Companies → Users

3. **Edit User**
   - Open your user record

4. **Go to Technical Settings Tab**
   - Scroll down to find groups

5. **Add Groups**
   - Find and add:
     - "Property Maintenance / Manager"
     - OR "Property Maintenance / User"

6. **Save and Refresh**

### Method 3: Upgrade Module (If still not working)

1. **Go to Apps**
   - Click Apps in top menu

2. **Find Property Maintenance**
   - Remove "Apps" filter
   - Search: "property"

3. **Upgrade Module**
   - Click on the module
   - Click "Upgrade" button
   - Wait for completion

4. **Assign Groups Again**
   - Follow Method 1 steps
   - Refresh browser

## Verification

After following the steps, you should see:
- **"Maintenance"** menu in the top navigation
- Inside you'll find:
  - Requests
  - Work Orders  
  - Preventive Maintenance
  - Configuration

## Still Not Working?

### Check User Permissions

Run this in the database (be careful!):

```sql
-- Check if user has the group
SELECT u.login, g.name 
FROM res_users u
JOIN res_groups_users_rel r ON r.uid = u.id  
JOIN res_groups g ON g.id = r.gid
WHERE u.login = 'admin' AND g.name LIKE '%Maintenance%';
```

### Check Menu Items

In Developer Mode:
1. Settings → Technical → User Interface → Menu Items
2. Search for "Maintenance"
3. Check if the menu exists and has proper groups assigned

### Manual Group Assignment (SQL)

If absolutely necessary (database console):

```sql
-- Find the group ID
SELECT id, name FROM res_groups WHERE name LIKE '%Maintenance%Manager%';

-- Add user to group (replace USER_ID and GROUP_ID)
INSERT INTO res_groups_users_rel (gid, uid) 
VALUES (GROUP_ID, USER_ID)
ON CONFLICT DO NOTHING;
```

## Quick Start After Menu Appears

1. **Create Property**
   - Maintenance → Configuration → Master Data → Properties

2. **Add Buildings and Units**
   - In property form, add buildings
   - In buildings, add units

3. **Create Maintenance Request**
   - Maintenance → Requests → Create

4. **Test the Workflow**
   - Submit → Approve → Convert to Work Order

## Need Help?

- Check module logs: `tail -f /var/log/odoo/odoo.log`
- Restart Odoo: `sudo systemctl restart odoo`
- Reinstall module if needed

---

© 2026 DevIntelle Consulting Services Pvt. Ltd.
