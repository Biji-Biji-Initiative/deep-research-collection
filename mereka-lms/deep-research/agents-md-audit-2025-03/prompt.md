# Research Prompt

**Date**: 2025-03-05
**Repository**: mereka-lms
**Researcher**: Development Team
**Priority**: high

## Research Question

Assess `mereka-lms/AGENTS.md` (current state) and compare it against the org standards in `agents-standards`. Produce a gap analysis, identify what's already implemented well, and propose a detailed improvement plan (including a concrete new outline for `AGENTS.md`, and a PR-ready task list).

## Context

Mereka LMS has an existing `AGENTS.md` file that has grown over time and may not conform to the organization's standards for agent instruction files. We need to ensure alignment with `agents-standards` repository which provides:
- Blueprint-driven generation
- Progressive disclosure principles
- Standardized section structure
- Linting and validation rules

## Scope

### Inputs (must read)

1. **Repo: Biji-Biji-Initiative/mereka-lms**
   - File: `AGENTS.md` (primary target)
   - Also check: `.github/copilot-instructions.md` (it already references AGENTS.md)

2. **Repo: Biji-Biji-Initiative/agents-standards**
   - File: `AGENTS.md` (the standard + rubric)
   - File: `audit/lint-agents-md.sh` (enforceable checks)
   - Optional: `research/internal/pain-points.md` (context on common failure modes)
   - Optional: any blueprint/generation guidance if present (e.g., `.ai/blueprint patterns`)

### Non-Negotiable Standards to Check (from agents-standards)

**A) Required section order (must exist and appear in this order):**
   1. Overview
   2. Core Commands
   3. Structure
   4. Conventions
   5. Validation
   6. Boundaries

**B) Quality / hygiene rules:**
   - AGENTS.md should be concise (target ≤150 lines; >300 is a hard fail per linter)
   - Commands must be real and runnable (no placeholders)
   - No duplication: link to README/docs instead of pasting runbooks
   - Must include a "Last updated: YYYY-MM-DD" line
   - Must not contain secrets (keys, tokens, credentials) or instructions that would leak them

**C) Boundaries format:**
   - Must use the 3-tier model and be explicit:
     - Always
     - Ask First
     - Never

## Method (do not skip steps)

1. **Build a standards checklist**:
   - Extract the required sections, ordering, and linter checks from agents-standards (quote the rules you're applying).

2. **Audit `mereka-lms/AGENTS.md` with evidence**:
   - List headings/sections in order.
   - Approximate line count.
   - Identify what content is agent-instructions vs human runbook vs duplication.

3. **Linter-alignment evaluation**:
   - Check required headings exist.
   - Check "Last updated" exists.
   - Check boundaries are in 3-tier format.
   - Check length category: ≤150 (pass), 151–300 (warn), >300 (fail).

4. **Gap analysis output**:
   - Produce a table: Standard requirement → Present? → Evidence (quote) → Risk → Fix.
   - Highlight: missing sections, wrong ordering, over-length, duplicated runbook content, unclear commands, missing boundaries formatting, missing last-updated.

5. **What's already implemented well**:
   - List concrete strengths and why they should be preserved.

6. **Improvement plan (detailed, PR-ready)**:
   - Provide a proposed AGENTS.md v2 outline that conforms to the required order and stays ≤150 lines.
   - Provide recommended wording for Boundaries (Always/Ask First/Never), derived from the existing safety rules but reformatted.
   - Provide a "content relocation plan": what gets moved out of AGENTS.md into docs/runbooks, and what stays with links.
   - Provide a CI plan: how to add/enable the lint script in mereka-lms to prevent drift.
   - Provide acceptance criteria (what must be true for the PR to be considered done).

7. **Deliverables format (exact)**:
   - Executive summary (5–10 bullets)
   - Implemented well (keep)
   - Gap table
   - Proposed AGENTS.md v2 (full skeleton text)
   - Step-by-step PR checklist (ordered)
   - Risks & mitigations

## Expected Deliverables

- [ ] Comprehensive standards checklist
- [ ] Complete audit with evidence
- [ ] Gap analysis table
- [ ] Strengths preservation plan
- [ ] Proposed AGENTS.md v2 outline
- [ ] PR-ready task list
- [ ] Risk mitigation strategies

## Success Criteria

1. All non-negotiable standards checked and documented
2. Clear gap analysis with evidence-based findings
3. Actionable improvement plan with concrete steps
4. PR-ready checklist that can be executed immediately
5. Proposed outline conforms to all standards (≤150 lines target)

## References

- [agents-standards repository](https://github.com/Biji-Biji-Initiative/agents-standards)
- [mereka-lms repository](https://github.com/Biji-Biji-Initiative/mereka-lms)
- [Organization agent instruction standards](https://github.com/Biji-Biji-Initiative/agents-standards/blob/main/README.md)
