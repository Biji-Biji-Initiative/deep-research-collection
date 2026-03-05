# DR-3: Climate Exchange Technical Audit and Roadmap

## Audience

Engineering maintainers and operators evaluating production readiness, governance posture, and an execution roadmap for CIE.

## Prerequisites

- Familiarity with the repo layout (apps/api, apps/web, services/worker, packages/*)
- Ability to run local gates: `make check-fast`, `make verify-ci`, `make verify-runtime-required`

## How to Use

1. Use the **Executive Summary** to identify the biggest leverage points (trust spine vs ops posture).
2. Convert “liabilities” into beads with explicit ACs and release gates.
3. Re-run the local gates and validate on the live site after each major change.

## Troubleshooting

- If conclusions here conflict with current code/specs, update the report with a dated note and links to evidence.
- If a recommendation increases CI runtime unacceptably, split it into PR-fast vs nightly-deep lanes.

## Change Log

| Date | Change |
|------|--------|
| 2026-02-15 | Imported DR-3 from prior audit notes (was `DRNEW`) and standardized doc sections |


## Executive Summary
The climate-exchange repository already contains the nucleus of a high-integrity, government-ready climate intelligence platform: a tool-contract-driven backend, signed evidence receipts, durable run/event logs, and a front-end that can render auditable artifacts (CSV + Vega-Lite) with accessibility checks baked into CI. The architectural pattern—“every computed claim must be backed by a tool receipt + provenance, and every run can be replayed and packaged as evidence”—is unusually strong for an early-stage product and is directly aligned with what Pacific governments and international development agencies need: traceability, reproducibility, and defensible reporting.

The repo’s biggest weaknesses are not “missing features”; they’re operational hardening and productization gaps:

Deployment posture is inconsistent (Vercel + Cloud Run + PM2/VPS configs coexist), creating drift and unclear “source of truth” for production.
Security is demo-grade (unauthenticated API endpoints, bearer-token-only admin controls); it needs SSO/RBAC, tenant isolation, audit trails, and key management appropriate for state actors and donors.
Ingestion/harvesting is duplicated (API-side scheduler + worker-side harvest loop), risking concurrency issues and data inconsistency as you scale.
CI gates are present but not enforced (e.g., eval workflow effectively doesn’t fail builds), which will become a quality cliff as scope expands.
Data governance is directionally correct (explicit CARE + FAIR posture) but needs concrete, enforceable controls and compliance artifacts. The CARE principles are particularly relevant in the Pacific context because they emphasize authority, ethics, and collective benefit where indigenous/community data is involved.  The FAIR guiding principles provide the complementary “machine + metadata” discipline donors increasingly expect. 
A world-class v1 for Pacific governments and development agencies should double down on your differentiator—verified evidence packs—and then add: (a) multi-tenant governance, (b) datasets/provenance registry beyond “tools,” (c) robust ingestion for slow/free APIs, and (d) procurement-ready packaging (hosting options, security posture, and measurable service levels).

Branch selection and current state of the codebase
Branch posture and what was audited
You requested that the audit start by reviewing branches and prioritizing the most recently updated branch (not main). Within climate-exchange, the most recent tip commit (by commit timestamp) is on fix/json-persist-and-taxonomy at commit 92486eb (created 2026‑02‑15). I used that commit SHA as the primary “snapshot” for inspecting the platform surface (API contracts, tool registry, connectors, migrations, workflows, and UI rendering). I also referenced files on main when needed to access content that was not fetchable from the branch snapshot due to tool restrictions (notably some specs and migrations).

High-level architecture as implemented
At a high level, the system is a monorepo with three runtime planes:

Web app: Next.js UI rendering artifacts (Vega-Lite), briefing packs, catalog views.
API: Fastify server exposing /chat, /chat/stream (SSE), /tools, /runs, /manifest, /briefing-pack, receipts/blobs/artifacts proxy endpoints, and admin endpoints.
Worker: scheduled ingestion, catalog harvesting, optional IBTrACS ingest, and cache prewarming.
State and storage:

PostgreSQL (+ PostGIS): run/event tables, catalog tables, cache tables (tool cache + epoch), harvest run audit.
Redis (optional): hot cache + idempotency locks; Postgres advisory locks used when Redis absent.
S3/MinIO: receipt objects, tool blobs (inputs/results), and artifact payloads (csv/specs).
Key differentiator:

Receipts: tool outputs are wrapped in a strict schema envelope and then signed; verification is “fail-closed” in verified mode; run evidence can be packaged into a canonical bundle / briefing pack.
System and data flow diagram
mermaid
Copy
flowchart LR
  U[User in browser] --> W[Web UI\napps/web (Next.js)]
  W -->|REST| A[API\napps/api (Fastify)]
  W -->|SSE| A

  subgraph Core State
    PG[(PostgreSQL + PostGIS)]
    R[(Redis\noptional)]
    S3[(S3/MinIO\nreceipts, blobs, artifacts)]
  end

  A --> PG
  A --> R
  A --> S3

  A -->|runTool()| C[Connectors + tools\npackages/connectors + apps/api/tools]
  C -->|external calls| X1[DKAN/CKAN portals]
  C -->|external calls| X2[ClimateSERV\nCHIRPS/NMME]
  C -->|external calls| X3[PSMSL tide gauges]
  C -->|external calls| X4[IBTrACS cyclone data]
  C -->|cache + locks| R
  C -->|persisted cache| PG

  C -->|artifact payloads| S3
  C -->|signed receipts| S3

  A -->|verifyRunEvidence()| V[Evidence gate\n(receipt + ledger checks)]
  V -->|manifest/bundle| S3

  subgraph Background
    WK[Worker\nservices/worker]
  end

  WK --> PG
  WK --> R
  WK --> S3
  WK -->|harvest/ingest| X1
  WK -->|bulk ingest| X4
Code health: strengths and liabilities
Strengths observed

Fail-closed verification discipline: runTool() enforces a strict envelope schema and refuses to “patch” invalid tool outputs. This is the right posture for government-grade evidence.
Explicit provenance coupling: tool inputs/results are persisted to blob storage and linked into run events; SSE has truncation logic that preserves dereferenceable pointers (blob_ref/tool_result_blob_ref) for large payloads.
Operational realism for slow APIs: the ClimateSERV connector includes idempotent job submission reuse, progress polling, early fetch probes, request segmentation across long time ranges, and concurrency limits—exactly what you need when free services are slow and flaky.
Accessibility is not an afterthought: the repo includes Playwright + axe-core checks for WCAG 2.1 AA-level tags across core routes, with artifact output saved for inspection. This aligns with public-sector digital service expectations. 
Liabilities observed

Single-file API “god object”: apps/api/src/index.ts mixes health checks, core domain routing, chat orchestration, SSE protocol implementation, receipt layering, run storage, artifact proxying, and admin endpoints. Refactoring into internal modules (or service boundaries) will reduce defect risk and make security reviews tractable.
Deployment drift: docs and config indicate multiple production strategies (Vercel + Cloud Run, plus PM2/VPS config). This invites “it works in prod but not in CI” failures and complicates audits.
CI gate softness: workflows exist for runtime verification and evals, but key steps are marked continue-on-error or effectively forced to pass. This is fine temporarily, but it will collapse confidence once external stakeholders rely on the platform.
Auth posture is demo-only: most API endpoints are unauthenticated; admin endpoints are protected only via a bearer token. Government buyers will require SSO, RBAC, and auditable access controls.
Duplicate harvesting logic: there is both an API-side daily UTC scheduler and a worker-side periodic harvest loop. In a scaled environment (multiple instances), you need a single source of scheduling truth with distributed locks.
Data model, ingestion pipelines, and verification mechanics
What the database currently represents
From the SQL migrations and API queries visible in the repo, the system stores:

Run/event ledger: chat_run and chat_run_event store a replayable timeline suitable for reconstructing sessions and generating evidence packs.
Catalog harvesting + materialized dataset metadata: catalog_source, catalog_harvest_run, catalog_dataset, and catalog_resource store harvested DKAN/CKAN metadata with a full-text search vector for local search.
Ingestion skeleton: dataset_registry and ingestion_run exist as a scaffold for idempotent ingest cycles.
Tool cache + epoch: tool_cache plus cache_epoch support persisted caching and cross-process invalidation (epoch bump). This is a sophisticated choice for low-bandwidth contexts where recomputation is expensive.
Ingestion and harvesting as implemented
There are two overlapping patterns:

Catalog harvesting: DKAN + CKAN harvesters populate catalog tables and log catalog_harvest_run.
Connector-level caching: for slow tools (ClimateSERV/IBTrACS/PSMSL), results are cached with long TTLs, with idempotency locks to prevent stampedes.
A key design point here is that external services change. Your own spec already flags NOAA access method deprecations (OpenDAP retirement, FTP terminations). Official NOAA service change notices confirm these cutovers and recommend migrating to HTTPS/grib filter approaches. 
This means the ingestion layer must:

treat source availability as a first-class health signal,
maintain a “dependency calendar,” and
keep adapters swappable.
Receipts and evidence packs
Receipts today are signed using HMAC-SHA256 over RFC8785 canonical JSON (via a JSON canonicalization step) and verified server-side when retrieved. The code explicitly notes that this is a demo posture and should later migrate to asymmetric signing via KMS/HSM. This is a correct trajectory for government procurement because asymmetric verification enables third-party validation without sharing secrets.

The platform also generates:

Answer receipts (binding the final markdown answer to tool receipt IDs),
Run receipts (binding the run to an event-log hash),
Briefing packs / canonical bundles (downloadable evidence containers).
This is the strongest part of the system: it’s not “an AI chatbot,” it’s an evidence-producing climate workflow engine.

Technical roadmap to a world-class platform for Pacific governments and development agencies
Architecture changes to prioritize
The roadmap below is sequenced to maximize procurement readiness while preserving your core differentiator (verified evidence).

Consolidate scheduling and ingestion orchestration

Move all scheduled harvesting/ingestion into a single control plane:

Use the worker as the only scheduler for:
DKAN/CKAN catalog harvest,
periodic pre-warms,
bulk dataset sync (e.g., IBTrACS subsets),
cache cleanup / epoch bumps.
Keep the API purely request/response + on-demand jobs + admin triggers.
Enforce distributed single-flight via Redis locks (or Postgres advisory locks), not in-process flags.
Formalize a provenance-first “dataset registry”

Evolve dataset_registry into the canonical table for all datasets (not just harvested catalog entries):

dataset_id (internal stable ID)
source_system / source_key
access_url and retrieval methods
license classification (public/shared/restricted)
update cadence + last refresh
schema metadata: expected columns/units, spatial/temporal coverage
“verification posture”: what constitutes trustworthy output for this dataset?
This aligns with FAIR expectations: richly described data objects with clear access conditions and reuse constraints. 

Upgrade receipt signing to asymmetric verification

For governments and donors:

Use a managed key system (cloud KMS or HSM-backed signing) so that:
signing keys never leave the boundary,
verification can be performed publicly using published public keys,
key rotation and audit logs are standard.
Introduce multi-tenant isolation

A “Pacific governments + donors” platform needs clean separation:

Tenant = country, ministry, or program.
Data partitioning:
logical (tenant_id column + RLS policies), and/or
physical (separate schemas / separate DBs for high-sensitivity tenants).
Artifact storage partitioning:
bucket prefix by tenant + environment,
deny cross-tenant reads at the proxy layer.
Adopt an internal event backbone for long-running jobs

You already have SSE for client streaming. Pair it with a durable internal job model:

job table with state machine: queued/running/succeeded/failed
job_event table for progress (mirrors SSE)
support resuming, retries, and operator intervention
This makes the system resilient when ClimateSERV jobs take minutes and when free services spike latency.

Data ingestion and verification strategies for slow free APIs
Your ClimateSERV connector already implements several best-practice patterns:

idempotent submit for async jobs,
progress polling with time budgets,
segmentation for long date windows,
bounded concurrency and cache TTLs.
To make this production-grade across all sources, standardize five controls across every connector:

Idempotency keys
Every remote request should be keyed by normalized params + versioned connector code + source dataset version.

Content addressing and immutable snapshots
Store raw upstream payloads (or derived canonical subsets) in object storage with hashes. Tie:

retrieved_at
hash_sha256
source_url
parser_version into provenance.
Health-aware backoff and circuit breakers
When a source fails consecutively, degrade gracefully to cached results or return “source unavailable” while surfacing a clear operational health state.

Verification gates for derived metrics
For each tool output, enforce:

expected date coverage,
unit checks,
missingness thresholds,
bounding-box sanity checks,
schema validation.
Dependency calendar + adapter abstraction
NOAA’s OpenDAP termination and FTP service retirement are explicit examples of why connectors must be swappable and versioned, with migration playbooks. 

Storage, indexing, caching: recommended end-state
A pragmatic “world-class but not overbuilt” target:

PostgreSQL + PostGIS: metadata registry, RBAC, audit log, catalog search, run ledger.
Object storage: receipts, raw source snapshots, artifact payloads, evidence bundles.
Redis: hot cache, idempotency locks, SSE coordination, rate limit state.
Analytical engine:
keep DuckDB-in-process for moderate workloads (cyclone stats), or
transition heavy aggregations to a managed warehouse if requirements expand.
Search:
Postgres FTS for catalog (already),
add trigram index for fuzzy matching and multilingual search expansions later.
Real-time vs batch:

Most climate datasets are batch (daily/monthly updates); treat “real-time” as eventing about changes and alerts, not necessarily sub-second recalculation.
Use “near-real-time” where it matters (cyclone advisories, forecast products), and batch for analytics/historical.
Product features prioritized for government and donor stakeholders
Stakeholder-driven feature map
Below is a prioritized feature set that aligns with the way governments and development agencies actually consume climate intelligence: dashboards for executives, defensible reporting for donors, and GIS-grade exports for technical teams.

Feature	Primary stakeholder value	Why it matters for procurement	Implementation complexity
Evidence-grade “Briefing Pack” exports (PDF/Doc + machine bundle)	Ministers, donors, auditors	Turns insights into defensible deliverables; reduces political risk	Medium
Role-based access control (RBAC) + SSO	Government IT, program leads	Mandatory for most government deployments	High
Dataset catalog with license class + provenance	Analysts, data stewards	Builds trust; reduces misuse; supports FAIR/CARE narratives 	Medium
Audit trails (who accessed what, when)	Donors, auditors	Needed for compliance reviews and dispute resolution	High
Interactive dashboards (hazards, exposure, projects)	Program managers	Converts data into prioritization decisions	Medium
Scenario modeling (what-if for adaptation investments)	Planners, donors	Enables transparent trade-offs and ROI narratives	High
Alerts & threshold monitoring (flood/drought/cyclones)	Disaster agencies	Operational relevance; drives stickiness	Medium–High
Data export (CSV/GeoJSON + API)	GIS teams, analysts	Makes platform useful inside existing workflows	Medium
Multilingual UI + localized reporting templates	Cross-ministry adoption	Critical for broad uptake; reduces training burden	Medium
Offline/low-bandwidth mode (cached dashboards)	Outer-island users	Pacific reality: connectivity constraints	High

UX direction: what’s already good and what to strengthen
Your current UI rendering approach—Vega-Lite specs + optional underlying data table—maps nicely to accessibility expectations and transparency. The W3C WCAG 2.1 recommendation provides the normative baseline many governments reference for digital accessibility. 

To level up:

Make every visualization reportable: “Download chart spec,” “Download data,” “Download citation list,” and “Download evidence receipts.”
Add an “Explain this chart” panel that is deterministic (no LLM required) and derived from metadata + computed values.
Treat maps as first-class accessible components:
keyboard navigation alternatives,
tabular summaries for choropleths,
configurable contrast and label sizes.
Implementation plan with milestones, effort, and risks
Milestone plan
Milestone	Scope	Effort	Key risks	Risk controls
Security foundation	Tenant model, RBAC scaffolding, SSO integration, API auth middleware	High	Scope creep; integration delays with gov IdPs	Start with OIDC-compatible providers; ship “least privilege” defaults
Ingestion unification	Single scheduler (worker), distributed locks, remove duplicate harvesting logic	Medium	Data drift during migration	Dual-run with reconciliation; promote worker as source of truth
Provenance registry v1	Normalize dataset_registry + source snapshot hashing + provenance APIs	Medium	Schema churn	Versioned schemas; strict backward compatibility
Evidence pack hardening	Deterministic bundle generation, signed bundle manifests, re-verification tool	Medium	Bundle size + storage costs	Size budgets; tiered artifact retention policies
CI/CD enforcement	Remove “soft pass” gates, add coverage + contract tests, quality budgets	Medium	Initial build failures create friction	Phase in: warn → fail for new code only → full enforcement
Observability + SLOs	Metrics, tracing, alerting; define SLOs for key endpoints	Medium	Signal overload	Start with a small SLO set and expand quarterly
“Government pilot” UX	Dashboards + reporting templates + training flows	Medium	Stakeholder misalignment	Pilot-driven iteration; instrument usage analytics

Mermaid roadmap timeline
Feb 22
Mar 01
Mar 08
Mar 15
Mar 22
Mar 29
Apr 05
Apr 12
Apr 19
Apr 26
May 03
May 10
May 17
May 24
Security foundation (RBAC/SSO)
CI/CD enforcement
Observability + initial SLOs
Ingestion unification
Provenance registry v1
Evidence pack hardening
Government pilot UX + templates
Foundations
Data and provenance
Productization
Climate Exchange roadmap


Show code
Governance, privacy, and compliance practices for Pacific nations and donors
Governance posture to adopt
Your repo’s governance posture already states a public-only demo approach and explicitly references both CARE and FAIR. The CARE principles emphasize collective benefit, authority to control, responsibility, and ethics—high relevance in Pacific contexts where indigenous/community governance is central. 
FAIR provides the complementary discipline for metadata, access conditions, and reuse. 

To make this operationally real (not just narrative), implement:

Data classification: public / shared / restricted / sensitive-within-government. Enforce export policies by class.
Provenance-by-default: every dataset shown in the UI must expose:
provenance source,
retrieval date/time,
license,
processing steps,
evidence receipts when computations occur.
PII and sensitive data controls:
“No PII in receipts” is a good rule; enforce via schema redaction and automated checks.
Data minimization and purpose limitation: only ingest what’s needed to answer policy questions.
Security baseline:
encryption at rest (DB + object storage),
TLS everywhere,
secret management (you already use Infisical—good),
key rotation, and separation of duties.
Compliance artefacts governments and donors expect
Even when not legally mandated, donors typically expect:

security policy and access control model,
audit logging and retention policy,
vulnerability management and patch cadence,
incident response plan,
data sharing and licensing posture.
For accessibility, many public-sector environments align to WCAG 2.1 requirements. 

Go-to-market and procurement strategy for governments and development agencies
Positioning: what you should sell
Don’t sell “AI.”

Sell: Verified climate intelligence with defensible evidence packs:

“Every chart can be exported with its raw data, license, and receipts.”
“Every briefing can be replayed, re-generated, and independently verified.”
This is procurement-friendly because it converts AI risk into auditability.

Pilot designs that convert to procurement
A strong pilot is small, measurable, and politically safe:

Pilot duration: 6–10 weeks
Scope:
one country,
2–3 ministries/agencies,
3–5 priority questions (e.g., coastal inundation exposure, cyclone track density, rainfall anomaly trends, facilities coverage)
Deliverables:
dashboard + briefing pack templates,
evidence pack export used in at least one real meeting,
documented data governance posture.
Success metrics:
time-to-answer (from question → defensible brief),
adoption (weekly active users across agencies),
evidence usage (downloads of briefing packs / receipts),
trust indicators (percentage of outputs accepted without rework).
Pricing models that match government procurement realities
Country license + support (annual): simplest for ministries and donor-funded programs.
Program-based pricing: aligned to donor projects; includes a capped number of stakeholders and training.
Hybrid hosting:
managed SaaS for speed,
“country-hosted” option for data residency / sovereignty.
Partnerships to pursue:

national meteorological services and disaster agencies (credibility),
regional bodies (distribution),
donor implementers (integration into existing M&E workflows).
Appendix with data sources, API contracts, schemas, tests, SLOs, and UX guidance
Recommended data sources and APIs
Free/primary sources that are already aligned with the repo’s connector map:

ClimateSERV CHIRPS/NMME: async job model with submitDataRequest + progress polling + result fetch. 
PSMSL tide gauge station data and files. 
IBTrACS tropical cyclone best-track archive (NOAA NCEI), including basin subsets and versioned releases. 
CKAN Action API for discovery/search of datasets (package_search/package_show). 
NOAA NOMADS access method changes: plan for HTTPS + supported subsetting methods (avoid retired OpenDAP and FTP paths per the service notices). 
Premium sources to consider later (when you need higher-resolution or nationally-authorized datasets):

national datasets via MoUs (e.g., higher-resolution lidar, cadastral layers),
commercial hazard models (cyclone surge, infrastructure fragility),
satellite analytics products with SLAs.
Sample API contracts
Below is an illustrative OpenAPI-style sketch. It is not a full spec, but it shows the “shape” that procurement teams and integrators expect. (Align to OpenAPI 3.1.x for modern tooling. )

yaml
Copy
openapi: 3.1.1
info:
  title: Climate Exchange API
  version: 1.0.0
servers:
  - url: https://api.example.gov.cx
security:
  - bearerAuth: []
paths:
  /v1/health:
    get:
      summary: Readiness probe
      security: []
      responses:
        "200": { description: Ready }
        "503": { description: Unavailable }

  /v1/catalog/datasets:
    get:
      summary: Search datasets
      parameters:
        - in: query
          name: q
          schema: { type: string }
        - in: query
          name: source_key
          schema: { type: string }
        - in: query
          name: license_class
          schema: { type: string, enum: [public, shared, restricted] }
        - in: query
          name: page
          schema: { type: integer, minimum: 1, default: 1 }
        - in: query
          name: page_size
          schema: { type: integer, minimum: 1, maximum: 200, default: 50 }
      responses:
        "200":
          description: Dataset results
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/DatasetSearchResponse"

  /v1/runs:
    post:
      summary: Create a run (deterministic or agentic)
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/RunCreateRequest" }
      responses:
        "200": { description: Run created }

  /v1/runs/{run_id}:
    get:
      summary: Fetch run + event ledger
      parameters:
        - in: path
          name: run_id
          required: true
          schema: { type: string, format: uuid }
      responses:
        "200": { description: Run ledger }

  /v1/runs/{run_id}/evidence-bundle:
    get:
      summary: Download canonical evidence bundle
      responses:
        "200": { description: Evidence bundle JSON/ZIP }

  /v1/receipts/{receipt_id}:
    get:
      summary: Fetch receipt + verification result
      responses:
        "200": { description: Receipt }

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
  schemas:
    RunCreateRequest:
      type: object
      required: [message, verification_mode]
      properties:
        message: { type: string, maxLength: 4096 }
        verification_mode: { type: string, enum: [verified, assistive, offline_replay] }
        tenant_id: { type: string }
        session_id: { type: string }
    DatasetSearchResponse:
      type: object
      required: [ok, results]
      properties:
        ok: { type: boolean }
        results:
          type: array
          items: { $ref: "#/components/schemas/DatasetSummary" }
    DatasetSummary:
      type: object
      required: [dataset_id, title, source_key]
      properties:
        dataset_id: { type: string }
        source_key: { type: string }
        title: { type: string }
        description: { type: string }
        license: { type: string }
        license_class: { type: string }
        provenance:
          type: object
          properties:
            retrieved_at: { type: string, format: date-time }
            source_url: { type: string }
            hash_sha256: { type: string }
Example data schemas
A minimal provenance object that scales:

json
Copy
{
  "source_id": "climateserv:chirps",
  "publisher": "SERVIR / NASA partners",
  "access_url": "https://…",
  "retrieved_at": "2026-02-15T08:00:00Z",
  "license": "Public Domain",
  "snapshot": {
    "hash_sha256": "…",
    "stored_uri": "s3://…/snapshots/…"
  },
  "processing": [
    {
      "step_id": "op_1234abcd",
      "tool_name": "climate.rainfall.chirps_timeseries",
      "code_version": "git:92486eb",
      "params_hash": "…",
      "started_at": "…",
      "ended_at": "…"
    }
  ],
  "receipts": ["rcpt_…"]
}
Suggested tests, monitoring, and SLOs
Tests to add / strengthen

Contract tests for every tool envelope: schema, provenance presence, artifact hashing, and receipt signing.
Replay determinism tests: given the same run ledger + tool blobs, regenerate the same briefing pack byte-for-byte (or with strictly defined allowed diffs).
Ingestion correctness tests:
DKAN: enforce payload size guardrails and public-only filtering.
CKAN: assert stable parsing under missing fields.
Source adapter tests for service changes (e.g., NOAA access method changes). 
Accessibility gates as hard requirements, aligned to WCAG 2.1 AA. 
Monitoring and SLOs

Start with a small, procurement-friendly set:

API availability SLO (monthly): 99.5% for /v1/health and /v1/catalog/*
Latency SLO:
p95 < 500ms for catalog search (cached)
p95 < 2s for receipts/blob retrieval (artifact proxy may be higher)
Freshness SLO:
catalog harvest completes at least every 24h (or per configured cadence)
Integrity SLO:
100% of verified-mode runs must have valid evidence verification (otherwise fail closed)
UX/UI guidance for interactive visualizations and accessibility
Use Vega-Lite outputs as the canonical visualization format because they are:
declarative,
reproducible,
exportable,
linkable to raw data and receipts.
Always ship a tabular fallback for charts (you already do this), and treat it as an accessibility feature, not a debugging feature.
Adopt WCAG 2.1 AA as your baseline. 
For maps:
provide non-map summaries: ranked tables, top-N lists, downloadable GeoJSON,
ensure tooltips are keyboard-accessible or have a focus equivalent,
avoid color-only encodings; always support patterns/labels and high contrast.
Notes on external data provider documentation
ClimateSERV’s developer API documentation explicitly defines async job submission and parameters (datatype, begintime/endtime, geometry, etc.), validating your connector strategy. 
PSMSL provides station-based access patterns and documented file structures for RLR/Metric datasets, supporting reliable ingestion and citation guidance. 
IBTrACS is versioned (v4r01), has a DOI and documented update schedule, and is explicitly positioned as a unified global best-track archive; this supports provenance and repeatability requirements. 
NOAA service change notices for NOMADS/OpenDAP termination and FTPPRD termination are a concrete reminder to treat “data access methods” as volatile dependencies and to build resilient adapters. 
