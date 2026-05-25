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
