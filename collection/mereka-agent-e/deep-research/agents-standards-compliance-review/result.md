# Repo-standardization review for Biji-Biji-Initiative/mereka-agent-e

**Research Topic**: agents-standards-compliance-review
**Date Conducted**: 2026-03-09
**Date Completed**: 2026-03-09

## Executive summary

`Biji-Biji-Initiative/mereka-agent-e` currently appears to be a **placeholder repo** with a single "Initial commit" that adds only `README.md` and `.gitignore`, and **no agent instruction artifacts** (no `AGENTS.md`, `CLAUDE.md`, `.ai/blueprint.yaml`, or tool adapters).

The organization's standard (from `Biji-Biji-Initiative/agents-standards`) is a **blueprint-first instruction platform** where `.ai/blueprint.yaml` is the source of truth and instructions are generated (not hand-written) for multiple tools (`AGENTS.md`, `CLAUDE.md`, and optional adapters for Copilot/Gemini/Cursor). The associated linter (`lint-agents-md.sh`) enforces the presence of core sections—Overview (H1), Commands, Structure, Conventions, Boundaries—plus quality signals like date, <=150-line target, and "no secrets"; it also recommends optional Validation/Deployment sections.

Because `mereka-agent-e` has **no codebase structure, scripts, CI, or deploy manifests yet**, the critical "repo-specific" parts of an `AGENTS.md` (real commands, concrete structure, enforceable conventions) cannot be accurately populated today without placeholders. This is a governance decision point: **either** (a) treat it as "not yet active / out of scope" until real development begins, **or** (b) onboard now with a minimal blueprint and generated files that clearly indicate commands/structure are placeholders and must be updated when code lands. The improvement plan below supports both paths, but prioritizes confirming scope first (since the standards repo explicitly limits rollout to a defined set of active repos).

## Repo current state

### Instruction-file inventory

The repo's only commit (titled "Initial commit") shows exactly two files were added: `.gitignore` and `README.md`. No `AGENTS.md`-family files appear in the commit file list, which strongly implies the repo has **no agent instruction files at any path** (root or subdirectories).

The repo README is a short placeholder stating: "This repo is dedicated for Agent E development."

### Repository type, stack, commands, structure

Because the repo contains only a README and a general-purpose `.gitignore`, there is not enough evidence to determine whether it is a service, monorepo, infra repo, or library from code layout; likewise, there are no package manager manifests (e.g., `package.json`, `pyproject.toml`, `requirements.txt`) or CI/deploy files to infer stack or runnable commands.

**Inference (explicitly labeled):** the `.gitignore` resembles a Python-oriented template (e.g., `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.pdm-*`) and includes Cursor ignore entries. This suggests Python tooling may have been considered, but it is not definitive because `.gitignore` templates are often copied wholesale regardless of actual stack.

### Cross-check against the org audit signal

The `agents-standards` repo includes an org-wide audit report dated **2026-03-05** that lists repos with "NO agent instructions," and that list includes `mereka-agent-e`.

Given `mereka-agent-e` has had no commits beyond the initial commit adding only README and `.gitignore`, this is consistent with the inventory findings.

## Standards baseline from Biji-Biji-Initiative/agents-standards

### Blueprint-first model and generated outputs

The standards repo defines a "repo-local blueprint" (`.ai/blueprint.yaml`) as the **source of truth** with a generator that produces:

- `AGENTS.md` (universal)
- `CLAUDE.md` (Claude-specific)
- `.github/copilot-instructions.md` (if enabled)
- `GEMINI.md` (if enabled)
- `.cursor/rules/project.mdc` (if enabled)

This is documented both in the platform description and implemented directly in `generator/build_instructions.py`.

The blueprint schema (`blueprints/schema.json`) requires (at minimum) `name`, `type`, `stack`, and `fragments`, and supports repo types including `service`, `monorepo`, `infra`, `docs-site`, `library`, and `forked`.

### Linter expectations for AGENTS.md

The linter script (`lint-agents-md.sh`) checks for:

- A top-level H1 (treated as "Overview")
- Sections for **Commands**, **Structure**, **Conventions**, **Boundaries**
- Optional but recommended sections for **Validation** and **Deployment**
- Line count target (<=150, warn <=300, fail >300)
- Presence of a "Last updated" date
- A 3-tier boundaries format detection (supports emoji or `Always:/Never:` and also bold markdown `**Always**:` / `**Never**:`)
- "No hardcoded secrets" heuristics
- Presence of fenced code blocks (warn if absent)

### Rollout governance and scope

The standards repo repeatedly emphasizes that the system is intended for **active repos**, with a defined rollout tracker and an explicit statement that "legacy/demo/experiment repos" are out of scope.

The current "In Scope" tracker lists 9 repos; `mereka-agent-e` is **not** included in that list.

## Gap analysis and findings

### Gap analysis table

| Standard element / expectation | What the standard expects | Current state in `mereka-agent-e` | Gap status |
|---|---|---|---|
| `AGENTS.md` exists | Generated universal instructions file | Not present; repo only has `.gitignore` + `README.md` | Missing |
| `CLAUDE.md` exists | Generated Claude adapter | Not present | Missing |
| `.ai/blueprint.yaml` exists | Source-of-truth, required by model | Not present | Missing |
| Tool adapters | Copilot/Gemini/Cursor adapters optionally generated | Not present | Missing |
| Generated vs hand-written | Files should be generated; generator adds a "GENERATED ... edit blueprint" header | No generated files exist yet; generator behavior defined in `agents-standards` | Missing |
| Required `AGENTS.md` sections | Overview(H1), Commands, Structure, Conventions, Boundaries | No `AGENTS.md`; therefore none can be satisfied | Missing |
| Optional sections | Validation, Deployment recommended | No `AGENTS.md` | Missing |
| Line-count target | ~90-150 lines (linter target <=150) | No `AGENTS.md` | Missing |
| Last-updated date | "Last updated" line required | No `AGENTS.md`; generator can add date | Missing |
| 3-tier boundaries | Always / Ask First / Never detection | No `AGENTS.md`; core `boundaries` fragment exists in standards | Missing |
| Real runnable commands | Commands should reflect actual repo dev loop | Cannot be derived today because repo has no build/test scaffolding | Blocked by missing codebase |
| Governance scope alignment | Focus on "in-scope" active repos | `mereka-agent-e` not listed in current in-scope tracker | Governance decision needed |

### What is already good

The repo is small and has not accumulated ad-hoc instruction files or duplicated "org-level" guidance, which avoids the cleanup and de-duplication work that the standards repo is explicitly trying to prevent.

The presence of a `.gitignore` (even if template-derived) suggests early baseline hygiene (not committing common environment/bytecode artifacts).

### What is missing and what needs to be done

The repo is missing every artifact required for standards compliance:

- Blueprint source-of-truth `.ai/blueprint.yaml` (required by the platform model and schema).
- Generated universal and tool-specific instructions (`AGENTS.md`, `CLAUDE.md`, optional adapters).
- Concrete repo-specific content (commands, structure, conventions) that the linter expects.

Additionally, there is a governance ambiguity: the standards repo's rollout tracker is scoped to 9 active repos and explicitly notes that legacy/demos/experiments are out of scope; `mereka-agent-e` is not currently in the in-scope list.

## Prioritized improvement plan

### Phase 0: Scope decision

**Objective:** Decide whether `mereka-agent-e` should be onboarded now or treated as out-of-scope until it has an actual codebase.

**Actions:** Check whether this repo is actively worked on in 2026 and/or part of the K8s cluster / active roadmap. The standards repo explicitly limits rollout to active repos and treats legacy/demo/experiment repos as no-action.

**Owner type:** Human (repo owner/tech lead) with support from an agent.

**Expected outputs:** A documented decision in the repo (e.g., an issue or README note) stating either:
- "In scope, proceed with blueprint onboarding," or
- "Out of scope until project scaffolding exists; revisit when code lands."

**Risk/dependency:** If onboarded prematurely, `AGENTS.md` may contain placeholders and can drift into misinformation, undermining the standards' "real commands" intent (even if the linter passes).

### Phase 1: Inventory + blueprint drafting

**Objective:** Create a minimal but correct `.ai/blueprint.yaml` aligned with what the repo actually is today.

**Actions (if onboarding now):** Draft `.ai/blueprint.yaml` using schema-supported fields (`name`, `type`, `stack`, `fragments`, and optionally `commands`, `structure`, `conventions`, `boundaries`, `tools`, `claude`, `last_updated`).

Because the generator only emits Commands/Structure/Conventions sections if present in the blueprint, a blueprint that omits these will generate an `AGENTS.md` that fails the linter's required-section checks. Therefore, even a "scaffold" blueprint should include minimal versions of these fields.

**Owner type:** Either (agent can draft; human validates assumptions).

**Expected outputs:** `.ai/blueprint.yaml` committed (or ready for PR).

**Risk/dependency:** Repo type and stack are not inferable from current contents; pick a type only if you can justify it. The schema allows `service`, `library`, etc., but the choice should match the real intended repo.

### Phase 2: Generate files

**Objective:** Generate instruction files using the standards generator (do not hand-write outputs).

**Actions:** Run the generator described/implemented in `agents-standards` to produce outputs from `.ai/blueprint.yaml`. The generator explicitly produces `AGENTS.md` and `CLAUDE.md` and can optionally produce Copilot/Gemini/Cursor adapters depending on `tools.*` flags.

**Owner type:** Either (agent or human with local tooling access to agents-standards).

**Expected outputs:** Generated files added to `mereka-agent-e`:
- `AGENTS.md`
- `CLAUDE.md`
- optionally `.github/copilot-instructions.md`, `GEMINI.md`, `.cursor/rules/project.mdc` (recommended for multi-tool parity)

**Risk/dependency:** Ensure generated files keep "project-specific" content minimal and avoid copying org-level guidance—this is an explicit architectural goal of fragments + blueprint composition.

### Phase 3: Lint and refine

**Objective:** Ensure `AGENTS.md` meets the linter's required checks.

**Actions:** Run the linter script (or replicate its checks in CI later). It validates required sections, line count, last-updated date, boundaries format, secrets heuristics, and code fences, and warns on missing optional sections.

**Owner type:** Either.

**Expected outputs:** `AGENTS.md` passing with "0 failures" and minimal warnings (the linter treats warnings as acceptable but failures as not).

**Risk/dependency:** Placeholders may technically pass lint but still be misleading; mitigate by making placeholders explicit ("No install/build commands yet") and scheduling updates when the repo scaffolding arrives.

### Phase 4: Add drift detection / CI

**Objective:** Prevent hand-edits to generated files and ensure blueprint remains the source of truth.

**Actions:** Implement a CI check that regenerates instruction files from `.ai/blueprint.yaml` and fails if diffs exist (the standards repo's rollout tracker explicitly calls out this as "Phase 3: CI Drift Detection").

**Owner type:** Human + agent (CI wiring may require org conventions).

**Expected outputs:** A workflow in `mereka-agent-e` that detects drift on PRs.

**Risk/dependency:** The repo currently has no CI workflows; introduce carefully and ensure it does not block future bootstrapping work.

### Phase 5: Review effectiveness after usage

**Objective:** Validate that the instructions help agents/humans and remain accurate.

**Actions:** After the repo has real code, revise the blueprint to include real install/dev/test/lint/build commands, real structure paths, and repo-specific conventions. The standards repo explicitly encourages avoiding stale copies by keeping a single source of truth and updating as the repo evolves.

**Owner type:** Either.

**Expected outputs:** Updated blueprint + regenerated outputs.

**Risk/dependency:** Without periodic updates, the repo may again appear in "no instruction" or "low quality" audit results; the standards repo already runs weekly audits and reports trends.

## Proposed first PR scope and acceptance criteria

### Minimal useful first PR

Because `mereka-agent-e` currently has no codebase and therefore cannot provide real project commands, the smallest useful PR should focus on **establishing the blueprint pipeline** and producing **clearly labeled scaffold instructions** that pass the linter structurally while explicitly stating that commands are placeholders until code is added.

**Files to add (exact paths):**
- `.ai/blueprint.yaml` (new, source of truth; required fields per schema)
- `AGENTS.md` (generated; must include Overview/H1, Commands, Structure, Conventions, Boundaries, plus last-updated date)
- `CLAUDE.md` (generated thin adapter)
- Optional (recommended to align with "multi-tool by design"):
  - `.github/copilot-instructions.md`
  - `GEMINI.md`
  - `.cursor/rules/project.mdc`

### Likely archetype, with justification constraints

The blueprint schema supports a `type` value including `service` and `library`.

Given only the README statement "dedicated for Agent E development," there is insufficient evidence to choose confidently.

**Recommendation:** Set `type: service` only if Agent E is intended to be a deployable bot/service; otherwise `type: library` if it is expected to be a shared package. Treat this as part of Phase 0-1 scope decision.

### Draft blueprint content outline

This outline is designed to satisfy the linter and generator behavior (sections appear only if present in the blueprint).

- `name: mereka-agent-e`
- `description: <short, specific>`
- `type: service|library` (choose deliberately)
- `stack: []` (until real stack is known; schema allows an array and does not specify a minimum length)
- `fragments: [boundaries, git-workflow, validation, secrets]` (all exist and encode shared org guidance)
- `commands:` include **explicit placeholders** that are truthful, e.g. `echo "No build system yet"`; this causes generator to emit "## Commands" and a fenced code block.
- `structure:` minimally document the current repo structure (`README.md`, `.gitignore`) and reserve paths like `src/` or `docs/` as "TBD when code scaffolding lands."
- `conventions:` minimal rules that are enforceable now (e.g., "Do not commit secrets; use env vars," "Update blueprint when repo scaffolding changes"), plus any project-specific expectations.
- `tools:` set adapters to true if you want Copilot/Gemini/Cursor outputs in this first PR.
- `last_updated: "2026-03-09"` (current date in Asia/Jakarta, ISO format)

### Acceptance criteria and definition of done

Acceptance criteria are based entirely on the standards linter and generator model:

- `AGENTS.md` and `CLAUDE.md` are **generated** from `.ai/blueprint.yaml` and include the generator's "GENERATED ... edit the blueprint" header.
- `AGENTS.md` passes linter required checks: has an H1, Commands/Structure/Conventions/Boundaries sections, "Last updated" line, and uses fenced code blocks.
- `AGENTS.md` remains <=150 lines (or at least <=300 with only warnings, but <=150 is the target).
- Any placeholder commands are clearly labeled as placeholders and do not pretend to build/test the project.

## Risks and open questions

The main risk is premature standardization: the standards repo explicitly focuses on active repos, and `mereka-agent-e` is not listed in the current "In Scope" tracker; onboarding may be unnecessary until development begins.

A second risk is "false correctness": because the linter checks for section presence more than semantic correctness, you can pass lint with placeholder commands; however, this conflicts with the spirit of "real commands only" and could mislead contributors/agents once the repo becomes active. The mitigation is to make placeholders explicit and to schedule a blueprint update as soon as any scaffolding is added.

## References

- [agents-standards repository](https://github.com/Biji-Biji-Initiative/agents-standards)
- [mereka-agent-e repository](https://github.com/Biji-Biji-Initiative/mereka-agent-e)
- Org-wide audit report dated 2026-03-05
- Standards linter (`lint-agents-md.sh`)
- Generator (`generator/build_instructions.py`)
