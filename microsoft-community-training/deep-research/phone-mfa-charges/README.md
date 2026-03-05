# Phone MFA Charges Investigation

**Date**: 2025-11-07  
**Status**: ✅ **COMPLETE**  
**Impact**: Identified root cause, disabled phone MFA, achieved 60.6% reduction in sign-ins

---

## 📊 Quick Summary

### Problem
- Phone MFA charges spiked from 98 MYR (July) to 3,816 MYR (September)
- October charges: 2,919 MYR (1,986 authentications)
- Root cause: Automated API calls from `ms.aiteach.my@bijibiji.onmicrosoft.com`

### Solution
- ✅ Phone MFA disabled: November 6, 2025
- ✅ Sign-ins reduced: 127/day (Nov 5) → 50/day (Nov 6) = 60.6% reduction
- ✅ Expected savings: ~2,770 MYR/month

---

## 📁 Documentation Structure

### Reports (`reports/`)
- **[COMPLETE_INVESTIGATION_REPORT.md](reports/COMPLETE_INVESTIGATION_REPORT.md)** - ⭐ **START HERE** - Complete investigation findings (consolidated)
- **[FINANCE_REFUND_REQUEST.md](reports/FINANCE_REFUND_REQUEST.md)** - 💰 **FINANCE TEAM** - Email template for requesting refund/credit
- **[MICROSOFT_SUPPORT_ESCALATION.md](reports/MICROSOFT_SUPPORT_ESCALATION.md)** - Escalation template for Microsoft Support (technical)

### CLI Documentation (`cli/`)
- **[CLI_PERMISSIONS_SETUP.md](cli/CLI_PERMISSIONS_SETUP.md)** - Permission configuration
- **[CLI_ACCESS_STATUS.md](cli/CLI_ACCESS_STATUS.md)** - Access status summary
- **[CLI_VERIFICATION_PROOF.md](cli/CLI_VERIFICATION_PROOF.md)** - Verification proof

### Data (`data/`)
- Invoice analysis JSON files
- Sign-in log exports
- Service charge breakdowns

---

## 🎯 Key Findings

### Root Cause
- **User**: `ms.aiteach.my@bijibiji.onmicrosoft.com`
- **App**: Office365 Shell WCSS-Client (automation)
- **Pattern**: 622 automated API calls in October (72% of user's sign-ins)
- **Third-party apps**: TeamsMaestro (assigned Sep 17, during spike)

### Impact
- **October**: 1,986 phone authentications = 2,919 MYR
- **November 5**: 127 sign-ins/day
- **November 6**: 50 sign-ins/day (60.6% reduction)

### Resolution
- Phone MFA (SMS/Voice) disabled Nov 6, 2025
- Sign-ins continue but phone MFA charges STOP
- Expected savings: ~2,770 MYR/month

---

## 📚 Reading Order

1. **Start here**: This README
2. **Complete investigation**: [COMPLETE_INVESTIGATION_REPORT.md](reports/COMPLETE_INVESTIGATION_REPORT.md) ⭐ **ALL KEY FINDINGS**
3. **Finance team**: [FINANCE_REFUND_REQUEST.md](reports/FINANCE_REFUND_REQUEST.md) 💰 **REFUND REQUEST EMAIL**
4. **Technical escalation**: [MICROSOFT_SUPPORT_ESCALATION.md](reports/MICROSOFT_SUPPORT_ESCALATION.md) - For technical escalation

---

## 🔗 Related Documents

- **Project Overview**: [../../README.md](../../README.md)
- **Workstream**: [../../workstreams/identity-auth.md](../../workstreams/identity-auth.md)
- **CLI Reference**: [../../cli-reference.md](../../cli-reference.md)

---

**Last Updated**: 2025-11-07  
**Status**: ✅ Investigation complete, phone MFA disabled, monitoring for December invoice
