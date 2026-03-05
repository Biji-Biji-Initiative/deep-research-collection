# Microsoft Support Escalation Template

**Subject**: Unusual Phone MFA Charges - Request for Detailed Billing Breakdown and Goodwill Credit Consideration

**Priority**: High  
**Category**: Billing Inquiry  
**Tenant**: Biji-biji Initiative (bijibiji.onmicrosoft.com)  
**Subscription**: SkillsforJobsIndonesia (b5596ef4-4479-4819-8bc2-0197024f2051)

---

## Issue Summary

We are experiencing unusually high phone MFA (SMS/voice) charges beginning September 2025. Our charges increased from a baseline of ~77 authentications/month (July-August) to 2,596 authentications in September and 1,986 in October, resulting in unexpected costs of 6,735.54 MYR.

**Invoices**:
- September 2025 (E0200XBCN0): 2,596 phone authentications = 3,816.12 MYR
- October 2025 (E0200XKLYB): 1,986 phone authentications = 2,919.42 MYR

---

## Investigation Conducted

We have conducted a thorough investigation and found:

1. **Invoice math is correct** - Charges match calculations (units × 1.47 MYR)

2. **Two users account for 95.6% of sign-ins**:
   - `ms.aiteach.my@bijibiji.onmicrosoft.com`: 861 sign-ins (October)
   - `skillsforjobs.my.admin@bijibiji.onmicrosoft.com`: 300 sign-ins (October)

3. **Sign-in to phone authentication ratio**: 1.63 phone authentications per sign-in, suggesting:
   - Multiple MFA challenges per sign-in (retries/failures)
   - Failed sign-ins triggering phone MFA charges

4. **Automation pattern detected**: Office365 Shell WCSS-Client accounts for 64% of sign-ins, indicating automated API calls

5. **Phone MFA disabled**: We have disabled phone MFA (SMS/voice) on November 6, 2025 to prevent future charges

---

## Request for Information

We need Microsoft's assistance to:

1. **Provide detailed billing breakdown**:
   - Phone authentications by user (who triggered each charge)
   - Phone authentications by application
   - Phone authentications by date/time
   - Distinction between successful vs. failed sign-ins

2. **Clarify billing behavior**:
   - Why do failed sign-ins trigger phone MFA charges?
   - Why does the ratio exceed 1:1 (1.63 phone auths per sign-in)?
   - Is there any retry logic causing multiple charges?

3. **Historical data**:
   - Authentication method configuration history (when was phone MFA enabled?)
   - Conditional Access policy changes in September 2025
   - Any Microsoft service changes that could explain spike

---

## Request for Goodwill Credit

Given:
- ✅ Unexpected spike (59x increase from baseline)
- ✅ Charges occurred despite phone MFA being intended as fallback only
- ✅ Failed sign-ins triggering charges (may not be expected behavior)
- ✅ Proactive action taken (phone MFA disabled)

We respectfully request consideration for **goodwill credit** for the unexpected charges in September-October 2025.

---

## Evidence Attached

We have prepared a comprehensive investigation folder with:
- Complete invoice analysis
- Sign-in log analysis (1,215 October sign-ins)
- User account investigation
- Authentication method configuration
- Independent audit report

**Location**: Investigation folder contains all evidence

---

## Next Steps Requested

1. Microsoft Support to review investigation folder
2. Provide detailed billing breakdown by user
3. Clarify billing behavior for failed sign-ins
4. Consider goodwill credit for unexpected spike
5. Provide guidance on preventing future charges

---

## Contact Information

**Tenant**: Biji-biji Initiative (bijibiji.onmicrosoft.com)  
**Subscription**: SkillsforJobsIndonesia (b5596ef4-4479-4819-8bc2-0197024f2051)  
**Primary Contact**: [Your contact information]

---

**Thank you for your assistance.**


