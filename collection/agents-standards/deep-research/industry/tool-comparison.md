# AI Coding Tool Instruction File Comparison

> Last updated: 2026-03-05

## The Landscape

AGENTS.md is now an official open standard under the **Agentic AI Foundation (AAIF)** / Linux Foundation (announced Dec 2025). Co-founded by OpenAI, Anthropic, and Block. Adopted by **60,000+ repos** on GitHub since Aug 2025.

Canonical spec: [agents.md](https://agents.md/) | [GitHub repo](https://github.com/agentsmd/agents.md)

## Tool-by-Tool Matrix

| Tool | Primary File | Secondary / Legacy | AGENTS.md Support | Size Guideline |
|------|-------------|-------------------|-------------------|----------------|
| **Claude Code** (Anthropic) | `CLAUDE.md` | `~/.claude/CLAUDE.md` (global), `SKILL.md` (skills) | Yes (reads it) | < 300 lines |
| **OpenAI Codex** | `AGENTS.md` | `AGENTS.override.md` (global in `~/.codex/`) | Native (co-created it) | < 500 lines |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.instructions.md` (file-scoped, YAML frontmatter) | Yes (since Aug 2025) | No official limit |
| **Cursor** | `.cursor/rules/*.mdc` | `.cursorrules` (legacy, deprecated) | Yes | Per-rule scoping |
| **Windsurf** | `.windsurfrules` | `global_rules.md` (global) | Native | No official limit |
| **Google Jules / Gemini CLI** | `AGENTS.md` | `GEMINI.md` (session context) | Native | No official limit |
| **Factory (Droid)** | `AGENTS.md` | `.factory/droids/*.md` | Native | < 150 lines |
| **Devin** | `AGENTS.md` | Built-in knowledge mgmt | Native | No official limit |
| **VS Code Copilot Agents** | `.github/agents/*.md` | `.instructions.md` | Yes | Per-agent scoping |

## Key Insight

AGENTS.md is the **universal baseline** every tool reads. Tool-specific files (CLAUDE.md, .cursorrules, .windsurfrules) add vendor-specific features but are not mutually exclusive.

## Instruction Chain (how files compose)

```
Global (~/.codex/AGENTS.override.md or ~/.claude/CLAUDE.md)
  → Repo root AGENTS.md (universal)
  → Repo root CLAUDE.md / .cursorrules / etc. (tool-specific)
  → Subdirectory AGENTS.md (scoped)
  → SKILL.md (on-demand, progressive disclosure)
  → Referenced docs (agent reads when instructed)
```

## Governance

**Agentic AI Foundation (AAIF)** under Linux Foundation:
- Anchor projects: AGENTS.md (OpenAI), MCP (Anthropic), goose (Block)
- Members: OpenAI, Anthropic, Block, Google, Microsoft/GitHub, Cursor, Factory, Amp
- Website: [aaif.io](https://aaif.io/)

## Related Standards

| Standard | Purpose | URL |
|----------|---------|-----|
| Agent Skills (agentskills.io) | SKILL.md specification for reusable capabilities | [agentskills.io/specification](https://agentskills.io/specification) |
| Model Context Protocol (MCP) | Tool/resource integration protocol | [modelcontextprotocol.io](https://modelcontextprotocol.io) |
| AGENT.md (singular) | Competing format with Amp support | [github.com/agentmd/agent.md](https://github.com/agentmd/agent.md) |

## Sources

- [AGENTS.md Official Site](https://agents.md/)
- [AAIF Announcement - Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
- [OpenAI co-founds AAIF](https://openai.com/index/agentic-ai-foundation/)
- [Anthropic Donates MCP to AAIF](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
- [AGENTS.md Emerges as Open Standard - InfoQ](https://www.infoq.com/news/2025/08/agents-md/)
- [OpenAI Codex AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md/)
- [GitHub Copilot Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [Cursor Rules Docs](https://cursor.com/docs/context/rules)
- [Windsurf AGENTS.md Docs](https://docs.windsurf.com/windsurf/cascade/agents-md)
- [Factory AGENTS.md Docs](https://docs.factory.ai/cli/configuration/agents-md)
- [Devin AGENTS.md Docs](https://docs.devin.ai/onboard-devin/agents-md)
