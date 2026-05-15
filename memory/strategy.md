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
- 2026-05-13 (EOD): Proposed rule for Friday weekly review — **approved-setup staleness check**. Any setup carrying `Approved: YES` that does not fill within 2 trading days must be re-evaluated against fresh indicators in the next pre-market routine. If the entry zone has been outrun or technicals no longer support it, flip to `Approved: NO — stale` and require a brand-new setup proposal. Goal: prevent stale approvals from quietly drifting forward and producing late, low-quality fills.
- 2026-05-14 (EOD): No strategy changes — strategy cannot be meaningfully refined while the data pipeline is down. No scan ran for the 4th straight day. The blocker is infrastructure, not strategy. Holding all rules unchanged until a pre-market routine successfully re-baselines indicators. Item flagged for the 2026-05-16 Friday weekly review: if the scheduler/`ta` issues are not resolved by then, the weekly review itself will have no fresh data to work with.
- 2026-05-15 (EOD): No strategy rule changes today — first full day of fresh data since the outage worked the existing rules correctly (AMZN approval gate held, NVDA stale rule held, MSFT re-arm gate held its half-trigger). Two candidate rules tabled for the 2026-05-16 Friday weekly review (formalize via ADR if accepted): (1) **Approval-zone immutability** — once a setup is published with an entry zone, the agent may NOT widen / shift / re-bracket that zone intraday; only Santiago redefines, or the setup auto-stales. (2) **Half-trigger ledger** — when a re-arm condition partially fires (1 of N conditions met), log the partial state in `open_positions.md` and `learnings.md` at the routine where it first triggers, so subsequent routines inherit the state cheaply. Both rules are operating de facto today; the weekly review should decide whether to formalize.
