# ADR-0003: Approval-zone immutability — agent may not redefine entry/stop/target intraday

**Date**: 2026-05-15
**Status**: Accepted
**Supersedes**: none

## Context

On 2026-05-15, the AMZN-2026-05-15 swing-long setup was proposed pre-market with an entry zone of $264.00–$265.50 (calibrated against SMA 20 at $263.84), a stop at $260.00, and a target of $278–$280. Santiago did not approve it.

Through the trading day the technicals materially **improved**:
- RSI cooled from 62.9 (pre-market) → 57.3 (midday) → 57.8 (EOD).
- R:R from a hypothetical fill widened from the planned 3.0:1 → 4.7:1 (midday) → 4.05:1 (EOD).
- Stochastic K remained deeply oversold (~6.7) all session.

But price drifted just below the entry zone the entire day — pre-market $267.21 → 09:36 open $261.30 → midday $263.13 → EOD $263.56. At each checkpoint, AMZN was within roughly **$1 of the lower bound** of the entry zone with improving technicals. The pull to "widen the zone to $260–$265" or to "lower the limit to $263" or to flip `Approved: YES` without Santiago and execute at the better R:R was real.

The midday and EOD routines deliberately resisted that pull, logged the rationale in `memory/learnings.md` ("don't redefine an approval-pending setup's entry zone unilaterally to 'make the trade work' intraday"), and held the setup at `Approved: NO` with the original parameters intact. This was the correct call: an agent that can mutate the parameters of a pending approval is, in effect, an agent that can self-approve any improved-looking technical state. That is not an approval gate; it is a rubber stamp.

This rule has been operating de facto since 2026-05-15 midday. This ADR codifies it.

## Decision

**Before** (implicit): The agent was free to refine entry zone, stop-loss, or target on a still-pending setup as new data arrived intraday.

**After** (explicit, added to `memory/strategy.md`):

> Once a setup is published to `memory/open_positions.md` under "Pending Setups" with an entry zone, stop-loss, and target, those parameters are **immutable** until one of the following terminal events:
>
> 1. **Santiago redefines** the setup (via direct file edit, `/approve` with parameter override, or explicit instruction in `#chat` / `#approvals`).
> 2. **The setup auto-stales** under ADR-0002 (2 trading days without a fill) — at which point a brand-new proposal with fresh parameters is required.
> 3. **The setup fills** — at which point stop / trailing-stop / take-profit management proceeds under the existing risk rules.
>
> Between those events, the agent MAY:
> - Re-read indicators and log them in `memory/open_positions.md` or `memory/market_context.md`.
> - Update the "current status" / "indicator drift" / "R:R if filled now" annotations.
> - Recommend in a journal entry or daily brief that Santiago consider re-pricing.
>
> The agent MAY NOT:
> - Widen or narrow the entry zone.
> - Move the stop-loss (in either direction).
> - Move the target.
> - Change the position size.
> - Flip `Approved: NO` to `Approved: YES` on its own.
>
> If the technicals have moved enough that the agent believes the setup should be re-priced, the correct action is to **document the case in `#chat` / journal and wait for Santiago**. Not to silently mutate the parameters.

## Consequences

- **Positive**:
  - The approval gate retains its purpose: Santiago decides what's "in zone," not the agent. The agent cannot sneak around the gate by relabeling parameters.
  - Forces an audit trail. Any change to a setup's parameters now requires either Santiago action or a fresh proposal, both of which leave clear records.
  - Reduces the temptation to "make the trade work" intraday — which historically is when most over-fitting and chasing happen.
- **Negative**:
  - The agent will sometimes watch genuinely-improved setups die unfilled because the parameters as written no longer match the market. Acceptable: a missed-but-disciplined trade is strictly better than an executed-but-rationalized one.
  - Slightly more friction for Santiago when a setup deserves a re-price: requires an explicit edit / approval action rather than the agent inferring it.
- **Neutral**:
  - Setups that fill cleanly within the originally-published zone are unaffected.
  - Closed / passed / stale setups are unaffected — re-arms always require a fresh proposal anyway.

## Validation Plan

For the next 8 trading weeks, log every case where:
1. A pending setup's technicals improve materially intraday (RSI cools by ≥ 5 points OR R:R from current price widens by ≥ 1.0×).
2. Price stays within $1 of the original entry zone but does not enter it.
3. The setup ultimately auto-stales (per ADR-0002) without filling.

For each such case, observe what happened to the symbol over the following 5 trading days. If a majority of these "almost-filled" setups would have been profitable from the post-improvement price, the rule's "negative" case is materializing — revisit whether a Santiago-acknowledged "soft repricing" channel (e.g., a `/repropose` slash command) should be added. If most of these setups went on to invalidate the original thesis (continued lower, broke the stop, etc.), the rule is well-calibrated.

## References

- Memory: `memory/strategy.md` adjustments log (2026-05-15 EOD entry first tabled this rule)
- Memory: `memory/learnings.md` 2026-05-15 EOD ("The approval gate is only meaningful when held against attractive trades")
- Setup: AMZN-2026-05-15 — the validation case. Improved technicals throughout the day, parameters held immutable, setup never filled.
- Journal: `journal/2026-05-15.md` midday + EOD sections (every routine that resisted the pull); `journal/2026-05-15-weekly.md` (this review's formalization)
- Related: ADR-0002 (2-day staleness rule — the "release valve" for setups that need re-pricing)
