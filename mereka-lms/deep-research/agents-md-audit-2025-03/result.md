# Audit of `mereka-lms/AGENTS.md` against `agents-standards`

## Information needs and sources reviewed

This audit needed to establish a defensible baseline for “what good looks like” (sections, length, boundaries model, maintenance rules), then compare `mereka-lms/AGENTS.md` content/shape against that baseline, and finally produce a remediation plan that is both org-aligned and PR-executable.

Primary sources reviewed (GitHub connector):

- `Biji-Biji-Initiative/mereka-lms/AGENTS.md` (at commit `83adf341…`) filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL1-L9999
- `Biji-Biji-Initiative/mereka-lms/.github/copilot-instructions.md` filecitegithub:Biji-Biji-Initiative/mereka-lms@main/.github/copilot-instructions.mdL1-L200
- `Biji-Biji-Initiative/mereka-lms/CLAUDE.md` filecitegithub:Biji-Biji-Initiative/mereka-lms@main/CLAUDE.mdL1-L9999
- `Biji-Biji-Initiative/agents-standards/README.md` filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL1-L200
- `Biji-Biji-Initiative/agents-standards/audit/lint-agents-md.sh` filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL1-L220
- `Biji-Biji-Initiative/agents-standards/generator/build_instructions.py` filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL1-L260
- `Biji-Biji-Initiative/agents-standards/CONTRIBUTING.md` filecitegithub:Biji-Biji-Initiative/agents-standards@main/CONTRIBUTING.mdL1-L200
- `Biji-Biji-Initiative/agents-standards/TODO.md` filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL1-L140
- `Biji-Biji-Initiative/agents-standards/research/internal/pain-points.md` filecitegithub:Biji-Biji-Initiative/agents-standards@main/research/internal/pain-points.mdL1-L200
- `Biji-Biji-Initiative/agents-standards/blueprints/examples/service.yaml` filecitegithub:Biji-Biji-Initiative/agents-standards@main/blueprints/examples/service.yamlL1-L160
- `Biji-Biji-Initiative/agents-standards/fragments/core/{boundaries,secrets,validation}.md` filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/boundaries.mdL1-L20 filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/secrets.mdL1-L40 filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/validation.mdL1-L40

## Standards baseline from `agents-standards`

### Operating model and intent

The org standard is explicitly **blueprint-driven**: the repo positions `.ai/blueprint.yaml` as the single source of truth and treats `AGENTS.md` / `CLAUDE.md` as generated outputs. The platform’s README calls out both “Blueprint is the source of truth” and “AGENTS.md and CLAUDE.md are generated outputs — never hand-edit them,” plus “Progressive disclosure — root files stay short.” filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60

The same README also gives *expected size targets* for generated outputs: `AGENTS.md` is “~90–150” lines; `CLAUDE.md` is “~15–30”; Copilot instructions are “~25.” filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL31-L41

### Canonical generated section order

The generator (`build_instructions.py`) describes how `AGENTS.md` is composed. It always emits an H1 repo title (serving as the “Overview”), then conditionally adds `## Commands`, `## Structure`, and `## Conventions`, followed by stack/core fragments (where `## Validation` and `## Secrets` can appear), then `## Boundaries` (explicit in blueprint), and finally a `Last updated: YYYY-MM-DD` footer. filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL33-L132

This aligns well with the section order you asked to enforce (Overview → Core Commands → Structure → Conventions → Validation → Boundaries), even though “Validation” is typically added via a fragment rather than a fixed generator block. filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/validation.mdL1-L20

### Enforceable checks

The repo includes a linter script that validates a single `AGENTS.md`. It checks:

- Must have an H1 (treated as “Overview”). filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL31-L47  
- Must have sections matching “Commands”, “Structure”, “Conventions”, “Boundaries” (flex matching). filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL49-L73  
- Optional sections: “Validation” and “Deployment”. filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL75-L92  
- Line-count thresholds: pass ≤150; warn ≤300; fail >300. filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL94-L110  
- Must contain a “Last updated/date/updated” string. filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL112-L120  
- Boundaries should look like a 3-tier model (“Always/Ask/Never” signals); the linter only detects Always+Never heuristically, but the “core/boundaries” fragment is explicit about Always/Ask First/Never. filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL122-L129 filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/boundaries.mdL1-L10

### Known org pain points relevant to `mereka-lms`

The internal “pain points” doc calls out specific failure modes that matter here: “Context budget exceeded” (AGENTS/CLAUDE too long), “Duplication causes staleness,” and “Mixed human/agent audience.” It explicitly cites `mereka-lms` as an example of “narrative paragraphs alongside commands” under “Mixed human/agent audience.” filecitegithub:Biji-Biji-Initiative/agents-standards@main/research/internal/pain-points.mdL55-L76

Also, the rollout tracker lists `mereka-lms` as **not yet migrated** (“Blueprint: TODO”) and instructs using the `service.yaml` archetype. filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL7-L20 filecitegithub:Biji-Biji-Initiative/agents-standards@main/blueprints/examples/service.yamlL1-L70

## Current state assessment of `mereka-lms` agent instructions

### Executive summary

- `mereka-lms/AGENTS.md` is **not blueprint-generated** and **does not appear to follow progressive disclosure**; it contains extensive runbook-grade operational content (deployment sequences, deep operational learnings, multi-page checklists). filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL1-L9999 filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60  
- The file has a correct **top-level H1** (“Repository Guidelines”) and strong **data-protection orientation** (explicit “Forbidden Actions” requiring confirmation; “Always create a backup first” posture). filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL1-L40  
- It includes recognizable equivalents of “Core Commands,” “Structure,” and “Conventions,” but the **required “Boundaries” section is not present in the explicit 3-tier model** used by the standard fragments and generator. filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL41-L120 filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/boundaries.mdL1-L10  
- It is extremely likely to **fail lint targets for length** (standards target 90–150 lines; linter fails above 300). The existing content is far larger than a concise agent instruction file. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL31-L41 filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL94-L110  
- It does **not include a “Last updated” line**, which is a hard fail in the linter and normally auto-added by the generator. filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL112-L120 filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL124-L132  
- Tool adapters exist in-repo (`.github/copilot-instructions.md`, `CLAUDE.md`), but they are **not aligned** with the standards’ desired thin adapter approach (especially `CLAUDE.md`). filecitegithub:Biji-Biji-Initiative/mereka-lms@main/.github/copilot-instructions.mdL1-L40 filecitegithub:Biji-Biji-Initiative/mereka-lms@main/CLAUDE.mdL1-L200 filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL31-L41  
- The org’s own pain-points doc specifically flags the “mixed human/agent” problem and calls out `mereka-lms` as an example. filecitegithub:Biji-Biji-Initiative/agents-standards@main/research/internal/pain-points.mdL55-L76

### Implemented well and worth preserving

The most valuable and *agent-appropriate* content already present is the safety posture and a small set of truly core commands:

The document leads with “Data Protection Rules” and explicitly separates actions that require explicit confirmation. This is directionally aligned with the org’s boundary model (“Always / Ask First / Never”) and should be kept, but reformatted into the standard structure. filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL3-L35 filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/boundaries.mdL1-L10

The repo also already has “project structure” and a “build/test/dev commands” section with concrete commands (`make bootstrap`, `tutor local quickstart`, `tutor images build …`, patch-apply workflow). These are the kinds of high-signal commands the standard generator expects to surface near the top. filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL60-L100 filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL44-L69

## Gap analysis against `agents-standards`

The table below maps each non-negotiable requirement to observed evidence, then links the risk to a concrete fix.

| Standard requirement | Present in `mereka-lms/AGENTS.md`? | Evidence | Risk if unchanged | Fix recommendation |
|---|---:|---|---|---|
| Overview (H1) | Yes | File begins with a top-level `#` heading (“Repository Guidelines”). filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL1-L2 | Low | Keep, but rename H1 to repo name (preferred by generator: `# {bp['name']}`). filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL41-L46 |
| Required section: Core Commands | Partially | Has `## Build, Test, and Development Commands` containing concrete commands. filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL72-L90 | Medium: commands exist but are buried under long content; “TTFS” suffers | Move a short `## Core Commands` directly after Overview, and reduce to the minimal “install/run/test/lint” set (plus 1–2 repo-specific workflows). This matches generator expectations for `## Commands`. filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL49-L69 |
| Required section: Structure | Yes | Has `## Project Structure & Module Organization` with directory descriptions. filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL56-L70 | Low | Convert to a compact “tree-style” block aligned with generator output. filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL71-L84 |
| Required section: Conventions | Yes | Has `## Coding Style & Naming Conventions` and additional conventions across the doc. filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL220-L235 | Medium: conventions become noisy, repeated, and stale | Fold into a short list under `## Conventions` + link to deeper docs/specs. This also addresses “duplication causes staleness.” filecitegithub:Biji-Biji-Initiative/agents-standards@main/research/internal/pain-points.mdL45-L63 |
| Required section: Validation | Present but not standardized | Contains testing/verification guidance scattered (e.g., `tutor local quickstart -I` as acceptance test; many repo scripts). filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL236-L245 | Medium: unclear “minimum bar” before PR | Add an explicit `## Validation` section with 3–5 steps, aligned to core fragment. filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/validation.mdL1-L12 |
| Required section: Boundaries + 3-tier model | No (explicitly) | Strong safety content exists (e.g., “Forbidden Actions require confirmation,” “Always create a backup first”), but there is no `## Boundaries` section in the standard Always/Ask First/Never format. filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL7-L35 | High: safety rules exist but aren’t machine-readable/consistent across repos; lint warns/fails; cross-tool interpretation degrades | Add `## Boundaries` with bullet lines for **Always / Ask First / Never**, mirroring the org fragment. filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/boundaries.mdL1-L10 |
| Conciseness (target 90–150 lines; fail >300) | No | Standards explicitly target ~90–150 lines for AGENTS.md, and linter fails above 300 lines. The current file contains extensive runbook material and long multi-section appendices. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL31-L41 filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL94-L110 | High: context budget blown; increased agent error rate due to noise, per pain points | Rewrite as progressive-disclosure index: keep rules + minimum commands + pointers; move runbooks to `docs/operations/…` and reference them. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60 |
| “Last updated: YYYY-MM-DD” required | Missing | Linter requires a date marker; generator auto-adds “Last updated …”. filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL112-L120 filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL124-L132 | High: guaranteed lint failure; harder to reason about staleness | Add/auto-generate footer via blueprint generator; do not hand-edit. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60 |
| Avoid duplication / mixed audience | Not met | File includes deep operational material (deployment sequences, secrets operational procedures, extensive checklists), which matches the “Mixed human/agent audience” pain point explicitly called out for `mereka-lms`. filecitegithub:Biji-Biji-Initiative/agents-standards@main/research/internal/pain-points.mdL55-L76 | High: staleness + context waste + conflicting sources | Reduce AGENTS to agent-only guardrails and pointers. Put runbooks in docs; reference them from AGENTS. This is consistent with “Progressive disclosure.” filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60 |
| Blueprint-driven generation (org direction) | Not implemented | `agents-standards` expects `.ai/blueprint.yaml` to generate outputs; `mereka-lms` is explicitly listed as “Blueprint: TODO” in rollout tracker. filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL7-L20 | High: drift from org; manual edits rot | Add `.ai/blueprint.yaml` based on `service.yaml` archetype. Generate files with generator and enforce with lint/CI. filecitegithub:Biji-Biji-Initiative/agents-standards@main/blueprints/examples/service.yamlL1-L160 filecitegithub:Biji-Biji-Initiative/agents-standards@main/CONTRIBUTING.mdL7-L55 |

## Proposed `AGENTS.md` v2 outline

The goal is to produce a blueprint-generated `AGENTS.md` that conforms to the canonical structure and stays within the org size target (~90–150 lines). filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL31-L41

Below is a concrete skeleton that you can use as the *intended generated output*. (In the improvement plan, I recommend generating this from `.ai/blueprint.yaml`, not editing by hand.) filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60

```md
<!-- GENERATED from .ai/blueprint.yaml — edit the blueprint, not this file -->

# mereka-lms

Open edX (Tutor) deployment + theming + automation for Mereka Academy. Source-of-truth for “how we run it” lives in docs/specs; this file is the agent quick-reference.

## Core Commands
```bash
install: make bootstrap
dev:     source infrastructure/tutor/tutor-env.sh && export TUTOR_ROOT="$(pwd)/tutor_env" && tutor local start -d
test:    make check-fast
lint:    make lint
build:   tutor images build openedx && tutor images build mfe
deploy:  # ArgoCD/GitOps-managed (see docs/operations/RELEASE_PROCESS.md)
```

## Structure
```
infrastructure/        Tutor configs, patches, themes, IaC
deploy/k8s/            Kustomize base + overlays
scripts/               Infra/QA/branding/migrations automation
specs/                 Machine-checkable requirements + ACs
docs/                  Onboarding, operations runbooks, ADRs
services/              Standalone services/webhooks
```

## Conventions
- Specs vs docs: specs define testable contracts; docs explain how-to.
- After any `tutor config save`, re-apply patches (see infra patch workflow).
- Always set `TUTOR_ROOT="$(pwd)/tutor_env"` before running Tutor commands.
- Prefer repo scripts for verification/runbooks over ad-hoc manual commands.

## Validation
Before opening a PR:
1) Run `make check-fast`
2) If infra/config changed, run `tutor local quickstart -I` (or the documented smoke gate)
3) Ensure no generated Tutor artifacts or secrets are committed

## Boundaries
- **Always**: For risky infra/data operations, take a backup first; follow existing patterns; run validation before PR.
- **Ask First**: Any production-impacting change (K8s manifests, GitOps refs/tags, DB/storage operations, CI workflow edits).
- **Never**: Hardcode or print secrets; delete/scale DB stateful resources without explicit approval; push directly to main.

## More Detail
- See `docs/onboarding/QUICK_START_LOCAL.md`
- See `docs/operations/TROUBLESHOOTING.md`
- See `docs/operations/RELEASE_PROCESS.md`
- See `docs/operations/BUILD_PIPELINE_RUNBOOK.md`
- See `docs/adr/` (architecture decisions)
---
Last updated: YYYY-MM-DD
```

Why this outline matches the standard:

- It mirrors the generator’s core structure (`Commands`, `Structure`, `Conventions`, `Boundaries`, footer). filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL41-L132  
- It explicitly uses the Always/Ask First/Never vocabulary from the core fragment. filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/boundaries.mdL1-L10  
- It keeps “details” as pointers (“progressive disclosure”), matching org principle. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60  

## Improvement plan and PR-ready task list

### Strategy

The org is already clear that `mereka-lms` should be migrated to the blueprint-driven system, using the `service.yaml` archetype. filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL7-L20

Therefore the best improvement plan is not “edit the long AGENTS.md”: it’s “introduce a blueprint, generate new concise files, relocate long runbook content to docs (or keep it where it already exists), and enforce via CI.”

### Detailed phased plan

Phase one focuses on getting `AGENTS.md` compliant and low-noise; phase two locks in drift prevention; phase three optionally addresses the current duplication across `AGENTS.md` / `CLAUDE.md` / Copilot instructions in an org-aligned way.

#### Phase one: introduce `.ai/blueprint.yaml` and generate outputs

1) Add `.ai/blueprint.yaml` to `mereka-lms` using the `agents-standards` service archetype as the starting point. filecitegithub:Biji-Biji-Initiative/agents-standards@main/blueprints/examples/service.yamlL1-L70  
   - Set `name: mereka-lms`, `type: service`, `stack: [k8s-argocd]` (as suggested by tracker), and pick core fragments `[boundaries, validation, secrets]` (and `git-workflow` if it exists/desired in your org standard set). filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL7-L20 filecitegithub:Biji-Biji-Initiative/agents-standards@main/CONTRIBUTING.mdL35-L55  
   - Populate `commands:` with the empirically correct, *minimal* commands already described in the current file (`make bootstrap`, Tutor env activation, tutor start/stop/quickstart, patch-apply, key verification gates). filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL72-L90  
   - Populate `structure:` using the current structure summary (infrastructure/scripts/services/docs/var/etc.). filecitegithub:Biji-Biji-Initiative/mereka-lms@83adf341/AGENTS.mdL56-L70  

2) Generate instruction files with the standard generator (`generator/build_instructions.py`). filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL9-L20  
   - Ensure it produces: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` (and optionally `GEMINI.md`, `.cursor/rules/project.mdc` depending on tool usage). filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL31-L41  

3) Run the linter against the new `AGENTS.md` and iterate until it passes. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL17-L21 filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL1-L220  

4) Relocate runbook-grade content out of `AGENTS.md` into appropriate doc locations (most are already in `docs/operations/*` per the existing file references), leaving only pointers in the blueprint `context_files:` section. This is directly aligned to the “progressive disclosure” goal and the field pain points (“mixed human/agent audience”, “context budget exceeded”). filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60 filecitegithub:Biji-Biji-Initiative/agents-standards@main/research/internal/pain-points.mdL24-L76  

Deliverable of phase one: a new concise `AGENTS.md` that contains only what the generator expects plus repo-specific essentials.

#### Phase two: enforce drift prevention in CI

5) Add a repo workflow step that runs `audit/lint-agents-md.sh` on PRs when `AGENTS.md` changes. The linter is designed for “single-repo validation.” filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL1-L220  

6) Add a “regenerate and diff” drift check, consistent with the standards roadmap. The `agents-standards/TODO.md` explicitly calls out “CI drift detection” via regenerate+diff failing if hand edits occur. filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL56-L66  

Deliverable of phase two: PRs cannot silently re-bloat or hand-edit generated instruction files.

#### Phase three: align adapters and reduce duplication across instruction surfaces

7) Replace the current hand-written `.github/copilot-instructions.md` with the generated version (only if you set `tools.copilot: true`), so Copilot gets key commands + conventions + boundaries inline (the generator does this because “Copilot doesn’t follow file references well”). filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL134-L190  

8) Make `CLAUDE.md` thin and Claude-specific (imports/skills/rules) and point it to `AGENTS.md` for universal guidance, matching the platform intent and the pain-point fix direction (“AGENTS universal; CLAUDE tool-specific”). filecitegithub:Biji-Biji-Initiative/agents-standards@main/research/internal/pain-points.mdL7-L17 filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL134-L191  

### PR-ready checklist

Use the following as your PR task list in `mereka-lms`:

1. Add `.ai/blueprint.yaml` (start from `agents-standards/blueprints/examples/service.yaml`; adapt to `mereka-lms`). filecitegithub:Biji-Biji-Initiative/agents-standards@main/blueprints/examples/service.yamlL1-L160  
2. Generate `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` using the standard generator. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL9-L20  
3. Ensure generated `AGENTS.md` includes, in order: Overview, Core Commands, Structure, Conventions, Validation, Boundaries, and contains `Last updated:` footer. filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL41-L132  
4. Run `agents-standards/audit/lint-agents-md.sh AGENTS.md`; fix until pass (0 failures). filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL1-L220  
5. Move (or delete from AGENTS) runbook-grade sections and replace with links via `context_files:` or `More Detail` pointers, to meet progressive disclosure. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60  
6. Add CI job: `lint-agents-md.sh` on PRs touching `AGENTS.md`. filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL1-L220  
7. Add CI drift check: regenerate from blueprint and fail if diff non-empty. filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL56-L66  

### Acceptance criteria

Your remediation is “done” when:

- `AGENTS.md` passes the linter and is within the intended size band (target ≤150; must be ≤300). filecitegithub:Biji-Biji-Initiative/agents-standards@main/audit/lint-agents-md.shL94-L110  
- `AGENTS.md` contains explicit `## Boundaries` with Always/Ask First/Never (or equivalent produced by generator from blueprint boundaries). filecitegithub:Biji-Biji-Initiative/agents-standards@main/fragments/core/boundaries.mdL1-L10  
- `AGENTS.md` ends with `Last updated: YYYY-MM-DD`. filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL124-L132  
- CI prevents hand-edits/drift (lint + regenerate/diff). filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL56-L66  

## Risks and mitigations

The largest risk is that removing content from `AGENTS.md` breaks workflows for agents/operators who have been relying on it as a one-stop runbook. This is a known transitional issue in moving from “mixed human/agent audience” to “progressive disclosure.” filecitegithub:Biji-Biji-Initiative/agents-standards@main/research/internal/pain-points.mdL55-L76 The mitigation is to move that content into stable doc locations (`docs/operations/*`, ADRs, specs) and ensure the new `AGENTS.md` contains a curated “More Detail” section pointing to the canonical docs, matching the generator’s `context_files` feature. filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL112-L123

A second risk is continued drift if files remain hand-edited. The standards explicitly address this by making the blueprint the source of truth and proposing CI regeneration/diff checks. filecitegithub:Biji-Biji-Initiative/agents-standards@main/README.mdL49-L60 filecitegithub:Biji-Biji-Initiative/agents-standards@main/TODO.mdL56-L66 The mitigation is to implement the drift check in the same PR (or immediately after), so the repo cannot regress.

A third risk is cross-tool inconsistency: Copilot, Claude, and other tools respond differently to references and long documents. The generator explicitly bakes in a strategy: keep universal content in `AGENTS.md`, keep adapters thin, and inline key sections for Copilot because it doesn’t follow references reliably. filecitegithub:Biji-Biji-Initiative/agents-standards@main/generator/build_instructions.pyL134-L152 Aligning `mereka-lms` to that approach reduces “surprise variance” across tools.