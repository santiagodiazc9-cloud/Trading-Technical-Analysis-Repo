# ADR-0001: No new long entries when daily RSI > 70

**Date**: 2026-05-08
**Status**: Accepted
**Supersedes**: none

## Context
Week 1 of paper-trading operation. Watchlist of 10 large-caps was repeatedly bullish-but-overbought: AAPL, NVDA, META, AMZN, GOOGL all showing RSI > 70 simultaneously across the week. Zero trades were taken — the right call — but the rule that produced "stay out" was implicit in the agent's reasoning, not codified. Without a written rule, future routines could rationalize entries on any of these names.

## Decision
**Before** (implicit): "evaluate overall risk/reward including momentum readings."

**After** (explicit, in `memory/strategy.md` and CLAUDE.md decision checklist):
> Do NOT enter new long positions when daily RSI > 70 UNLESS there is a confirmed momentum breakout AND a volume surge ≥ 1.5× 20-day average.

This applies to swing entries. Day-trade entries are governed by intraday RSI on the 5-min chart, not daily.

## Consequences
- **Positive**: Eliminates "bullish but extended" trap. Forces the agent to wait for pullbacks or breakouts with confirmation, both of which historically have better R:R.
- **Negative**: Will miss some breakouts that don't have the volume surge. Acceptable given we'd rather miss a winner than chase into a top.
- **Neutral**: Day trades unchanged. Mean-reversion shorts in overbought conditions still considered case-by-case.

## Validation Plan
Track every watchlist name where daily RSI > 70 over the next 4 weeks. Note what happens 5 trading days later (pulled back, consolidated, broke out higher with volume). If breakouts-with-volume win rate would have been > 60%, the rule is too tight and we revisit. If pullback-or-consolidation rate is > 70%, the rule is correctly calibrated.

## References
- Memory: `trading/learning/patience-over-activity/W1`
- Memory: `trading/rule/rsi-70-no-new-longs/principle`
- Journal: `journal/2026-05-08-weekly.md`
- Pattern observed across: AAPL, NVDA, META, AMZN, GOOGL (Week ending 2026-05-08)
