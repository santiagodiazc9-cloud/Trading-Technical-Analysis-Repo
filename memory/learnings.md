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
- 2026-05-15: **`ta` build fix found.** Root cause is older setuptools (`install_layout` AttributeError during the legacy setup.py path). Workaround: `pip install --user --break-system-packages --upgrade setuptools wheel` BEFORE `pip install --user ta`. After that, `ta-0.11.0` installs cleanly and `scripts/research.py scan` runs against all 10 watchlist symbols. Suggest baking this into the routine bootstrap or a `requirements-bootstrap.txt` so it runs once before the main requirements.

## Synthesis Lessons
- 2026-05-15: **Stoch oversold + RSI neutral is not enough** when long-term SMA structure is broken. MSFT today (Stoch K 5.6, RSI 50, but SMA50 < SMA200 and below SMA20) looks textbook for mean-reversion but is fighting both its own trend AND an overbought broad tape. Rule of thumb: require at least one of {SMA 20 reclaim, MACD bullish cross, sector ETF green vs SPY} before acting on a mean-reversion signal against a long-term-bearish structure.
- 2026-05-15: **Sector ETF check materially moves confidence.** AMZN setup today read like 7+ on fundamentals + technicals alone, but XLY rolling-over vs SPY (consumer-discretionary weakness) capped synthesis confidence at 6. The sector momentum sub-agent is doing real work — don't skip it.
- 2026-05-15: **Data-pipeline outages masquerade as discipline.** Four straight days (5/11–5/14) of "no trades" looked like patience but was actually blindness. After pipeline returns, the first routine often reveals that "what we missed" was nothing to chase (today: NVDA fully outrun, MSFT structurally wrong, AMZN still requires patience for $264 pullback). The correct read: be glad we couldn't trade blind — but also be aware that the next outage will not always be so benign.
- 2026-05-15 (EOD): **The approval gate is only meaningful when held against attractive trades.** AMZN improved through the day — RSI cooled 62.9 → 57.8, R:R from a hypothetical fill widened from 3.0:1 to 4.6:1, and price closed $0.44 below the lower bound of the entry zone. The temptation to widen the zone, lower the limit, or quietly flip `Approved: YES` was real. Holding the line preserved the gate's purpose: Santiago decides what's "in zone," not the agent. If the gate only holds when trades are unattractive, it isn't a gate — it's a rubber stamp. **Rule of thumb:** an approval-pending setup's entry zone, stop, and target are immutable until either (a) Santiago explicitly redefines them, or (b) the stale-by date triggers a fresh proposal. No "intraday adjustments."
- 2026-05-15 (EOD): **Half-trigger logging at midday pays compound interest at EOD.** MSFT held the SMA-20 reclaim through the full session (1 of 2 re-arm conditions confirmed). Because midday already logged the partial state into `open_positions.md` + `learnings.md`, tonight's snapshot ships clean to Monday's pre-market routine without re-deriving — the routine just reads "1/2 conditions held, watch for MACD cross" and proceeds. Cheap to write at midday, expensive to reconstruct from scratch later. **Rule of thumb:** when a setup hits a fraction of its re-arm gate, log the partial state immediately — even if no proposal results today.
- 2026-05-15 (EOD): **Audit "patience" honestly at weekly review.** Five trading days into Phase 2 (5/11–5/15) and the trade ledger reads zero. That number conflates four causes — infrastructure outage (5/11–5/14), patient pass on extended/structurally-broken setups (5/13–5/14 NVDA/MSFT), approval-blocked setup (5/15 AMZN), and clean patient pass (5/15 broad watchlist). Friday's weekly review must score these separately or the system will mistake blindness for discipline. **Rule of thumb:** weekly review categorizes each flat day into {patient | infra-blocked | approval-blocked | mixed} before computing a "discipline" stat.

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
