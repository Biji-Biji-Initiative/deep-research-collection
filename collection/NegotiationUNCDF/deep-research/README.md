# Deep Research Organization

This directory contains two separate research initiatives:

## 1. General Research (`general_research/`)
Contains general deep research tools and documentation:
- **config/**: Configuration files for research parameters
- **logs/**: Execution logs and API responses
- **results/**: Research findings and analysis results
- **scripts/**: Python scripts for research execution
- **docs/**: Documentation and strategy files
  - COMPLETE_EVALUATION_STRATEGY.md
  - GRANT_EVAL_V3_IMPROVEMENT_SUMMARY.md
  - README_DEEP_RESEARCH.md
  - Additional implementation trackers and plans

## 2. Grant Eval V3 Research (`grant_eval_v3_research/`)
Specialized research for Grant Evaluation V3 system:
- **config/**: Research prompts and configurations
  - research_prompt.md
- **logs/**: API response logs from research sessions
- **results/**: Timestamped research results
  - Session summaries
  - Extracted analysis
  - API responses
  - Configuration snapshots
- **scripts/**: Research execution scripts
  - research_executor.py
- **docs/**: Grant Eval V3 specific documentation

## Directory Structure

```
deep_research/
├── general_research/
│   ├── config/
│   ├── logs/
│   ├── results/
│   ├── scripts/
│   │   ├── deep_research_setup.py
│   │   ├── execute_deep_research.py
│   │   ├── execute_grant_eval_v3_research.py
│   │   └── test_setup.py
│   └── docs/
│       ├── COMPLETE_EVALUATION_STRATEGY.md
│       ├── GRANT_EVAL_V3_IMPROVEMENT_SUMMARY.md
│       ├── README_DEEP_RESEARCH.md
│       ├── grant_eval_v3_deep_research_prompt.md
│       ├── grant_eval_v3_implementation_tracker.md
│       └── grant_eval_v3_research_plan.md
│
└── grant_eval_v3_research/
    ├── config/
    │   └── research_prompt.md
    ├── logs/
    │   └── api_responses_[timestamp].jsonl
    ├── results/
    │   └── [timestamp]/
    │       ├── api_responses.jsonl
    │       ├── research_results.json
    │       ├── session_config.json
    │       ├── session_summary.md
    │       └── EXTRACTED_ANALYSIS.md
    ├── scripts/
    │   └── research_executor.py
    └── README.md
```

## Usage

### General Research
Execute from the `general_research/scripts/` directory:
```bash
python execute_deep_research.py
```

### Grant Eval V3 Research
Execute from the `grant_eval_v3_research/scripts/` directory:
```bash
python research_executor.py
```

## Purpose
Both research tracks aim to improve the Grant Evaluation system through:
- Deep analysis of evaluation methodologies
- Testing and validation of approaches
- Documentation of findings and improvements
- Iterative refinement of the evaluation framework