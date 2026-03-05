# Progressive Disclosure for Agent Instructions

> Last updated: 2026-03-05

## What Is It?

Show only what the agent needs right now. Point to more detail on demand. Agents get demonstrably worse with too much upfront context — bigger context windows do NOT solve "context rot."

## The Five Layers

| Layer | Contents | When Loaded | Token Cost |
|-------|----------|-------------|------------|
| **L0: Frontmatter** | name + description (YAML) | Always in context | ~20 tokens |
| **L1: AGENTS.md body** | Commands, style, boundaries | Session start | 200-800 tokens |
| **L2: Subdirectory AGENTS.md** | Package-specific guidance | Agent enters directory | 100-400 tokens |
| **L3: SKILL.md** | Detailed how-to for tasks | On demand (agent invokes) | 200-1000 tokens |
| **L4: Referenced files** | Full specs, API docs, schemas | Agent reads when instructed | Variable |

## Why It Matters

1. **Context rot** — irrelevant instructions degrade agent performance even when context window has room
2. **Token economics** — every line in AGENTS.md competes with actual code for context space
3. **Signal-to-noise** — agents follow instructions better when fewer, more relevant instructions are present
4. **Multi-agent** — different agents need different slices (explorer needs structure, implementor needs conventions)

## AGENTS.md v1.1 Proposal

[Issue #135](https://github.com/agentsmd/agents.md/issues/135) explicitly recommends progressive disclosure as a first-class pattern:
- Optional YAML frontmatter for metadata indexing
- Subdirectory scoping as the primary disclosure mechanism
- Skills/tools as the on-demand layer

## How Anthropic Implements It

Claude Code's skill system is a textbook progressive disclosure architecture:
1. **SKILL.md frontmatter** — indexed always, body loaded only when invoked
2. **Skills < 500 lines** — split into separate files if longer
3. **`context: fork`** — heavy skills get their own context window
4. **Agent routing** — skills declare which agent types should use them

Source: [Anthropic Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## Patterns for AGENTS.md

### Pattern 1: Layered Files (Monorepo)
```
repo/
├── AGENTS.md              # Global: commands, style, boundaries
├── packages/
│   ├── api/AGENTS.md      # API-specific: routes, middleware, auth
│   └── web/AGENTS.md      # Web-specific: components, styling, SSR
└── infrastructure/
    └── AGENTS.md          # Infra-specific: Terraform, K8s, CI
```

### Pattern 2: Reference Links (Single File)
```markdown
## Architecture
See `docs/architecture.md` for the full system design.
For API contracts, see `specs/api-v2.md`.
```
Agent reads these only when working on related tasks.

### Pattern 3: Conditional Sections (Agent-Type Tags)
```markdown
<!-- agent:explorer -->
## Project Structure
src/ — application code
tests/ — test suites
<!-- /agent:explorer -->

<!-- agent:implementor -->
## Conventions
- Use snake_case for Python, camelCase for TypeScript
- All new functions need docstrings
<!-- /agent:implementor -->
```
Not yet supported by any tool, but a natural evolution.

### Pattern 4: Skills as Disclosure Layer
```markdown
## Deployment
For deployment instructions, use the `k8s-deployer` skill.
For secrets management, use the `secrets-management` skill.
```
Body of AGENTS.md stays short; detail lives in skills.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| **Kitchen sink** | 500+ line AGENTS.md with everything | Split into subdirectory files + skills |
| **Copy-paste org rules** | Every repo repeats the same 50 lines | Global AGENTS.md or org-level rules |
| **Inline troubleshooting** | 100 lines of "if X then Y" | Move to referenced doc, link from AGENTS.md |
| **Full API docs** | Schemas, endpoints, examples inline | Reference the spec file |

## Key Articles

- [Why AI Agents Need Progressive Disclosure, Not More Data](https://www.honra.io/articles/progressive-disclosure-for-ai-agents)
- [Progressive Disclosure in AI Agent Skill Design (Towards AI)](https://pub.towardsai.net/progressive-disclosure-in-ai-agent-skill-design-b49309b4bc07)
- [Progressive Disclosure: Control Context and Tokens](https://medium.com/@martia_es/progressive-disclosure-the-technique-that-helps-control-context-and-tokens-in-ai-agents-8d6108b09289)
- [Progressive Disclosure Might Replace MCP](https://www.mcpjam.com/blog/claude-agent-skills)

## Our Situation

Current average AGENTS.md: **360 lines**. Combined with CLAUDE.md, skills, and rules, agents load **1500-3000 tokens** of instructions before seeing any code. Research suggests this is approaching the degradation threshold.

**Recommendation**: Target 150-250 lines for AGENTS.md body. Extract org-level content to global config. Use skills for detailed procedures.
