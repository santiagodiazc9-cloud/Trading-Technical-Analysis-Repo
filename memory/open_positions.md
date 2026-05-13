# Open Positions

## Current Positions
None. Portfolio is 100% cash at $100,000.00. 0% deployed.

## Pending Orders
None.

## Watchlist Alerts
- NVDA: prior swing setup entry zone ($206–$210) appears outrun (was $215.21 at last scan). Needs fresh evaluation before re-arming.
- MSFT: cleanest mean-reversion candidate from 2026-05-09 scan — RSI 53.8, stochastic deeply oversold (~18.6). Pending formal proposal in pre-market 2026-05-14.
- TSLA: day-trade only — long-term daily SMA still bearish.
- AAPL / AMD / GOOGL: all overbought on the last available scan — observe, do not chase.

## Pending Setups

### Setup #1 — NVDA Swing Long (proposed 2026-05-08)
- Direction: LONG
- Entry Zone: $206.00–$210.00
- Stop-Loss: $202.50
- Target: $218.00–$220.00
- Position Size: 4 shares (~$832 at $208 mid-entry)
- R:R: ~2.2:1
- Catalyst: AI cycle intact, analyst target $272, strong macro backdrop
- Approved: NO — STALE (was Approved YES via Discord 2026-05-11 11:26Z, but NVDA traded $215.21 at last scan on 2026-05-09 — above the entry zone — and no fill ever occurred. Per the staleness rule proposed today, this setup must be re-evaluated against fresh indicators on 2026-05-14 pre-market before any re-approval.)
- Status: **STALE — DO NOT EXECUTE.** Awaiting fresh evaluation.

### Setup #2 — MSFT Mean-Reversion Long (carried forward, never formally proposed)
- Direction: LONG
- Entry Zone: $410–$413 (TBD with fresh data)
- Stop-Loss: $405
- Target: $422–$425
- R:R: ~2.5:1
- Catalyst: Stochastic deeply oversold (~18.6 on 2026-05-09), RSI neutral (~53.8). Mean-reversion off SMA 20.
- Approved: NO — not yet proposed
- Status: **PENDING FORMAL PROPOSAL** — pre-market 2026-05-14 to run `research.py analyze MSFT` and either write a setup card to Discord `#approvals` or drop it.

## Market Open Execution Log — 2026-05-13 9:35 AM ET
- No record of a pre-market or open-execution routine running today. Account state (0 trades, 0 positions) is consistent with no routine output.

## Midday / Notes
- Midday scan 2026-05-13: no record of execution.
- EOD review 2026-05-13 (3:45 PM ET): 0 day-trade positions to close. 0 swing positions. Portfolio 100% cash overnight. Daily loss cap not hit (0.00% P&L). No rule violations. NVDA approved setup flipped to STALE — see Setup #1.

## Tomorrow's Watch List (2026-05-14)
- **NVDA** (Priority 1): re-evaluate from scratch. If price has reset into $208–$213 with RSI < 65 and MACD not extended, re-propose. If still > $215, keep stale and look elsewhere.
- **MSFT** (Priority 2): formal swing proposal candidate if stochastic crossover above 20 confirms with RSI < 60.
- **TSLA** (Priority 3 — day trade only): clean 5-min breakout above prior resistance only.
- **SPY / QQQ**: defensive shift if SPY < $725 or QQQ < $695 on the open.

## Pre-Market Notes for 2026-05-14
- First action: confirm `scripts/research.py scan` actually runs (the `ta` package failed to install in today's EOD routine). If it still fails, log infra alert and fall back to manual review.
- Investigate scheduler gap: no journal entries for 2026-05-11 or 2026-05-12. Verify the launchd/cron jobs are firing on schedule.
- Re-check every `Approved: YES` setup against current price before market open (staleness rule).
- May 16 (Friday) is monthly OpEx — reduce overnight exposure later in the week if anything has been entered.
