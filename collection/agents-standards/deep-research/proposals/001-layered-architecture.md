# Proposal 001: Layered Instruction Architecture

> Status: Draft
> Author: Gurpreet / Claude
> Date: 2026-03-05

## Problem

Every AGENTS.md repeats org-level content (git workflow, secrets pattern, PM2 rules, ArgoCD conventions). This causes 400+ lines of duplication, staleness when standards change, and context budget waste.

## Proposed Architecture

```
Layer 0: Tool Global Config (always loaded)
  ~/.claude/CLAUDE.md, ~/.codex/AGENTS.override.md
  → User preferences, model routing, global rules

Layer 1: Org-Level AGENTS.md (loaded per org membership)
  agents-standards/AGENTS.md
  → Shared conventions: git workflow, PR format, code style, boundary model
  → NOT copied into repos — referenced via tool config or CI

Layer 2: Category AGENTS.md (loaded per project type)
  agents-standards/templates/agents-md/{type}.md
  → K8s app: ArgoCD, Helm, namespace patterns
  → Standalone: PM2, Caddy, build patterns
  → Infrastructure: data safety, Velero, Kyverno
  → Forked: upstream sync, customization boundaries

Layer 3: Project AGENTS.md (checked into each repo)
  {repo}/AGENTS.md
  → Project-specific: commands, structure, conventions, boundaries
  → ONLY project-unique content; no org/category duplication
  → Target: 100-150 lines

Layer 4: Subdirectory AGENTS.md (optional, for monorepos)
  {repo}/packages/{pkg}/AGENTS.md
  → Package-specific guidance
  → Target: 30-80 lines

Layer 5: Skills (on-demand)
  SKILL.md files loaded when agent invokes them
  → Detailed procedures, troubleshooting, deployment guides
```

## How Tools Compose These Layers

### Claude Code
- L0: `~/.claude/CLAUDE.md` + `~/.claude/rules/*.md` (auto-loaded)
- L1: Could use a shared skill or plugin that loads org AGENTS.md
- L3: `CLAUDE.md` at project root (auto-loaded)
- L5: Skills invoked on demand

### OpenAI Codex
- L0: `~/.codex/AGENTS.override.md` (auto-loaded)
- L3: `AGENTS.md` at project root (auto-loaded)
- L4: Subdirectory `AGENTS.md` (auto-loaded on entry)

### GitHub Copilot
- L1: `.github/copilot-instructions.md` (org-level via .github repo)
- L3: `.github/copilot-instructions.md` (repo-level)
- L4: `.instructions.md` (file-scoped with YAML frontmatter)

## Migration Path

### Phase 1: Identify org-level content (this proposal)
- Audit all AGENTS.md files for repeated content ✅ (done in overlap-analysis.md)
- Define what belongs at each layer

### Phase 2: Create org-level AGENTS.md
- Extract shared content to `agents-standards/AGENTS.md` (already started)
- Define the "thin project AGENTS.md" template

### Phase 3: Slim down project files
- Remove duplicated content from each repo's AGENTS.md
- Replace with links: "See org standards at agents-standards/AGENTS.md"
- Target: reduce average from 360 to 150 lines

### Phase 4: Tooling
- CI linter enforces layer separation (no org content in project files)
- Template generator pre-fills Layer 3 from project metadata

## What Belongs Where

| Content | Layer | Rationale |
|---------|-------|-----------|
| Git workflow (branching, commit format) | L1 Org | Same across all repos |
| PR conventions | L1 Org | Same across all repos |
| Code style (naming, formatting) | L1 Org | Same across all repos |
| Secrets management pattern | L1 Org | Same pipeline everywhere |
| ArgoCD GitOps workflow | L2 Category (K8s) | Only K8s repos need this |
| PM2 deployment pattern | L2 Category (Standalone) | Only standalone repos |
| Data safety / Velero | L2 Category (Infra) | Only infrastructure repos |
| Build commands | L3 Project | Different per project |
| Project structure | L3 Project | Different per project |
| Project-specific conventions | L3 Project | Different per project |
| Boundaries (Always/Ask/Never) | L3 Project | Different per project |
| Troubleshooting | L5 Skill | On-demand, detailed |
| Deployment procedures | L5 Skill | On-demand, detailed |

## Open Questions

1. How do tools that don't support org-level configs (Codex, Windsurf) get L1 content?
   - Option A: Include L1 as a preamble in L3 (defeats purpose)
   - Option B: CI copies L1 content into repo on push (generated section)
   - Option C: Accept that some tools won't get org context
2. Should L1 content be a skill that agents can invoke?
3. How to handle repos outside the org (forks, external)?
