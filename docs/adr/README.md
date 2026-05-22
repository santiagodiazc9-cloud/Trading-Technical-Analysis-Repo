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

## Index

| ADR | Date | Status | Summary |
|-----|------|--------|---------|
| [0001](0001-rsi-70-no-new-longs.md) | 2026-05-08 | Accepted | No new longs when RSI > 70 on daily timeframe |
| [0002](0002-approved-setup-2day-staleness.md) | 2026-05-15 | Accepted | Approved setups auto-stale after 2 trading days without a fill |
| [0003](0003-approval-zone-immutability.md) | 2026-05-15 | Accepted | Agent cannot mutate entry zone, stop, target, or size intraday |
| [0004](0004-half-trigger-ledger.md) | 2026-05-15 | Accepted | Partial re-arm conditions logged and inherited across routines |
| [0005](0005-day-trading-session-approval.md) | 2026-05-20 | Accepted | Day trading uses session-level approval instead of per-trade gate |
| [0006](0006-market-posture-system.md) | 2026-05-22 | Accepted | SMA-based Market Posture System replaces the fixed price-level trip-wire |
| [0007](0007-short-selling-rules.md) | 2026-05-22 | Accepted | Short selling rules added — agent may now scan and propose short setups |

## Reading order

ADRs are listed numerically. To understand the *current* state of a rule, read the most recent ADR that touches it (find by grep). To understand *evolution*, read in order.
