# Pain Points: What's Broken in Our Agent Instructions

> Last updated: 2026-03-05

## P1: Critical Issues

### AGENTS.md vs CLAUDE.md confusion
- **Problem**: Some repos have both files with overlapping content. Agents don't know which takes precedence.
- **Impact**: Conflicting instructions, wasted context window
- **Evidence**: nfc-cards has 668-line AGENTS.md AND a CLAUDE.md; reka-slackbot has both
- **Proposed fix**: AGENTS.md = universal (all tools read it). CLAUDE.md = Claude-specific overrides only (memory, skills, hooks). See proposal 001.

### No sync mechanism
- **Problem**: When org standards change, 100+ repos need manual updates
- **Impact**: Standards drift; new rules never reach old repos
- **Evidence**: Priority list shows 101 repos pending; only 11 done
- **Proposed fix**: Org-level AGENTS.md inherited automatically (tool config, not copy-paste)

### Context budget exceeded
- **Problem**: Agents load AGENTS.md + CLAUDE.md + rules/ + skills + memory = 2500-3000 tokens before seeing code
- **Impact**: Reduced effective intelligence; "context rot"
- **Evidence**: Internal average is 360 lines per AGENTS.md alone
- **Proposed fix**: Progressive disclosure (see proposal 002); target 150-250 lines

## P2: High Priority

### Duplication causes staleness
- **Problem**: Same content in 3-5 files means updates happen in some but not all
- **Impact**: Agents get contradictory instructions depending on which repo they're in
- **Evidence**: 405 lines of duplicated content across ecosystem
- **Proposed fix**: Single source of truth with links (see overlap-analysis.md)

### No linting or validation
- **Problem**: Templates exist but nothing enforces them
- **Impact**: Files drift from standard; quality varies 15-20/21
- **Evidence**: vps/infrastructure scores 15/21 (B-) with no automated feedback
- **Proposed fix**: CI linter that checks section presence, line count, date, boundaries

### Mixed human/agent audience
- **Problem**: Some AGENTS.md files read like READMEs with agent instructions mixed in
- **Impact**: Agents process human-oriented prose that wastes context
- **Evidence**: mereka-lms has narrative paragraphs alongside commands
- **Proposed fix**: AGENTS.md is strictly for agents. Human docs go in README or docs/

## P3: Medium Priority

### No agent-type targeting
- **Problem**: All agents read the full file even when most sections aren't relevant
- **Impact**: Explorer agents load deployment instructions; reviewers load build commands
- **Evidence**: Industry moving toward agent-type tags (not yet standard)
- **Proposed fix**: Watch AGENTS.md v1.1 proposal; prototype with section comments

### Forked repos have stale instructions
- **Problem**: Forked repos (cal.com, twenty) have AGENTS.md that may conflict with upstream
- **Impact**: Agent edits may break upstream sync
- **Evidence**: cal.com has our AGENTS.md + upstream's conventions
- **Proposed fix**: Forked repo template should explicitly address upstream relationship

### No effectiveness measurement
- **Problem**: No way to know if an AGENTS.md is actually helping
- **Impact**: Can't justify time spent maintaining them
- **Evidence**: Anecdotal only ("agents seem to do better with good AGENTS.md")
- **Proposed fix**: Track agent error rates per repo; correlate with AGENTS.md quality score

## P4: Nice to Have

### No cross-tool testing
- **Problem**: AGENTS.md optimized for Claude Code; untested with Copilot, Cursor, Codex
- **Impact**: Other tools may interpret instructions differently
- **Proposed fix**: Test key repos with multiple tools; document behavioral differences

### No deprecation lifecycle
- **Problem**: Sections become stale but aren't removed
- **Impact**: Agents follow outdated instructions
- **Proposed fix**: Quarterly audit with scoring rubric (already in standard, not enforced)
