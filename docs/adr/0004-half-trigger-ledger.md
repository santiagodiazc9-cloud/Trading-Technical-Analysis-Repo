# ADR-0004: Half-trigger ledger — log partial re-arm conditions at the routine where they first fire

**Date**: 2026-05-15
**Status**: Accepted
**Supersedes**: none

## Context

The MSFT mean-reversion setup (Setup #2, originally proposed 2026-05-09) was resolved to PASS in the 2026-05-15 pre-market routine. The PASS came with an explicit re-arm gate carrying two conditions: **(a)** SMA 20 reclaim, and **(b)** positive MACD cross.

During the 2026-05-15 session, condition (a) fired and stuck:
- Pre-market: MSFT $409.44, below SMA 20 ($417.4) — gate open.
- Midday: MSFT $424.48, above SMA 20 ($417.5) — **condition (a) firing**.
- EOD: MSFT $423.39, above SMA 20 ($417.47), sustained the reclaim through the close — **condition (a) confirmed for the session**.

Condition (b) never fired (MACD histogram −1.15 at midday, −1.22 at EOD; line still below signal).

The midday routine wrote the half-trigger state into both `memory/open_positions.md` ("Half-trigger — see note below … Half of two required conditions met. Per the rule, **DO NOT propose** today. Watch for the MACD cross") and `memory/learnings.md` ("MSFT — partial trigger toward re-arming Setup #2"). The EOD routine inherited that state without re-deriving it; tomorrow's pre-market routine will start with the partial state already on the page.

This worked. The alternative — recomputing whether each re-arm condition fires at every routine, from scratch — would have meant the EOD routine re-running the SMA 20 reclaim check and re-discovering it, and Monday's pre-market routine doing the same. Cheap when there's one half-trigger to track; expensive when there are three setups each with a 2-or-3-condition gate.

This rule has been operating de facto since 2026-05-15 midday. This ADR codifies it.

## Decision

**Before** (implicit): Partial re-arm states were not formally tracked. Each routine independently re-evaluated whether each gate's conditions were currently met.

**After** (explicit, added to `memory/strategy.md`):

> When a multi-condition re-arm gate (set as part of a setup PASS or close-out) has **at least one but not all** of its conditions firing during a routine, the routine MUST log the partial state in two places:
>
> 1. In `memory/open_positions.md`, under the relevant setup's status block, with a heading like `Half-Trigger — N of M conditions met (as of YYYY-MM-DD HH:MM ET)`. List each condition individually and mark `MET` / `NOT YET`.
> 2. In `memory/learnings.md`, as a one-line summary entry under "Pattern Notes" or "Strategy Refinements" with the date and ticker.
>
> Subsequent routines (same day or next session) MUST read the half-trigger state and update it incrementally — confirming, downgrading (if a previously-met condition has flipped back), or upgrading (if another condition fires). A half-trigger does NOT count as a setup proposal and does NOT bypass the approval gate; a setup is only re-proposable when **all** gate conditions are firing simultaneously in the same routine.
>
> Half-triggers that go stale (no movement on the remaining conditions for **5 trading days**) are cleared from `open_positions.md` and the re-arm gate is closed without re-proposal. A fresh proposal is required to re-open the gate.

This rule applies to any setup whose PASS / close-out came with a multi-condition re-arm gate (e.g., "SMA 20 reclaim AND positive MACD cross", "earnings beat AND price > $200", "sector ETF green vs SPY AND RSI < 60").

## Consequences

- **Positive**:
  - Cheap to write at the routine where the partial trigger first fires; subsequent routines just inherit the state. Compounds over multi-day setups.
  - Creates an audit trail for *why* a setup was re-proposed: future-Santiago reading the eventual proposal can see exactly which conditions accumulated when.
  - Makes it harder to "drift" a setup to re-proposal by lowering the gate — every condition is named and tracked, and the final proposal must list all of them firing.
- **Negative**:
  - Adds a small amount of bookkeeping to every routine that touches a passed-but-watched setup.
  - Half-triggers can clutter `open_positions.md` if many setups are on watch simultaneously. Mitigated by the 5-trading-day stale clearance.
- **Neutral**:
  - Setups with single-condition gates are unaffected (one condition either fires or doesn't — no "partial" state).
  - Setups in active execution (already approved or filled) are unaffected.

## Validation Plan

Over the next 8 trading weeks, count:
1. Number of half-triggers logged per routine.
2. Number of half-triggers that progressed to all-conditions-met → re-proposal.
3. Number of half-triggers that went stale (cleared after 5 trading days).
4. Number of re-proposed setups (post-half-trigger) that filled and what their outcomes were.

If half-triggers are frequently progressing to clean re-proposals with positive outcomes, the rule is doing real work. If half-triggers consistently go stale, either the original re-arm gates are too strict (revisit gate calibration), or the rule is overhead with no payoff (revisit whether to track at all).

## References

- Memory: `memory/strategy.md` adjustments log (2026-05-15 EOD entry first tabled this rule)
- Memory: `memory/learnings.md` 2026-05-15 EOD ("Half-trigger logging at midday pays compound interest at EOD")
- Memory: `memory/open_positions.md` — MSFT half-trigger entries at midday (12:30 ET) and EOD (15:46 ET) of 2026-05-15
- Setup: MSFT Setup #2 — the validation case. SMA 20 reclaim fired and stuck; MACD cross pending.
- Journal: `journal/2026-05-15.md` (midday + EOD sections documenting the cheap-to-write / expensive-to-reconstruct insight); `journal/2026-05-15-weekly.md` (this review's formalization)
- Related: ADR-0003 (approval-zone immutability — both rules reinforce the "no agent-driven mutation of pending state" principle)
