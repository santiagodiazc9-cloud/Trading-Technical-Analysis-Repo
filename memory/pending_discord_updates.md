# Pending Discord Updates

This file is a fallback log. When a routine's `notify.py` call fails (Discord webhook unreachable, network error, bot REST API rejection, etc.), the routine appends its summary here with a timestamp instead of halting. The dispatcher routine (or a manual catch-up) flushes these to Discord on its next successful run.

The legacy filename was `pending_clickup_updates.md` — kept the renamed file as the single fallback queue across all notification surfaces.

---

## 2026-05-15 12:11 UTC — Pre-Market Research (cloud routine)

Discord notify calls failed — `memory/discord_config.json` (webhooks) and `DISCORD_BOT_TOKEN` still not provisioned on this routine host. Routine completed all other steps; flush these once Discord credentials are present.

### #approvals (NEW SETUP CARD — buttons needed)
**Setup ID**: `AMZN-2026-05-15`
**Symbol / Direction**: AMZN LONG (swing, 2–10 day hold)
**Entry Zone**: $264.00–$265.50 (pullback to SMA 20 at $263.84) — NO CHASE above $265.50
**Stop-Loss**: $260.00
**Target**: $278.00–$280.00 (upper Bollinger Band)
**Position Size**: 74 shares (~$19,610 at $265 mid-entry — fits 20% cap)
**R:R**: 3.0:1
**Confidence**: 6/10
**Catalyst**: Q1 2026 beat (rev $181.5B, EPS $2.78 vs $1.64 est, record 13.1% op margin). AWS reaccelerated to +28% YoY. Multiple PT raises post-print. Stoch K = 6.7 oversold off healthy long-term uptrend.
**Caveats**: XLY (Consumer Discretionary ETF) rolling over vs SPY — sector headwind. MACD histogram cooling. Broad tape overbought (SPY RSI 78). Monthly OpEx tomorrow (5/16) — pin risk into close. Conditional execution: only fill in $264.00–$265.50 zone; skip on a gap-up open.
**Approve via**: edit `memory/open_positions.md` Setup #3 → add `Approved: YES` under the AMZN-2026-05-15 block.

### #daily-brief (silent summary)
**Title**: Pre-Market Brief — 2026-05-15
**Body**: **Pipeline restored.** First successful pre-market scan since 2026-05-09 (`ta` build issue fixed via setuptools+wheel upgrade). Market broadly overbought: SPY RSI 78.7, QQQ 80.6, XLK 80.5. 4 parallel research sub-agents (fundamentals, technicals, news, sector) ran for MSFT/AMZN/NVDA. 1 setup proposed (AMZN swing long, confidence 6/10) — only on pullback to $264-$265. NVDA Setup #1 confirmed STALE (price $235.78, prior zone $206-210 fully outrun). MSFT Setup #2 resolved PASS (long-term bearish SMA structure). Account flat: $100k cash, 0 positions. Caution: monthly OpEx tomorrow + NVDA earnings 5/20.

### Dashboard mirror
`Dashboard.md` regenerated. Pinned-message mirror in `#daily-brief` NOT updated — `DISCORD_BOT_TOKEN` still missing.

### Infra fix needed (carried from 2026-05-13 / 2026-05-14)
1. Provision `memory/discord_config.json` (copy of `discord_config.example.json` with real webhook URLs).
2. Set `DISCORD_BOT_TOKEN` in routine host's `.env`.
3. **NEW — ta install fix found**: bootstrap setuptools+wheel BEFORE `pip install -r requirements.txt`. Specifically: `pip install --user --break-system-packages --upgrade setuptools wheel && pip install --user --break-system-packages ta`. Worked cleanly today. Recommend adding to routine bootstrap.
4. Scheduler audit (only EOD has been firing): pre-market today DID fire — partial progress. Still verify market-open / midday / dispatcher trigger on schedule.
5. RuFlo MCP unavailable in cloud env — file-only fallback used today; vector recall / pattern storage skipped.

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
