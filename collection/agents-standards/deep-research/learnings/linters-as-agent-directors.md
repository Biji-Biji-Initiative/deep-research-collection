# Using Linters to Direct Agents

> Source: https://factory.ai/news/using-linters-to-direct-agents
> Found: 2026-03-05
> Relevance: Directly applies to our lint-agents-md.sh and how we enforce standards

## Key Thesis

As AI agents take over code generation, **linting rules become the primary enforcement mechanism**. Organizations should encode architectural principles into executable lint rules that agents can verify and self-correct against.

## Seven Categories of Agent-Focused Linting

1. **Grep-ability** — Named exports, consistent formatting (searchable code)
2. **Glob-ability** — Predictable file structure (reliable code placement)
3. **Architectural Boundaries** — Prevent cross-layer imports, module isolation
4. **Security & Privacy** — Block secrets, require input validation
5. **Testability** — Colocate tests, prevent network calls in unit tests
6. **Observability** — Standardize logging and error metadata
7. **Documentation Signals** — Require TSDoc for public APIs

## The Key Insight

> "Lint green" becomes the definition of "done."

Every rule you codify:
- Reduces review overhead
- Eliminates entire classes of regressions
- Turns architectural drift into auto-fixed diffs
- Enables agents to self-heal without human intervention

## How This Applies to Us

1. **Our `lint-agents-md.sh` is the right approach** — machine-checkable rules for AGENTS.md quality
2. **We should extend it** — not just section presence, but content quality checks
3. **Agents should run the linter themselves** — include lint command in AGENTS.md so agents self-check
4. **The cycle**: Observe agent mistakes → codify as lint rule → enforce → prevent regression
5. **Priority**: If you can only do one thing, make the codebase grep-able (named exports, absolute imports, predictable structure)

## Actionable for Our Standards

- Add to AGENTS.md template: a "Linting" section pointing to the project's lint config
- Consider: should `lint-agents-md.sh` also check that the project has its own code linting?
- The Factory recommendation of 150-line AGENTS.md aligns with progressive disclosure
