# ADR-0006: Chase rule and confluence gate must be evaluated in the same routine

**Date**: 2026-05-29
**Status**: Accepted
**Supersedes**: none (tightens CLAUDE.md hard rule 12 in combination with ADR-0003 and ADR-0004)

## Context

Week 4 produced one clean end-to-end audit trail of a setup lifecycle blocking itself correctly: AVGO 2026-05-28 → 2026-05-29.

Timeline:
- **5/28 pre-market**: AVGO Bull/Bear/Judge debate ran. Verdict PASS at confidence 6/10 (gate is 7). Tentative entry zone documented as $414–$418, stop $402, target $448, R:R 2.4:1.
- **5/28 midday**: AVGO half-trigger logged at **2 of 3** conditions met (Stoch K continuation up ✓, price > SMA 20 ✓, MACD hist > -2 ✗ at -2.67).
- **5/28 EOD**: still 2 of 3 (MACD hist -2.57 — decelerating improvement).
- **5/29 pre-market**: routine did not fire (scheduler gap — second pre-mkt miss in two weeks).
- **5/29 midday**: AVGO **3 of 3 conditions firing for the first time** (MACD hist -1.30 cleared the -2 gate by 0.70). BUT: same routine also detected +3.1% same-session move ($426.95 → $440.19) and the tentative entry zone $414–$418 now outrun by $22+.

The half-trigger gate had fired — the confluence rule said "propose". The chase rule (CLAUDE.md rule 12: "If a stock has already moved >3% today, observe but don't chase") said "do not propose". ADR-0003 (approval-zone immutability) added a third constraint: even if a proposal were drafted, widening the published-or-tentative entry zone from $414–$418 to ~$438–$442 would be an agent-driven mutation, not allowed.

All three rules agreed: PASS. The routine did pass. The system worked.

But the *audit trail* of how it worked exposed a latent risk: chase and confluence are currently checked as **sequential** steps in the routine — confluence first, then "should we publish?", then a chase audit during the publish step. If the routine generated and posted the setup card before the chase audit ran (a refactor away), a Day-1 chase fill could be approved. The rule that prevented today's chase fill was the agent's voluntary ordering of steps, not a mechanical interlock.

A second concern: the published / tentative entry zone is part of the gate. If the gate fires on a day where price has run past the zone, "rebracketing the zone to current price" is structurally the same as a self-approving zone widen — which ADR-0003 already prohibits, but only on a *published* setup. Pre-publish zones (tentative, logged for context) are not currently covered.

## Decision

**Before** (implicit, behaviorally enforced by routine ordering):
- Confluence gate fires → setup proposed → chase audit runs at publish time → if chase blocks, retract.

**After** (explicit, single-step check):

> A confluence gate firing concurrent with **any one** of the following in the same routine is an **automatic PASS** for that routine. No proposal is published, no setup card is sent, no approval flag is offered:
>
> 1. The underlying stock has moved **>3% in the current trading session** (CLAUDE.md rule 12, codified as a simultaneous check, not a sequential one).
> 2. A previously-logged tentative entry zone (from a prior session's PASS or half-trigger note) has been **outrun by more than half its width** — measured as `current_price > zone_high + 0.5 × (zone_high − zone_low)` for longs, or symmetrically for shorts.
> 3. The current price sits **more than 2 ATR above the SMA 20** (longs) or below (shorts) — a soft chase signal that captures cases where the stock didn't move >3% today but is still parabolically extended on a multi-day basis.
>
> The routine MUST log the automatic-PASS reason explicitly in `memory/open_positions.md` (under the relevant watch block) and in the journal entry, even though no setup card is generated. The journal line names which of the 3 conditions triggered the PASS.
>
> A half-trigger that converts to a full-trigger after one of these conditions has fired in the same routine does NOT generate a proposal. The gate firing is logged (per ADR-0004's accounting), but the chase / extension audit short-circuits the propose step.

This tightens CLAUDE.md rule 12 from "observe but don't chase" (which is checked at proposal time) to a precondition on the confluence gate itself.

## Why this matters

The AVGO 5/29 case worked because the agent voluntarily ordered the chase audit before the propose step. That ordering is not a formal interlock. The rule above makes the joint check mechanical:

- **No two-step race condition**: confluence + chase are evaluated against the same indicator snapshot in the same routine. No window where a setup is "proposed for 10 seconds then retracted by chase audit".
- **Pre-publish zone immutability**: condition #2 closes the gap in ADR-0003 by extending zone-immutability protection to tentative (pre-publish) zones. A tentative zone outrun by >50% of its own width is, structurally, asking the agent to widen the zone — which is what ADR-0003 prevents on published setups.
- **Parabolic extension catch**: condition #3 catches the case where price has crept >2 ATR above the SMA 20 across multiple sessions without any single day showing >3%. The intraday chase rule would not fire, but the multi-day extension is the same risk profile.

## Consequences

- **Positive**:
  - Mechanical interlock — no possibility of a confluence gate firing producing a proposal that the chase audit then retracts. The audit happens *as part of* the gate.
  - Closes the pre-publish zone immutability gap. Tentative zones logged from prior sessions are now protected from being implicitly widened by a same-routine full-trigger.
  - Adds a parabolic-extension catch (condition #3) that the current intraday chase rule doesn't capture.
  - Standardizes the journal/log output: every auto-PASS names the triggering condition by number, easier to retro and tune later.
- **Negative**:
  - Will produce more PASSes in tape regimes where the watchlist is leading hard (e.g., XLK +6.5% above SMA 20 on 5/28 conditions). Some "missed trades" will look better in hindsight than the rule allows. Acceptable: weeks where the leaders are extended are exactly the weeks where chasing hurts most.
  - Condition #3 (price > SMA 20 + 2 ATR) requires a fresh ATR(14) reading at the same time as the confluence check. Routines that don't currently fetch ATR for the watch name will need to add the indicator. `scripts/research.py analyze` already returns ATR — minor wiring.
- **Neutral**:
  - Setups proposed against a name that is *not* extended (price ≤ SMA 20 + 2 ATR AND today's move ≤ 3% AND no prior tentative zone outrun by >50% of its width) are unaffected.
  - Re-proposal pathway is unchanged: a fresh pre-market routine on a later session with the chase / extension conditions cleared can re-debate and propose.

## Validation Plan

Over the next 8 trading weeks, log every full-trigger fire in `memory/learnings.md` along with whether ADR-0006 short-circuited it. Track:

1. **Count of full-triggers** that hit conditions 1, 2, or 3 — and were auto-PASSed.
2. **Of those passed setups**, what did the stock do over the next 5–10 trading days? (Catch the obvious "we missed a winner" tail.)
3. **Count of full-triggers** that did NOT hit any of the three conditions and proceeded to proposal → approval → fill → outcome. (The control group for chase impact.)

Decision criteria for re-visit:
- If >70% of auto-PASSed setups subsequently underperform their would-have-been entry by EOD-of-fill +5 sessions, the rule is doing the right work — keep it.
- If <30% underperform (i.e., we are passing on winners), revisit the thresholds (3% → 4%? 2 ATR → 2.5 ATR? 50% of zone width → 60%?).
- If half-triggers consistently fail to convert before chase fires (i.e., the only path to a proposal is to chase, because everything that confluences has already run), revisit whether the multi-day half-trigger framework itself is the limiting factor.

## References

- Memory: `memory/strategy.md` Adjustments Log (this week's entry)
- Memory: `memory/learnings.md` 2026-05-29 EOD ("The chase rule is a redundant safety net that fires when the confluence gate has already passed")
- Memory: `memory/open_positions.md` SHORT WATCH → AVGO block (full audit trail of the 5/28 → 5/29 lifecycle)
- Trades: AVGO 2026-05-28 (proposed PASS 6/10) → 2026-05-29 midday (3/3 full-trigger, BLOCKED by chase)
- Journal: `journal/2026-05-28.md`, `journal/2026-05-29.md`
- Related ADRs:
  - ADR-0003 (approval-zone immutability — this ADR extends the principle to pre-publish tentative zones via condition #2)
  - ADR-0004 (half-trigger ledger — this ADR specifies what happens when the ledger's "all conditions firing" state is reached concurrent with chase conditions)
  - CLAUDE.md rule 12 (no chasing) — this ADR codifies the rule as a precondition on the confluence gate rather than a post-proposal audit
