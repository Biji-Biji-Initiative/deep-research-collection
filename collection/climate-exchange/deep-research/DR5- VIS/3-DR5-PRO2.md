Got it. Since you don’t have crisp answers yet (and you want to “get on the bike”), here’s an opinionated, world‑class implementation plan that your lanes can start executing immediately — without needing perfect product clarity up front.

I’m going to make explicit assumptions, bake them into Phase 0 as reversible defaults, and structure the work so you can refine later without rework.

Also: you mentioned the glossary — what I received is a pointer to docs/GLOSSARY.md (not the glossary content itself).  ￼
So I’ll include a terminology normalization packet as an early task (so agents can align quickly once they open the actual file).

⸻

The operating assumptions (so agents can build now)

Highest-stakes workflow (assumption)

CIE is primarily for prioritization + investment-style decisions:
	1.	Prioritize geographies/assets/interventions by risk/opportunity and confidence
	2.	Compare baseline vs scenarios vs peers and understand drivers
	3.	Publish defensible “briefings” where every claim can be traced to evidence

If any of this is wrong later, it won’t break the plan — it just changes which surfaces get the hero treatment first.

“Comparison verb” (you don’t need to know it — we choose it)

A comparison verb is simply the dominant user action: compare X to Y.
We’ll optimize for these three, in this order:
	1.	Baseline → Scenario (Δ / delta) (most common in climate and investment decisions)
	2.	Region/asset → Peers (ranking and allocation)
	3.	Current → Target (policy or program goals)

“Receipts” terminology (you’re right to suspect mismatch)

Most teams conflate 3 things:
	•	Evidence (user-facing): “Why should I trust this visual claim?”
	•	Provenance (chain): lineage from raw sources → transforms → model/tools → claim
	•	Receipt (machine-facing): a concrete record of a tool run / dataset version / hash / timestamp

Recommendation: keep “Receipt” internal, expose “Evidence” in the UI, and treat Provenance as the underlying structure.

This matters because it shapes what you build:
	•	UI/UX lane builds Evidence surfaces
	•	Agents SDK lane ensures Receipt objects exist + are stable
	•	Data lane ensures Provenance fields are propagated
	•	Infra lane ensures snapshots are reproducible

This also aligns with IPCC-style “calibrated uncertainty language” and traceability: findings grounded in evidence, with explicit confidence/likelihood conventions.  ￼

⸻

The North Star that makes CIE “pop”

CIE becomes lovable when every visual behaves like a Claim Object:

Claim Object = Visual + Delta + Uncertainty + Evidence + Shareable Snapshot

Where:
	•	Delta is first-class (baseline vs scenario vs peer)
	•	Uncertainty is not decorative; it changes interpretation (shaded bands preferred)  ￼
	•	Evidence is bound to marks/regions (not hidden in footnotes)
	•	Snapshots are reproducible and stable (archived view state) — same spirit as OWID’s “archived charts” concept  ￼
	•	Accessibility is real: table alternative + keyboard access + no hover-only data  ￼

That’s the differentiator stack.

⸻

Overall phased plan (build now, refine later)

Phase 0 (Week 1): Lock contracts + stop future chaos

Goal: make visualization work “API-like”: consistent, testable, provenance-ready.

Deliverables
	•	Visualization inventory generator (routes → components → libs → data inputs → trust hooks)
	•	A “Visualization Contract” type schema (Evidence/Provenance/Uncertainty)
	•	Standardized vis:* dev + CI commands (so every lane has repeatable checks)

Success metrics
	•	Inventory exists and is kept current automatically
	•	Every new visual PR must conform to contract + story coverage

⸻

Phase 1 (Days 1–30): Trust + clarity foundation (highest ROI)

Goal: everything gets more readable, reliable, and defensible — with minimal new surface area.

Deliverables
	•	Unified tooltip + legend + keyboard-focus behavior
	•	Evidence Drawer attached to visuals + KPI claims (even if initially thin)
	•	Uncertainty encoding v1 for the “top 3” chart types (bands/ranges)  ￼
	•	Loading/empty/error “fail-closed” states (no silent nonsense)
	•	Accessibility baseline: table alternatives for charts/maps  ￼

Success metrics
	•	Users can answer: “Compared to what?” + “How sure?” + “Show evidence” from any key visual
	•	Interaction latency stays smooth (see perf targets below)

⸻

Phase 2 (Days 31–60): The hero experience (comparison studio + linked analysis)

Goal: make “comparison” feel inevitable, fast, and shareable.

Deliverables
	•	Compare Studio: Baseline vs Scenario vs Δ view
	•	Crossfilter linking: map ↔ charts ↔ tables (persistent selection model)
	•	Snapshot/Share v1: stable state links (URL/state + stored snapshot option)  ￼

Success metrics
	•	A user can reproduce a decision view in 1 click
	•	Deltas are not eyeballed; they’re explicit

⸻

Phase 3 (Days 61–90): Moat (traceability + advanced uncertainty + signature maps)

Goal: build what competitors struggle to copy.

Deliverables
	•	Traceability Matrix / Evidence Graph (claims × sources × methods coverage)
	•	Uncertainty decomposition (what drives variance) + sensitivity explorer
	•	Map confidence overlays + bivariate mapping + time playback

Success metrics
	•	“Trust” becomes a visible product capability, not a promise

⸻

Performance targets (so it feels premium)

These are “world-class product feel” numbers — tune later:
	•	Interaction response (brush/select/hover): < 100ms perceived
	•	Panel rerender on filter: < 200ms median
	•	Map layer toggle: < 300ms median
	•	Worst-case large table scroll: 60fps (virtualized)

⸻

Agent-ready execution packets (start assigning today)

Below are 15 packets. They’re structured so Phase 0 creates the scaffolding that makes the later packets safe and fast.

Note: I’m referencing the repo’s known areas you listed (e.g., apps/web/app/..., apps/web/components/..., apps/web/lib/trustFeed.ts, apps/api/src/receipts/**). Your UI lane can plug in exact component names once Phase 0 inventory runs.

Packet list (backlog-ready)

#	Title	Lane	Priority	Est	Dependencies
0.1	Auto-generate Visualization Surface Inventory (routes → components → stack → data → trust)	UI/UX	P0	M	—
0.2	Add standardized vis:* scripts + CI gate (storybook/tests/a11y/perf smoke)	Infra	P0	M	—
0.3	Define Visualization Contract types (Claim/Evidence/Provenance/Uncertainty)	UI/UX	P0	M	0.1
0.4	Glossary normalization: Evidence vs Provenance vs Receipt (and rename UI labels)	UI/UX	P0	S	0.3
1.1	Evidence Drawer component + Evidence Badge (attach to any visual claim)	UI/UX	P0	M	0.3
1.2	Receipt plumbing API: stable receipt IDs + minimal fields needed for Evidence Drawer	Agents SDK	P0	M	0.3
1.3	Unified tooltip/legend/filter-chip interaction model (keyboard parity)	UI/UX	P0	M	0.3
1.4	Uncertainty Lens v1 (bands/ranges + labeling conventions)	UI/UX	P0	M	0.3
1.5	Data Health Strip (freshness/coverage/missingness + caveats slot)	Data/Ingestion	P1	M	0.3
1.6	Fail-closed states for visuals (loading/empty/error boundaries + skeletons)	UI/UX	P0	M	0.3
2.1	Compare Studio v1 (Baseline vs Scenario vs Δ)	UI/UX	P1	L	1.3
2.2	Crossfilter state engine (selection persistence, reset semantics, linked highlight)	UI/UX	P1	L	2.1
2.3	Snapshot/Share v1 (stable view state + archived snapshot option)	Infra	P1	L	0.2, 2.1
3.1	Traceability Matrix / Evidence Graph view	UI/UX	P2	L	1.1, 1.2
3.2	Advanced map modes: confidence overlay + bivariate + time playback	UI/UX	P2	L	2.2

Now, each packet expanded into implementation-ready shape:

⸻

Packet 0.1 — Auto-generate Visualization Surface Inventory

Lane: UI/UX | Priority: P0 | Est: M

Why: This eliminates rediscovery forever and gives you the living “system map” you asked for.

Implementation steps
	1.	Add a script (e.g., scripts/vis_inventory.ts) that:
	•	enumerates routes under apps/web/app/**
	•	scans imports for chart/map libs (Vega/Vega-Lite/Map renderer wrappers)
	•	maps route → primary components → data loaders (load*, view models, manifests)
	•	detects trust hooks usage (trustFeed, receipt references)
	2.	Output:
	•	docs/vis/surface_inventory.md
	•	docs/vis/stack_map.json (for later automation)
	3.	Add “diff mode” in CI to fail if inventory changes but docs aren’t updated.

Definition of done
	•	Running the script produces a complete inventory table
	•	CI flags mismatch between code and inventory

Verification
	•	vis:inventory (created in Packet 0.2) generates docs deterministically

Rollback
	•	Remove CI gate first; keep script output for reference

⸻

Packet 0.2 — Standardized vis:* scripts + CI gate

Lane: Infra | Priority: P0 | Est: M

Why: Every later packet can reference exact commands, and your “visual quality bar” becomes enforceable.

Implementation steps
	1.	Add scripts (root package scripts or equivalent):
	•	vis:inventory
	•	vis:storybook
	•	vis:test
	•	vis:a11y (axe/playwright)
	•	vis:vr (visual regression snapshots)
	2.	Add CI job that runs at least:
	•	inventory + typecheck + a11y smoke + story render smoke

DoD
	•	One command runs the entire visualization validation suite

Rollback
	•	Keep scripts but remove CI enforcement temporarily

⸻

Packet 0.3 — Visualization Contract types

Lane: UI/UX | Priority: P0 | Est: M

Why: Prevents one-off charts. Enables provenance + uncertainty + evidence as default.

Contract shape (minimum)
	•	ClaimSpec: title, metric, unit, baseline, delta mode
	•	UncertaintySpec: type (interval/quantile/ensemble), level (likely/very likely), notes
	•	EvidenceRef[]: receipt IDs, source IDs, timestamps, transform refs
	•	DataHealth: coverage, missingness, lastUpdated, caveats

DoD
	•	All existing visuals migrate to consume a ClaimSpec wrapper (even if some fields null initially)

Rollback
	•	Wrapper can pass-through raw config; no rendering changes required

⸻

Packet 0.4 — Glossary normalization (Evidence vs Provenance vs Receipt)

Lane: UI/UX | Priority: P0 | Est: S

Why: If language is confused, the UI will be confused.

Steps
	•	Update glossary and UI copy:
	•	User sees: Evidence
	•	Developer sees: Receipts
	•	System explains: Provenance
	•	Add short tooltip copy rules:
	•	uncertainty: plain language conventions (avoid jargon)
	•	evidence: what it is and why it matters

Notes
	•	Use ONS guidance: show uncertainty when it changes interpretation; prefer shaded bands.  ￼

⸻

Packet 1.1 — Evidence Drawer + Evidence Badge

Lane: UI/UX | Priority: P0 | Est: M

What it is
	•	A drawer/panel that opens from any visual claim:
	•	receipts list (source, timestamp, tool/model)
	•	transformations summary
	•	“what changed since last update”
	•	Badge indicates evidence coverage level (e.g., “3 sources”, “fresh 2d”, “low coverage”)

DoD
	•	Every major visual has a visible Evidence entry point
	•	Missing evidence fails closed (explicit “Evidence unavailable” state)

Verification
	•	Storybook stories for: full evidence, partial evidence, no evidence

⸻

Packet 1.2 — Receipt plumbing API (minimal stable model)

Lane: Agents SDK | Priority: P0 | Est: M

Goal
	•	Guarantee stable IDs and enough metadata for UI.

Minimum receipt fields
	•	receiptId, sourceId(s), createdAt, toolName, toolVersion/hash
	•	input hash, output hash (or dataset version pointer)
	•	optional: confidence/likelihood tags (if available)

DoD
	•	UI can request receipts for a claim and render them reliably

⸻

Packet 1.3 — Unified tooltip/legend/filter-chip model

Lane: UI/UX | Priority: P0 | Est: M

Why
	•	Consistent interaction is a “premium feel” amplifier.

Requirements
	•	Hover data must also appear on keyboard focus (no hover-only truths)  ￼
	•	Legends act as filters (chips) with multi-select semantics

⸻

Packet 1.4 — Uncertainty Lens v1

Lane: UI/UX | Priority: P0 | Est: M

What
	•	A toggle that adds uncertainty encodings across charts:
	•	shaded band around central estimate (preferred)  ￼
	•	Labeling conventions aligned to calibrated language (confidence vs likelihood)  ￼

DoD
	•	At least 3 core chart types support uncertainty mode

⸻

Packet 1.5 — Data Health Strip

Lane: Data/Ingestion | Priority: P1 | Est: M

What
	•	Standard data quality panel for every claim:
	•	coverage, missingness, freshness, caveats
	•	Output as structured fields so UI is consistent

A11y tie-in
	•	Provide table alternative for complex visuals (especially maps).  ￼

⸻

Packet 1.6 — Fail-closed visual states

Lane: UI/UX | Priority: P0 | Est: M

What
	•	Error boundaries for every visual surface
	•	Explicit empty states (“No data for selection”)
	•	Skeleton loaders with fixed layout to prevent jank

⸻

Packet 2.1 — Compare Studio v1 (Baseline vs Scenario vs Δ)

Lane: UI/UX | Priority: P1 | Est: L

DoD
	•	Baseline pinned
	•	Scenario selectable
	•	Δ view available everywhere the baseline/scenario exist

⸻

Packet 2.2 — Crossfilter state engine

Lane: UI/UX | Priority: P1 | Est: L

DoD
	•	Map selection highlights charts
	•	Chart brush filters map
	•	Reset semantics consistent and visible

⸻

Packet 2.3 — Snapshot/Share v1

Lane: Infra | Priority: P1 | Est: L

Why
	•	Stable citations are a trust superpower (OWID’s archived charts is a proven pattern).  ￼

DoD
	•	“Copy link” includes full visual state
	•	Optional archived snapshot that won’t change

⸻

Packet 3.1 — Traceability Matrix / Evidence Graph

Lane: UI/UX | Priority: P2 | Est: L

DoD
	•	Claims × sources coverage view
	•	Quickly shows “thin ice” vs “robust evidence”

⸻

Packet 3.2 — Advanced map modes

Lane: UI/UX | Priority: P2 | Est: L

DoD
	•	Confidence overlay (texture/hatch/opacity)
	•	Time playback
	•	Bivariate option for risk × exposure style views

⸻

30/60/90 plan (high-level sequencing)

0–30 days (ship trust + clarity)
	•	Inventory + contracts + commands (0.x packets)
	•	Evidence Drawer + uncertainty v1 + a11y baseline + fail-closed states (1.x packets)

31–60 days (ship the hero workflow)
	•	Compare Studio + crossfilter + snapshot sharing (2.x packets)

61–90 days (ship the moat)
	•	Traceability matrix + advanced map modes + uncertainty decomposition hooks (3.x packets)

⸻

Open decision gates (safe to postpone, but name them)
	1.	What is “receipt” in your system? tool-run log vs dataset lineage vs both
	2.	What level of uncertainty will you standardize on first? (likely range vs very likely range vs quantiles) — IPCC conventions exist, but product choice matters  ￼
	3.	Snapshots: client-only serialized state, or server-stored immutable snapshot IDs? (infra cost vs trust value)  ￼
	4.	Accessibility bar: minimum “table alternative everywhere” (recommended) vs selective (riskier)  ￼

⸻

What I recommend you do today (to “get on the bike”)

Assign just these 4 immediately (they unblock everything else):
	•	0.1 Inventory generator (UI/UX)
	•	0.2 vis:* commands + CI gate (Infra)
	•	0.3 Visualization Contract types (UI/UX)
	•	1.1 Evidence Drawer (UI/UX) + 1.2 Receipt plumbing (Agents SDK)

Once those land, Phase 1 becomes “paint by numbers,” and the product starts feeling premium fast.

If you want, in the next step we can take Phase 1 only and turn it into a day-by-day sequence (with owners and PR cut lines) once your agents confirm what “receipts” currently mean in code.