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
- 2026-05-13 (EOD): Candidate rule for Friday weekly review — `Approved: YES` setups should auto-stale after 2 trading days without a fill, requiring re-evaluation against fresh indicators before re-arming. NVDA swing approval from 2026-05-08 silently drifted into staleness because no rule forced a re-check.
- 2026-05-14 (EOD): Distinguish "patience" from "inability to evaluate." Staying in cash is a valid outcome ONLY when it's a decision made against fresh data. Four straight trading days (5/11–5/14) with no scan and no fresh setup is an infrastructure failure masquerading as discipline. Do not let a clean-looking flat P&L hide a broken pipeline.

## Infrastructure Notes
- 2026-05-08: Cowork scheduler sandbox blocks outbound Alpaca API connections (403 proxy error). Live order placement and real-time data require Santiago to run scripts manually from VS Code terminal. Automated routines best used for journaling, memory updates, and ClickUp notifications.
- 2026-05-13: Alpaca API IS reachable from this routine host (clock/account/positions/orders all returned cleanly). However the `ta` Python package fails to build during `pip install --user -r requirements.txt` (`Failed to build ta` / `install_layout` AttributeError). Effect: `scripts/research.py scan` cannot run from EOD/pre-market routines until a pre-built wheel or pinned version is provided. Account/positions/journal/snapshot steps still work; indicator review is degraded.
- 2026-05-13: Journal continuity gap — no entries for 2026-05-11 (Mon) or 2026-05-12 (Tue). Account state (0 trades, 0 positions, daytrade_count 0) is consistent with "scheduler didn't fire those days." Verify launchd/cron health before pre-market tomorrow.
- 2026-05-14: Scheduler gap confirmed as a recurring pattern. Only the EOD routine fired on 5/13 and 5/14; pre-market, market-open, midday, and the 15-min dispatcher did NOT run on 5/14 (`memory/last_poll.json` `last_poll_at` is still null; `open_positions.md` still carries the unprocessed "Pre-Market Notes for 2026-05-14" block). Net effect: NVDA stale setup never re-evaluated, MSFT proposal now 3 trading days overdue. ACTION: Santiago needs to audit why only EOD triggers fire — likely a cron/launchd schedule or GHA workflow issue affecting the other routine times.
- 2026-05-14: `pip install -r requirements.txt` fails as a batch because the `ta` package wheel build fails — and pip aborts the WHOLE batch, leaving zero deps installed (alpaca-py, dotenv, etc. all missing). Worked around by installing the other 6 deps individually. Permanent fix: pin a buildable `ta` version or pre-build a wheel, OR split requirements so a bad package can't cascade.

## Pending Approval Tracker
- 2026-05-08: NVDA swing setup (pullback to 206–210, stop below 200, target 216+) proposed across pre-market, midday, and EOD. Marked Approved YES on 2026-05-11 11:26Z. **STALE as of 2026-05-13**: NVDA was $215.21 at last scan (above entry zone) and no live indicator scan has run since. Do NOT auto-execute. Re-evaluate fresh in pre-market 2026-05-14 — if outside entry zone or indicators no longer support, flip to `Approved: NO — stale`.
- 2026-05-09: MSFT mean-reversion idea (entry $410–$413, stop $405, target $422–$425, ~2.5:1 R:R) was queued for formal proposal on Monday 2026-05-11 but never written up because the pre-market routine appears not to have run. Carry forward to 2026-05-14 pre-market checklist.

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
