# ADR-0006: Market Posture System replaces the fixed price-level trip-wire

**Date**: 2026-05-22
**Status**: Accepted
**Supersedes**: none (formalizes the replacement of the informal SPY/QQQ price-level trip-wire, which was never itself an ADR)

## Context

Through Weeks 2–3 the agent gated new longs with a fixed price-level trip-wire: SPY < $736 OR QQQ < $700 → no-new-longs. The trip-wire fired on 2026-05-18 and stayed active through 2026-05-19 (see `journal/2026-05-18.md`, `journal/2026-05-19.md`) — two full sessions of cash-only behavior.

The flaw surfaced quickly. A fixed price level has no relationship to market health once the market moves: SPY at $734 inside an uptrend is a buying opportunity, while SPY at $737 after a 15% crash is a dead-cat bounce. The same number means opposite things. By 2026-05-19 the trip-wire was already stale and context-free — it was blocking longs at a price ($734–$736) that sat comfortably above SMA 20 and ~6% above SMA 50, i.e. inside a healthy uptrend. The rule was being obeyed correctly but measuring the wrong thing.

On 2026-05-19 a posture-based replacement was written into `memory/strategy.md` ("Market Posture System"). It took live effect on 2026-05-20 with the first 🟢 GREEN classification. This ADR formalizes that change — it was made mid-week and never carried an ADR.

## Decision

Replace the fixed price-level trip-wire with a four-state **Market Posture System** classified from SPY's position relative to its moving averages.

**Before**: `SPY < $736 OR QQQ < $700` → binary no-new-longs. Fixed price, no context.

**After**: every pre-market routine classifies posture (first match wins):

| Posture | Condition | Stance |
|---|---|---|
| 🟢 GREEN | SPY > SMA 20 AND SMA 20 > SMA 50 | Full — new longs AND shorts |
| 🟡 CAUTION | SPY < SMA 20 but > SMA 50 | Reduced — confidence ≥ 8 only; prefer shorts |
| 🔴 RED | SPY < SMA 50 | Shorts only — no new longs |
| ⚫ BEAR | SPY < SMA 200 | Aggressive short bias; reduce long exposure |

- **Volatility override**: VIX > 25 → treat as CAUTION regardless of SMA; VIX > 35 → treat as RED.
- **CAUTION exception** (new long still allowed if ALL apply): confidence ≥ 8/10, SPY within 1% of SMA 20, setup's sector ETF still above its SMA 20.
- Posture is logged to `memory/market_context.md` so midday and EOD routines inherit it without re-deriving.

## Consequences

- **Positive**: Posture tracks actual trend health and re-prices itself automatically as the market moves — no manual level updates, no staleness. It also makes the bear case actionable: RED/BEAR explicitly enables shorts (paired with ADR-0007) rather than only sitting in cash.
- **Negative**: More complex than a single number — requires SMA 20/50/200 computation every pre-market and a VIX read. A "thin GREEN" (SPY barely above SMA 20) can flip to CAUTION on a single session; observed 2026-05-20 with only a 0.97% margin above SMA 20.
- **Neutral**: In a clearly trending market both systems agree — strong uptrends classify GREEN and would also sit above any reasonable fixed level.

## Validation Plan

Track each posture classification against the subsequent 3-session SPY move. If 🟢 GREEN is followed by a SPY drop > 2% within 3 sessions in more than 40% of cases over the next 10 classifications, the GREEN threshold is too loose — revisit (e.g. require SPY > 1% above SMA 20, not merely above it). Re-check at the 2026-06-19 weekly review.

## References

- Strategy: `memory/strategy.md` → "Market Posture System (added 2026-05-19...)"
- Journals: `journal/2026-05-18.md`, `journal/2026-05-19.md`, `journal/2026-05-20.md`
- Market context: `memory/market_context.md` → "Market Posture" (first GREEN classification 2026-05-20)
- Related: ADR-0007 (short selling rules — RED/BEAR posture consumer)
