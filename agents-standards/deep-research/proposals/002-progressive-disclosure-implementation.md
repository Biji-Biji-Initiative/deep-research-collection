# Proposal 002: Progressive Disclosure Implementation

> Status: Draft
> Author: Gurpreet / Claude
> Date: 2026-03-05

## Problem

Agents load 2500-3000 tokens of instructions before seeing any code. Research shows this degrades agent performance ("context rot"). Current average AGENTS.md is 360 lines; industry recommendation is 150.

## Proposal

Implement a 3-tier progressive disclosure system within each project's AGENTS.md:

### Tier 1: Always Loaded (AGENTS.md body — max 150 lines)
- Project identity (1-3 lines)
- Build/test/lint commands (exact, with flags)
- Project structure (top-level only)
- Core conventions (5-10 rules max)
- Boundaries (Always / Ask First / Never)
- "For more" pointers to Tier 2

### Tier 2: Directory-Scoped (subdirectory AGENTS.md — max 80 lines each)
- Package-specific commands
- Package-specific conventions
- Package-specific structure

### Tier 3: On-Demand (skills, referenced docs)
- Deployment procedures
- Troubleshooting guides
- Migration runbooks
- Architecture deep dives
- Historical decisions (ADRs)

## Template: Thin AGENTS.md (Target)

```markdown
# {project-name}

{1-2 sentence description}

## Commands
\`\`\`bash
{install}
{dev}
{test}
{lint}
{build}
\`\`\`

## Structure
\`\`\`
src/         — application code
tests/       — test suites
docs/        — documentation
\`\`\`

## Conventions
- {rule 1}
- {rule 2}
- {rule 3 — max 10}

## Boundaries
- Always: {safe defaults}
- Ask First: {sensitive ops}
- Never: {hard stops}

## More Detail
- Deployment: see `docs/deployment.md` or use `k8s-deployer` skill
- Troubleshooting: see `docs/troubleshooting.md`
- Architecture: see `docs/architecture.md`

---
Last updated: {date}
```

**Target: 60-100 lines** for this template when filled.

## Migration Strategy

For each repo:
1. Score current AGENTS.md with rubric
2. Identify content that belongs in L1 org, L2 category, or L5 skill
3. Move non-essential content to referenced docs or skills
4. Slim AGENTS.md to Tier 1 template
5. Re-score; verify >= 16/21

## Context Budget Target

| Component | Current (tokens) | Target (tokens) |
|-----------|-----------------|-----------------|
| AGENTS.md | 800-1200 | 300-500 |
| CLAUDE.md | 400-800 | 200-400 |
| Rules (auto-loaded) | 200-400 | 200-400 |
| Skills (on-demand) | 0-1000 | 0-1000 |
| **Total at session start** | **1400-2400** | **700-1300** |

## Measuring Success

1. **Line count** — Average AGENTS.md drops from 360 to <150
2. **Agent performance** — Fewer "ignored instruction" incidents
3. **Maintenance time** — Less time updating redundant content
4. **Staleness** — Quarterly audit scores stay >= 16/21
