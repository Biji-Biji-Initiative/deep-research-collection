# Deep Research Remap Matrix

This file maps deep-research source documents to executable backlog items so no input is lost during consolidation.

## Source Documents

1. `docs/deep-research/CIE Audit and Consolidation Plan.pdf`
2. `docs/deep-research/Audit and Consolidation Plan for entity["organization","CIE","climate intelligence exchange"] Aut.pdf` (legacy filename retained)
3. `docs/deep-research/CIE Deep Research Audit of Agent Runtime and Data Plane Reliability.pdf`
4. `docs/deep-research/CIE Frontend UX Research Brief for a World-Class Next.js + shadcn-Style Stakeholder Experience.pdf`
5. `docs/deep-research/CIE Stakeholder UX Overhaul Research Brief and Implementation Plan.pdf`

## Canonical Work Mapping

| Source | Backlog Mapping | Lane |
|---|---|---|
| Audit + Consolidation Plan (both filenames) | `Fix 17`, `Fix 19`, `Fix 21`, `PLAN-6`, `GATE-1` | Coordination + Agent Pipeline |
| Runtime/Data Plane Reliability Audit | `Fix 7`, `Fix 8`, `Fix 10`, `Fix 16`, `Fix 20`, `Fix 22`, `Fix 23`, `Fix 24`, `Fix 25`, `Fix 26`, `Fix 27`, `Fix 28`, `PLAN-3` | Data Plane |
| Frontend UX Research Brief | `Fix 30` through `Fix 45` | UI |
| Stakeholder UX Overhaul Plan | `Fix 31` through `Fix 45` (Wave UX-1 / UX-2 execution) | UI |

## Guardrails

- Canonical tracker: `docs/data-plane/BACKLOG.md`
- Compatibility path for legacy filename retained (same mapping as canonical filename):
  - `docs/deep-research/Audit and Consolidation Plan for entity["organization","CIE","climate intelligence exchange"] Aut.pdf`
- Do not archive these source PDFs until all mapped items are closed and verified.
