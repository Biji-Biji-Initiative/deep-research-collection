# Divergence Matrix: What Varies Across AGENTS.md Files

> Last updated: 2026-03-05

## Section Presence Matrix

| Section | reka | mereka-lms | bbi-infra | nfc | g-fin | climate | vps | team-skills | analytics | zoom |
|---------|------|-----------|-----------|-----|-------|---------|-----|-------------|-----------|------|
| Overview | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| Commands | Y | Y | Y | Y | Y | Y | Y | - | Y | - |
| Structure | Y | Y | Y (table) | Y (tree) | Y | Y | Y | Y | Y | - |
| Conventions | Y | Y | Y | Y (bold) | Y | Y | Y | Y | Y | Y |
| Validation | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| Boundaries | - | Y | Y (CRITICAL) | Y | Y | Y | Y | Y | Y | Y |
| Deployment | Y | Y | Y (Velero) | Y | Y | - | Y | - | Y | - |
| Security | Y | - | Y (full) | Y | - | - | Y | - | Y | - |
| Specs/Docs | - | Y | - | Y | Y | Y | - | - | - | - |
| Multi-agent | - | - | - | Y | - | Y | - | - | Y | - |
| Troubleshooting | - | Y | - | Y | - | - | - | - | - | Y |
| Gates | - | - | - | - | - | - | - | - | - | Y |

## Unique Patterns (only in one file)

| Pattern | Found In | Description |
|---------|----------|-------------|
| Machine-readable invariants (YAML) | g-finances | Constraints expressed as parseable YAML, not prose |
| Gate-based delivery (G0-G4) | zoom-rtms | CI-enforced progression with exit codes |
| Velero backup pre-flight | bbi-infrastructure | Mandatory backup before any destructive op |
| Receipt-gated narration | climate-exchange | Deterministic specialist routing pattern |
| Tutor methodology | mereka-lms | Open edX specific configuration and patching |
| PocketBase service templates | vps/infrastructure | Template for adding new PocketBase instances |
| Skill format specification | team-skills | Meta: defines how skills should be structured |

## Structural Divergences

| Aspect | Approach A | Approach B | Files Using A | Files Using B |
|--------|-----------|-----------|---------------|---------------|
| Structure format | Directory tree | Bullet list | nfc, climate | reka, analytics |
| Structure format | Table | - | bbi-infra | - |
| Boundary format | 3-tier (Always/Ask/Never) | CRITICAL warnings | 7 files | bbi-infra |
| Command format | Code blocks with comments | Bare commands | nfc, g-fin | reka, analytics |
| Length philosophy | Comprehensive (400+) | Minimal (<100) | nfc, g-fin, mereka-lms | zoom-rtms, team-skills |

## Standardization Opportunities

### High value (affects many files, easy to standardize)
1. **Boundary format** — Adopt 3-tier everywhere, add severity levels for infra
2. **Command format** — Always use code blocks with `# comments`
3. **"Last updated" date** — Mandatory, enforced by linter
4. **Structure format** — Standardize on directory tree for <20 entries, table for >20

### Medium value (improves consistency)
5. **Section ordering** — Fixed order matching the template
6. **Specs/docs convention** — Reference skill, don't inline
7. **Multi-agent section** — Optional but standardized format when present

### Low value (keep as project-specific)
8. **Troubleshooting** — Format varies, content is inherently unique
9. **Gates** — Only zoom-rtms uses it; may become a pattern
10. **Domain-specific sections** — Tutor methodology, PocketBase templates, etc.
