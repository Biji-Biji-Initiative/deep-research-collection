# Quick Fix Runbook: Video Playback Issues

## Symptom
Videos not playing on MCT platform

## Quick Diagnosis

### 1. Login to Azure CLI
```bash
az login --use-device-code
az account set --subscription "SkillsforJobsIndonesia"
```

### 2. Check CDN Endpoint Status

**For mctindonesia (undp.biji-biji.com):**
```bash
az afd endpoint list \
  --profile-name "mctindonesia-fdprofile" \
  --resource-group "mrg-microsoft-community-training-20230404012419" \
  --output table
```

**For mct12332123 (sfjid.biji-biji.com):**
```bash
az afd endpoint list \
  --profile-name "mct12332123-fdprofile" \
  --resource-group "mrg-microsoft-community-training-20230322120143" \
  --output table
```

**For talentaidbijibiji (talentaid.biji-biji.com):**
```bash
az afd endpoint list \
  --profile-name "talentaidbijibij-cdn-afd-c12c0bd" \
  --resource-group "mrg-talentaid-bijibiji" \
  --output table
```

### 3. Look for `EnabledState: Disabled`
If you see a media streaming endpoint with `Disabled` state, that's your problem.

## Quick Fix Commands

### Enable mctindonesia media streaming:
```bash
az afd endpoint update \
  --enabled-state Enabled \
  --endpoint-name "mctindonesia-mediasteaming" \
  --profile-name "mctindonesia-fdprofile" \
  --resource-group "mrg-microsoft-community-training-20230404012419"
```

### Enable mct12332123 media streaming:
```bash
az afd endpoint update \
  --enabled-state Enabled \
  --endpoint-name "mct12332123-mediasteaming" \
  --profile-name "mct12332123-fdprofile" \
  --resource-group "mrg-microsoft-community-training-20230322120143"
```

### Enable talentaidbijibiji media streaming:
```bash
az afd endpoint update \
  --enabled-state Enabled \
  --endpoint-name "talentaidbijibiji-mediastreaming" \
  --profile-name "talentaidbijibij-cdn-afd-c12c0bd" \
  --resource-group "mrg-talentaid-bijibiji"
```

## Verification
After enabling, verify the fix:
```bash
az afd endpoint show \
  --endpoint-name "mctindonesia-mediasteaming" \
  --profile-name "mctindonesia-fdprofile" \
  --resource-group "mrg-microsoft-community-training-20230404012419" \
  --query "{Name:name, EnabledState:enabledState}" \
  --output table
```

Expected output: `EnabledState: Enabled`

## Test
1. Navigate to the affected platform
2. Try playing a video
3. Verify video loads and plays correctly

## Prevention
Set up Azure Monitor alerts:
```bash
# Create alert rule for endpoint state changes
az monitor metrics alert create \
  --name "cdn-endpoint-disabled-alert" \
  --resource-group "mrg-microsoft-community-training-20230404012419" \
  --scopes "/subscriptions/b5596ef4-4479-4819-8bc2-0197024f2051/resourcegroups/mrg-microsoft-community-training-20230404012419/providers/Microsoft.Cdn/profiles/mctindonesia-fdprofile" \
  --condition "avg EnabledState < 1" \
  --description "Alert when CDN endpoint is disabled"
```

## Troubleshooting Decision Tree

```
Videos not playing?
├─> Check CDN endpoint status
│   ├─> Disabled? → Enable it (this runbook)
│   └─> Enabled? → Check storage account
│       ├─> Storage unavailable? → Check resource health
│       └─> Storage available? → Check web app
│           ├─> Web app stopped? → Start web app
│           └─> Web app running? → Check application logs
└─> Still not working? → Check Front Door routing rules
```

## Platform Reference

| Platform | Subscription | Resource Group | Profile Name | Endpoint Name |
|----------|-------------|----------------|--------------|---------------|
| undp.biji-biji.com | SkillsforJobsIndonesia | mrg-microsoft-community-training-20230404012419 | mctindonesia-fdprofile | mctindonesia-mediasteaming |
| sfjid.biji-biji.com | SkillsforJobsIndonesia | mrg-microsoft-community-training-20230322120143 | mct12332123-fdprofile | mct12332123-mediasteaming |
| talentaid.biji-biji.com | SkillsforJobsIndonesia | mrg-talentaid-bijibiji | talentaidbijibij-cdn-afd-c12c0bd | talentaidbijibiji-mediastreaming |

---
**Last Updated:** November 19, 2025

