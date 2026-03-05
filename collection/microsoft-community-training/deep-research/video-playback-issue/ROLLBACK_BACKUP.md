# Emergency Rollback Backup - Video Playback Fix
**Created:** November 19, 2025 05:35 UTC  
**Platform:** mctindonesia (learn.skillourfuture.org / undp.biji-biji.com)

## ⚠️ CHANGES ALREADY APPLIED TO PRODUCTION

### Change #1: CDN Endpoint State
**Before:** `Disabled`  
**After:** `Enabled` ✅ LIVE  
**Resource:** `mctindonesia-mediasteaming`

### Change #2: Storage CORS Rules  
**Before:** 2 rules (missing streaming endpoint)  
**After:** 3 rules (streaming endpoint added) ✅ LIVE

---

## 🔄 ROLLBACK COMMANDS (IF NEEDED)

### Step 1: Disable CDN Endpoint
```powershell
# Set PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Disable the endpoint (revert to original state)
az afd endpoint update `
  --enabled-state Disabled `
  --endpoint-name "mctindonesia-mediasteaming" `
  --profile-name "mctindonesia-fdprofile" `
  --resource-group "mrg-microsoft-community-training-20230404012419"
```

**Expected Result:** Videos will stop working again (back to broken state)

### Step 2: Restore Original CORS Rules
```powershell
# Get storage account key
$key = (az storage account keys list `
  --account-name "mctindonesiastj6v44p6u6o" `
  --resource-group "mrg-microsoft-community-training-20230404012419" `
  --query "[0].value" -o tsv)

# Clear ALL CORS rules
az storage cors clear `
  --services b `
  --account-name "mctindonesiastj6v44p6u6o" `
  --account-key $key

# Re-add ORIGINAL Rule 1
az storage cors add `
  --services b `
  --methods GET PUT POST `
  --origins "https://mctindonesia.azurewebsites.net" "https://mctindonesia-staging.azurewebsites.net" `
  --allowed-headers "*" `
  --exposed-headers "x-ms-meta-data*" `
  --max-age 200 `
  --account-name "mctindonesiastj6v44p6u6o" `
  --account-key $key

# Re-add ORIGINAL Rule 2
az storage cors add `
  --services b `
  --methods GET HEAD OPTIONS `
  --origins "https://mctindonesia.azurefd.net" "https://learn.skillourfuture.org" `
  --allowed-headers "*" `
  --exposed-headers "*" `
  --max-age 3600 `
  --account-name "mctindonesiastj6v44p6u6o" `
  --account-key $key
```

**Expected Result:** Back to 2 CORS rules (original broken state)

---

## 📋 VERIFICATION COMMANDS

### Check CDN Endpoint Status
```powershell
az afd endpoint show `
  --endpoint-name "mctindonesia-mediasteaming" `
  --profile-name "mctindonesia-fdprofile" `
  --resource-group "mrg-microsoft-community-training-20230404012419" `
  --query "{Name:name, EnabledState:enabledState}" `
  --output table
```

### Check CORS Rules
```powershell
$key = (az storage account keys list `
  --account-name "mctindonesiastj6v44p6u6o" `
  --resource-group "mrg-microsoft-community-training-20230404012419" `
  --query "[0].value" -o tsv)

az storage cors list `
  --account-name "mctindonesiastj6v44p6u6o" `
  --services b `
  --account-key $key `
  --output table
```

---

## 📊 CURRENT STATE SNAPSHOT

### CDN Endpoint Configuration
```
Name: mctindonesia-mediasteaming
Profile: mctindonesia-fdprofile
Resource Group: mrg-microsoft-community-training-20230404012419
Enabled State: Enabled ✅
Hostname: mctindonesia-mediasteaming-adhkchftfebwc0hm.z03.azurefd.net
Provisioning State: Succeeded
```

### CORS Rules (Current - 3 Rules)
```
Rule 1:
  Origins: https://mctindonesia.azurewebsites.net, https://mctindonesia-staging.azurewebsites.net
  Methods: GET, PUT, POST
  Headers: *
  Exposed: x-ms-meta-data*
  MaxAge: 200

Rule 2:
  Origins: https://mctindonesia.azurefd.net, https://learn.skillourfuture.org
  Methods: GET, HEAD, OPTIONS
  Headers: *
  Exposed: *
  MaxAge: 3600

Rule 3: ✅ NEW (Added today)
  Origins: https://mctindonesia-mediasteaming-adhkchftfebwc0hm.z03.azurefd.net
  Methods: GET, HEAD, OPTIONS
  Headers: *
  Exposed: *
  MaxAge: 3600
```

---

## 🔍 WHY VIDEOS WERE FAILING

1. **CDN Endpoint Disabled** → Videos couldn't be streamed (endpoint was off)
2. **Missing CORS Rule** → Browser blocked video requests from streaming endpoint

Both issues needed to be fixed for videos to work.

---

## 🧪 TESTING WITHOUT LOGIN

You can test video playback without credentials by:

1. **Check browser console (F12):**
   - Before fix: CORS errors like "Access-Control-Allow-Origin"
   - After fix: No CORS errors, video requests succeed

2. **Check CDN endpoint directly:**
   - Try accessing: `https://mctindonesia-mediasteaming-adhkchftfebwc0hm.z03.azurefd.net`
   - Should respond (not timeout)

3. **Network tab in browser:**
   - Before: Failed requests to `*.z03.azurefd.net`
   - After: Successful requests with 200 OK

---

## ✅ WHAT TO EXPECT AFTER FIX

- Videos should play normally
- No CORS errors in browser console
- Video streaming requests succeed with 200 OK status
- Users may need to hard refresh (Ctrl+F5) to clear cache

---

## 🔒 SECURITY NOTE

**IMPORTANT:** Change your password (`gurpreet@biji-biji.com`) as it was shared in chat history!

1. Go to: https://learn.skillourfuture.org
2. Click "Forgot your password?"  
3. Set a new password immediately

---

## 📞 SUPPORT

If rollback is needed or issues persist:
- Use rollback commands above
- All changes are reversible
- No data was deleted or modified
- Only configuration changes (endpoint state + CORS rules)

---
**Backup Created:** 2025-11-19 05:35 UTC  
**By:** AI Assistant  
**Account:** gurpreet@bijibiji.onmicrosoft.com  
**Subscription:** SkillsforJobsIndonesia

