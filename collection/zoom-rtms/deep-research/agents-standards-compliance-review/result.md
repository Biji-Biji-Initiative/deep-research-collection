# Deep comparative review of `zoom-rtms` agent instructions against `agents-standards`

**Research Topic**: agents-standards-compliance-review
**Date Conducted**: 2026-03-09
**Date Completed**: 2026-03-09

## Executive summary

`zoom-rtms` has **strong operational delivery constraints** (PR-only to `main`, automation-first promotion, explicit stop conditions, required PR metadata), but its **root `AGENTS.md` is not compliant with the org's current standards model**: it fails the required "Commands / Structure / Boundaries / Last updated" expectations and is therefore scored low by the org audit tooling.

At the same time, the repo contains a **very detailed `CLAUDE.md`** that carries many of the missing "how to build / run / validate / structure" instructions, which helps Claude Code specifically but conflicts with the standards direction (universal content should live in generated `AGENTS.md`, while `CLAUDE.md` should be thin and tool-specific).

The recommended path is to **adopt `.ai/blueprint.yaml` using the `service` archetype**, migrate the essential universal content out of `CLAUDE.md`/other docs into generated outputs, and add **lint + drift prevention** to keep outputs aligned over time. This aligns with the explicit rollout tracker entry for `zoom-rtms` and the platform's "single source of truth" design.

## Evidence table

| Standard / expectation (agents-standards) | Current state in zoom-rtms | Evidence | Gap severity | Recommendation |
|---|---|---|---|---|
| Blueprint-driven workflow: `.ai/blueprint.yaml` is the source of truth; outputs are generated. | No `.ai/blueprint.yaml` in repo (404 when fetched); existing instructions appear hand-maintained across multiple files. | Standards "Quick Start" and "Key Principles" describe blueprint -> generated outputs. Contributing explicitly says "don't write AGENTS.md by hand." | High | Add `.ai/blueprint.yaml` and generate `AGENTS.md` + adapters from it. Avoid future hand-edits of generated files. |
| Required sections in `AGENTS.md`: Overview (H1), Commands, Structure, Conventions, Boundaries. | Root `AGENTS.md` is delivery-policy heavy and missing the required Commands/Structure/Boundaries headings in the expected format. | Linter defines required sections. Org audit flags `zoom-rtms` missing "Commands, Structure, Boundaries." | High | Ensure generated `AGENTS.md` includes all required sections (tier-1, <=150 lines). |
| Boundaries format: Always / Ask First / Never (3-tier). | Root `AGENTS.md` has "Stop conditions" and "Delivery model" but not Always/Ask/Never boundaries (and linter will treat it as missing). | Boundaries model is documented in core fragment and linter checks for boundaries. | High | Add explicit boundaries to blueprint (`boundaries.always/ask_first/never`) so generator emits the proper section. |
| "Last updated" date required by lint and audit rubric. | Root `AGENTS.md` has no "Last updated" date. | Linter checks "Last updated" line. | High | Add `last_updated:` in blueprint; generator will emit footer. |
| Line count target: keep root `AGENTS.md` short (typically <=150; platform expects ~90-150). | Root `AGENTS.md` is short (39 lines), but short **because it omits required operational content**. | Platform states `AGENTS.md` ~90-150 lines. Linter targets <=150. Org audit shows 39 lines. | Medium | Expand `AGENTS.md` to "thin but complete" (commands/structure/conventions/boundaries) while staying <=150 lines via progressive disclosure pointers. |
| Multi-tool output: generate `AGENTS.md`, `CLAUDE.md`, Copilot, Gemini, Cursor adapters from one blueprint. | Repo has `CLAUDE.md`, but no Copilot/Gemini/Cursor adapters; `CLAUDE.md` contains a lot of universal content that standards want in `AGENTS.md`. | Platform lists generated outputs from one blueprint. Generator supports those outputs. Cross-tool strategy proposal reinforces "single source, generated adapters." | High | Turn on `tools.copilot/gemini/cursor` as needed and generate adapters; shrink `CLAUDE.md` to tool-specific. |
| Repo is in-scope and should use `service.yaml` archetype. | `zoom-rtms` is explicitly listed as "TODO" in the rollout tracker and tagged as a `service` using `service.yaml`. | Rollout tracker row: `zoom-rtms | service | ... | Use service.yaml archetype`. | High | Start from `blueprints/examples/service.yaml`, customize for zoom-rtms, then generate outputs. |
| Progressive disclosure: keep "always loaded" instructions short; move deep operational detail to linked docs/skills. | Root `AGENTS.md` is thin; however `CLAUDE.md` is extremely comprehensive and will likely exceed recommended "startup context" budgets. | Progressive disclosure proposal spells out Tier 1/Tier 2/Tier 3 model. `zoom-rtms` has many deep docs (e.g., deployment standard, contributing guide) suitable for Tier 3 references. | Medium | Keep root `AGENTS.md` "thin but complete"; point to `docs/*` for deeper runbooks/specs; optionally add directory-scoped `AGENTS.md` later. |

## What's already good in `zoom-rtms`

The strongest aspect of the current root `AGENTS.md` is that it encodes **enforceable delivery guardrails**: PR-only to `main`, `main` as release trigger, "don't manually edit GitOps env branches" for routine releases, plus a clear stop condition when `main` CI is red. These are exactly the kinds of policy constraints that prevent risky agent behavior in production pipelines.

The repo also has a detailed, operationally grounded documentation ecosystem that can support progressive disclosure well: a deployment standard describing immutable artifact promotion and PR-based GitOps promotion rails, and a contributing guide spelling out TypeScript/Biome/Vitest standards and PR metadata requirements.

Although it is not aligned with the standards "thin `CLAUDE.md`" goal, the existing `CLAUDE.md` demonstrates that the team has already captured much of what agents need to succeed: concrete npm commands, repo structure and module map, and hard safety rules (e.g., the "React Compiler is mandatory" constraint).

Finally, there is an archived `.archive/AGENTS.md` that contains classic "agent onboarding" content (structure, commands, testing, coding style, security tips). Even though it is outdated in path details, it's still a valuable recovery source for *topics* that belong in Tier-1 `AGENTS.md`.

## Gap analysis

The gaps fall into four main buckets: missing content, misplaced content, governance/process gaps, and tooling/automation gaps.

### Missing Content

The standards platform and linter require `AGENTS.md` to include Commands, Structure, Conventions, and Boundaries (Always/Ask/Never) plus a "Last updated" date and (ideally) fenced code blocks for commands. In the org-wide audit report dated 2026-03-05, `zoom-rtms` is explicitly graded `C` (13/21) and flagged as missing Commands, Structure, and Boundaries. This aligns with the repo's current root `AGENTS.md` focus on delivery/PR policy rather than build/run/validate guidance.

### Misplaced Content

Much of what *should* be universal Tier-1 guidance (commands, structure, conventions, boundaries) lives in tool-specific and human docs rather than the universal `AGENTS.md`. In particular, `zoom-rtms`'s `CLAUDE.md` contains extensive commands, architecture, test strategy, and operational policies. Meanwhile, the standards platform's explicit design is: universal content lives in `AGENTS.md`, and `CLAUDE.md` should be generated and kept thin, pointing back to `AGENTS.md`. This mismatch matters because non-Claude tools that only read `AGENTS.md` will be under-instructed, while Claude Code may be over-loaded.

### Governance/Process Gaps

`zoom-rtms` is not yet on the "one blueprint per repo -> generate outputs" model. The standards repo explicitly positions `.ai/blueprint.yaml` as the source of truth and says not to hand-edit generated outputs. `zoom-rtms` currently has no `.ai/blueprint.yaml` and therefore cannot participate in the platform's standard linting and drift controls.

### Tooling/Automation Gaps

The standards platform is built to generate multiple tool adapters (Copilot, Gemini, Cursor) from the same blueprint. `zoom-rtms` currently appears to have only `CLAUDE.md` and no generated adapter files, meaning cross-tool instruction consistency is not guaranteed.

### Audit discrepancy to note

There is a notable disagreement inside `agents-standards` reporting: the org-wide report produced by `audit-org.sh` scores `zoom-rtms` as **13/21 (C)** with missing Commands/Structure/Boundaries, but an "Internal AGENTS.md Audit Report" (same date) lists `zoom-rtms` as **18/21 (A-)** with "Completeness (ultra-minimal)" as the weakest dimension.

The most plausible explanation is that the two reports were run against **different evaluation sets or different snapshots** (the internal report states it covered "12 AGENTS.md files across ... repos on VPS," which may reflect a different repository subset or earlier file variant), while the org audit script is directly coupled to the linter-enforced section detection and matches the current `zoom-rtms/AGENTS.md` structure.

## Prioritized improvement plan

### Phase 1: Immediate fixes

**Goal**: Get `zoom-rtms` to a standards-aligned baseline quickly (complete Tier-1 `AGENTS.md`, correct boundaries format, add date), without losing the current delivery safety rails.

**Actions**:
- Create `.ai/blueprint.yaml` using the `service` archetype starter and fill the mandatory fields (`name`, `type`, `stack`, `fragments`) plus project-specific `commands`, `structure`, `conventions`, `boundaries`, and `context_files`. This follows the prescribed workflow in the standards README and contributing guide.
- Generate `AGENTS.md` and a thin `CLAUDE.md` using the generator script, then run the single-file linter against the generated `AGENTS.md` and ensure it passes with zero failures.

**Owner role**: RTMS repo maintainer (with Platform Engineering review)

**Effort**: M

**Expected impact**: `zoom-rtms` upgrades from the org-audit "C / missing Commands/Structure/Boundaries" baseline to a "B+/A" profile, while preserving current release safety constraints as explicit boundaries.

### Phase 2: Blueprint adoption and content rebalancing

**Goal**: Align repository guidance with the standards "progressive disclosure" and "layered architecture" intent: **complete but thin** root `AGENTS.md`, with deeper detail in referenced docs (Tier 3), and tool-specific content in tool-specific files.

**Actions**:
- Move universal instructions currently living in `CLAUDE.md` (commands, structure, general testing conventions) into the blueprint so they appear in generated `AGENTS.md`. Trim `CLAUDE.md` down to tool-specific only (skills/imports/rules), consistent with generator output expectations.
- Keep the most critical "hard rules" (example: do not disable dashboard React Compiler) as universal Conventions/Boundaries, since those are repo truths rather than Claude-only preferences.
- Point Tier-1 `AGENTS.md` to Tier-3 docs that already exist (deployment standard, contributing guide, architecture/runbooks) via `context_files`.

**Owner role**: RTMS maintainer + Documentation owner

**Effort**: M

**Expected impact**: Agents in *any* tool gain the "minimum viable repo mastery" from `AGENTS.md`, while deep ops detail remains accessible without bloating startup context (progressive disclosure).

### Phase 3: Generated multi-tool outputs

**Goal**: Remove instruction drift risk across tools by generating adapters.

**Actions**:
- Enable the relevant `tools.*` flags in `.ai/blueprint.yaml` (Copilot, Gemini, Cursor) if those tools are used by the team, then generate and commit the adapter files. This matches the platform's "What Gets Generated" and generator capabilities.
- Ensure generated adapters include the "do not edit" generated header, and that `CLAUDE.md` points to `AGENTS.md` for universal content (per generator design).

**Owner role**: RTMS maintainer

**Effort**: S-M

**Expected impact**: Better cross-tool consistency and easier future updates (edit blueprint once).

### Phase 4: CI lints and drift prevention

**Goal**: Prevent regressions where someone hand-edits generated files or lets them drift.

**Actions**:
- Add CI checks in `zoom-rtms` to (a) lint `AGENTS.md` using the standards linter and (b) regenerate outputs from `.ai/blueprint.yaml` and fail if the diff is non-empty. This directly matches the Phase 3 drift detection ideas in the standards rollout tracker.
- Optionally (later) incorporate the layered architecture separation rule (avoid duplicating org-level content inside project files) as that governance tooling matures.

**Owner role**: Platform Engineering + RTMS maintainer

**Effort**: M

**Expected impact**: Long-term maintainability and consistency; avoids a return to "hand-edited and stale" instruction drift.

## Proposed target state for `zoom-rtms`

The ideal end-state is a **standards-generated instruction set** anchored by `.ai/blueprint.yaml` and compiled into a short but complete root `AGENTS.md`.

### Target `AGENTS.md` shape

The target should follow the platform's baseline structure: **H1 overview + Commands + Structure + Conventions + Boundaries + More Detail + Last updated**, staying in the platform's expected ~90-150 line range and under the linter's <=150 target.

The repo-specific "delivery model / stop conditions / PR metadata requirements" that are currently strong in `zoom-rtms/AGENTS.md` should be preserved, but expressed inside the standards format (Conventions and Boundaries).

### `.ai/blueprint.yaml` recommendations

A new `.ai/blueprint.yaml` for `zoom-rtms` should use `type: service` (as specified by the rollout tracker). It should include stack fragments carefully: `zoom-rtms` uses npm today (per `package.json` scripts), while the existing `node-pnpm` stack fragment forbids npm/yarn; so either avoid `node-pnpm` until the repo migrates to pnpm, or treat this as a small standards gap to resolve separately.

Because `zoom-rtms` is deployed via GitOps/ArgoCD and has explicit "don't mutate GitOps env branches" rules, the `k8s-argocd` stack fragment is a high-fit inclusion.

### Archived content reincorporation

Archived content should be reincorporated **selectively**: the `.archive/AGENTS.md` is useful as a map of topics to restore (commands, structure, testing, security), but its concrete paths and implementation assumptions are outdated relative to the current TypeScript/Fastify structure.

## Draft implementation starter

### Suggested `.ai/blueprint.yaml` outline for `zoom-rtms`

```yaml
name: zoom-rtms
description: TypeScript/Fastify service that captures Zoom RTMS sessions, generates AI meeting summaries, and delivers outcomes to Slack and Google Drive.
type: service

# NOTE: Avoid node-pnpm until zoom-rtms actually uses pnpm, or add a node-npm stack to agents-standards.
stack:
  - k8s-argocd

fragments:
  - boundaries
  - git-workflow
  - validation
  - secrets

commands:
  install: npm install
  dev: npm run dev
  test: npm test
  lint: npm run lint
  build: npm run build
  deploy: "# main builds/publishes; infra promotion is PR-driven (see docs/DEPLOYMENT_STANDARD.md)"

structure:
  src/: backend (Fastify server, domain logic, integrations, pipeline)
  ui/: in-meeting Zoom App (Vite + React)
  dashboard/: ops dashboard (Next.js)
  scripts/: dev harness, doctor, smoke, ops tools
  packages/: workspace packages (core/contracts)
  test/: vitest suites
  docs/: documentation (runbooks, platform guide)
  specs/: specs / ADRs (deep detail)
  prompts/: prompt packs + schemas + policies
  transcripts/: local artifacts/state (gitignored)

conventions:
  - Use PRs to main; never push directly to main.
  - Follow PR metadata contract (Risk Class, Validation Evidence, Rollback Plan, Rollout Notes).
  - Use npm scripts (validate/test/lint) as the source of truth for local verification.
  - Keep webhook and deployment security checks enabled outside local dev.
  - Dashboard React Compiler must remain enabled (do not disable to "fix" builds).

boundaries:
  always:
    - Run npm run validate (or npm run typecheck + npm run lint) and npm test before merge.
    - Keep deliveries PR-based; let automation promote immutable digests.
    - Update docs when routes/config/integration contracts change.
  ask_first:
    - Any change to CI/workflows or release gates.
    - Any change to deployment/promotion rails or GitOps process.
    - Any change to auth/RBAC/security enforcement defaults.
  never:
    - Push directly to main.
    - Manually edit/push GitOps environment branches for routine releases.
    - Commit secrets or real tokens; keep .env files uncommitted.
    - Disable dashboard React Compiler.

context_files:
  - docs/DEPLOYMENT_STANDARD.md
  - docs/contributing/guide.md
  - docs/platform-guide/architecture.md
  - docs/platform-guide/configuration.md
  - docs/playbooks/troubleshooting.md

tools:
  agents_md: true
  claude_md: true
  copilot: true
  gemini: true
  cursor: true

claude:
  # Keep thin: only tool-specific extras, not universal repo mastery.
  imports:
    - docs/DEPLOYMENT_STANDARD.md
    - docs/platform-guide/architecture.md
  skills: []
  rules: []

last_updated: "2026-03-09"
```

### Proposed section outline for generated `AGENTS.md`

```markdown
<!-- GENERATED from .ai/blueprint.yaml - edit the blueprint, not this file -->

# zoom-rtms
(1-2 sentence description)

## Commands
```bash
install: ...
dev: ...
test: ...
lint: ...
build: ...
deploy: ...
```

## Structure
(top-level directory map)

## Conventions
(<=10 bullets)

## Boundaries
- Always: ...
- Ask First: ...
- Never: ...

## More Detail
- See `docs/DEPLOYMENT_STANDARD.md`
- See `docs/contributing/guide.md`
- See `docs/platform-guide/architecture.md`
- See `docs/platform-guide/configuration.md`
- See `docs/playbooks/troubleshooting.md`

---
Last updated: YYYY-MM-DD
```

### Checklist for the improvement PR in `zoom-rtms`

1. Add `.ai/blueprint.yaml` based on `blueprints/examples/service.yaml`.
2. Encode the current delivery model, stop conditions, and PR metadata requirements into Conventions/Boundaries so they remain first-class and enforceable.
3. Migrate the essential universal content from `CLAUDE.md`/docs into blueprint fields (Commands/Structure/Conventions/Boundaries) so it becomes tool-agnostic.
4. Run generator from `agents-standards/generator/build_instructions.py` and commit generated outputs.
5. Run `audit/lint-agents-md.sh` on the generated `AGENTS.md` and ensure it passes.
6. (Optional but recommended) Enable adapters (Copilot/Gemini/Cursor) in the blueprint if those tools are in use; commit the generated adapter files.
7. Add CI drift detection (regen + diff, plus lint) per the standards tracker guidance.

## References

- [agents-standards repository](https://github.com/mereka-io/agents-standards)
- [zoom-rtms repository](https://github.com/mereka-io/zoom-rtms)
- Org-wide audit report dated 2026-03-05
- Standards README - Quick Start and Key Principles
- Standards Contributing guide
- Cross-tool compatibility proposal
- Progressive disclosure proposal
