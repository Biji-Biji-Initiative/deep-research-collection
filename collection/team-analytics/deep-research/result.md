# Repository Audit of Agent Instructions for team-analytics Against agents-standards

## Executive Summary

As of March 9, 2026, **Biji-Biji-Initiative/team-analytics is not aligned with the org's blueprint-driven agent-instruction operating model**: it currently has **no root `AGENTS.md` and no `.ai/blueprint.yaml`**, while most "universal" guidance lives in an **extremely large `CLAUDE.md`** and a **Copilot file that points to `CLAUDE.md`** as the context source. This inverts the standards model where **`AGENTS.md` is the universal baseline**, **adapters are thin/generated**, and **`CLAUDE.md` is minimal and Claude-specific.** The biggest blockers are (1) **missing blueprint source-of-truth**, (2) **missing `AGENTS.md` baseline + linter compliance**, and (3) **high drift risk from hand-maintained, tool-specific instruction sprawl and deeply operational content living in the wrong file.**

## Current State in team-analytics

### Instruction file inventory found in-scope

Within `team-analytics`, the following instruction-related files are present and materially serving "agent instruction" roles:

- **`CLAUDE.md` (repo root)**: currently acts as the *primary* instruction corpus, covering overview, commands, architecture, specs references, deployment, and detailed development guidelines.
- **`.github/copilot-instructions.md`**: a short file, but it explicitly directs the user/agent to use `CLAUDE.md` for full context (i.e., Copilot depends on Claude-specific doc as the de facto source of truth).
- **`README.md`**: includes "Quick Start", "Project Structure", "Testing", "Deployment" pointers, and references to `CLAUDE.md`. This is human-facing but also agent-useful.
- **`specs/README.md`**: strong spec index and progressive-disclosure structure; frequently referenced by `CLAUDE.md`.

Files explicitly requested by scope that are **absent** in current default branch:

- **`AGENTS.md` / `agents.md`**: **not present** at repo root (confirmed by direct lookup attempts) and thus cannot serve as universal baseline today. (Discrepancy noted below.)
- **`.ai/blueprint.yaml`**: **not present**.
- **`GEMINI.md`**: **not present**.
- **`.cursor/rules/*`**: **not present**.

### Does team-analytics currently have a valid AGENTS.md?

**No, not currently.** The repo's instruction architecture is effectively:

- **Source-of-truth today (de facto):** `CLAUDE.md` + supporting human docs (`README.md`, `specs/*`).
- **Copilot adapter:** points to `CLAUDE.md` rather than to a universal baseline (`AGENTS.md`).

#### Discrepancy flagged: audits indicate AGENTS.md existed recently

The **agents-standards org audit report dated 2026-03-05** includes an entry for `team-analytics` (implying the audit observed an `AGENTS.md` at that time), but the current repo state (March 9, 2026) does not surface a root `AGENTS.md`. This strongly suggests **the file was deleted or moved after the audit run**, or the repo default branch changed relative to the audit target. Treat this as a **high-confidence drift event** requiring reconciliation.

### Practical quality assessment of current instruction architecture

`team-analytics` has high *volume* and high *specificity* of guidance (good for productivity), but the **packaging is incompatible with the standard model** and creates tool fragmentation:

- `CLAUDE.md` contains broad, universal guidance (commands, structure, conventions) *plus* deep operational detail—so it is not "Claude-only."
- `.github/copilot-instructions.md` is not a thin "adapter" to a universal baseline; it is a pointer to the Claude document.
- Blueprint-driven generation, lintability, and "always/ask/never" boundary governance are not implemented.

### Current scoring

These scores are aligned to the governance intent implied by the org tools (linter + blueprint model). `1 = poor`, `5 = excellent`.

| Dimension | Score | Rationale |
|---|---:|---|
| Clarity | 4 | `CLAUDE.md` is detailed and actionable; `README.md` + specs index are structured. |
| Enforceability | 1 | No blueprint, no enforced linter workflow, no "generated outputs only" discipline. |
| Completeness | 3 | Commands/architecture/spec references exist, but boundaries model and cross-tool adapters are missing/misaligned. |
| Security | 3 | No obvious hardcoded secrets in instruction files, but operational detail is extensive and should be located in runbooks/specs rather than universal agent instructions. (Lint policy explicitly checks for potential secrets patterns.) |
| Parsability | 2 | Large monolithic `CLAUDE.md` is hard to parse; lacks the standardized sections the linter expects for `AGENTS.md`. |
| Maintenance | 2 | High drift risk: hand-maintained, tool-specific files without blueprint regeneration; audit discrepancy suggests recent change. |
| Signal-to-noise | 2 | Lots of helpful detail, but too much belongs in specs/docs/runbooks rather than top-level agent instructions. |

Adoption readiness (standards migration):

- **Universal-tool compatibility:** Low (no `AGENTS.md`; Copilot points to Claude doc).
- **Blueprint readiness:** Low (no `.ai/blueprint.yaml`).
- **Drift risk:** High (hand-maintained instructions + recent audit mismatch).
- **Ease of migration:** Medium (content exists; mostly needs refactoring into the standardized architecture).

## Standards Baseline from agents-standards

### Intended operating model

The normative model in `agents-standards` is explicitly **blueprint-driven**:

- **Blueprint is source of truth** (`.ai/blueprint.yaml` in target repo).
- A generator compiles blueprint → **`AGENTS.md` + `CLAUDE.md` + adapters** (Copilot, Gemini, Cursor).
- Output targets: **`AGENTS.md` ~90–150 lines**, **`CLAUDE.md` ~15–30 lines**, adapters ~15–25 lines.
- Principle: **progressive disclosure**—keep root instruction files short, push deep detail into contextual docs.
- The rollout tracker explicitly lists `team-analytics` as **TODO** and recommends using the **service archetype**.

### Lint rubric (enforced structure)

The org linter defines a **lintable structure** for `AGENTS.md`:

- Must have a top-level heading (acts as Overview) and sections matching: **Commands, Structure, Conventions, Boundaries**.
- Optional recommended sections: **Validation**, **Deployment**.
- **Line count**: target ≤150, acceptable ≤300; above 300 fails.
- Must include a **"Last updated"** date.
- Boundaries should use a **3-tier model** (Always / Ask First / Never).
- Checks for possible hardcoded secrets, and expects fenced code blocks for commands.

### Cross-tool compatibility and layered architecture

Two relevant proposals (both marked **Draft**, so treat as directional but not yet fully "operational law"):

- **Proposal 001 (Layered Instruction Architecture):** recommends keeping project `AGENTS.md` slim (100–150 lines) and pushing deep procedures into "skills/on-demand docs"; also defines layers for org/category/project/subdir instructions.
- **Proposal 003 (Cross-tool Compatibility):** recommends **AGENTS.md as universal** and **generated thin adapters** for Copilot/Gemini/Cursor; `CLAUDE.md` should become minimal and tool-specific.

### Practical blueprint template to start from

The **service archetype example** shows the canonical blueprint fields to populate: `commands`, `structure`, `conventions`, `boundaries`, `context_files`, tool toggles, and `last_updated`.

## What's Good

`team-analytics` already contains strong raw material that is worth preserving and re-homing into the correct layers:

The repo has a **high-quality documentation topology for progressive disclosure**: `README.md` provides a concise overview + quick start and then points to more detailed docs/specs, while `specs/README.md` is a well-structured index into domain specs (core/data/quality/ops/ui/etc.). This is extremely compatible with the standards principle of keeping root instruction files short while linking to deeper truth sources.

There is already a consistent **"Specs vs Docs" convention** called out in the Copilot instructions, including normative RFC2119 language and acceptance criteria patterns. This is valuable content to uplift into the universal baseline and blueprint conventions.

The project also has strong **operational maturity signals** in documentation (explicit test commands, dashboard vs pipeline split, deployment pointers). Even if these appear in the wrong file today (`CLAUDE.md`), the depth indicates you have the real knowledge; the migration is mainly about **repackaging and governance**, not inventing content from scratch.

## Gap Analysis

The table below compares the org standard vs current repo state and gives an implementation-ready fix with "owner artifact."

| Standard expectation | Current state in team-analytics | Evidence | Why it matters | Severity | Recommended fix | Owner artifact |
|---|---|---|---|---|---|---|
| Blueprint is source of truth (`.ai/blueprint.yaml`) | Missing | No `.ai/blueprint.yaml` present; team-analytics listed "TODO" in rollout tracker | Without blueprint, you cannot generate, lint, or prevent drift across tool adapters | Critical | Add `.ai/blueprint.yaml` using service archetype; populate commands/structure/boundaries | `.ai/blueprint.yaml` |
| `AGENTS.md` exists and is universal baseline | Missing today | Org model expects `AGENTS.md` as universal; repo currently relies on `CLAUDE.md` and Copilot points to it | Tool-agnostic baseline is required for cross-tool consistency and lintability | Critical | Generate `AGENTS.md` from blueprint; keep it ≤150 lines with required sections | `AGENTS.md` (generated) |
| `CLAUDE.md` is minimal and Claude-specific | `CLAUDE.md` is large and contains universal + operational content | Standards target ~15–30 lines; current `CLAUDE.md` is being used as "full project context" | Creates inversion: Claude doc becomes universal baseline; other tools can't reliably consume it | High | Reduce `CLAUDE.md` to Claude-only (imports/skills/hooks), move universal content to `AGENTS.md`, and deep ops to specs/runbook | `CLAUDE.md` (generated/minimal) + docs migration |
| Copilot instructions are thin/generated adapters pointing to AGENTS | Copilot file points to `CLAUDE.md` | "Full project context: See `CLAUDE.md`" | Copilot adapter should not depend on Claude-specific file; should be consistent across tools | High | Generate `.github/copilot-instructions.md` from blueprint/AGENTS; include "AUTO-GENERATED" header | `.github/copilot-instructions.md` (generated) |
| Lintable structure in `AGENTS.md` (Commands/Structure/Conventions/Boundaries, last updated, code blocks) | Not applicable currently (no AGENTS); CLAUDE does not map cleanly to rubric | Linter requires specific section structure and last-updated marker | Without lint compliance, governance cannot enforce quality and consistency | Critical | Create `AGENTS.md` with required sections + 3-tier boundaries and "Last updated" | `AGENTS.md` + CI lint job |
| Progressive disclosure: keep root instruction files short | Root instruction corpus is concentrated in large `CLAUDE.md` | Principle is explicit in standards materials | Long files waste context windows and increase drift; deep procedures belong in specs/runbooks | High | Summarize to essentials in `AGENTS.md`; link to `specs/README.md` / runbook for depth | `AGENTS.md` + keep specs as truth |
| Cross-tool adapters exist (Gemini/Cursor) | Missing today | Standards list generated GEMINI/Cursor outputs | Users on other tools lose guidance consistency; org strategy assumes adapters exist | Medium | Enable blueprint tool toggles and generate `GEMINI.md` and optional `.cursor/rules/project.mdc` | `GEMINI.md`, `.cursor/rules/project.mdc` (generated) |
| Governance: drift detection CI | Not present in repo | TODO proposes drift detection phase; standards governance plane assumes audits/linters | Prevents hand-edits to generated docs and keeps adapters in sync | Medium–High | Add CI workflow: regenerate from blueprint + `git diff --exit-code`; lint AGENTS | `.github/workflows/*` in team-analytics |
| Audit reconciliation: historical audit vs current state | Audit from 2026-03-05 suggests AGENTS existed; now absent | Audit report exists; mismatch indicates drift | This is a process smell and undermines trust in instruction governance | Medium | Identify commit/PR removing AGENTS; decide whether removal was intentional; restore via blueprint | Audit notes + PR history review |
| Stale/risky instruction artifacts removed or clearly quarantined | Potential deprecated guidance may exist outside the standard toolchain | Layering proposal suggests on-demand skills, not lingering deprecated instruction artifacts | Stale docs mislead agents and humans; increases production risk | Medium | Move deprecated guidance into `/docs/archive/` or delete; annotate with status | docs cleanup PR (optional) |

## What Needs To Be Done

The immediate objective is to **re-establish the standards "spine"** (blueprint → generated `AGENTS.md` → generated adapters → minimal `CLAUDE.md`) while preserving existing knowledge by relocating it to specs/docs.

First, **create `.ai/blueprint.yaml` for team-analytics using the service archetype** and populate it with the real commands, structure, conventions, and boundaries already present across `README.md`, `CLAUDE.md`, and `specs/README.md`. This is explicitly the recommended path in the standards quick start and contributing workflow.

Second, **generate and commit** the following outputs: `AGENTS.md` (universal), minimal `CLAUDE.md` (Claude only), and generated `.github/copilot-instructions.md` (adapter). The current Copilot file should stop pointing to `CLAUDE.md` as "full context" and instead be a thin adapter to `AGENTS.md`, consistent with the cross-tool proposal.

Third, ensure `AGENTS.md` passes the org linter rubric (required sections, last-updated, ≤150 target lines, 3-tier boundaries). This is the minimum for governance and future audits.

Fourth, **refactor the current `CLAUDE.md`**: keep only Claude-specific configuration and move deep operational runbooks into `specs/operations/*` (which already exists as a home for that level of detail). Then, the universal baseline stays small and tool-agnostic.

## Improvement Plan

### PR one (immediate fixes)

Goal: restore standards-compliant "instruction architecture" in one PR without breaking developer workflows.

Create `.ai/blueprint.yaml` for team-analytics using the service archetype and **copy over only the essential, cross-tool content**:

- Commands: install/test/lint/build for Python pipeline and `apps/dashboard` (pnpm), plus common Temporal CLI entrypoints (as in README/CLAUDE today).
- Structure: top-level directories (`lib/`, `temporal/`, `apps/dashboard/`, `scripts/postgres/`, `specs/`, `k8s/`).
- Conventions: "Specs vs Docs", normative language (RFC2119), acceptance criteria IDs; plus a small set of repo-specific coding conventions.
- Boundaries: Always/Ask First/Never designed for this repo (see Suggested AGENTS outline below).
- Context files: include `specs/README.md` and the most important operational specs (deployment/runbook/lifecycle) so tools can discover them without bloating the baseline.

Run the generator from `agents-standards` to produce and commit:

- `AGENTS.md` (universal baseline), linted to match the rubric and line count targets.
- Minimal `CLAUDE.md` (Claude-specific only).
- Generated `.github/copilot-instructions.md` (thin adapter). Replace the current manual one that points to `CLAUDE.md`.
- Optionally generate `GEMINI.md` and `.cursor/rules/project.mdc` if this repo is used with those tools (standards support generating them).

Refactor the existing large `CLAUDE.md` content:

- Move deep operational sections into `specs/operations/*` or `/docs/` where appropriate (many already exist).
- Keep `README.md` and `specs/README.md` as the stable progressive-disclosure entry points.

### PR two (structural standardization)

Goal: reduce context load, improve modularity, and support monorepo-like subareas cleanly.

Introduce **subdirectory `AGENTS.md`** files if needed (optional, but recommended by the layered architecture draft for complex repos). Example: create `apps/dashboard/AGENTS.md` to contain Next.js/pnpm/UI conventions and keep root `AGENTS.md` focused on repo-wide invariants.

Ensure adapters across tools remain consistent:

- Generated adapters only; no hand edits.
- If Cursor/Gemini are relevant, keep them generated and committed.

### PR three (governance, CI, drift prevention)

Goal: make the architecture self-enforcing.

Add CI checks to team-analytics:

- **Lint check:** run `audit/lint-agents-md.sh AGENTS.md` (from agents-standards) and enforce pass.
- **Drift check:** regenerate from `.ai/blueprint.yaml` and fail if `git diff` is non-empty. This matches the direction in the cross-tool proposal and TODO "Phase 3: CI Drift Detection."

Reconcile audit discrepancy:

- Identify the PR/commit that removed `AGENTS.md` after the 2026-03-05 audit and document the rationale in that PR thread (or in a short `docs/adr/agent-instructions.md`).

## Proposed Target File Layout

Target layout after Phase 2 (with optional dashboard subinstructions):

```text
team-analytics/
├─ .ai/
│  └─ blueprint.yaml                 # Source of truth (hand-maintained)
├─ AGENTS.md                         # Generated universal baseline (≤150 lines)
├─ CLAUDE.md                         # Generated Claude-only (minimal)
├─ GEMINI.md                         # Generated (optional)
├─ .cursor/
│  └─ rules/
│     └─ project.mdc                 # Generated (optional)
├─ .github/
│  └─ copilot-instructions.md        # Generated adapter (thin)
├─ apps/
│  └─ dashboard/
│     ├─ AGENTS.md                   # Optional: dashboard-specific guidance
│     └─ ...
├─ specs/
│  ├─ README.md                      # Spec index (already strong)
│  └─ ...
└─ docs/
   └─ ...                            # Human docs, ADRs, reviews, etc.
```

This matches the standards "What Gets Generated" and "Key Principles" (blueprint source-of-truth; generated baseline + adapters; progressive disclosure).

## Suggested AGENTS.md Outline

Target: **120–150 lines**, fully lint-compliant (Overview + Commands + Structure + Conventions + Boundaries + optional Validation/Deployment) per the org linter.

Suggested outline (and what to pull from existing files):

**Overview**
- One-paragraph description of team-analytics purpose and the main runtime shape: "Temporal (Python) → PostgreSQL → Next.js dashboard."
- Link to `README.md` and `specs/README.md` as progressive-disclosure anchors.

**Commands**
- Python: `pytest`, `ruff check` (from existing guidance).
- Dashboard: `cd apps/dashboard`, `pnpm install`, `pnpm dev`, `pnpm build`, `pnpm lint` (from existing guidance).
- Minimal Temporal CLI commands: `python -m temporal.cli smoke|collect|status|cancel|result` (keep short; link to `specs/operations/temporal-pipeline.md` for details).

**Structure**
- Bullet-light directory map: `lib/`, `temporal/`, `apps/dashboard/`, `scripts/postgres/`, `specs/`, `k8s/`.
- If adding `apps/dashboard/AGENTS.md`, keep only a pointer here.

**Conventions**
- Promote what is already good from Copilot instructions:
  - Specs (`specs/`) = testable contracts ("WHAT MUST BE TRUE")
  - Docs (`docs/`) = explanatory ("WHAT IS / HOW TO USE")
  - Use RFC2119 normative terms in specs
  - Acceptance criteria IDs (`AC-001`, `AC-002`) and verification mapping
- Add a small number of repo-specific code conventions (example types: "no hardcoded SQL string interpolation," "prefer existing patterns in adjacent modules"). Keep this short.

**Boundaries**
- Use the linter's implied 3-tier model (Always / Ask First / Never).
- Suggested content (example, customize to team norms):
  - Always: run tests/lint before PR; keep specs updated when changing contracts; prefer incremental refactors.
  - Ask First: changes to PostgreSQL schema baseline/migrations; changes to Temporal workflow semantics; changes to dashboard public APIs/routes; modifications to K8s manifests.
  - Never: hardcode secrets/tokens; bypass parameterization in SQL; push directly to main; introduce breaking schema changes without migration + spec update.

**Validation** (optional but recommended)
- One short paragraph + code block listing the minimal "pre-commit" checks (`pytest`, `ruff`, dashboard lint/build).

**Deployment** (optional but recommended)
- Keep it to *pointers* only: link to `specs/operations/deployment.md` and `specs/operations/runbook.md` rather than embedding runbook steps in AGENTS.

**Last updated**
- Required by linter.

## Suggested CLAUDE.md Outline

Target: **~15–30 lines**; Claude-only configuration and behavior overrides, consistent with the standards "generated CLAUDE.md is minimal" model.

Suggested outline:

**Claude Code Notes**
- "This file is Claude-specific. For repo instructions, see `AGENTS.md`."
- If you use Claude Code imports, list the small set of `context_files` Claude should load by default (e.g., `specs/README.md`, `specs/operations/runbook.md`).
- If you use Claude "skills/rules/hooks", reference them explicitly (only if they exist and are maintained).
- Keep *all* build/test/structure/conventions/boundaries out of this file (those belong in `AGENTS.md`).

## Risks / Open Questions

The biggest risk is **governance ambiguity caused by the recent audit mismatch**: `agents-standards` reports imply `AGENTS.md` existed for team-analytics on 2026-03-05, but it does not exist now. This must be resolved (deleted vs moved vs branch mismatch) to restore confidence in the instruction system.

Another risk is **over-correcting by dumping all the `CLAUDE.md` content into `AGENTS.md`**. The linter and standards explicitly target short files and progressive disclosure; the correct move is to keep `AGENTS.md` concise and link to existing specs/runbooks.

Open questions that affect blueprint specifics:

- Should `team-analytics` be treated as a "service" blueprint (recommended by standards tracker) or a "monorepo" blueprint because it includes a substantial Next.js app? The standards TODO currently labels it a **service** and suggests service archetype, but a subdirectory `apps/dashboard/AGENTS.md` may be the best compromise.
- Are Gemini and Cursor officially used by this repo's contributors? If yes, enable those adapter outputs via blueprint tool toggles; if not, keep them off initially and add later.

---

## Summary Recommendations

**Minimum viable PR recommendation:** One PR that adds `.ai/blueprint.yaml`, generates `AGENTS.md` + minimal `CLAUDE.md` + generated `.github/copilot-instructions.md`, and updates any references so Copilot/adapters point to `AGENTS.md` (not `CLAUDE.md`).

**Gold standard end state recommendation:** Blueprint-driven repo with short, lint-compliant `AGENTS.md`, minimal Claude-only `CLAUDE.md`, generated adapters for every supported tool (Copilot/Gemini/Cursor), and CI drift detection that regenerates from blueprint and fails on diff.

**Verdict: Red** for team-analytics readiness (missing blueprint + missing `AGENTS.md` baseline + tool-adapter inversion).
