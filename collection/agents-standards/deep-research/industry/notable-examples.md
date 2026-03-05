# Notable AGENTS.md Examples from Industry

> Last updated: 2026-03-05

## Reference Implementations

| Repo | Stars | Lines | Notable Pattern | URL |
|------|-------|-------|-----------------|-----|
| **openai/codex** | High | 88 files | Hierarchical sub-directory AGENTS.md throughout monorepo | [GitHub](https://github.com/openai/codex/blob/main/AGENTS.md) |
| **agentsmd/agents.md** | Canonical | Self-referential | The spec itself as an AGENTS.md | [GitHub](https://github.com/agentsmd/agents.md/blob/main/AGENTS.md) |
| **github/awesome-copilot** | Community | Curated | Community-contributed agent configs | [GitHub](https://github.com/github/awesome-copilot/blob/main/AGENTS.md) |
| **github/spec-kit** | Official | Spec-driven | GitHub's spec-driven development toolkit | [GitHub](https://github.com/github/spec-kit/blob/main/AGENTS.md) |

## Collections & Galleries

| Resource | What It Contains | URL |
|----------|-----------------|-----|
| **PatrickJS/awesome-cursorrules** | Large collection of .cursorrules (transferable patterns) | [GitHub](https://github.com/PatrickJS/awesome-cursorrules) |
| **mgechev/skills-best-practices** | Professional skill authoring with LLM validation | [GitHub](https://github.com/mgechev/skills-best-practices) |

## What the Best Examples Have in Common

1. **Commands first** — build/test/lint with exact flags, not just tool names
2. **Structure section** — key directories explained in 5-10 lines
3. **Explicit boundaries** — "never touch X", "always do Y", "ask before Z"
4. **Real code snippets** — one example > three paragraphs of description
5. **Sub-150 lines at root** — detail pushed to subdirectories or referenced docs

## What To Study

- How openai/codex splits 88 AGENTS.md files across a monorepo
- How the canonical spec balances brevity with completeness
- How awesome-cursorrules maps tool-specific rules to universal patterns
