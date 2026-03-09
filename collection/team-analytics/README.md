# Team Analytics Research

This folder contains deep research reports for the team-analytics repository.

## Research Index

### Agent Instructions Audit
| Topic | File | Description |
|-------|------|-------------|
| Audit Prompt | [prompt.md](./deep-research/prompt.md) | Deep repository audit prompt for agent-instruction quality |
| Audit Report | [result.md](./deep-research/result.md) | Complete audit report against agents-standards |

## Audit Summary

**Verdict: Red** - team-analytics is not currently aligned with the org's blueprint-driven agent-instruction operating model.

### Key Findings
- Missing root `AGENTS.md` and no `.ai/blueprint.yaml`
- Most "universal" guidance lives in an extremely large `CLAUDE.md`
- Copilot file points to `CLAUDE.md` as the context source (inverts standards model)
- High drift risk from hand-maintained, tool-specific instruction sprawl

### Priority Actions
1. Create `.ai/blueprint.yaml` using service archetype
2. Generate `AGENTS.md` (universal baseline, ~90-150 lines)
3. Reduce `CLAUDE.md` to Claude-specific only (~15-30 lines)
4. Generate thin adapters for Copilot/Gemini/Cursor
5. Add CI drift detection

## Statistics

- **Total Research Documents**: 2
- **Audit Date**: March 9, 2026
- **Repository**: Biji-Biji-Initiative/team-analytics
- **Standards Reference**: Biji-Biji-Initiative/agents-standards
