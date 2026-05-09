# Architecture Decision Records (ADRs)

This directory holds the audit trail of strategy and architecture changes for the trading agent. Every meaningful rule change — risk parameters, indicator thresholds, routine logic, infrastructure swaps — gets one ADR.

## Why

Memory files (`learnings.md`, `strategy.md`) drift over time. ADRs are immutable: once accepted, they capture the *moment* a decision was made and the *reasoning* at that moment. Future-Santiago reading "we changed RSI threshold from 70 to 75" in `strategy.md` won't know why; ADR-0007 explains it was after three trades caught by the 70 threshold all reversed within a day.

## Workflow

1. **Authoring**: The Friday Weekly Review routine creates a new ADR if any rule changed. Manual ADRs are also fine — write one any time you make a non-trivial change.
2. **Numbering**: Sequential 4-digit prefix (`0001-…`, `0002-…`). Never reuse a number, even if an ADR is rejected.
3. **Status**: `Proposed` → `Accepted` (default) → `Superseded by ADR-NNNN` (if a later ADR replaces it). `Rejected` for plans that didn't happen.
4. **Indexing**: Each ADR is also stored in RuFlo memory under namespace `trading-adrs` with key `adr/NNNN`, so a future routine can semantically search across the full decision log.

## File naming

`<NNNN>-<short-slug>.md` — e.g. `0001-tighten-rsi-threshold-to-75.md`.

## Template

See `routines/5_weekly_review.md` step 4a for the canonical ADR template.

## Reading order

ADRs are listed numerically. To understand the *current* state of a rule, read the most recent ADR that touches it (find by grep). To understand *evolution*, read in order.
