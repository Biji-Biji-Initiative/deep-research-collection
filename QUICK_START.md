# Quick Start Guide

## Adding Research from a New Repository

### 1. Create Repository Folder
```bash
mkdir -p [repo-name]/deep-research
```

### 2. Add Repository README
```bash
cat > [repo-name]/README.md << EOF
# [Repository Name] Research

## Research Index

| Topic | Date | Status |
|-------|------|--------|
EOF
```

### 3. Create Research Folder
```bash
mkdir -p [repo-name]/deep-research/[topic-name]
```

### 4. Add Prompt and Result
```bash
# Copy template
cp templates/RESEARCH_TEMPLATE.md [repo-name]/deep-research/[topic-name]/prompt.md

# Create result file (use template sections)
touch [repo-name]/deep-research/[topic-name]/result.md
```

### 5. Update Indexes
- Update `[repo-name]/README.md` with research entry
- Update main `README.md` repository index

### 6. Commit and Push
```bash
git add [repo-name]/
git commit -m "[repo-name]: add research on [topic]"
git push
```

## Common Commands

### List All Research
```bash
find . -name "prompt.md" -type f
```

### Search Research Content
```bash
grep -r "search term" --include="*.md"
```

### Count Research by Repository
```bash
for dir in */; do
  count=$(find "$dir" -name "prompt.md" | wc -l)
  echo "${dir%/}: $count research reports"
done
```

## File Structure Reference

```
[repo-name]/
├── README.md                    # Repository index
└── deep-research/
    ├── [topic-1]/
    │   ├── prompt.md            # Research question
    │   └── result.md            # Research findings
    └── [topic-2]/
        ├── prompt.md
        └── result.md
```

## Tips

1. **Use descriptive folder names**: `firebase-migration-analysis` not `research-1`
2. **Include dates in prompts**: Helps with tracking and archival
3. **Cross-reference related research**: Link to other relevant reports
4. **Keep prompts focused**: One clear research question per report
5. **Update indexes**: Always update README files when adding new research

## Need Help?

- Check [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines
- Review [examples/](./examples/) for reference
- Open an issue for questions or suggestions
