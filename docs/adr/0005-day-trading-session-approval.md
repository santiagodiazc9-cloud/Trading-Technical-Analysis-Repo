# ADR-0005: Day trading session approval — session-level gate replaces per-trade approval for intraday engine

**Date**: 2026-05-20
**Status**: Accepted
**Supersedes**: none (adds to CLAUDE.md Rule 15, does not replace it)

## Context

CLAUDE.md Rule 15 requires explicit user approval before any trade is placed. This works well for the swing trading workflow where proposals are posted to Discord, the user reviews them asynchronously, and taps Approve. Swing setups have hours to days between proposal and execution.

The day trading engine (`scripts/daytrader/engine.py`) polls every 5 minutes during market hours and acts on real-time signals. A per-trade approval loop at this cadence is not practical — by the time the user approves, the 5-minute window has passed.

## Decision

Day trading uses a **session-level approval** model:

- Each morning, the user explicitly approves a bounded trading session by setting `memory/daytrader_session.json`:
  ```json
  { "session_approved": true, "max_trades": 2, "max_loss_usd": 500, "trades_taken": 0, "loss_usd": 0.0 }
  ```
- This constitutes explicit user approval for up to `max_trades` trades within that session, with a hard stop at `max_loss_usd` drawdown.
- The engine reads this file before every order. If `session_approved` is `false`, no order is placed regardless of signal strength.
- The session expires at market close. The file is reset to `session_approved: false` at the start of every morning's pre-market routine.
- The user can revoke approval at any time by editing the file (e.g. from the web dashboard's session toggle) — the engine checks the file before each trade.

## Why this satisfies Rule 15

Rule 15 requires "explicit user approval". Setting `session_approved: true` with specific budget parameters is explicit approval — it defines the scope (number of trades, loss limit), the user has full visibility, and it can be revoked at any time. It is equivalent to saying "go ahead, take up to 2 trades today, stop if you lose $500."

This is the same mental model as a trader giving a desk operator a "discretionary order" for the session — the operator can act within the defined parameters without calling back for each fill.

## Consequences

- The web dashboard (Phase 3) will expose a session toggle on the `/daytrader` page.
- Discord slash command `/session approve|revoke` will be added (Phase 3).
- `memory/daytrader_session.json` is gitignored (runtime state, machine-specific).
- The pre-market routine (`routines/1_pre_market_research.md`) will reset `session_approved: false` and `trades_taken: 0` at the start of each day as a safety default.
