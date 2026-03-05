---
title: AI Search + Agent SICCI Deep Audit (2026-02-19)
status: draft
vehicle: research
created: 2026-02-19
updated: 2026-02-19
author: SICCI Engineering
---

# AI Search + Agent SICCI Deep Audit (2026-02-19)

## Overview

This audit evaluates the end-to-end AI concierge and search implementation across UI/UX, API behavior, retrieval grounding, mobile ergonomics, and production readiness.

Core objective: make the product lovable and trustworthy by enforcing a strict boundary:

- Search = deterministic find and navigation.
- Agent SICCI = probabilistic AI guidance with grounded sources.

## Usage

Use this audit as the execution brief for P0/P1/P2 work:

1. Fix boundary confusion and silent failure modes first (P0).
2. Tighten API operability and grounding quality (P1).
3. Add observability and regression safety rails (P2).

## Executive Summary

What is strong:

- AI responses are grounded against SICCI search results and can return citations.
- The concierge panel supports explicit warnings and retry behavior.
- Recent mobile/fixed-control hardening has improved baseline usability.

What is blocking lovable quality:

- Search and AI behavior were mixed inside the same command surface.
- Duplicate AI provider paths increased drift risk.
- Deterministic search failures were not consistently visible to users.

## Severity-Ranked Findings

| ID   | Severity | Finding                                                    | Impact                                    |
| ---- | -------- | ---------------------------------------------------------- | ----------------------------------------- |
| F-01 | P0       | Search and agent behavior mixed in command surface         | Confusing user mental model, trust loss   |
| F-02 | P0       | Silent/unclear search failure states                       | Users interpret outage as missing content |
| F-03 | P0       | Assistant route lacked timeout and bounded output controls | Unpredictable latency/cost and brittle UX |
| F-04 | P1       | Coexisting assistant/concierge provider paths              | Maintenance drift and demo inconsistency  |
| F-05 | P1       | Citation quality not claim-linked                          | Lower confidence in AI answers            |
| F-06 | P1       | Fixed-controls layering risk on mobile                     | Overlay obstruction risk                  |

## Search vs Agent Boundary Contract

### UX contract

- Search surfaces (`/search`, Cmd+K) must only show deterministic navigation/search output.
- Agent SICCI widget must own AI answering and source-backed guidance.

### Technical contract

- Search surfaces call `/api/search` and `/api/search/suggestions` only.
- Agent SICCI calls `/api/ai/concierge` only.
- Command-center exports must not encourage duplicate production AI wiring.

## Mobile UX Audit Notes

- Fixed utility controls must not obstruct overlays or dialogs.
- Agent SICCI must remain full-height, dismissible, and scroll-safe on mobile.
- Focus-mode expansion must always allow easy collapse and recovery.

## API + Retrieval Audit Notes

- Grounding pipeline is directionally correct: site search -> context -> response.
- API routes need hard timeouts, bounded output, and explicit typed errors.
- Retrieval failures must produce actionable user-visible fallback guidance.

## Data Coverage / Built-Not-Integrated

- Public data grounding currently covers members, organizations, people, events, news, testimonials, and pages.
- Next integration opportunity: structured claim-to-citation mapping in AI response payloads.

## Implementation Plan

### P0 (48 hours)

1. Keep `SearchCommand` deterministic only.
2. Keep AI in `SicciAgentWidget` only.
3. Restore explicit search error UI + retry.
4. Add API timeout and bounded generation controls.

### P1 (7 days)

1. Remove duplicate production AI wiring paths.
2. Add claim-linked citation rendering.
3. Tighten i18n and copy consistency for search/agent separation.

### P2 (30 days)

1. Add AI/search operational telemetry dashboards.
2. Add mobile regression e2e tests for overlays and fixed controls.
3. Expand retrieval quality and confidence instrumentation.

## Verification Checklist

- `pnpm --filter @sicci/web lint`
- `pnpm --filter @sicci/web typecheck`
- `pnpm --filter @sicci/web test __tests__/api/ai-concierge.test.ts __tests__/api/search.test.ts __tests__/search.test.ts __tests__/unit/search.test.ts`
- `pnpm --filter @sicci/web test tests/unit/command-center/assistant-provider.test.ts tests/unit/command-center/concierge-grounding.test.ts tests/unit/command-center/search-provider.test.ts`
- `pnpm --filter @sicci/web test __tests__/components/concierge/ConciergePanel.test.tsx`
- `pnpm -s specs:lint && pnpm -s docs:lint`

## Related

- `docs/features/global-search.md`
- `docs/features/ai-concierge.md`
- `specs/platform/search.spec.md`
- `specs/platform/ai-concierge.spec.md`
- `docs/architecture/frontend-production-ux-tracker.md`
