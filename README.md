# Deep Research Collection

Centralized repository for collecting and organizing deep research reports across all Biji-Biji Initiative repositories.

## Purpose

This repository serves as a centralized knowledge base for all deep research reports generated across our projects. Each research report includes:
- Original research prompt/question
- Complete research findings and results
- Metadata about the source repository

## Structure

```
deep-research-collection/
├── README.md
├── templates/
│   └── RESEARCH_TEMPLATE.md
├── CONTRIBUTING.md
├── collection/
│   └── [repo-name]/
│       ├── README.md
│       └── deep-research/
│           ├── [topic-1]/
│           │   ├── prompt.md
│           │   └── result.md
│           └── [topic-2]/
│               ├── prompt.md
│               └── result.md
```

## Usage

### Adding Research from a Repository

1. Navigate to the appropriate repository folder (create if it doesn't exist)
2. Create a new folder under `deep-research/` with a descriptive name
3. Add two files:
   - `prompt.md`: The original research question or prompt
   - `result.md`: The complete research findings

### Example Structure

```
collection/
├── mereka-lms/
│   ├── README.md
│   └── deep-research/
│       ├── firebase-to-mongodb-migration/
│       │   ├── prompt.md
│       │   └── result.md
│       ├── authentication-flow-analysis/
│       │   ├── prompt.md
│       │   └── result.md
│       └── course-progress-tracking/
│           ├── prompt.md
│           └── result.md
│
└── reka-slackbot/
    ├── README.md
    └── deep-research/
        ├── temporal-workflow-patterns/
        │   ├── prompt.md
        │   └── result.md
        └── agent-orchestration-analysis/
            ├── prompt.md
            └── result.md
```

## Repository Index

| Repository | Research Count | Last Updated | Focus Areas |
|------------|---------------|--------------|-------------|
| [NegotiationUNCDF](./collection/NegotiationUNCDF/) | 33 | March 2025 | Grant evaluation, mock orchestrator, iterative learning |
| [climate-exchange](./collection/climate-exchange/) | 30 | March 2025 | Climate data, agentic systems, visual system implementation |
| [agents-standards](./collection/agents-standards/) | 15 | March 2025 | Agent architecture, tool compatibility, progressive disclosure |
| [microsoft-community-training](./collection/microsoft-community-training/) | 13 | March 2025 | Azure resources, video playback, MFA investigation |
| [mereka-backend-v2](./collection/mereka-backend-v2/) | 5 | March 2025 | System analysis, model design, API requirements |
| [mereka-lms](./collection/mereka-lms/) | 3 | March 2025 | Open edX deployment, AGENTS.md audit |
| [team-analytics](./collection/team-analytics/) | 2 | March 2026 | Agent instructions audit, blueprint-driven architecture |
| [zoom-rtms](./collection/zoom-rtms/) | 1 | March 2026 | AGENTS.md compliance, blueprint adoption, service archetype |
| [mereka-agent-e](./collection/mereka-agent-e/) | 1 | March 2026 | Repo-standardization review, placeholder repo assessment |
| [vps-infrastructure](./collection/vps-infrastructure/) | 1 | February 2026 | Infisical secrets management, infrastructure automation |
| [sicci](./collection/sicci/) | 1 | February 2026 | AI search agent implementation |
| [elevate](./collection/elevate/) | 1 | March 2025 | LEAPS framework, participant tracking |

**Total**: 12 repositories, 106 research documents

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on adding new research reports.

## License

This repository is part of Biji-Biji Initiative's knowledge management system.
