# Research Template

Use this template when adding new deep research reports to this collection.

## Folder Structure

```
[research-topic]/
├── prompt.md
└── result.md
```

## prompt.md Template

```markdown
# Research Prompt

**Date**: [YYYY-MM-DD]
**Repository**: [source-repo-name]
**Researcher**: [name or team]
**Priority**: [high/medium/low]

## Research Question

[Clear, specific question or topic to research]

## Context

[Background information and why this research is needed]

## Scope

- What should be covered
- What should NOT be covered
- Any constraints or limitations

## Expected Deliverables

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

## References

- [Link to relevant issue/PR]
- [Related documentation]
- [External resources]
```

## result.md Template

```markdown
# Research Results

**Research Topic**: [topic name]
**Date Conducted**: [YYYY-MM-DD]
**Date Completed**: [YYYY-MM-DD]

## Executive Summary

[2-3 sentence summary of key findings]

## Key Findings

### Finding 1
[Description, evidence, and implications]

### Finding 2
[Description, evidence, and implications]

## Detailed Analysis

### Background
[Detailed context]

### Methodology
[How the research was conducted]

### Results
[Detailed findings with evidence]

## Recommendations

1. [Recommendation 1]
   - Rationale: [why]
   - Priority: [high/medium/low]
   - Effort: [high/medium/low]

2. [Recommendation 2]
   - Rationale: [why]
   - Priority: [high/medium/low]
   - Effort: [high/medium/low]

## Action Items

- [ ] [Action item 1] - [assignee] - [due date]
- [ ] [Action item 2] - [assignee] - [due date]

## References

- [Link 1]
- [Link 2]

## Appendix

[Additional data, code snippets, or supporting materials]
```

## Best Practices

1. **Naming Conventions**
   - Use kebab-case for folder names: `firebase-migration-analysis`
   - Be descriptive but concise
   - Include date if time-sensitive: `2024-01-auth-flow-analysis`

2. **Content Guidelines**
   - Keep prompts focused and specific
   - Include context and business impact
   - Document methodology in results
   - Provide actionable recommendations

3. **Maintenance**
   - Update repository index in main README
   - Add tags/labels for categorization
   - Link to related research when applicable

4. **Review Process**
   - Have research reviewed by at least one team member
   - Update findings if new information emerges
   - Archive outdated research in `archived/` subfolder
