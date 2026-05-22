# ADR-0007: Short selling rules — agent may now scan and propose short setups

**Date**: 2026-05-22
**Status**: Accepted
**Supersedes**: none

## Context

CLAUDE.md Rule 11 has always permitted shorts ("Equities only. Long and short allowed."), but through Weeks 1–3 the agent only ever scanned and proposed long setups. The old price-level trip-wire (see ADR-0006) handled bearish/sideways tape purely defensively: it blocked new longs and parked the account in cash. Downside opportunity was left entirely on the table.

The Market Posture System (ADR-0006) made this gap concrete. RED and BEAR postures explicitly call for a "shorts only" / "aggressive short bias" stance — but the agent had no short entry criteria to act on, so those postures would still have produced nothing but cash. On 2026-05-19 a full short-selling ruleset was written into `memory/strategy.md` ("Short Selling Rules") alongside the posture system. META was flagged as the first concrete short candidate on 2026-05-20 (below SMA 20/50/200, MACD deepening negative). This ADR formalizes the ruleset — added mid-week, never carried an ADR.

## Decision

Add a short-selling ruleset to `memory/strategy.md`. The agent now actively scans for short setups every pre-market routine.

**Short swing entry — all six required:**
1. Price below SMA 20 AND SMA 20 declining (negative slope over 5 sessions)
2. ADX > 25 (no shorting choppy tape — symmetric with long rule)
3. MACD histogram negative AND deepening
4. RSI 40–65 and declining (do NOT short RSI < 35 — bounce risk)
5. Entry zone = failed bounce to SMA 20, failed 61.8% Fib retracement, or volume-confirmed break of consolidation support
6. Sector ETF also bearish (below SMA 20, MACD negative) — no counter-trend shorts

**Short-specific hard rules:**
- No shorting within 2 trading days of earnings (squeeze risk); cover open shorts the session before earnings
- No shorting into SMA 200 without a prior confirmed breach (the 200 is a bounce magnet)
- The −7% cut rule applies symmetrically — a short up 7% against entry is covered immediately
- No shorting on ex-dividend dates
- Cover at least half if RSI drops below 30 (violent oversold reversals)
- A shorted name that gaps up > 3% → reassess thesis; default is cover and re-evaluate

**Short day trade:** EMA 9 < EMA 21 on 5-min, price below a declining VWAP, RSI < 50 and falling, first 90 / last 60 minutes only, cover by 3:45 PM ET.

## Consequences

- **Positive**: The agent can now profit in declining and sideless markets instead of only avoiding losses. RED/BEAR posture finally has actionable setups. Short rules mirror the long discipline (ADX gate, sector confirmation, defined entry zones) so the bar for a short proposal is as high as for a long.
- **Negative**: Shorts carry asymmetric risk — theoretically unbounded loss, short-squeeze blowups, and borrow availability/cost that paper trading does not model. The ruleset is entirely untested: zero shorts have been taken to date. More rules also means more surface area to maintain and more ways to misclassify a setup.
- **Neutral**: In 🟢 GREEN posture with strong sector ETFs the short scan typically returns nothing — no behavior change in healthy uptrends.

## Validation Plan

Track the first 10 short trades separately from longs. Concrete metrics: (1) short win rate — if < 40% over the first 10 shorts, tighten entry criteria at the next weekly review; (2) confirm the "no short within 2 trading days of earnings" rule actually fires and prevents a squeeze; (3) confirm the "RSI < 30 → cover half" rule triggers correctly; (4) confirm no short is stopped out by an overnight gap that one of the hard rules should have prevented. First review point: the weekly review after the 5th short trade closes, or 2026-06-19, whichever comes first.

## References

- Strategy: `memory/strategy.md` → "Short Selling Rules (added 2026-05-19)"
- CLAUDE.md: Rule 11 (long and short allowed)
- Journal: `journal/2026-05-20.md` (META flagged as first short candidate)
- Market context: `memory/market_context.md` → "SHORT WATCH" (META)
- Related: ADR-0006 (Market Posture System — RED/BEAR postures consume these rules)
