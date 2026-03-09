# Deep Repository Audit Prompt: team-analytics Agent Instructions

**Target Repository**: Biji-Biji-Initiative/team-analytics
**Standards Reference**: Biji-Biji-Initiative/agents-standards
**Audit Date**: March 9, 2026

---

You are conducting a deep repository audit of agent-instruction quality for Biji-Biji-Initiative/team-analytics against the standards and operating model defined in Biji-Biji-Initiative/agents-standards.

Your job is not just to summarize files. You must determine the current instruction architecture, compare it against the org standard, identify concrete gaps, explain what is already good, and produce an implementation-ready improvement plan for team-analytics.

## Scope

### 1. Inspect team-analytics for:
- AGENTS.md / agents.md at repo root and subdirectories
- CLAUDE.md
- .github/copilot-instructions.md
- GEMINI.md
- .cursor/rules/*
- .ai/blueprint.yaml
- README.md
- specs/, docs/, k8s/, scripts/, apps/dashboard/, temporal/, lib/

### 2. Inspect agents-standards for:
- README.md
- CONTRIBUTING.md
- TODO.md
- audit/lint-agents-md.sh
- audit/audit-org.sh
- research/proposals/001-layered-architecture.md
- research/proposals/003-cross-tool-compatibility.md
- any relevant templates, blueprints, fragments, or generated examples

## Core Questions to Answer

A. Does team-analytics currently have a valid AGENTS.md? If yes, where is it and what is its quality? If not, what files are currently serving that role?

B. How closely does team-analytics match the intended standards model:
   - blueprint-driven source of truth
   - AGENTS.md as universal baseline
   - CLAUDE.md as Claude-specific only
   - thin/generated adapters for Copilot/Gemini/Cursor
   - progressive disclosure
   - lintable structure and governance

C. What is already strong in team-analytics and can be reused?

D. What is missing, duplicated, misplaced, too long, tool-specific, stale, or risky?

E. What should be done next, in what order, and with what artifacts?

## Audit Method

### 1. Start with file inventory
- List every instruction-related file found in team-analytics.
- Explicitly note whether AGENTS.md exists now.
- If audits/history mention an AGENTS.md but the current repo does not surface one, flag that discrepancy and explain likely interpretations (deleted, moved, not indexed, or stale audit artifact).

### 2. Establish the standards baseline from agents-standards
Extract the intended operating model:
- .ai/blueprint.yaml is source of truth
- AGENTS.md and CLAUDE.md are generated outputs
- AGENTS.md should be roughly 90-150 lines
- CLAUDE.md should be minimal and Claude-specific
- Copilot/Gemini/Cursor files should be thin/generated adapters
- root docs should use progressive disclosure

Extract the lint rubric:
- required sections: Overview, Commands, Structure, Conventions, Boundaries
- recommended sections: Validation, Deployment
- has date / last updated
- 3-tier boundaries format: Always / Ask First / Never
- no hardcoded secrets
- uses fenced code blocks

### 3. Assess team-analytics against that baseline
For each file, classify content into:
- belongs in AGENTS.md
- belongs in CLAUDE.md
- belongs in generated adapters
- belongs in README/specs/docs instead of root instruction files

Identify duplication and inversion of responsibility:
- e.g. if Copilot points to CLAUDE instead of AGENTS
- if CLAUDE currently acts like the universal repo instruction file
- if project-specific detail is mixed with broader org-level or deployment-level content

### 4. Score the repo
Give a structured score using the same dimensions implied by the org tooling:
- clarity
- enforceability
- completeness
- security
- parsability
- maintenance
- signal-to-noise

Also give a practical adoption score:
- universal-tool compatibility
- blueprint readiness
- drift risk
- ease of migration

### 5. Produce a gap analysis
For each gap, include:
- gap
- evidence
- why it matters
- severity (critical / high / medium / low)
- recommended fix
- owner artifact (AGENTS.md, CLAUDE.md, .ai/blueprint.yaml, generated adapter, README/spec, CI workflow, fragment/template)

### 6. Produce an improvement plan for team-analytics
- Phase 1: immediate fixes (1 PR)
- Phase 2: structural standardization
- Phase 3: governance / CI / drift prevention
- Be explicit about exact files to create/update and what each should contain.

## Required Deliverables

1. **Executive summary** - one paragraph stating current maturity and biggest blockers
2. **Current-state inventory** - instruction files found, likely source-of-truth today, missing files
3. **What's good** - specific strengths worth preserving
4. **Gap analysis table** - standard vs current state vs evidence vs fix
5. **What needs to be done now** - short action list ordered by impact
6. **Improvement plan** - 30 / 60 / 90 day plan or PR1 / PR2 / PR3 plan
7. **Proposed target architecture** for team-analytics
   - .ai/blueprint.yaml
   - AGENTS.md
   - minimal CLAUDE.md
   - generated .github/copilot-instructions.md
   - optionally GEMINI.md / .cursor/rules/project.mdc
8. **Suggested AGENTS.md outline** for team-analytics (max 120-150 lines)
9. **Suggested CLAUDE.md outline** (only Claude-specific content)
10. **Risks / assumptions / unresolved questions**

## Important Reasoning Rules

- Do not assume AGENTS.md exists just because an older audit mentions it; verify current state.
- Treat agents-standards as the normative reference, but call out where the standards are still draft/proposed versus already operational.
- Be concrete. Quote exact sections, commands, and headings where possible.
- Prefer reuse over rewrite: if team-analytics already has good commands, structure, testing, and architecture docs, recommend moving or reshaping rather than rewriting from scratch.
- Distinguish between:
  - universal cross-tool instructions
  - Claude-specific instructions
  - human documentation
  - deep operational detail that should live in specs/docs instead of root instruction files

## Output Format

Use these sections exactly:
1. Executive Summary
2. Current State in team-analytics
3. Standards Baseline from agents-standards
4. What's Good
5. Gap Analysis
6. What Needs To Be Done
7. Improvement Plan
8. Proposed Target File Layout
9. Suggested AGENTS.md Outline
10. Suggested CLAUDE.md Outline
11. Risks / Open Questions

End with:
- a "minimum viable PR" recommendation
- a "gold standard end state" recommendation
- a one-line verdict: Green / Yellow / Red for team-analytics readiness
