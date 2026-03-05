# Proposal 004: Audit Dashboard Workflow

> Status: Accepted
> Author: Gurpreet / Claude
> Date: 2026-03-05

## Problem

Miranda needs visibility into the current state of AGENTS.md across 100+ repos to drive standardization. But copying files into this repo creates stale snapshots that diverge immediately.

## Decision

**Option D: Linter + Dashboard Report (Hybrid)**

- Each repo owns its own AGENTS.md (source of truth stays there)
- `tools/audit-org.sh` fetches all repos via GitHub API, scores them, generates a report
- `tools/lint-agents-md.sh` is a single-repo linter any repo can run in CI
- Audit reports give the bird's-eye view without stale copies
- GitHub Action runs weekly, commits updated report

## Architecture

```
agents-standards/
├── tools/
│   ├── audit-org.sh              # Fetch + score all org repos
│   ├── lint-agents-md.sh         # Single-repo linter (for CI)
│   └── generate-adapters.sh      # AGENTS.md → copilot/gemini/cursor (future)
├── reports/
│   └── YYYY-MM-DD-audit.md       # Generated audit reports
└── .github/workflows/
    └── weekly-audit.yml          # Runs audit-org.sh on schedule
```

## Workflow

```
1. audit-org.sh runs (manually or via CI)
2. Fetches AGENTS.md from every org repo via GitHub API
3. Scores each file against the 21-point rubric
4. Generates reports/YYYY-MM-DD-audit.md with:
   - Per-repo scores and grades
   - Missing sections flagged
   - Line count vs 150-line target
   - Overlap detection (repeated content across repos)
   - Priority recommendations
5. Miranda reviews report → identifies worst repos →
   agent/human opens PR in that repo → improves AGENTS.md →
   next audit shows improvement
```

## Why Not Other Options

| Option | Why Not |
|--------|---------|
| Copy files into this repo | Stale on day one; two sources of truth |
| PR bot that auto-fixes | Too complex for now; standards still evolving |
| Linter only (no dashboard) | No central visibility for Miranda |
| Git submodules | Terrible DX; breaks on private repos |

## Future Extensions

- GitHub Action opens issues in repos scoring below threshold
- Linter available as a reusable workflow other repos can reference
- Adapter generation (proposal 003) integrated into the same tooling
