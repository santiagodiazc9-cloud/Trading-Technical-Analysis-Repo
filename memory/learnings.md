# Learnings & Observations

## Trading Rules Discovered
- No trades were taken today, reinforcing the importance of patience and waiting for clean setups rather than forcing executions.

## Common Mistakes
- [Will be tracked here to avoid repeating]

## Pattern Notes
- Watchlist scan showed that many large-cap tech names can appear bullish while still being overbought; avoid chasing extended moves.

## Strategy Refinements
- 2026-05-08: End-of-day review completed with no trades; prioritize high-quality setups and avoid overtrading on stretched positions.
- 2026-05-08 (EOD): Full trading day passed with zero executions. Watchlist healthy but prices extended — staying in cash was the correct decision.

## Infrastructure Notes
- 2026-05-08: Cowork scheduler sandbox blocks outbound Alpaca API connections (403 proxy error). Live order placement and real-time data require Santiago to run scripts manually from VS Code terminal. Automated routines best used for journaling, memory updates, and ClickUp notifications.

## Pending Approval Tracker
- 2026-05-08: NVDA swing setup (pullback to 206–210, stop below 200, target 216+) proposed across pre-market, midday, and EOD — still AWAITING APPROVAL. Valid into 2026-05-09 if price holds support zone.

## Weekly Review — Week Ending 2026-05-08

### Week 1 Summary
- **System setup week**: The agent was deployed, connected to Alpaca paper account ($100,000), and all scripts validated.
- **Trades taken**: 0. Correct decision — multiple watchlist symbols were overbought (RSI > 70) and in extended price action.
- **Key observation**: NVDA and TSLA showed the most signal activity but neither offered a clean low-risk entry within our risk rules.
- **Process lesson**: The approval gate workflow is critical — even in automated mode, no trade should be placed without explicit user confirmation. This was respected correctly in Week 1.

### Patterns from Week 1
- Large-cap tech (AAPL, NVDA, META, AMZN, GOOGL) all showed bullish bias but overbought readings simultaneously — a classic "trend is up but chasing is dangerous" environment.
- MSFT showed oversold Stochastic on shorter timeframes, potentially the cleanest mean-reversion setup for next week.
- TSLA momentum is intraday-driven; daily SMA alignment is bearish — treat as day-trade only until daily trend clarifies.

### Rules to Reinforce
1. RSI > 70 on daily = NO NEW LONGS unless breakout + volume confirmation.
2. Prefer setups where price has pulled back to VWAP or SMA 20 rather than chasing highs.
3. Never force a trade in Week 1 of a new system. Patience is the highest-quality decision.
4. Always post setups to ClickUp and wait for user approval before execution.
