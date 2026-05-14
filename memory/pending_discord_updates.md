# Pending Discord Updates

This file is a fallback log. When a routine's `notify.py` call fails (Discord webhook unreachable, network error, bot REST API rejection, etc.), the routine appends its summary here with a timestamp instead of halting. The dispatcher routine (or a manual catch-up) flushes these to Discord on its next successful run.

The legacy filename was `pending_clickup_updates.md` — kept the renamed file as the single fallback queue across all notification surfaces.

---

## 2026-05-14 19:47 UTC — End-of-Day Review (cloud routine)

Discord notify calls failed again — `memory/discord_config.json` (webhooks) and `DISCORD_BOT_TOKEN` in `.env` are still missing on this routine host. Routine completed all other steps; flush these once Discord credentials are provisioned.

### #daily-brief (silent summary)
**Title**: End-of-Day Review — 2026-05-14
**Body**: Flat day: 0 trades, 0 positions, P&L $0.00 (0.00%). 100% cash overnight. Scheduler gap confirmed — only EOD ran today; pre-market/midday/dispatcher did not fire, so the NVDA stale setup was never re-evaluated and the MSFT proposal is now 3 trading days overdue. `ta` package still blocks `research.py scan` (4th consecutive day).

### Dashboard mirror
`Dashboard.md` regenerated successfully (live=true, positions=0, pending_setups=2). Pinned-message mirror in `#daily-brief` NOT updated — `DISCORD_BOT_TOKEN` missing.

### #risk-alerts (infra escalation — medium)
Scheduler is only firing the EOD routine. Pre-market (8:00 AM), market-open (9:35 AM), midday (12:30 PM), and the 15-min dispatcher did not run on 2026-05-14 (`last_poll.json.last_poll_at` is null; `open_positions.md` still carries the unprocessed pre-market block). Journal also missing 5/11–5/12. The agent currently cannot scan, propose setups, or process approvals — only journal. Needs a launchd/cron/GHA schedule audit.

### Infra fix needed (carried from 2026-05-13, still open)
1. Provision `memory/discord_config.json` (copy of `discord_config.example.json` with real webhook URLs) on the routine host.
2. Set `DISCORD_BOT_TOKEN` in the routine host's `.env`.
3. Fix the `ta` package install (pin a buildable version or pre-build a wheel) — its wheel-build failure aborts the entire `pip install -r requirements.txt` batch, leaving zero deps installed. EOD worked around it by installing the other 6 deps individually.
4. NEW: audit the routine scheduler — only the EOD trigger is firing; pre-market / market-open / midday / dispatcher are not.

---

## 2026-05-13 19:46 UTC — End-of-Day Review (cloud routine)

All three Discord notify calls failed because `memory/discord_config.json` (webhooks) and `DISCORD_BOT_TOKEN` in `.env` are missing in this routine host. The routine completed all other steps; these messages need to be flushed once Discord credentials are provisioned.

### #chat (reflective question)
**Title**: Reflection — 2026-05-13
**Body**: An approved NVDA swing setup has been sitting at `Approved: YES` since 2026-05-08 and never filled — NVDA ran above the entry zone and the approval quietly drifted forward. Should approvals auto-stale after N trading days without a fill (proposing N=2)?

### #daily-brief (silent summary)
**Title**: End-of-Day Review — 2026-05-13
**Body**: 0 trades, 0 positions, P&L $0.00 (0.00%). 100% cash. NVDA approved setup flipped to STALE (price outran entry zone). MSFT mean-reversion carried forward. Infra: `ta` package failed to install — `research.py scan` unavailable this run. Journal continuity gap for 5/11 and 5/12 noted.

### Dashboard mirror
`Dashboard.md` regenerated successfully (live=true, positions=0, pending_setups=2). Pinned-message mirror in `#daily-brief` was NOT updated because `DISCORD_BOT_TOKEN` is missing.

### Infra fix needed
1. Provision `memory/discord_config.json` (copy of `discord_config.example.json` with real webhook URLs) on the routine host.
2. Set `DISCORD_BOT_TOKEN` in the routine host's `.env`.
3. Install `ta` Python package successfully (currently fails wheel build) so `scripts/research.py scan` is usable from cloud routines.
