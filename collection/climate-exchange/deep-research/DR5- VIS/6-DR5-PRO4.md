Yes — we’re good to plan the attack sequence.

I’m going to orchestrate this the way a world-class viz team would: lock a premium visual system first (so it “pops”), fix structural correctness bugs next (so it’s trustworthy), then layer in evidence/uncertainty as progressive enhancement (so we don’t stall waiting for perfect semantics/data).

One important clarification: I don’t have the full text of the deep-research report rendered inside this chat, but I do have the exact issue targets you asked it to validate (SelectionBusProvider, artifact proxy bypass, inlineSpec shadowing, MapExplorer layer IDs/cleanup, decade contract mismatch, CSS token drift, briefing receipt fan-out, largest GeoJSON/Vega specs). I’ll use those as the backbone and direct agents to reference the report for file/line evidence + confirm via git grep during Phase 0.

Also: your “Glossary” upload is a pointer to docs/GLOSSARY.md, and agents should use it to standardize terms (Evidence vs Provenance vs Receipt).  ￼

⸻

Master attack sequence

Phase 0 — Recon + locking quality gates (do this first, no debate)

Goal: zero rediscovery, one shared truth: where visuals live, what stack is used, what’s broken, what’s heavy.

Outputs
	1.	Visualization Surface Inventory (route → components → stack → data → trust hooks)
	2.	Hotspot list (files where vis + trust + heavy data meet)
	3.	Performance baseline (slow routes + biggest payloads/specs)
	4.	A “Definition of Done” gate for every vis PR (screenshots, a11y, perf smoke, fail-closed states)

Why this is Phase 0

Because “world-class” isn’t brilliance — it’s repeatability. This phase prevents everyone from building “their version” of pop.

⸻

Phase 1 — Make it pop everywhere (premium visual system foundations)

Goal: immediately improve perceived quality without waiting for perfect data contracts.

Non-negotiables shipped here
	•	VisualFrame wrapper (consistent hierarchy: title/subtitle/unit/delta/actions)
	•	Unified tooltip + legend behavior (feels the same across every chart/map)
	•	Fail-closed states (loading skeleton, empty, error; never silently wrong)
	•	Theme unification (Vega theme + map colors + tokens)
	•	Mobile rules (controls collapse into a drawer, legends never clip)

This is where the product starts feeling “expensive.”

⸻

Phase 2 — Fix structural correctness (so pop isn’t lying)

Goal: resolve the specific anti-patterns/issues you flagged so interactions are coherent and maintainable.

This phase is where we tackle:
	•	Selection bus / crossfilter plumbing (the map/workspace selection architecture)
	•	Compare correctness (artifact proxy bypass)
	•	Vega spec rendering correctness (inlineSpec shadowing)
	•	Map layer ID stability + cleanup (index-based IDs create bugs)
	•	Contract mismatches (decades) (string “1970s” vs numeric)
	•	CSS token drift (undefined tokens causing silent theme divergence)

⸻

Phase 3 — Evidence + uncertainty as progressive enhancement (the moat)

Goal: make trust defensible without blocking earlier delivery.

Shipped as enhancements:
	•	Evidence Drawer + evidence badge everywhere (even if initially “thin”)
	•	Receipt/Provenance stabilization (IDs, tool run metadata, lineage pointers)
	•	Uncertainty lens (only where it changes decisions; bands/fans, confidence overlays)
	•	Traceability matrix (claims × sources coverage)

⸻

Phase 4 — Hero experiences (Comparison Studio + spatial instrument)

Goal: the “signature demo” that makes CIE unforgettable.
	•	Baseline vs scenario vs Δ (delta) is first-class
	•	Map ↔ charts ↔ tables are linked with persistent selection semantics
	•	Shareable/snapshot states reproduce exactly what users saw

⸻

What I want the coding agents to do next (exactly)

Step 1: Read these parts of this thread

Tell them to treat this conversation as the spec, with these anchors:
	1.	North Star: “Claim Object = Visual + Delta + Evidence + Fail-closed + Shareable state”
	2.	Phases: 0 → 4 above
	3.	Known issues to verify + fix:
	•	SelectionBusProvider presence/absence in workspace map route
	•	artifact proxy bypass in compare components
	•	inlineSpec shadowing in ArtifactsPanel/VegaLiteView
	•	MapExplorer layer IDs are index-based + cleanup gaps
	•	decade contract mismatch (“1970s” vs numeric decade)
	•	CSS token drift (e.g., --color-surface-2 undefined)
	•	loadBriefingData.ts receipt fan-out behavior + heavy payloads
	4.	Glossary alignment: open docs/GLOSSARY.md (via your pointer) and normalize UI language.  ￼

Step 2: Run Phase 0 probes and post artifacts back

They should produce these files (commit them to dev under docs/vis/):
	•	docs/vis/surface_inventory.md
	•	docs/vis/hotspots.md
	•	docs/vis/perf_baseline.md
	•	docs/vis/data_samples/ (2–3 sample payloads: map, briefing, compare)

If you already have the deep research report: they should also paste the report section that lists exact file paths + line refs for the issues above. That lets me lock P0/P1 ordering with certainty.

⸻

Execution-ready task packets (world-class standards)

Below are 12 packets that match the phases and lane boundaries. Each has (a) owner lane, (b) success criteria, (c) verification checklist. Agents can start immediately; Phase 0 packets don’t require product answers.

⸻

Packet 0.1 — Surface inventory generator + hotspot map
	•	Lane: UI/UX
	•	Priority: P0
	•	Definition of done:
	•	Inventory lists every route surface with: primary components, vis stack, data loaders, trust hooks
	•	Hotspots list highlights: map/briefing/rooms/compare + largest specs/payloads
	•	Verification checklist:
	•	pnpm lint / pnpm typecheck
	•	Inventory updates when routes/components change

⸻

Packet 0.2 — Visual PR quality gate (CI)
	•	Lane: Infra
	•	Priority: P0
	•	DoD:
	•	CI job runs “vis smoke” suite: inventory check + story render + a11y smoke
	•	Verification:
	•	CI fails when a visual surface changes without inventory update

⸻

Packet 1.1 — VisualFrame component (premium hierarchy everywhere)
	•	Lane: UI/UX
	•	Priority: P0
	•	DoD:
	•	At least 2 key surfaces (likely rooms + briefing OR map) wrap visuals in a consistent frame:
	•	title/subtitle/unit
	•	delta chip slot
	•	action bar: Evidence / Share / Download (even if stubbed)
	•	Verification:
	•	screenshot diff before/after (desktop + mobile)
	•	no layout shift during loading

⸻

Packet 1.2 — Unified tooltip + legend/filter-chip semantics
	•	Lane: UI/UX
	•	Priority: P0
	•	DoD:
	•	One tooltip model used across charts/maps
	•	Legends act as filter chips with multi-select + clear reset
	•	Verification:
	•	keyboard focus reveals the same info as hover
	•	interaction feels consistent on 3 surfaces

⸻

Packet 1.3 — Fail-closed states (loading/empty/error)
	•	Lane: UI/UX
	•	Priority: P0
	•	DoD:
	•	Every visualization surface has explicit:
	•	skeleton loading
	•	empty-state with reason
	•	error-state with retry and safe fallback
	•	Verification:
	•	simulate missing data + API error + slow network

⸻

Packet 1.4 — Theme/token unification (Vega + map + CSS tokens)
	•	Lane: UI/UX
	•	Priority: P0
	•	DoD:
	•	Fix CSS token drift (undefined tokens) and align chart/map colors
	•	Vega theme defaults enforce consistent axes/grid/typography
	•	Verification:
	•	token scan shows no undefined core tokens
	•	chart + map look like one product

⸻

Packet 2.1 — Fix SelectionBusProvider / selection plumbing in workspace map route
	•	Lane: UI/UX
	•	Priority: P0
	•	DoD:
	•	The workspace map surface supports selection persistence and shared state (map ↔ panels)
	•	Verification:
	•	select region on map → selection state visible and stable
	•	selection survives minor re-renders; reset semantics clear

⸻

Packet 2.2 — Fix compare artifact proxy bypass
	•	Lane: UI/UX (with Infra consult if proxy is infra-owned)
	•	Priority: P0
	•	DoD:
	•	Compare surfaces use the intended artifact proxy path; no bypass that breaks caching/auth/receipts
	•	Verification:
	•	compare view works in prod-like env; network traces confirm proxy usage

⸻

Packet 2.3 — Fix inlineSpec shadowing (ArtifactsPanel/VegaLiteView)
	•	Lane: UI/UX
	•	Priority: P0
	•	DoD:
	•	Vega spec passed/rendered deterministically; no shadowed variables causing wrong charts
	•	Verification:
	•	unit test or story proving correct spec path
	•	regression story for the previously broken case

⸻

Packet 2.4 — MapExplorer layer ID stability + cleanup
	•	Lane: UI/UX
	•	Priority: P0
	•	DoD:
	•	Layer IDs are stable (not index-based)
	•	Layers clean up on unmount/update; no stale layers or memory leaks
	•	Verification:
	•	toggle layers repeatedly → no duplicate IDs, no orphaned layers
	•	performance doesn’t degrade after repeated interactions

⸻

Packet 2.5 — Fix decade contract mismatch
	•	Lane: Data/Ingestion (UI/UX dependent for display formatting)
	•	Priority: P1
	•	DoD:
	•	One canonical decade representation throughout the stack
	•	UI formats decades consistently (“1970s”) but uses stable numeric contract under the hood
	•	Verification:
	•	tool output + UI viewmodel agree; no stringly-typed decade bugs

⸻

Packet 3.1 — Evidence Drawer v1 + “thin evidence” safe fallback
	•	Lane: UI/UX
	•	Priority: P1
	•	DoD:
	•	Evidence Drawer exists for all key claims (KPI, chart, map region)
	•	If evidence missing → explicit “Evidence unavailable” state (fail closed)
	•	Verification:
	•	stories: full evidence / partial / none

⸻

Packet 3.2 — Receipt/provenance minimal fields + stable IDs
	•	Lane: Agents SDK
	•	Priority: P1
	•	DoD:
	•	Every tool output can include stable receiptId + minimal metadata needed by Evidence Drawer
	•	Verification:
	•	run same tool twice → stable IDs where appropriate + deterministic linkage

⸻

Standards (what “world-class” means in PR review)

Every visualization PR must include:
	1.	Before/after screenshots (desktop + mobile)
	2.	Fail-closed states demonstrated (loading + empty + error)
	3.	Interaction check (tooltip/legend behavior consistent)
	4.	A11y check (keyboard path to core information)
	5.	Perf note (“no regression” — measured on target surface)
	6.	Evidence hook (even if drawer content is thin)

If any item is missing, PR doesn’t merge.

⸻

The single most important orchestration rule

Do not start Compare Studio or advanced uncertainty work until Phase 1 foundations + Phase 2 correctness fixes are merged.

That’s how world-class teams avoid “beautiful instability.”

⸻

What I need from you (minimal)

Nothing conceptual. Just do this operationally:
	1.	Tell agents: run Phase 0 probes and commit docs/vis/*
	2.	Have them paste the deep-research report’s file/line evidence for the known issues into the PR description (or add docs/vis/report_extracts.md)
	3.	Then I’ll convert it into a locked P0/P1/P2 execution order with exact file targets and merge slices.

If you want, paste the Phase 0 artifacts here once they exist (surface inventory + hotspots), and I’ll immediately turn them into the final “attack sequence” with per-route worklists and a merge plan that minimizes conflicts across lanes.