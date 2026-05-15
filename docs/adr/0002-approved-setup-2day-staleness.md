# ADR-0002: Approved setups auto-stale after 2 trading days without a fill

**Date**: 2026-05-15
**Status**: Accepted
**Supersedes**: none

## Context

Week 2 (May 11–15, 2026) exposed a process gap. The NVDA swing setup proposed on 2026-05-08 (entry $206–$210, stop $202.50, target $218–$220) was flipped to `Approved: YES` on 2026-05-11 11:26Z, then never re-evaluated for four trading days because the cloud pre-market routine was infra-blocked (`ta` package build failure) from 2026-05-11 through 2026-05-14. By the time the pipeline came back on 2026-05-15, NVDA was trading $235.78 — roughly **12% above the high of the original entry zone** — and the approval flag was still live.

If a fresh scan had not happened to surface the staleness, a literal-minded execution layer could have either (a) sat indefinitely on a dead approval, or (b) been tempted to "stretch" the entry zone to make the trade work at the new price. Both are bad outcomes: the first quietly idles capital; the second sneaks around the approval gate by mutating its terms.

The candidate rule was first proposed in the 2026-05-13 EOD review (see `memory/learnings.md` strategy refinements). The 2026-05-15 pre-market and market-open routines applied it informally to AMZN-2026-05-15 (logged "Stale-by date: this setup auto-stales after 2 trading days without fill"). This ADR formalizes that practice.

## Decision

**Before** (implicit): An `Approved: YES` setup remained valid until either it filled or a future routine happened to re-check it.

**After** (explicit, added to `memory/strategy.md` and enforced by every pre-market / market-open / midday routine):

> A pending setup carrying `Approved: YES` that has **not filled within 2 full trading days** of the approval timestamp must be re-evaluated against fresh indicators in the next pre-market routine. If the entry zone has been outrun, the catalyst has expired, or the technical structure no longer supports the original thesis, the setup is automatically flipped to `Approved: NO — stale` and a brand-new proposal is required to re-arm.
>
> "Two trading days" counts the approval date as Day 0 and increments by one for each subsequent regular session. Weekends, holidays, and full-day market closures do not increment the counter.
>
> The market-open execution routine MUST refuse to fill any approved setup whose `Approved: YES` timestamp is more than 2 trading days old without a fresh re-evaluation logged that same session.

This rule applies to both swing and day-trade setups. Day-trade approvals already implicitly expire intraday, but this codifies the multi-day case explicitly.

## Consequences

- **Positive**:
  - Prevents stale approvals from drifting silently across multiple sessions (the exact NVDA failure mode this week).
  - Forces every approval to be re-validated against current market structure before execution — no "approved at $206, now executing at $235" outcomes.
  - Closes the loophole where an infra-outage or scheduler gap could leave an approval indefinitely valid.
- **Negative**:
  - Adds a re-evaluation step that may cancel a still-attractive setup that just hasn't reached its entry zone. Mitigated by requiring a *fresh* proposal, not a wholesale rejection — the underlying thesis can be re-proposed with updated zone/stop/target.
  - Slightly higher cognitive load for Santiago: an approval is no longer a "set and forget" act; it has a built-in expiration.
- **Neutral**:
  - Setups that fill within 2 trading days behave exactly as before.
  - Already-resolved setups (filled, passed, or explicitly closed) are unaffected.

## Validation Plan

Track every `Approved: YES` setup over the next 8 trading weeks. Score outcomes into three buckets:

1. **Filled within 2 trading days** — rule had no effect (the approval lived its normal life).
2. **Auto-staled at Day 3 and re-proposed with adjusted levels** — rule worked: it forced a re-evaluation that yielded a fresh, calibrated setup.
3. **Auto-staled at Day 3 and not re-proposed** — rule's "negative" case: we walked away from a setup we might have taken. Inspect each case: did the underlying thesis hold up over the following 5 trading days?

If bucket 3 dominates AND those skipped setups would have been profitable in retrospect more than 40% of the time, the rule is too aggressive — extend to 3 trading days. If bucket 1 dominates (most approvals fill quickly), the rule is well-calibrated.

## References

- Memory: `memory/strategy.md` adjustments log (2026-05-13 entry first proposed the rule; this ADR formalizes it)
- Memory: `memory/learnings.md` strategy refinements 2026-05-13 (NVDA stale rule candidate); 2026-05-15 EOD "approval gate held under intraday pressure" (AMZN-2026-05-15 validation case)
- Trades / setups: NVDA-2026-05-08 (failure case that motivated the rule); AMZN-2026-05-15 (first setup to ship with the stale-by date applied)
- Journal: `journal/2026-05-13.md` (rule proposed); `journal/2026-05-15.md` (rule operating de facto); `journal/2026-05-15-weekly.md` (this weekly review's formalization)
