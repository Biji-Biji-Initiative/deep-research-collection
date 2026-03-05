# Finance Team - Strategic Billing Adjustment Request (Phone MFA)

**Purpose**: Negotiation-focused email template to secure a goodwill credit/adjustment for September–October phone authentication charges, framed around fairness, partnership, and remediation.

---

## 📧 READY-TO-SEND EMAIL (Copy/Paste This Section)

---

**To**: Microsoft Billing Support / Azure Support  
**CC**: Microsoft Account Team (if applicable)  
**Subject**: Request for Billing Adjustment and Goodwill Credit – September–October Phone MFA Charges  
**Priority**: High  
**Category**: Billing Dispute / Billing Adjustment

---

Dear Microsoft Billing Support,

We’re seeking your help to resolve an outlier billing event related to phone authentication (SMS/voice MFA) on our Azure subscription. This is not a typical usage pattern for us, we have already remediated the underlying cause, and we’re asking for a fair, partnership‑oriented adjustment.

### Who we are
• Tenant: Biji-biji Initiative (bijibiji.onmicrosoft.com)  
• Subscription: SkillsforJobsIndonesia (b5596ef4-4479-4819-8bc2-0197024f2051)

### What happened (objective facts)
• Baseline usage (Jul–Aug 2025): ~77 phone authentications/month (~98–115 MYR)  
• September 2025: 2,596 phone authentications = 3,816.12 MYR (Invoice E0200XBCN0)  
• October 2025: 1,986 phone authentications = 2,919.42 MYR (Invoice E0200XKLYB)  
• Total impact (Sep–Oct): 6,735.54 MYR; ~59× deviation from baseline

### Why it happened (root cause we verified)
Our independent investigation shows the spike was driven by automation, not normal user activity:
• Two users accounted for 95.6% of sign‑ins (primarily `ms.aiteach.my@…`)  
• Dominant application: Office365 Shell WCSS‑Client (automated API calls)  
• 1.63 phone authentications per sign‑in suggests retries/failures triggered billable events  
• A third‑party Teams app assignment on Sep 17 aligned with the spike

### What we did (remediation already complete)
• Disabled phone MFA (SMS + Voice) on Nov 6, 2025 in favor of Microsoft Authenticator  
• **Verified zero phone MFA charges**: Direct Microsoft Graph API query confirms **0 phone MFA events** out of 100 MFA sign-ins since Nov 6  
• Sign‑ins reduced 22.8% (149 → 115), with automation (Office365 Shell WCSS‑Client) dropping 41.2% (119 → 70)  
• **Critical**: Phone MFA policy disabled at tenant level—system cannot send phone MFA challenges, ensuring zero billable events going forward

### Why an adjustment is fair
• This was an aberration, not our intended or ongoing usage pattern  
• Charges were caused by automated flows and retries, not human authentication value  
• We took rapid corrective action to prevent recurrence  
• We value Microsoft and want to close our books accurately and fairly

### Our requests
1) Billing adjustment (goodwill credit): Please apply a one‑time credit of 6,735.54 MYR for September–October 2025.  
   • If a full credit is not possible, what would a fair partial credit look like from Microsoft’s perspective (e.g., 50–75%) so we can close our month‑end?  
2) Billing breakdown (for our auditors):  
   • Phone authentications by user, by application, by date/time, and success vs. failure  
3) Clarification:  
   • Should failed sign‑ins and retry prompts generate billable phone auth events?  
   • Is there recommended configuration to ensure automated flows do not trigger chargeable MFA?
4) Prevention guidance:  
   • Any Microsoft best practices we should adopt beyond moving to Microsoft Authenticator only

### Calibrated questions (to align on next steps)
• How would Microsoft define a fair outcome, given a 59× deviation that is now remediated and verified eliminated?  
• What would it take to apply a one‑time credit this billing cycle so Finance can close by [DATE]?  
• We've verified zero phone MFA charges post‑Nov 6 via direct API queries—can you confirm this aligns with Microsoft's billing records?

### Evidence package (attached on request)
• Invoice analysis with month‑by‑month units and MYR totals  
• Sign‑in log analysis (1,215 Oct sign‑ins): users, apps, failure patterns, ratio math  
• **Post‑remediation verification**: Direct Microsoft Graph API query shows **0 phone MFA events** out of 100 MFA sign-ins since Nov 6 (100% verified)  
• November 5–6 sign‑in logs showing immediate impact (149 → 115 sign‑ins, 41.2% automation reduction)  
• Authentication method config history and third‑party app assignments  
• Independent audit report and executive summary

We appreciate your partnership and prompt support. We have verified that phone MFA charges are eliminated going forward (0 phone MFA events confirmed via Microsoft Graph API since Nov 6), and we're seeking your assistance to resolve the September–October outlier charges. Please let us know what additional detail would help you process the credit. If easier, we're available for a brief call to finalize the resolution.

Sincerely,  
[Finance Contact Name]  
[Title], Biji-biji Initiative  
[Email] | [Phone]  
Invoices: E0200XBCN0 (Sep), E0200XKLYB (Oct)

---

## Send‑Ready Short Version (Optional)

Subject: Billing Adjustment Request – Phone MFA (Sep–Oct) – 6,735.54 MYR  
Dear Microsoft Billing,  
We experienced a one‑time spike in phone MFA charges (Sep–Oct total 6,735.54 MYR; ~59× baseline) driven by automated API activity and retries, not human authentications. We disabled phone MFA on Nov 6 and moved to Microsoft Authenticator; **verified zero phone MFA charges** via direct API queries (0 phone MFA events out of 100 MFA sign-ins since Nov 6).  
Request: One‑time goodwill credit of 6,735.54 MYR (or fair partial credit) and a billing breakdown by user/app/date with success vs. failure. Evidence package is available on request. Thank you for helping us close month‑end fairly.  
– [Name], Biji‑biji Initiative, Subscription b5596ef4‑4479‑4819‑8bc2‑0197024f2051

---

## How Finance Should Use This
1. Fill in bracketed fields (names, date, contacts).  
2. Attach the evidence pack from the investigation folder (zip).  
3. Submit via Azure Portal (Cost Management → Invoices → Help + Support) or your account team.  
4. If no response within 3 business days, reply‑all with the short version and ask for status/ETA.

## Key Anchors and Framing
- Fairness and partnership, not blame.  
- Full‑credit anchor with acceptable partial‑credit fallback.  
- Clear remediation and prevention already in place.  
- Specific questions that make “credit + clarification” the easiest path to resolution.

