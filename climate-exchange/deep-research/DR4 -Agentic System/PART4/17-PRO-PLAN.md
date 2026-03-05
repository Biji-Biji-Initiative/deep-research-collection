Got it. No more flailing with mail. Here’s the world‑class, “golden reference” report + the exact playbook your 4 agents should follow from here, with clear ownership, hard gates, and a single source of truth that will later drive the UI and tool routing.

Everything below is designed so you stop “probing like a kid with a stick” and instead run a controlled engineering program.

⸻

CIE Data Plane Reality Report

Date: Feb 21, 2026
Scope: “Do we actually have the data?” + “Can tools reach it?” + “Is it visible in UI?”
Inputs: Your pasted audit output + DB checks + trust‑feed/UI discovery (as shown in your transcript)

Executive summary

Temporal ingestion is broadly healthy: there is real data in source_snapshot across major climate domains (rainfall, cyclone tracks, sea level, ocean physics, earthquakes, coral reef watch, etc.).
The system is failing because the tool/connector layer is not wired to the snapshot store consistently, and in a few cases expects a different payload format or different keys than what Temporal writes. The UI is partially visible via the trust‑feed-backed /inventory page, but it is currently misleading (many “unknown” datasets actually exist; some high‑value datasets aren’t even registered, so they’re invisible).

Bottom line: You don’t have an “ingestion problem.” You have a data reachability + registry integrity problem.

⸻

1) What’s visible in the UI right now?

Based on your logs:
	•	There is an API endpoint: GET /admin/ingestion/trust-feed (implemented in apps/api/src/routes/inventory-trust-feed.ts).
	•	The web app has an /inventory page (you referenced it as climate.mereka.dev/inventory) that renders trust-feed results.
	•	It currently shows something like 16 operational, 1 degraded, 28 unknown (numbers from your transcript).

Why it’s misleading
	1.	Key mismatches: trust-feed config uses dataset keys/source keys that don’t match what Temporal stored. Result: UI says “unknown” even when the DB has real rows (e.g., CMEMS/ocean physics, ERA5).
	2.	Orphaned ingested datasets: datasets exist in DB but aren’t registered in trust-feed config at all (e.g., pacific_sealevel), so the UI can’t possibly show them.
	3.	Local flat files (FTP/CSV assets in data/) are not represented in trust-feed, so the UI has no visibility into them.

Conclusion: Yes, it’s “visible,” but only through a partial, currently inconsistent inventory layer.

⸻

2) The critical truth: “Ingested” ≠ “Tool‑reachable”

You already observed the archetypal failure:

L3 mixed-domain run symptom (example)
	•	Tools executed (sea level + cyclone tools called)
	•	tool_results_count = 0 + receipt guard fired
	•	DB status showed succeeded even though output was “Could not compute” (telemetry integrity bug)

This is exactly what happens when:
	•	connectors can’t read stored snapshots (format/key mismatch), or
	•	tools use stale local files / remote fetch timeouts, or
	•	receipts pipeline isn’t attached

So we need to treat “ingestion health” and “tool reachability” as separate measurable layers.

⸻

3) Highest-impact data plane defects (from your audit)

This is the “why tools return no receipts even though data exists.”

A) PSMSL/sea level — CRITICAL

What you have: sea level rows stored in DB under Temporal snapshots (real coverage exists).
Why it fails: connector expects a different payload structure and/or queries the wrong keys.
Effect: sea level tool falls back to live API; live API fails; result becomes ERR_SOURCE_UNAVAILABLE → 0 receipts.

This is not “missing data.” It’s schema/key mismatch between ingestion output and connector reader.

B) IBTrACS/cyclone — HIGH

What you have: cyclone track rows stored in DB (Temporal) AND a local CSV.
Why it fails: tool path ignores snapshot store and uses local CSV with a freshness threshold; when stale it tries remote download; your timeout is too short for 35MB.
Effect: tool runs → fails → 0 receipts, even though DB has 76k+ rows.

This is not “missing data.” It’s the tool reading the wrong store (local/remote) instead of the snapshot store.

C) CHIRPS registry — MEDIUM

What you have: CHIRPS rows stored in snapshot store.
Why UI fails: registry points to a non-existent source key (e.g., climateserv vs chirps).
Effect: UI trust feed “unknown,” and future local-first paths will break.

D) Local CHIRPS CSV missing — LOW

chirps_local tool fails immediately if the file isn’t present.

E) pacific_sealevel dataset — Strategic gap

Your transcript called out a high-value daily sea level dataset (pacific_sealevel) that is not consumed by any tool and not registered in trust-feed, so it is effectively invisible and unusable.

⸻

4) Golden Reference requirement (what you asked for)

You want a single document that answers:
	•	What datasets exist (Temporal + local flat files + live APIs)
	•	Coverage ranges (start/end) + freshness
	•	Which tools read them
	•	Whether the UI currently surfaces them
	•	For a given domain, what are the multiple sources and which is primary

To do this properly, the document must be auto-generated. If it’s handwritten, it will rot in 48 hours.

⸻

5) The world-class plan to fix this (without guesswork)

Phase 0 — Stop-the-line methodology

Before you spend more money on probes:

Gate: “No second probe without review”

Mechanically enforce:
	•	Probe runner writes “review required”
	•	Separate review step generates a report
	•	Human ack required to proceed

This prevents spending $ again before learning from the last run.

Owner: GentleOtter (coord), implemented by FoggyRiver or GreenWolf (whoever owns harness)

Success: It becomes physically impossible to run a second probe without a review artifact.

⸻

Phase 1 — Build the Data Inventory Truth Layer

Objective

Create a single canonical dataset registry that is used by:
	•	Temporal ingestion metadata
	•	trust-feed API
	•	tool connectors
	•	UI inventory page

Deliverables
	1.	Canonical registry: docs/data/dataset_registry.md + dataset_registry.json
Each dataset entry has:
	•	dataset_id (stable)
	•	domain (sea_level, cyclone, rainfall…)
	•	source_key (snapshot store key) and/or local_path
	•	coverage_start, coverage_end, resolution
	•	freshness_sla and last_refresh_at
	•	tools (tool keys that consume it)
	•	ui_visibility (true/false)
	•	priority within domain (primary/secondary/fallback)
	•	reachability flags: {ingested, tool_reads_snapshot, tool_reads_local, tool_calls_remote}
	2.	Generator script: scripts/gen_data_coverage_reference.mjs
	•	Queries snapshot store for row counts/coverage
	•	Scans data/ for CSV/GeoJSON/XLSX assets (FTP/local)
	•	Maps tool keys → datasets (from your tool catalog file)
	•	Produces:
	•	docs/DATA_COVERAGE_REFERENCE.md (golden)
	•	reports/data_coverage/data_coverage.json (machine readable)
	•	reports/data_coverage/data_coverage.csv (for spreadsheets)
	3.	Trust-feed alignment
trust-feed should be driven from the registry (or validated against it), not hand-maintained constants.

Owner: FoggyRiver (data integrity lane), with review by GentleOtter

Success: Running one command regenerates the doc and it reflects reality.

⸻

Phase 2 — Make tools snapshot-first (reachability unification)

Objective

Eliminate the split brain where Temporal writes into Postgres but tools read local CSVs or remote APIs.

Work items (ordered)
	1.	Sea level
	•	Fix PSMSL connector to read the actual snapshot format OR standardize ingestion payload to what connector expects.
	•	Add a connector/tool for pacific_sealevel and make it the primary sea-level dataset if it’s truly richer (as your audit suggests).
	2.	Cyclone
	•	Teach IBTrACS tool to read from snapshot store (source_snapshot) as primary.
	•	Local CSV becomes optional cache/fallback, not the source of truth.
	3.	Rainfall
	•	Fix CHIRPS registry mapping so UI reflects snapshot reality.
	•	Optional: export snapshot to local CSV for offline resilience (but snapshot store should be the primary).

Owner: GreenWolf (connectors/tools), with FoggyRiver as co-owner for registry mapping

Success: Mixed-domain L3 can obtain receipts for both cyclone + sea level without relying on remote fetches.

⸻

Phase 3 — UI deepening (what you explicitly requested)

Objective

Make /inventory the “operator dashboard for truth,” not a misleading list.

UI requirements
	•	3 tabs:
	1.	Temporal snapshots (Postgres)
	2.	Local assets (data/ folder: CSV/GeoJSON/XLSX)
	3.	Live APIs (connectors that call remote services)
	•	For each dataset row:
	•	domain, dataset_id, source_key/path
	•	row_count, last_refresh
	•	coverage start/end
	•	tools that consume it
	•	reachability badge (ingested + tool-readable + UI-visible)
	•	warnings (key mismatch, orphaned, remote-only, stale)

Owner: Stormy (UI)

Success: A new operator can look at the page and immediately understand what data exists and what tools can use it.

⸻

6) Ownership map (only your 4 agents)

GentleOtter (Coordinator)

Job: enforce process gates + ensure owners deliver artifacts
Deliverables:
	•	Probe discipline gate merged (no second probe without review)
	•	A single “tracking page” in docs that lists:
	•	what’s done
	•	who owns what
	•	what’s blocked
	•	Definition of Done for data-plane readiness

Definition of Done:
	•	L3 mixed-domain probe can pass on a clean run where tools use snapshot-first data

⸻

GreenWolf (Tools/Connectors/Ingestion plumbing)

Job: make tools actually reach ingested data
Deliverables (priority order):
	•	PSMSL connector fix (format/key mismatch)
	•	IBTrACS tool reads snapshot store OR timeout/cache strategy fixed
	•	Any Temporal pipeline key standardization needed

Definition of Done:
	•	sea_level and cyclone tools each produce receipts from ingested sources

⸻

FoggyRiver (Data Integrity + Golden Reference)

Job: build “single source of truth” inventory and expose orphaned datasets
Deliverables:
	•	Auto-generated docs/DATA_COVERAGE_REFERENCE.md from scripts
	•	Registry-driven trust-feed validation
	•	Identify and register “orphaned but valuable” datasets (e.g., pacific_sealevel)

Definition of Done:
	•	The doc regenerates cleanly and explains every dataset’s reachability + coverage

⸻

Stormy (UI)

Job: visualize reality and reduce operator confusion
Deliverables:
	•	Inventory UI upgraded to show:
	•	Temporal snapshots + local assets + live APIs
	•	per-domain multiple sources
	•	reachability and coverage
	•	Links to the golden doc and raw JSON artifacts

Definition of Done:
	•	Inventory page matches the golden doc and explains “unknowns” with root causes (key mismatch, orphaned, etc.)

⸻

7) What “success looks like” (concrete acceptance gates)

Data Plane Gates
	•	G1: For each priority domain (cyclone, sea level, rainfall), there is at least one dataset that is:
	•	ingested ✅
	•	tool-readable ✅
	•	produces receipts ✅
	•	G2: trust-feed UI no longer marks ingested datasets “unknown” due to key mismatches
	•	G3: local FTP/CSV assets are visible in inventory with coverage and tool mapping

Agentic Gates (ties back to your orchestration reliability)
	•	A1: Mixed-domain queries produce ≥2 receipts (one per domain) and do not loop
	•	A2: “tools executed but 0 receipts” becomes a stop-the-line defect label, not a silent “succeeded”
	•	A3: Probe runner blocked until review artifact exists

⸻

8) Immediate next step (what to do tomorrow morning)

Tell your agents this exact sequence:
	1.	FoggyRiver: implement the generator script + regenerate the golden doc
	2.	GreenWolf: fix PSMSL connector mismatch and/or wire pacific_sealevel as primary
	3.	Stormy: adjust UI to consume the machine-readable data_coverage.json
	4.	GentleOtter: merge ProbeLock gate so nobody burns money without learning

⸻

If you want, I’ll also give you a ready-to-paste “Golden Reference Doc” template (with the exact tables and “coverage bar” visualization format) so your agents don’t invent their own structure and fragment the truth.