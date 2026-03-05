# Content Overlap Analysis

> Last updated: 2026-03-05

## Duplication Map

| Duplicated Content | Files | Lines Each | Total Waste | Fix |
|-------------------|-------|-----------|-------------|-----|
| Beads/CASS/NTM commands | 3 files | 30-50 | ~120 lines | Link to ~/AGENTS.md |
| Infisical secrets pattern | 5 files | 15-25 | ~100 lines | Link to secrets-management skill |
| Specs-vs-docs footer | 4 files | ~20 | ~80 lines | Link to specs-vs-docs skill |
| PM2 deployment workflow | 3 files | ~10 | ~30 lines | Link to PM2 skill |
| Next.js 16 build rules | 2 files | ~15 | ~30 lines | Canonical in nfc-cards, link elsewhere |
| ArgoCD GitOps workflow | 3 files | ~15 | ~45 lines | Link to gitops-deployment skill |
| **Total estimated** | | | **~405 lines** | |

## Centralization Strategy

### Already centralized (link, don't copy)
- `~/AGENTS.md` — VPS-wide conventions, NTM, CASS, beads
- `~/.claude/rules/secrets.md` — Infisical architecture
- `~/.claude/rules/pm2-apps.md` — PM2 patterns
- `~/.claude/rules/nextjs.md` — Next.js 16 rules
- `~/.claude/rules/gitops-enforcement.md` — ArgoCD rules
- `~/.claude/skills/secrets-management/SKILL.md` — Full secrets workflow

### Needs centralization (create new shared asset)
- **Org-level AGENTS.md** — Universal sections all repos need (git workflow, PR conventions, code style)
- **Deployment pattern library** — K8s vs PM2 vs Docker decision tree
- **Troubleshooting template** — Standard format for known issues section

## Impact of Deduplication

| Metric | Before | After (est.) | Change |
|--------|--------|-------------|--------|
| Avg file length | 360 lines | 180-250 lines | -30-50% |
| Maintenance burden | Update N files | Update 1 source | -80% |
| Agent context cost | ~2500 tokens | ~1500 tokens | -40% |
| Staleness risk | High (no sync) | Low (single source) | Significant |
