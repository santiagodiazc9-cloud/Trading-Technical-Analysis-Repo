# Active Strategy

## Current Approach
Starting with a **conservative, paper-trading** approach. Focus on high-probability setups with clear risk/reward.

## Day Trading Rules
- Only trade the first 2 hours and last hour of the session
- Use 5-min chart for entry, 15-min for trend confirmation
- Require EMA 9/21 crossover + RSI confirmation + VWAP alignment
- Max 2 day trades per day
- Close ALL day trades by 3:45 PM ET

## Swing Trading Rules
- Enter on daily chart setups only
- Require SMA 20/50 alignment + MACD crossover
- Hold 2-10 days, never longer without re-evaluation
- Trail stops using ATR once in profit
- Max 3 swing positions at a time

## What's Working
- Discipline: No trades forced during Week 1 (setup week). Overbought conditions identified correctly on AAPL, NVDA, TSLA — decision to pass was correct.
- Watchlist scanner functioning: 10 symbols scanned successfully, signals generated for 8 of 10.
- Memory architecture validated: all read/write routines working as intended.

## What's Not Working
- No live trade data yet to evaluate setup quality.
- Market entry timing is untested — need at least one clean setup to confirm execution workflow.

## Adjustments Log
- 2026-05-08: Initial strategy framework established
- 2026-05-08 (Weekly Review): Week 1 was system calibration — no trades taken. Core rules unchanged. Adding emphasis on patience: do NOT enter trades when RSI > 70 on the daily timeframe unless there is a confirmed momentum breakout with volume surge. This rule formalizes the observation that several watchlist names were extended this week.
