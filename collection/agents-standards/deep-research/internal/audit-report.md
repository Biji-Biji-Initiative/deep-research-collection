# Internal AGENTS.md Audit Report

> Last updated: 2026-03-05
> Scope: 12 AGENTS.md files across Biji-Biji Initiative repos on VPS

## Quality Scores (21-point rubric)

| Project | Lines | Score | Grade | Weakest Dimension |
|---------|-------|-------|-------|-------------------|
| nfc-cards | 668 | 20/21 | A+ | Signal-to-noise (too long) |
| bbi-infrastructure | 451 | 19/21 | A | Signal-to-noise |
| reka-slackbot | 291 | 19/21 | A | Maintenance (no date) |
| team-skills | 167 | 18/21 | A- | Completeness (meta, not app) |
| zoom-rtms | 40 | 18/21 | A- | Completeness (ultra-minimal) |
| climate-exchange | 387 | 18/21 | A- | Security (implicit) |
| g-finances | 490 | 17/21 | B+ | Enforceability |
| mereka-lms | 450 | 17/21 | B+ | Parsability (dense) |
| team-analytics | 220 | 17/21 | B+ | Completeness |
| ~/AGENTS.md (Global) | 483 | 16/21 | B | Signal-to-noise (broad) |
| vps/infrastructure | 367 | 15/21 | B- | Clarity (blurs boundaries) |

**Average: 360 lines, 17.6/21 score**

## Findings

### Strengths
- All files have working commands (not aspirational)
- Boundary sections (Always/Ask/Never) present in 8/11 files
- Spec-driven development adopted by 4 repos (g-finances, nfc-cards, climate-exchange, mereka-lms)
- Multi-agent coordination documented where needed

### Systemic Issues

1. **Too long** — 6 files exceed 150-line industry recommendation; avg is 360 lines
2. **Duplication** — ~400-500 lines of content repeated across files (see overlap-analysis.md)
3. **No dates** — Only 2 files have "Last updated" lines
4. **No versioning** — When standard changes, no mechanism to update 100+ repos
5. **Mixed audiences** — Some files serve both agents AND humans
6. **CLAUDE.md + AGENTS.md confusion** — Unclear which tool reads which; some repos have both with overlapping content

## Repo Category Patterns

### K8s Apps (reka-slackbot, mereka-lms, bbi-infrastructure, team-analytics)
- Heavy on deployment/ops sections
- ArgoCD GitOps patterns repeated
- Infisical secrets pattern repeated
- Average: 353 lines

### Standalone Apps (nfc-cards, g-finances, climate-exchange)
- PM2 patterns repeated
- Build tool specifics (Next.js --webpack, bun vs pnpm)
- Average: 515 lines (longest category)

### Infrastructure/Meta (vps/infrastructure, team-skills, ~/AGENTS.md)
- Broadest scope, lowest signal-to-noise
- Global rules that should live in org config, not per-file
- Average: 339 lines
