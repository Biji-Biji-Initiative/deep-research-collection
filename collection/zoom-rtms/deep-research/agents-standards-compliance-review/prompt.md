# Research Prompt

**Date**: 2026-03-09
**Repository**: zoom-rtms
**Researcher**: Platform Engineering Team
**Priority**: high

## Research Question

Assess agent instruction quality in the `zoom-rtms` repository against the standards and operating model defined in the `agents-standards` repository. Perform a deep comparative review to identify gaps, strengths, and produce a prioritized improvement plan.

## Context

The `agents-standards` repository defines the organization's standards for AI agent instructions, including blueprint-driven workflows, required AGENTS.md sections, boundaries format, and multi-tool output generation. The `zoom-rtms` repository needs to be evaluated against these standards to ensure consistency across the platform and enable better multi-tool support.

## Scope

### Review in `zoom-rtms`
- Root `AGENTS.md`
- Any archived, alternate, or historical `AGENTS.md` files
- Supporting docs explicitly referenced by AGENTS files
- Any evidence of repo-specific delivery, testing, security, or operational conventions

### Review in `agents-standards`
- README / CONTRIBUTING / rollout tracker
- Audit and linting guidance
- Layered architecture proposal
- Cross-tool compatibility proposal
- Blueprint-driven generation model
- Any service archetype or service blueprint examples
- Anything defining required/expected sections, target length, governance, and maintenance model

### Key Evaluation Questions

1. **Existence and coverage**
   - How many `AGENTS.md` files exist in `zoom-rtms`?
   - Which one is the active source of truth?
   - Is there any useful content in archived versions that should be restored?

2. **Compliance with standards**
   - Blueprint-driven workflow compliance
   - Whether AGENTS is hand-written vs generated
   - Presence and quality of: overview, commands, project structure, conventions, boundaries, security guidance, validation guidance
   - File conciseness and maintainability
   - Multi-tool output support

3. **Practical usefulness for coding agents**
   - Can agents understand how to work safely in the repo?
   - Can agents find code and major modules?
   - Can agents run and validate the app?
   - Are coding/testing conventions clear?
   - Are deployment boundaries understood?

4. **Historical recovery**
   - Which useful sections were lost from current root file?
   - Which parts should be restored as project-specific instructions?

5. **Improvement strategy**
   - Should it adopt `.ai/blueprint.yaml` using the `service` archetype?
   - What stack/fragments should it use?
   - Which instructions should remain in generated AGENTS?
   - Should additional adapters be generated?

## Expected Deliverables

- [x] Executive summary with overall verdict
- [x] Evidence table with standards vs current state
- [x] List of what's already good
- [x] Gap analysis (missing content, misplaced content, governance/process gaps, tooling/automation gaps)
- [x] Phased improvement plan
- [x] Proposed target state for `zoom-rtms`
- [x] Draft implementation starter with blueprint outline

## References

- [agents-standards repository](https://github.com/mereka-io/agents-standards)
- [zoom-rtms repository](https://github.com/mereka-io/zoom-rtms)
- Org-wide audit report dated 2026-03-05
