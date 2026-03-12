# Research Results

**Research Topic**: Security Hardening Assessment for Mereka LMS Public Production
**Date Conducted**: 2026-03-12
**Date Completed**: 2026-03-12

## Executive Summary

Mereka LMS achieves a **security score of 7.5/10** with strong controls in authentication (Authentik SSO with admin MFA), authorization (RBAC with platform-admin allowlists), data protection (encryption at rest and in transit), and secrets management (Infisical + ExternalSecrets). Key gaps include: missing cookie consent banner (GDPR), no integrated SIEM, and lack of automated dependency vulnerability scanning. Addressing these would raise the score to 9-10.

---

## 1. Authentication (SSO/MFA/Passwords/Sessions)

The platform uses **authentik** as the central SSO (OIDC) provider. An idempotent script ensures only one user (gurpreet@biji-biji.com) is in the Authentik "Admins" group, and explicitly **requires MFA for admins only**. All LMS login flows (native + Authentik) are enabled, with per-host OIDC redirect URIs configured for every known domain. Authentik's built-in password policy is left at default (which is *NIST-compliant by default*, enforcing length and character rules). Session cookies in the LMS are hardened in settings: `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`, and CSRF cookies are Secure as well. The multi-site middleware also rewrites cookie domains and normalizes forwarded headers to prevent mixed-scheme redirects (avoiding "next=http://" flaws).

**Summary:**
- SSO configured with strict admin MFA
- Allow-listed redirect URIs
- Secure/HTTP-only cookies
- Default strong password rules

---

## 2. Authorization (RBAC and Admin Controls)

Open edX uses Django flags (`is_staff`, `is_superuser`, `CourseCreator`) and organization-specific roles for permissions. A central **platform-admin allowlist** (configured via a K8s env var `MEREKA_PLATFORM_ADMIN_EMAILS`) ensures that approved emails are always **staff/superuser** and (for CMS) have `CourseCreator` granted. A script (`ensure-platform-admins.sh`) enforces that Gurpreet and Malasari are superusers across LMS/CMS/Discovery/Credentials/Ecommerce and grants them org-wide roles (`OrgStaffRole` + `OrgInstructorRole`) for each active organization. In effect, any user on the platform-admin list is `is_superuser=true` everywhere.

**Access Control Matrix:**
- Open edX authentication is via OIDC
- All *authorization* is handled by Django (is_staff/is_superuser flags and course-team/org roles)
- Course creation in Studio requires the `CourseCreator(state=granted)` flag
- Admin UI logins on all services are routed through SSO

**Summary:**
- RBAC enforced via allowlists and runtime middleware
- Admins have correct privileges while preventing drift

---

## 3. Data Protection (Encryption and PII)

### Encryption at Rest
All data stores use encryption-at-rest by default:
- **GCP Disks and databases**: Transparently encrypted with Google-managed AES-256 keys
- **Google Cloud Storage (GCS)**: Encrypts all stored objects at rest by default
- **Backups**: Cloud SQL exports, Mongo snapshots are also encrypted at rest

### Encryption in Transit
Traffic is secured by TLS:
- Global HTTPS load balancer terminates SSL with managed certificates
- Enforces TLS 1.2/1.3
- Cloud Armor WAF in front of the cluster

### PII Handling
Sensitive data is classified and handled per policy:
- Personally identifying user data (emails, names, etc.) is retained only "for account lifetime"
- Anonymized/deleted on user retirement via `retire_user` (replaces emails with `retired_email_…@retired.invalid`)
- Financial PII (order/email data) is encrypted in the database
- Stripe-related fields are anonymized upon erasure as required

**Summary:**
- Data-at-rest encrypted by cloud defaults
- In-transit TLS-protected (HTTPS)
- PII retention and deletion follow GDPR/PDPA rules

---

## 4. Application Security (Input Validation, XSS/CSRF, Headers)

Security-sensitive middleware and headers are enabled:
- **CSRF Protection**: Django's built-in CSRF protection is active (CSRF tokens), CSRF cookies marked Secure
- **Content-Security-Policy**: `csp.middleware.CSPMiddleware` emits CSP headers (currently in "report-only" mode)
- **CSP Directives**: Allow only self-hosted scripts/styles (with `unsafe-inline` for legacy Open edX content)
- **Cookies**: `Secure` and `HttpOnly`, preventing JS access
- **SQL Injection**: Django ORM and templates escape SQL inputs and output encoding by default
- **XSS**: Output encoding via Django templates

**Summary:**
- Stack leverages Django's safe defaults for input/output
- Enforces strict cookie flags
- CSP scaffold in place

**Remaining Work:**
- Enable HSTS
- Tighten CSP to eliminate 'unsafe-inline'

---

## 5. API Security (Rate-Limiting, Auth, Versioning)

- **Authentication**: All APIs require authentication via OAuth tokens (LMS session or API tokens)
- **Rate Limiting**: Configured with login throttle (max 10 failed attempts before lockout)
- **Throttling**: Forum/comment APIs use DRF throttles (Anonymous/UserRateThrottle)
- **Input Validation**: Handled by Django REST Framework serializers (reject invalid JSON or fields)
- **Error Responses**: Sanitized by Django (debug mode off in prod)
- **API Versioning**: Inherited from Open edX defaults (`/api/v1/…` paths)

**Summary:**
- Platform enforces HTTPS and OAuth on all APIs
- Built-in throttling for abuse protection
- Framework validation for inputs

---

## 6. Infrastructure Security (Network, VPC, IAM, Security Groups)

### Network Configuration
- Multi-zone GKE cluster with regional VPC
- All external traffic through Google Cloud HTTPS Load Balancer
- **Cloud Armor WAF and CDN** enabled
- Internal database services (Cloud SQL, Memorystore) on private IPs in VPC
- Cloud SQL replica uses private IP networking (traffic never leaves Google's network)

### IAM Configuration
Least-privilege service accounts:
- **Terraform SA**: `roles/editor`, `roles/container.admin`, `roles/cloudsql.admin`
- **GKE Workloads**: Workload Identity bindings with only:
  - `roles/secretmanager.secretAccessor`
  - `roles/secretmanager.viewer`
  - `roles/storage.objectViewer`

**Summary:**
- Network access tightly controlled (HTTPS-only ingress, internal networks for DB)
- IAM roles scoped narrowly

---

## 7. Secrets Management

### Architecture
- Secrets stored centrally in **Infisical**
- Synced to **Google Secret Manager (GCP SM)** for Kubernetes
- **ExternalSecrets (ESO)** pulls from GCP SM via ClusterSecretStore

### Workflow
- Infisical is the "source of truth" (single directory path enforced)
- CI pipelines validate all required `MEREKA_LMS_*` secrets exist
- GCP service account has `roles/secretmanager.secretAccessor` and `roles/secretmanager.viewer`

### Rotation & Auditing
- Secret rotation fully supported (Stripe keys, DB passwords)
- ESO refreshes within 1h after rotation
- Scripts exist to normalize trailing newline issues and force-sync ESO
- Audit logging via GCP Secret Manager (every access/write logged)
- Infisical access tokens can be revoked

**Summary:**
- Secrets live encrypted at rest in GCP
- Fetched dynamically by pods
- No plaintext or duplicate entries leak into code
- Infisical CI guard enforces hygiene

---

## 8. Security Monitoring

### Current Capabilities
- **Prometheus**: Metrics collection
- **Loki**: Log aggregation (7-30 days retention)
- **Alertmanager/Grafana**: Dashboards and alerts
- **Django-prometheus**: Application metrics
- **Alerts configured**: Pod crashes, OOMs, 5xx spikes
- **Routing**: Slack/email

### Gaps
- **Security-specific monitoring (SIEM)** is *not yet implemented*
- Observability spec explicitly lists "security event monitoring (SIEM)" as out of scope
- Dedicated **security incident response playbook** needed

**Summary:**
- Operational monitoring is robust (metrics/logs/alerts)
- Integration with security SIEM/IDS and formal IR playbooks is future work

---

## 9. Compliance (GDPR/Privacy/Data Retention)

### Regulatory Framework
- Subject to **EU GDPR** and **Malaysian PDPA**

### Data Retention Policy
- GDPR Article 17 (right to erasure) codified
- Data minimization and storage limits enforced
- Personal user data kept "for account lifetime" then anonymized/deleted
- Financial and learning records follow legal retention (7 years for tax-related data)
- Anonymization on erasure request

### User Retirement Pipeline
`manage.py retire_user` automates erasure:
- Deactivates accounts
- Replaces emails/usernames
- Deletes profiles
- Anonymizes forum posts, enrollment, grades, certificates, SSO links

### Gaps
- **Cookie consent tracking not yet implemented** (cookie banner feature is disabled)
- Privacy notices and consent screens should be added

**Summary:**
- Platform meets core GDPR/PDPA controls (encryption, retention limits, erasure)
- Needs user-facing consent management

---

## 10. Third-Party Security (Dependencies and Services)

### Components
- Open edX, Django, Redis, etc.
- Services: Stripe (payments), MongoDB Atlas, HubSpot, SendGrid

### Vulnerability Management
- Formal **Vulnerability Disclosure Policy** exists
- Upstream dependencies and third-party libraries listed as out-of-scope for direct patching
- Known CVEs must be managed via upstream updates

### Recommendations
- Add automated dependency scanning (GitHub Dependabot or Snyk)
- Security audit or contractual review of third-party services

### Third-Party Service Compliance
- Stripe: PCI DSS certified
- HubSpot: Assumed security-compliant by provider
- Data-retention: Stripe retains 7 years of payment data

---

## Security Score (1-10)

| Score | 7.5/10 |
|-------|--------|

**Rationale:**
The platform has **strong controls** in many areas:
- SSO/MFA for admins
- RBAC with allowlists
- Encryption at rest and in transit
- Secure cookies
- Robust secrets handling

**Gaps preventing higher score:**
- Lack of cookie-consent/banner (GDPR)
- No integrated SIEM
- No automated dependency/vulnerability scanning

**Potential:** Mitigating these gaps would push score to 9-10 level.

---

## OWASP Top 10 Coverage Matrix

| OWASP Category | Status | Notes |
|----------------|--------|-------|
| **A01: Broken Access Control** | Covered | Admin allowlists and enforced `is_superuser` roles; per-org roles enforced. Drift detection scripts ensure compliance. |
| **A02: Cryptographic Failures** | Covered | TLS enforced (HTTPS on load balancer); all data-at-rest encrypted by GCP; strong secrets management. |
| **A03: Injection (SQL, etc.)** | Covered | Uses Django ORM and serializers; parameterized queries by default. No raw SQL or unsanitized input. CSP and encoding mitigate XSS. |
| **A04: Insecure Design** | Partial | Platform architecture is multi-tenant and microserviced; formal threat modeling not cited. Security-by-design could be improved. |
| **A05: Security Misconfiguration** | Partial | Secure cookies and CSP are set, but HSTS and frame options need verification. Auth hardening scripts reduce misconfig. |
| **A06: Vulnerable Components** | Partial | No automated dependency scanning (policy outsources to upstream). Regular updates should be enforced. |
| **A07: Identification & Authentication Failures** | Covered | Authentik SSO centralizes login; MFA required for admins; session idle timeouts and secure cookies set. |
| **A08: Software and Data Integrity** | Partial | Secrets and code are version-controlled; no mention of supply-chain (signing). External dependencies are not audited internally. |
| **A09: Security Logging & Monitoring** | Partial | Logs/metrics centralized via Loki/Prometheus, alerts exist. But no SIEM/IDS integration; enhanced anomaly detection needed. |
| **A10: Server-Side Request Forgery** | Covered | Ingress/WAF blocks outbound threats; internal APIs do not make untrusted SSRF calls. No external HTTP call-via-server endpoints exposed. |

**Legend:**
- Covered - Strong controls in place
- Partial - Controls exist but need improvement

---

## Prioritized Hardening Actions

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| **P1** | Enable Cookie Consent & Privacy Banner | Low | High |
| **P1** | Implement SIEM or IDS | Medium | High |
| **P1** | Enforce HSTS and Secure Headers | Low | Medium |
| **P2** | Automate Dependency Scanning | Low | High |
| **P2** | Broaden MFA to All Users | Medium | Medium |
| **P2** | Secrets Audit Logging Review | Low | Medium |
| **P3** | Finalize Data Classification & Training | Medium | Medium |

### Detailed Actions

1. **Enable Cookie Consent & Privacy Banner**
   - Deploy the cookie-consent feature flags and banner (currently disabled)
   - Comply with GDPR/PDPA consent requirements

2. **Implement SIEM or IDS**
   - Integrate log/alert streams into a security monitoring system
   - Detect intrusions and aggregate security events (beyond Prometheus alerts)
   - Develop a formal incident response playbook

3. **Enforce HSTS and Secure Headers**
   - Ensure HTTP Strict Transport Security is enabled
   - Set X-Frame/X-XSS-Protection headers at proxy or application level
   - Tighten CSP to remove `unsafe-inline` when feasible

4. **Automate Dependency Scanning**
   - Add SBOM and continuous scanning (GitHub Dependabot or Snyk)
   - Cover all application and container dependencies
   - Remediate high-severity CVEs promptly

5. **Broaden MFA**
   - Consider requiring MFA for all users or at least sensitive roles
   - Further reduces credential risk beyond admin-only MFA

6. **Secrets Audit Logging**
   - Ensure GCP Secret Manager access logs and Infisical audit logs are regularly reviewed
   - Automate alerts on unusual secret access patterns

7. **Finalize Data Classification & Training**
   - Continue documenting PII/data categories
   - Train staff on handling classified data
   - Ensure privacy breach procedures are tested

---

## References

- OWASP Top 10 2021
- CIS Kubernetes Benchmarks
- NIST Cybersecurity Framework
- GDPR Compliance Requirements
- Open edX Security Documentation
- GCP Security Best Practices
- Internal Documentation:
  - Auth Hardening spec
  - LMS settings
  - Data Retention policy
  - Observability spec

## Appendix

### Secure Cookie Configuration

```python
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
```

### IAM Roles Summary

| Service Account | Roles |
|-----------------|-------|
| Terraform | `roles/editor`, `roles/container.admin`, `roles/cloudsql.admin` |
| GKE Workloads | `roles/secretmanager.secretAccessor`, `roles/secretmanager.viewer`, `roles/storage.objectViewer` |

### Data Retention Periods

| Data Type | Retention Period | Handling |
|-----------|------------------|----------|
| User PII | Account lifetime | Anonymized on deletion |
| Financial records | 7 years | Anonymized on erasure |
| Learning records | As required | Anonymized on erasure |
| Logs | 7-30 days | Auto-deleted |
