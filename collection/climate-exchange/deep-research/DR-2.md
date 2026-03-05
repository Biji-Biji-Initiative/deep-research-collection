# DR-2: Beads as a Control Plane (Graph Hygiene + Critical Path Unblocking)

## Audience

Maintainers and agents operating the Beads backlog as a dependency graph (not a flat TODO list).

## Prerequisites

- `br` installed and initialized for this repo
- Familiarity with Beads statuses/types/priorities and dependency edges
- Ability to run: `br stats`, `br dep tree`, `br dep cycles`, `make check-fast`

## How to Use

1. Treat every open bead as an executable contract:
   - explicit scope/non-goals
   - testable ACs with IDs
   - exact verification commands
2. Make blockers explicit using dependency edges (`blocks`, `parent-child`, `related`).
3. Keep history stable:
   - update existing beads when objective unchanged
   - reopen only when closure is false
   - create new beads only for true objective changes or splits

## Troubleshooting

- If Insights shows “empty” or NaN nodes: ensure dependency edges exist and export is regenerated.
- If robot triage recommends nonsense: audit statuses (blocked vs open) and missing `blocks` edges.
- If notes become unreadable: move long evidence to artifacts or external logs; keep notes short and normative.

## Change Log

| Date | Change |
|------|--------|
| 2026-02-15 | Initial DR-2 drafted: critical path guidance + bead hygiene rules |


## Core Principle: Preserve Node Identity

When refining scope, clarifying acceptance criteria, adjusting priority/status, or evolving implementation details **within the same objective**, update the existing bead.

Create a new bead only when the fundamental objective changes (architectural pivot, different problem statement, or split into independent units). In that case:
- close the original bead with a canonical close reason (e.g., `superseded-by:<id>`)
- add dependency edges to preserve graph continuity

## Critical Path Example: Unblocking the a11y Gate (`cie-162`)

`cie-162` becomes valuable only when its blockers are landed. The minimal intended unblock order:

1. `cie-2zl` (P0) Receipt/Evidence drawers accessible dialogs
2. `cie-2m9` (P0) Controllable streaming + ARIA status
3. `cie-23n` (P1) Visualization accessibility (captions + data table alternatives)
4. `cie-b12` (P1) Navigation + IA consistency

Recommendation: add a “Critical Path” line directly in `cie-162` referencing those 4 deps in order.

## Tightening “Verified Mode Is Not Theatre”

Three beads together define whether “verified” means anything end-to-end:

- `cie-1t7`: verified streaming gating (no final output before evidence verification)
- `cie-11v`: run replay contract test must be assertion-based (not print-based)
- `cie-3gz`: health/readiness must be truthful with real probes

For each, ensure:
- deterministic failure injection exists
- negative tests prove the system fails closed (not fail-after-final)
- the intended gate is explicitly named as release-blocking (PR-fast vs nightly-deep)

## Consolidate Error Contract Before UX Recovery Work

If UI recovery flows depend on a stable error envelope, define one canonical envelope and enforce it:

- `cie-b09` should require the same error envelope across Chat, Tools runner, Run load/replay endpoints.
- Ensure `debug_id` is present and propagated as a correlation key in server logs.

This prevents multiple “almost the same” error shapes that drift over time.

## Receipts: Key Policy + Audit-Grade Provenance

Two beads control auditability:

- `cie-27b`: key policy by environment (no dev fallback in certified contexts)
- `cie-1c3`: provenance fields end-to-end (dataset identity + license + pin IDs where applicable)

For “world-class,” both need:
- explicit fail-closed error codes
- at least one negative runtime test proving refusal when required provenance/policy is missing

## Backlog Hygiene Rules That Pay Off Immediately

- **No open children under closed parents** (graph invariant).
- Keep `notes` short; store long evidence in artifacts/log files and link them.
- Normalize `close_reason` vocabulary:
  - `implemented`, `done-docs`, `superseded-by:<id>`, `wontfix`, `duplicate`

## Recommended Work Sequencing (Minimize Rework)

1. Specs/contract: `cie-b09`
2. Runtime truth: `cie-11v`, `cie-3gz`, `cie-1t7`
3. UX primitives: `cie-2zl`, `cie-2m9`
4. Viz a11y + nav: `cie-23n`, `cie-b12`
5. Gate: `cie-162`
6. UX recovery: `cie-19o`
