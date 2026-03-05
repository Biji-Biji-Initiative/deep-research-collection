# Azure CLI Permissions Setup for Entra ID Sign-In Logs

**Date**: 2025-11-06  
**Purpose**: Configure Azure CLI to query Entra ID sign-in logs and audit logs via Microsoft Graph API

---

## ✅ Current Status

**Good News**: Sign-in logs ARE accessible via CLI now!

```bash
# Test query (works as of 2025-11-06)
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/auditLogs/signIns?\$top=5" \
  --headers "Content-Type=application/json"
```

**Result**: ✅ SUCCESS - Returns sign-in data

---

## 🔐 Required Permissions

### For Querying Sign-In Logs

**Microsoft Graph API Permissions**:
- ✅ `AuditLog.Read.All` - Read audit logs (sign-in logs)
- ✅ `Directory.Read.All` - Read directory data (for user lookups)

**Entra ID Roles** (one of the following):
- ✅ `Global Administrator` - Full access (recommended for CLI automation)
- ✅ `Security Reader` - Read-only access to security data
- ✅ `Audit Logs Reader` - Read-only access to audit logs

### Current User
- **User**: `gurpreet@bijibiji.onmicrosoft.com`
- **User ID**: `406b929b-e2e7-4148-848c-d0dd4e5b6ea5`
- **Status**: ✅ Has access to sign-in logs (confirmed via test query)

---

## 🔧 How to Configure Permissions (If Needed)

### Option 1: Assign Directory Role (Recommended)

**Via Azure Portal**:
1. Navigate to: https://entra.microsoft.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RolesAndAdministrators
2. Search for role: **Global Administrator** or **Security Reader**
3. Click **Add assignments**
4. Select user: `gurpreet@bijibiji.onmicrosoft.com`
5. Click **Add**

**Via Azure CLI**:
```bash
# Get Global Administrator role template ID
GLOBAL_ADMIN_ROLE_ID="62e90394-69f5-4237-9190-012177145e10"

# Get role directory ID
ROLE_DIR_ID=$(az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/directoryRoles?\$filter=roleTemplateId eq '$GLOBAL_ADMIN_ROLE_ID'" \
  --headers "Content-Type=application/json" \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['value'][0]['id'] if d.get('value') else '')")

# Add user to role (requires Global Admin)
USER_ID="406b929b-e2e7-4148-848c-d0dd4e5b6ea5"
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/directoryRoles/$ROLE_DIR_ID/members/\$ref" \
  --headers "Content-Type=application/json" \
  --body "{\"@odata.id\": \"https://graph.microsoft.com/v1.0/directoryUsers/$USER_ID\"}"
```

### Option 2: Grant App Permissions (For Service Principal)

If using a service principal instead of user account:

1. **Create App Registration**:
   ```bash
   az ad app create --display-name "Cost-Optimization-CLI" \
     --required-resource-accesses @app-permissions.json
   ```

2. **Grant Admin Consent**:
   - Navigate to: https://entra.microsoft.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview
   - Select your app
   - Go to **API permissions**
   - Click **Grant admin consent**

3. **Required Permissions**:
   ```json
   {
     "resourceAppId": "00000003-0000-0000-c000-000000000000",
     "resourceAccess": [
       {
         "id": "b0afded3-3588-46d8-8b3d-9842fad7e4c0",
         "type": "Role",
         "description": "AuditLog.Read.All"
       },
       {
         "id": "7ab1d382-f21e-4acd-a863-ba3e13f7da61",
         "type": "Role",
         "description": "Directory.Read.All"
       }
     ]
   }
   ```

---

## ✅ Verification Steps

### Test 1: Basic Graph API Access
```bash
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/me" \
  --headers "Content-Type=application/json"
```
**Expected**: Returns user profile ✅

### Test 2: Sign-In Logs Access
```bash
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/auditLogs/signIns?\$top=5" \
  --headers "Content-Type=application/json"
```
**Expected**: Returns array of sign-in objects ✅

### Test 3: Directory Roles Access
```bash
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/directoryRoles" \
  --headers "Content-Type=application/json"
```
**Expected**: Returns list of directory roles ✅

---

## 📝 CLI Login Best Practices

### For Graph API Access

**Standard Login** (uses default scopes):
```bash
az login
```

**With Graph API Scope** (explicit):
```bash
az login --scope https://graph.microsoft.com/.default
```

**For Service Principal**:
```bash
az login --service-principal \
  --username <app-id> \
  --password <client-secret> \
  --tenant <tenant-id>
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "accessDenied" Error
**Symptom**: `{"error":{"code":"accessDenied","message":"..."}}`

**Solution**:
1. Verify user has Global Administrator or Security Reader role
2. Check if admin consent is required for app permissions
3. Wait 5-10 minutes after role assignment (propagation delay)

### Issue 2: "Insufficient privileges"
**Symptom**: Can query some endpoints but not others

**Solution**:
- Some operations require **Global Administrator** specifically
- **Security Reader** may not be sufficient for all operations
- Check specific permission requirements for the endpoint

### Issue 3: Token Expired
**Symptom**: `401 Unauthorized` after working initially

**Solution**:
```bash
# Re-authenticate
az login --scope https://graph.microsoft.com/.default
```

---

## 📚 Useful CLI Commands

### Query Sign-In Logs
```bash
# Last 24 hours
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/auditLogs/signIns?\$filter=createdDateTime ge $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --headers "Content-Type=application/json"

# Specific user
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/auditLogs/signIns?\$filter=userPrincipalName eq 'ms.aiteach.my@bijibiji.onmicrosoft.com'" \
  --headers "Content-Type=application/json"

# With pagination
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/auditLogs/signIns?\$top=100&\$skip=0" \
  --headers "Content-Type=application/json"
```

### Query Directory Roles
```bash
# List all roles
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/directoryRoles" \
  --headers "Content-Type=application/json"

# Check user's roles
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/users/gurpreet@bijibiji.onmicrosoft.com/memberOf" \
  --headers "Content-Type=application/json"
```

### Query Authentication Methods
```bash
# Get authentication methods policy (requires Global Admin)
az rest --method GET \
  --url "https://graph.microsoft.com/beta/policies/authenticationMethodsPolicy" \
  --headers "Content-Type=application/json"
```

---

## ✅ Checklist

- [x] User can query sign-in logs via CLI
- [x] User can query directory roles
- [x] User can query user profiles
- [ ] User has Global Administrator role (verify if needed)
- [ ] Admin consent granted for app permissions (if using service principal)
- [ ] Documentation updated with permission requirements

---

## 📖 References

- [Microsoft Graph API Permissions](https://learn.microsoft.com/en-us/graph/permissions-reference)
- [Entra ID Directory Roles](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions)
- [Azure CLI Authentication](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli)

---

**Last Updated**: 2025-11-06  
**Status**: ✅ CLI access confirmed working

