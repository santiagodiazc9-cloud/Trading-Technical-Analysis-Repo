# Pending Discord Updates

This file is a fallback log. When a routine's `notify.py` call fails (Discord webhook unreachable, network error, bot REST API rejection, etc.), the routine appends its summary here with a timestamp instead of halting. The dispatcher routine (or a manual catch-up) flushes these to Discord on its next successful run.

---

### 2026-05-25 12:13 UTC — Pre-Market Brief (Discord config missing in cloud env)
- **Channel**: #daily-brief
- **Title**: Pre-Market Brief — 2026-05-25 (Memorial Day)
- **Body**: 🇺🇸 Memorial Day — US markets CLOSED today; next open 2026-05-26. Posture: 🟢 GREEN STRENGTHENED (SPY $745.67, +1.93% above SMA 20). GOOGL position -1.06% unrealized (well above -7% cut at $359.98; MACD deteriorated, Stoch persists oversold). 0 setups proposed today; tape extended (AAPL/AMD/ARM/PANW all RSI > 70), MACD divergent under rising SPY. MSFT half-trigger STALED 5/22 EOD per ADR-0004 (MACD never crossed). NVDA in post-earnings watch zone $215-$220 (RSI 53.7 ✓); needs MACD positive cross at 5/26 pre-market to confirm. Weekly count 0/3.
- **Reason**: `memory/discord_config.json` missing in cloud routine host (recurring known gap — see 2026-05-15 weekly review note).
- **Setups to push as cards**: 0 (no setups proposed today).
- **Alerts**: 0 (no high-severity events).

### 2026-05-25 19:45 UTC — End-of-Day Review Brief (Discord config missing in cloud env)
- **Channel**: #daily-brief
- **Title**: End-of-Day Review — 2026-05-25
- **Body**: Memorial Day (markets closed). Equity $99,790.90 | cash $80,259.43 | deployed 19.57%. Daily P&L $0.00 (mark-to-market frozen at Fri 5/22 close). 1 swing position: GOOGL 51 sh @ $387.07, unreal -$209.10 (-1.06%); trailing stop active, -7% cut at $359.98 (~6% buffer). 0 trades closed. 0 day-trades. MSFT half-trigger STALED 5/22 EOD (clean ADR-0004 retirement). NVDA in watch zone $215-220 — MACD not yet confirming. Tomorrow priorities: NVDA MACD direction, GOOGL SMA-20 reclaim attempt, AVGO base-building. Hard rule violations: NONE. Daily loss cap: NOT hit.
- **Reason**: `memory/discord_config.json` missing in cloud routine host (recurring known gap).
- **Dashboard mirror**: failed (`DISCORD_BOT_TOKEN` missing in .env — bot edit/pin requires token).
- **Alerts**: 0 (no high-severity events).

### 2026-05-26 12:00 UTC — Pre-Market Brief (Discord config missing in cloud env)
- **Channel**: #daily-brief
- **Title**: Pre-Market Brief — 2026-05-26
- **Body**: Week 4 day 1 post-Memorial Day. 🟢 GREEN STRENGTHENED (SPY $745.67, SMA 20 $731.54, margin 1.93%). Equity $99,812.83 | cash $80,259.43 | deployed 19.59% | day-trades 0. 0 setups proposed — patient pass. NVDA still in watch zone ($215.34, RSI 53.7, SMA 20 reclaim $214.75 ✓) but MACD positive cross has NOT fired (-0.87). VST/CRM MACD crosses fired but broken long-term structure. Market-scan returned only earnings names (A/AZO 5/27, ADSK 5/28 — all 0-2 day binary, skip). Tape: tired-uptrend leaders RSI > 70 (AAPL/AMD/ARM/PANW/LLY). GOOGL position -0.95% (improving from -1.06%), manual trigger $375. Trade count 0/3. Confidence on new entries: 4/10.
- **Reason**: `memory/discord_config.json` missing in cloud routine host (recurring known gap).
- **Setups to push as cards**: 0 (no setups proposed today).
- **Dashboard mirror**: failed (`DISCORD_BOT_TOKEN` missing in .env — bot edit/pin requires token). `Dashboard.md` regenerated locally; live equity $99,818.44 / +$27.54 daily.
- **Alerts**: 0 (no high-severity events — Ruflo MCP unavailable is the standing cloud-env state, no repeat-alert needed).
