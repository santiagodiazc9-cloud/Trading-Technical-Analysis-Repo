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

## 2026-05-15 20:33 UTC — Friday Weekly Review (cloud routine)

`notify.py brief` and `notify.py dashboard` both failed: `memory/discord_config.json` (webhooks) and `DISCORD_BOT_TOKEN` (.env) still not provisioned in cloud routine host. Routine completed all on-disk steps (ADRs written, strategy + learnings + watchlist + weekly journal + market context updated, dashboard regenerated). Flush this once Discord credentials are present.

### #daily-brief (silent summary — Friday Weekly Review)
**Title**: Weekly Review — Week ending 2026-05-15
**Body**: 0 trades / P&L $0.00 (0.00%) / win rate N/A — 2nd consecutive flat week (Week 2 close). Setups this week: AMZN-2026-05-15 (conf 6/10) held under approval gate all day, never filled; NVDA-2026-05-08 confirmed STALE; MSFT Setup #2 PASS with half-trigger (1 of 2 re-arm conditions confirmed). **3 new ADRs formalized today:** ADR-0002 approved-setup 2-day staleness, ADR-0003 approval-zone immutability, ADR-0004 half-trigger ledger — all govern setup lifecycle, no entry-rule changes. Discipline audit: 4 of 5 trading days were infra-blocked (5/11–5/14 cloud-scheduler/`ta`-package outage); only 1 clean day (5/15) of evaluable discipline data. Confidence in current approach: **7/10** (up 1 vs mid-week). Plan for Week 3: AMZN stale-by 5/19, MSFT half-trigger watch into Microsoft Build 2026 conf 5/19–22, NVDA Q1 FY27 earnings 5/20 AMC = binary risk no entry until post-print pullback to $215-$220.

### Dashboard mirror
`Dashboard.md` regenerated (live=true, positions=0, pending_setups=3). Pinned-message mirror in `#daily-brief` NOT updated — `DISCORD_BOT_TOKEN` still missing.

### Reflective question (deferred from EOD 5/15)
Best honest answer to "Did patience cost us a real trade this week, or just a phantom one?" — phantom. The two setups that drifted past us during the 5/11–5/14 outage were either binary-event-risked (NVDA = 5/20 earnings inside the swing window) or counter-trend-against-broken-structure (MSFT = SMA 50 < 200 below SMA 20). The rule set as currently calibrated would have passed on both even with a live pipeline. Cost of the outage was epistemic (we couldn't see), not trade (we missed a winner). Revisit on 5/22 weekly review once NVDA earnings and Microsoft Build have played out.

### Infra fix still needed (re-confirmed; no progress this week)
1. Provision `memory/discord_config.json` (copy of `discord_config.example.json` with real webhook URLs) on the cloud routine host.
2. Set `DISCORD_BOT_TOKEN` in the cloud routine host's `.env`.
3. Bake the `ta`-package install fix (`pip install --user --break-system-packages --upgrade setuptools wheel` BEFORE the main `pip install -r requirements.txt`) into the routine bootstrap so it doesn't need to be remembered every run.
4. Cloud scheduler audit — 5/11–5/14 only fired EOD partial; 5/15 fired all 5 routines on schedule. Confirm whether 5/15 was the start of a stable pattern or a one-day reprieve.
5. RuFlo MCP unavailable in cloud env — file-only fallback used all week.

---

## 2026-05-15 19:46 UTC — End-of-Day Review (cloud routine)

`notify.py brief` and `notify.py dashboard` both failed: `memory/discord_config.json` (webhooks) and `DISCORD_BOT_TOKEN` (.env) still not provisioned in cloud routine host. Routine completed all on-disk steps; flush these once Discord credentials are present.

### #daily-brief (silent summary)
**Title**: End-of-Day Review — 2026-05-15
**Body**: Flat day: 0 trades, 0 positions, P&L $0.00 (0.00%). 100% cash overnight. AMZN-2026-05-15 still armed (`Approved: NO`) — EOD price $263.56 closed $0.44 below the $264–$265.50 entry zone (RSI cooled 62.9 → 57.8, R:R now 4.05:1 if filled). MSFT held SMA 20 reclaim ($423.39 vs $417.5) all session — 1 of 2 re-arm conditions confirmed into close, MACD cross still pending. NVDA Setup #1 still STALE; 5/20 AMC earnings binary risk unchanged. 0/5 positions, 0/3 weekly trades, daily loss cap not approached. Top observation: approval gate held under intraday pressure — that is the gate working as designed.

### Dashboard mirror
`Dashboard.md` regenerated successfully (live=false, positions=0, pending_setups=3). Pinned-message mirror in `#daily-brief` NOT updated — `DISCORD_BOT_TOKEN` still missing.

### Risk alert / reflective question
None pushed today. No daily loss cap breach, no hard rule violation. Reflective question deferred to tomorrow's Friday weekly review (4:30 PM ET) to be asked against the full week's data.

### Infra fix still needed (re-confirmed; no progress since 2026-05-15 16:30 UTC)
1. Provision `memory/discord_config.json` (copy of `discord_config.example.json` with real webhook URLs) on the cloud routine host.
2. Set `DISCORD_BOT_TOKEN` in the cloud routine host's `.env`.

---

## 2026-05-15 16:30 UTC — Midday Scan (cloud routine)

`notify.py brief` failed: `memory/discord_config.json` still missing in cloud routine host. Routine completed all on-disk steps; the brief below needs to be flushed once Discord credentials are provisioned.

### #daily-brief (silent summary)
**Title**: Midday Scan — 2026-05-15
**Body**: 0 positions to manage. 0 trades placed. 0 new setups proposed. AMZN-2026-05-15 still armed (`Approved: NO`); midday price $263.13 just below the $264–$265.50 entry zone (RSI cooled to 57.3, R:R now 4.7:1 if filled here, but conditional gate still unmet — kept zone as Santiago-defined). MSFT reclaimed SMA 20 ($424.48 vs $417.5) — 1 of 2 re-arm conditions met for Setup #2; MACD cross still pending. NVDA pulled back to $228.29 (RSI 76.7→67.7) but not yet in $215–$220 watch zone; 5/20 earnings binary risk unchanged. Broad tape de-risked mildly (SPY −0.93%, QQQ −1.18%) — momentum names led the cool-off (NVDA −3.2%, AMD −4.0%, TSLA −4.4%). Defensive posture intact. 0/5 positions, 0/3 weekly trades, 0% deployed.

### Dashboard mirror
`Dashboard.md` regenerated. Pinned-message mirror in `#daily-brief` NOT updated — `DISCORD_BOT_TOKEN` still missing.

### Infra fix still needed (re-confirmed; no progress since 2026-05-15 13:35 UTC)
1. Provision `memory/discord_config.json` (copy of `discord_config.example.json` with real webhook URLs) on the cloud routine host.
2. Set `DISCORD_BOT_TOKEN` in the cloud routine host's `.env`.

---

## 2026-05-15 13:35 UTC — Market Open Execution (cloud routine)

`notify.py brief` failed: `memory/discord_config.json` still missing in cloud routine host. Routine completed all on-disk steps; the brief below needs to be flushed once Discord credentials are provisioned.

### #daily-brief (silent summary)
**Title**: Market Open Execution — 2026-05-15
**Body**: 0 trades placed. 3 setups skipped — NVDA stale, MSFT pass, AMZN-2026-05-15 awaiting Santiago approval (AND fresh quote $261.30 below the $264.00–$265.50 entry zone, conditional gate failed). Portfolio 100% cash, 0/5 positions, 0/3 weekly trades used. Pause toggle absent (treated unpaused). RuFlo MCP unavailable — file-only mode. ClickUp `pending_setups` list polled read-only, 0 tasks (Phase 3 — routines no longer write).

### Dashboard mirror
`Dashboard.md` regenerated successfully (live=false [Alpaca live-equity call skipped or fell back], positions=0, pending_setups=3). Pinned-message mirror in `#daily-brief` was NOT updated because `DISCORD_BOT_TOKEN` is still missing in the cloud routine host.

### Infra fix still needed (re-confirmed)
1. Provision `memory/discord_config.json` (copy of `discord_config.example.json` with real webhook URLs) on the cloud routine host.
2. Set `DISCORD_BOT_TOKEN` in the cloud routine host's `.env`.
