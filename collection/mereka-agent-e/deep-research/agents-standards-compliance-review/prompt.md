# Research Prompt

**Date**: 2026-03-09
**Repository**: mereka-agent-e
**Researcher**: Platform Engineering Team
**Priority**: high

## Research Question

Conduct a repo-standardization review for `Biji-Biji-Initiative/mereka-agent-e` against the instruction standards and workflow defined in `Biji-Biji-Initiative/agents-standards`.

## Context

The `agents-standards` repository defines the organization's blueprint-first model for AI agent instructions. All repos should have `.ai/blueprint.yaml` as the source of truth, with generated outputs (AGENTS.md, CLAUDE.md, and tool adapters) rather than hand-edited files. This review assesses whether `mereka-agent-e` follows these standards.

## Scope

### A. Inventory the repo
Search the root and subdirectories for:
- AGENTS.md
- CLAUDE.md
- .ai/blueprint.yaml
- .github/copilot-instructions.md
- GEMINI.md
- .cursor/rules/*.mdc
- Any docs that act as substitute agent instructions

Determine:
- Repository type from codebase shape: service, monorepo, infra, library, or other
- Likely stack from package managers, framework files, deployment manifests, CI, Docker, k8s, etc.
- Actual runnable commands (install, dev, build, test, lint, typecheck, start, deploy/preview)
- Project structure (key directories, entrypoints, apps/packages/modules, config directories, test locations)
- Project-specific conventions (naming, architecture boundaries, state management, API patterns, testing patterns)
- Repo-specific boundaries (what agents may safely change, what requires approval, what must never be changed)

### B. Compare against standards from agents-standards
- Blueprint-first workflow
- Generated-files approach
- Required linter sections
- Line-count target (~90-150 lines)
- Progressive disclosure / keep project file thin
- Separation of org-level vs project-level guidance
- Multi-tool outputs
- Auditability and lintability

### C. Perform gap analysis
For every expected standard element, mark one of:
- Present and good
- Present but weak
- Missing
- Not applicable

Minimum comparison matrix:
- AGENTS.md exists
- CLAUDE.md exists
- .ai/blueprint.yaml exists
- File is generated vs hand-written
- Required sections covered
- Optional sections covered
- Last updated date present
- 3-tier boundaries present
- Commands are accurate and executable
- Structure section is concrete
- Conventions are repo-specific
- Secrets guidance present
- Adapters exist for Copilot/Gemini/Cursor
- Content is thin and project-specific
- CI/lint flow exists or can be added

### D. Judge what is already good
Call out strengths in the repo that would make standardization easier:
- Clean README
- Obvious scripts in package.json
- Clear folder structure
- Good CI config
- Stable deployment config
- Existing docs that can be mined into blueprint fields

### E. Identify what needs to be done
Be explicit about:
- What files need to be created
- What information needs to be collected
- What standards decisions must be made
- Whether the repo should use service, monorepo, infra, or another archetype
- Whether the repo seems active enough to be in scope

### F. Produce an improvement plan
Return a phased plan with:
- Phase 0: scope decision (confirm repo is active/in-scope)
- Phase 1: inventory + blueprint drafting
- Phase 2: generate AGENTS.md / CLAUDE.md / adapters
- Phase 3: lint and refine
- Phase 4: add drift detection / CI
- Phase 5: review effectiveness after usage

### G. Propose a first PR
Design the smallest useful first PR:
- Exact files to add
- Likely archetype
- Likely fragments/stacks needed
- Draft outline of AGENTS.md sections
- Acceptance criteria
- Definition of done

## Expected Deliverables

- [x] Executive summary
- [x] Repo current state
- [x] Standards baseline
- [x] Gap analysis table
- [x] What's good already
- [x] What needs to be done
- [x] Prioritized improvement plan
- [x] First PR proposal
- [x] Risks / open questions

## References

- [agents-standards repository](https://github.com/Biji-Biji-Initiative/agents-standards)
- [mereka-agent-e repository](https://github.com/Biji-Biji-Initiative/mereka-agent-e)
- Org-wide audit report dated 2026-03-05
