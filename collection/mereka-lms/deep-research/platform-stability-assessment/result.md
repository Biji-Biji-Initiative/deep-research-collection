# Research Results

**Research Topic**: Platform Stability Assessment for Mereka LMS
**Date Conducted**: 2026-03-12
**Date Completed**: 2026-03-12

## Executive Summary

Mereka LMS achieves a **stability score of 6/10 (Moderate)**. The platform has strong foundational protections with managed databases (Cloud SQL, MongoDB Atlas) providing built-in HA and backups, and PDBs for critical workloads. However, significant gaps exist: autoscaling is manual (HPAs not enabled in production), some services lack PDBs and health probes, error handling is ad-hoc without circuit breakers or DLQs, and chaos engineering is absent. Addressing these gaps would significantly improve platform resilience.

---

## 1. Service Health Configurations (Kubernetes)

### PodDisruptionBudgets (PDBs)

PDBs exist for key components with `minAvailable: 1`:

| Service | PDB Status | Min Available |
|---------|------------|---------------|
| LMS | Configured | 1 |
| CMS | Configured | 1 |
| Caddy (ingress) | Configured | 1 |
| Redis | Configured | 1 |
| MySQL | Configured | 1 |
| Discovery | Missing | - |
| Forums | Missing | - |
| Credentials | Missing | - |

**Gap:** PDBs are missing for Discovery, Forums, and Credentials services.

### Horizontal Pod Autoscalers (HPAs)

HPAs are **documented but NOT enabled in production**:

| Service | Recommended HPA | Current Status |
|---------|-----------------|----------------|
| LMS | min 2, max 8 replicas | Manual scaling only |
| CMS | min 1, max 3 replicas | Manual scaling only |

**Current status:** "Not configured (manual scaling only)"

**Gap:** No automatic scaling under load surges makes the system vulnerable.

### Health Probes

Health probes are recommended for each service:

| Service | Probe Endpoint | Port |
|---------|---------------|------|
| LMS | `/heartbeat` | 8000 |
| CMS | `/heartbeat` | 8000 |
| Credentials | `/health/` | 8000 |

**Verification:** A script in the repo requires every non-worker container to have readiness/liveness probes.

**Gap:** Need to verify probes are actually configured in deployment YAMLs.

---

## 2. Error Handling Patterns

### Current State

| Pattern | Status | Notes |
|---------|--------|-------|
| Exception Handling | Framework defaults | Django/DRF handles exceptions |
| Retry Logic | Celery defaults | Background tasks use standard retry |
| Circuit Breakers | Not implemented | No custom circuit breaker component |
| Dead Letter Queues | Not implemented | Failed tasks purged manually |

### Celery Task Handling

- Background tasks use Celery with standard retry logic
- Runbooks refer to **manually purging** failed tasks ("Purge failed tasks (if safe to retry)")
- No automated dead-letter queue beyond Celery's own retries
- Credential issuance failures handled by manual runbook steps, not autonomous recovery

### Gaps

- No custom circuit breaker for external service calls
- No DLQ for failed tasks requiring manual intervention
- Errors mostly surfaced in logs without automated recovery

---

## 3. Data Durability (Backups/Recovery)

### MySQL (Cloud SQL)

| Feature | Status | Details |
|---------|--------|---------|
| Automated Backups | Enabled | Cloud SQL managed |
| Binary Logging | Enabled | Required for PITR |
| Point-in-Time Recovery | Supported | Restore to any point within retention |
| Restore Testing | Not documented | No explicit restore drills found |

**PITR Capability:** With binary logging and backups enabled, you can restore up to a specific point in time.

### MongoDB Atlas

| Feature | Status | Details |
|---------|--------|---------|
| Continuous Cloud Backups | Enabled | Scheduled snapshots + oplog |
| Point-in-Time Recovery | Supported | Restore to any minute within retention |
| Restore Testing | Not documented | No explicit restore drills found |

**PITR Capability:** Atlas provides continuous backups allowing restore to any minute within the retention window.

### Cluster-Level Backup (Velero)

| Component | Backup Strategy |
|-----------|-----------------|
| MySQL PVC | Hourly snapshots |
| MongoDB PVC | Hourly snapshots |

**Gap:** Regular restore tests should be part of DR planning but no explicit restore-drill documents found.

---

## 4. Database Consistency

### MySQL (Cloud SQL)

| Feature | Status | Details |
|---------|--------|---------|
| Storage Engine | InnoDB | ACID-compliant by default |
| Transaction Integrity | Preserved | Standard ACID guarantees |
| HA Mode | Available | Synchronous replication across zones |
| Automatic Failover | Yes (HA mode) | No data loss on failover |

**Failover Behavior:**
- HA mode: Automatic failover to standby without data loss
- Zonal mode: Requires manual recovery (PITR or failover)

### MongoDB Atlas

| Feature | Status | Details |
|---------|--------|---------|
| Replica Set | 3-node default | Across AZs |
| Write Concern | Majority | Durability guaranteed |
| Automatic Failover | Yes | Election promotes new primary |
| Data Loss on Failover | None | Retryable writes transparently replayed |
| Replication Lag | Minimal | Atlas provides metrics/alerts |

**Failover Behavior:** Atlas automatically holds replica set election and promotes new primary **without any data loss**.

### Summary

Both databases use standard replication and ACID protocols. Failover procedures are handled by Cloud SQL/Atlas by default.

---

## 5. Dependency Resilience

### MongoDB Atlas

| Aspect | Status | Notes |
|--------|--------|-------|
| Built-in HA | Yes | Automatic failover on node failures |
| Regional Outage | No fallback | LMS DB unreachable if Atlas region fails |
| Retry Logic | Not documented | No explicit retry patterns found |

### Redis

| Aspect | Status | Notes |
|--------|--------|-------|
| Deployment | Single-instance | Redis rules |
| Failure Impact | Performance degradation | Requests hang or slow |
| Known Issues | Redis host drift | Causes ~5% of incidents |
| Fallback | None | Requires manual fix |
| Circuit Breaker | Not implemented | No alternate caching |

**Runbook Finding:** "Redis host drift" causes requests to hang or slow, accounting for about 5% of incidents.

### Elasticsearch

| Aspect | Status | Notes |
|--------|--------|-------|
| Usage | Discovery search | Used for course search |
| Failure Impact | Search unavailable | No fallback documented |
| Retry Logic | Not documented | No search-specific retries |

### Summary

No explicit resilience patterns (retry loops, fallback caches) for dependencies. System expects these services to be highly available.

| Dependency | HA Built-in | Custom Resilience | Outage Impact |
|------------|-------------|-------------------|---------------|
| MongoDB Atlas | Yes | No | Full DB unavailable |
| Redis | No | No | Performance degradation |
| Elasticsearch | Unknown | No | Search unavailable |

---

## 6. Incident History

### Incident Frequency Table

| Cause | Frequency | Notes |
|-------|-----------|-------|
| Kubernetes service selector mismatches | 70% | Pods had no endpoints |
| Missing HTTPS port on ingress | 10% | Configuration error |
| Database connection failures | 10% | Connectivity issues |
| Redis issues | 5% | Host drift, performance |
| Other | 5% | Various causes |

### Common Incident Types

1. **Infrastructure/Configuration Issues (70%)**
   - Service selector mismatches
   - Missing ports
   - Label drift

2. **Database Connectivity (10%)**
   - Connection failures
   - Timeout issues

3. **Cache Issues (5%)**
   - Redis host drift
   - Performance degradation

### Remediation Status

- Runbooks document remediation steps
- Scripts exist to fix common issues (e.g., service selector fixes)
- No evidence of widespread application logic bugs
- No data corruption incidents recorded

---

## 7. Chaos Engineering Readiness

### Current State

| Aspect | Status |
|--------|--------|
| Formal Chaos Testing | Not implemented |
| Failure Injection | Not practiced |
| Chaos Tools | None found |
| Resilience Validation | Manual drills only |

### Assessment

**No evidence** of formal chaos testing or failure-injection in the repo or docs:
- No mentions of chaos tools
- No deliberately killing services
- Platform relies on traditional monitoring and manual drills via runbooks
- No automated chaos experiments

---

## Stability Score (1-10)

| Score | 6/10 (Moderate) |
|-------|-----------------|

### Strengths

- **PDBs for critical workloads** - At least one pod remains during maintenance
- **Managed databases with HA** - Cloud SQL and Atlas provide built-in replication and failover
- **Detailed runbooks** - Diagnosis and recovery procedures documented
- **Backup schedules** - Velero backups for cluster data including DB volumes
- **Strong SLAs** - 99.99% (Cloud SQL) and Atlas HA provide solid foundation

### Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| Manual scaling only (no HPAs) | High | Vulnerable to load surges |
| Missing PDBs for some services | Medium | Risk of service disruption |
| No circuit breakers/DLQs | Medium | Failures bubble up |
| No dependency fallbacks | Medium | Single points of failure |
| No restore drills documented | Medium | DR readiness uncertain |
| No chaos engineering | Low | Resilience unproven |

---

## Remediation Recommendations

### Priority 1: Critical

| Action | Details | Effort |
|--------|---------|--------|
| Enable Autoscaling | Apply recommended HPA configs (LMS: 2-8, CMS: 1-3) | Medium |
| Add Missing PDBs | Create PDBs for Discovery, Forums, MFE, Credentials | Low |
| Enforce Health Probes | Ensure every deployment has readiness/liveness probes | Medium |

### Priority 2: High

| Action | Details | Effort |
|--------|---------|--------|
| Improve Error Resilience | Add retry/backoff logic and circuit breakers for external calls | Medium |
| Configure Celery DLQ | Set up dead-letter queue for failed tasks | Medium |
| Set Up Alerts | Replication lag, Redis latency, probe failures | Low |

### Priority 3: Medium

| Action | Details | Effort |
|--------|---------|--------|
| Disaster Drills | Test PITR restores for Cloud SQL and Atlas | Medium |
| Velero Restore Tests | Practice cluster recovery in staging namespace | Medium |
| Tune Probe Timeouts | Ensure ≥5s timeouts to avoid false failures | Low |

### Priority 4: Enhancement

| Action | Details | Effort |
|--------|---------|--------|
| Chaos Testing | Begin small-scale failure injection in staging | High |
| Redis HA | Consider Redis Cluster or Sentinel for HA | High |

---

## Implementation Roadmap

### Phase 1: Immediate (Week 1-2)
1. Apply HPA configurations for LMS and CMS
2. Create PDBs for missing services
3. Verify health probes on all deployments

### Phase 2: Short-term (Week 3-4)
1. Implement circuit breakers for external calls
2. Configure Celery DLQ
3. Set up critical alerts

### Phase 3: Medium-term (Month 2)
1. Conduct disaster recovery drills
2. Document restore procedures
3. Validate PITR capabilities

### Phase 4: Long-term (Month 3+)
1. Introduce chaos engineering practices
2. Evaluate Redis HA options
3. Continuous resilience improvement

---

## References

- Kubernetes configs and runbooks in Mereka repo
- GCP Cloud SQL Documentation
- MongoDB Atlas High Availability Documentation
- Open edX Deployment Guide
- Google SRE Principles

## Appendix

### HPA Configuration Recommendations

```yaml
# LMS HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lms-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lms
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### PDB Configuration Template

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: discovery-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: discovery
```

### Health Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /heartbeat
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
readinessProbe:
  httpGet:
    path: /heartbeat
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 5
```

### Incident Cause Distribution

```
Service selector mismatches    ████████████████████████████████████████ 70%
Missing HTTPS port             █████ 10%
DB connection failures         █████ 10%
Redis issues                   ██ 5%
Other                          ██ 5%
```
