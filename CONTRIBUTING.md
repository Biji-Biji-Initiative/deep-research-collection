# Contributing Guide

Thank you for contributing to the Deep Research Collection! This guide will help you add new research reports properly.

## Getting Started

### Prerequisites

- Access to Biji-Biji Initiative GitHub organization
- Read access to source repositories
- Understanding of the research topic

### Initial Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Biji-Biji-Initiative/deep-research-collection.git
   cd deep-research-collection
   ```

2. Create a new branch for your contribution:
   ```bash
   git checkout -b add-research-[topic-name]
   ```

## Adding New Research

### Step 1: Create Repository Folder

If this is the first research from a repository, create its folder:

```bash
mkdir -p collection/[repo-name]/deep-research
```

Create a repository-specific README:

```bash
cat > collection/[repo-name]/README.md << EOF
# [Repository Name] Research

This folder contains deep research reports for [repository-name].

## Research Index

| Topic | Date | Status |
|-------|------|--------|
| [Add entries as research is added] | | |

## Quick Links

- [Repository URL](https://github.com/Biji-Biji-Initiative/[repo-name])
- [Related Documentation](link)
EOF
```

### Step 2: Create Research Folder

```bash
mkdir -p collection/[repo-name]/deep-research/[topic-name]
```

### Step 3: Add Prompt

Create `prompt.md` using the template:

```bash
cp templates/RESEARCH_TEMPLATE.md collection/[repo-name]/deep-research/[topic-name]/prompt.md
# Edit the file with your research prompt
```

### Step 4: Add Results

Create `result.md` using the template:

```bash
# Use the result section from the template
# Edit collection/[repo-name]/deep-research/[topic-name]/result.md
```

### Step 5: Update Index

Update the repository's README.md:

```markdown
## Research Index

| Topic | Date | Status |
|-------|------|--------|
| [Your Topic](./deep-research/[topic-name]) | YYYY-MM-DD | Completed |
```

Update the main README.md repository index:

```markdown
| Repository | Research Count | Last Updated |
|------------|---------------|--------------|
| [repo-name](./collection/[repo-name]/) | [count] | YYYY-MM-DD |
```

## File Naming Conventions

- **Folder names**: Use kebab-case (e.g., `firebase-migration-analysis`)
- **Files**: Always use `prompt.md` and `result.md`
- **Branches**: Use format `add-research-[topic]` or `update-research-[topic]`

## Commit Message Format

```
[repo-name]: [action] research on [topic]

- Added prompt for [topic]
- Completed research on [topic]
- Updated [topic] with new findings
```

Example:
```
mereka-lms: add research on firebase migration

- Added research prompt
- Completed analysis of migration strategies
- Documented recommendations
```

## Pull Request Process

1. **Create PR** with descriptive title:
   - `[repo-name]: Add research on [topic]`
   - `[repo-name]: Update research on [topic]`

2. **Description should include**:
   - Summary of research
   - Why it's important
   - Key findings (1-2 sentences)
   - Link to original issue/discussion (if applicable)

3. **Review requirements**:
   - At least one approval from team member
   - CI checks must pass (if configured)

4. **Merge**:
   - Squash and merge preferred
   - Delete branch after merge

## Updating Existing Research

1. Create branch: `update-research-[topic]`
2. Make updates to `result.md`
3. Add changelog section:

```markdown
## Changelog

### [YYYY-MM-DD]
- Updated findings based on new data
- Added section on implementation challenges
- Revised recommendations
```

## Best Practices

### For Prompts
- Be specific and focused
- Include business context
- Define clear scope and boundaries
- List expected deliverables

### For Results
- Start with executive summary
- Use clear headings and structure
- Include evidence and data
- Provide actionable recommendations
- Link to relevant resources

### For Maintenance
- Review and update outdated research quarterly
- Archive research older than 1 year to `archived/` folder
- Cross-reference related research topics

## Questions?

- Open an issue in this repository
- Contact the team in #dev-discussions Slack channel
- Tag @biji-biji/dev-team in your PR

## License

By contributing to this repository, you agree that your contributions will be licensed under the same license as this project.
