# Proposal 003: Cross-Tool Compatibility Strategy

> Status: Draft
> Author: Gurpreet / Claude
> Date: 2026-03-05

## Problem

We maintain multiple instruction files per repo (AGENTS.md, CLAUDE.md, copilot-instructions.md, GEMINI.md, .cursor/rules/). Content overlaps and diverges. When standards change, N files need updating per repo.

## Current State

Our adapter strategy (from team-skills):
- `AGENTS.md` — Universal baseline (all tools read it)
- `CLAUDE.md` — Claude-specific (memory, skills, hooks config)
- `copilot-instructions.md` — Thin adapter pointing to AGENTS.md
- `GEMINI.md` — Thin adapter pointing to AGENTS.md
- `.cursor/rules/` — Thin adapter pointing to AGENTS.md
- Factory Droid reads AGENTS.md natively

**29 repos** have copilot + gemini adapters. **5 repos** have Cursor rules.

## Proposal: Single Source, Generated Adapters

### Architecture

```
AGENTS.md (source of truth)
  ↓ generate-adapters.sh
  ├── .github/copilot-instructions.md  (generated)
  ├── GEMINI.md                         (generated)
  ├── .cursor/rules/project.mdc         (generated)
  └── CLAUDE.md                         (hand-maintained, Claude-specific only)
```

### What Goes Where

| Content | AGENTS.md | CLAUDE.md | Generated Adapters |
|---------|-----------|-----------|-------------------|
| Build commands | Y | N | Copied from AGENTS.md |
| Project structure | Y | N | Copied |
| Code conventions | Y | N | Copied |
| Boundaries | Y | N | Copied |
| Skills config | N | Y | N/A |
| Memory/hooks | N | Y | N/A |
| Agent teams | N | Y | N/A |
| Model routing | N | Y | N/A |
| Tool-specific features | N | Y (Claude) | Tool-specific format |

### CLAUDE.md becomes minimal

After extracting universal content to AGENTS.md, CLAUDE.md should only contain:
- Skill references
- Memory configuration
- Hook configuration
- Agent team settings
- Claude-specific behavioral overrides

**Target: 30-50 lines** (down from current 200-400)

### Generated Adapter Format

**copilot-instructions.md:**
```markdown
<!-- AUTO-GENERATED from AGENTS.md — do not edit directly -->
{AGENTS.md content, reformatted for Copilot}
```

**GEMINI.md:**
```markdown
<!-- AUTO-GENERATED from AGENTS.md — do not edit directly -->
{AGENTS.md content, reformatted for Gemini}
```

**.cursor/rules/project.mdc:**
```markdown
---
description: Project conventions from AGENTS.md
globs: ["**/*"]
alwaysApply: true
---
<!-- AUTO-GENERATED from AGENTS.md — do not edit directly -->
{AGENTS.md content, reformatted for Cursor}
```

### CI Integration

```yaml
# .github/workflows/sync-agent-docs.yml
on:
  push:
    paths: ['AGENTS.md']
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - run: ./tools/generate-adapters.sh
      - run: git add .github/copilot-instructions.md GEMINI.md .cursor/
      - run: git diff --cached --exit-code || git commit -m "chore: sync agent docs from AGENTS.md"
```

## Migration Path

1. Create `tools/generate-adapters.sh` in agents-standards repo
2. Test on 2-3 repos (team-skills, nfc-cards, reka-slackbot)
3. Add CI workflow to tested repos
4. Roll out to remaining repos
5. Remove hand-maintained adapters; replace with generated ones

## Open Questions

1. Should CLAUDE.md content that's Claude-specific be kept separate, or should we use AGENTS.md sections with `<!-- claude-only -->` markers?
2. How to handle Cursor's MDC format (YAML frontmatter + glob patterns) — this adds features AGENTS.md doesn't support
3. Should generated files be committed to git or generated at tool-load time?
