# Pending Discord Updates

This file is a fallback log. When a routine's `notify.py` call fails (Discord webhook unreachable, network error, bot REST API rejection, etc.), the routine appends its summary here with a timestamp instead of halting. The dispatcher routine (or a manual catch-up) flushes these to Discord on its next successful run.

The legacy filename was `pending_clickup_updates.md` — kept the renamed file as the single fallback queue across all notification surfaces.

---

## 2026-05-18 12:40 ET — Midday Scan (actual current routine)

`notify.py` calls blocked: `memory/discord_config.json` missing. Flush once Discord credentials are provisioned.

### #daily-brief (silent summary)
**Title**: Midday Scan — 2026-05-18
**Body**: 0 positions / $100k cash / 0% deployed | No setups proposed at midday (binary NVDA event tonight constrains Tech entries) | MSFT half-trigger unchanged (1/2, MACD hist -0.83, RSI 56.4) | AMZN $265.02 re-entered the retired AMZN-2026-05-15 entry zone ($264-$265.50) with Stoch K 1.17 extreme oversold — ADR-0002/0003 forbid intraday self-arming, flagged for fresh evaluation at next pre-market | AMD cooled to ~3.7% above VWAP (was 7.2%), watch VWAP $399-400 | SPY MACD bearish cross persists (hist -0.19) — caution intact, still above $725 SMA 20 | 0/3 weekly trades used.

---

## 2026-05-19 pre-market — Pre-Market Research

`notify.py` calls blocked: `memory/discord_config.json` missing. Flush once Discord credentials are provisioned.

### #risk-alerts (high — RuFlo version drift)
Ruflo MCP running v3.7.0-alpha.21; pinned to alpha.20. Memory store degraded (not initialized). Pre-market ran in file-only fallback. Confirm alpha.21 is safe before updating `.mcp.json` pin.

### #daily-brief (silent summary)
**Title**: Pre-Market Brief — 2026-05-19
**Body**: 0 setups proposed. NVDA earnings AMC tonight — binary event, no Tech entries today. AMZN-2026-05-15 formally retired (ADR-0002 stale). MSFT half-trigger 4th session — MACD hist -0.684, SMA 20 reclaim held. AMD extended 7.2% above VWAP — no chase. Memory correction: Microsoft Build 2026 is June 2-3, not May 19. Priority watch: post-NVDA print at 5/20 pre-market → AMD VWAP pullback ($399-400) and MSFT MACD cross are the two highest-quality setups in the queue. 0/3 weekly trades used. $100k cash.

---

## 2026-05-18 ~15:45 ET — End-of-Day Review

`notify.py brief` and `notify.py send chat` could not run: `memory/discord_config.json` missing. Flush once Discord credentials are provisioned.

### #daily-brief (silent summary)
**Title**: End-of-Day Review — 2026-05-18
**Body**: P&L $0.00 (0.00%) | 0 trades, 0 closes | 0 open positions | NVDA earnings tonight (no exposure, binary risk rule respected), MSFT half-trigger 1/2 x3 sessions (MACD cross pending; Microsoft Build starts 5/19), AMZN-2026-05-15 stales tomorrow pre-market | SPY MACD bearish cross — first momentum stall since May rally | 0/3 weekly slots used.

### #chat (reflective question)
**Title**: Reflection — 2026-05-18
**Body**: The AMZN-2026-05-15 setup has been at Approved: NO for 3 trading days. Tonight it closes $266.48 — literally $0.98 above the upper bound of the entry zone you never approved. Stochastic is at 3.19 (extreme oversold). The setup stales tomorrow pre-market. Looking back: was the hesitation right? And if AMZN pulls back into $264–$265.50 tomorrow, would you want a fresh proposal — or is this tape not one you want to trade into ahead of the NVDA earnings print?

---

## 2026-05-16 15:01 UTC — Security Scan (cloud routine, Saturday weekly)

`notify.py brief` / `notify.py alert` could not run: `httpx` is not installed in the cloud routine host AND `memory/discord_config.json` is still missing. Routine completed all on-disk + ClickUp steps. Findings were posted to ClickUp `risk_and_errors` instead (3 tasks: 2× HIGH, 1× combined MEDIUM/LOW). Flush these once Discord credentials + httpx are present.

### #risk-alerts (HIGH — two findings, would tag @here)
1. **`scripts/discord_bot_cloud.py:70`** — GH_TOKEN embedded in git remote URL persists in `.git/config` on cloud host. If filesystem exposed (debug shell, snapshot, log of `git remote -v`) the token leaks. Fix: per-command `-c http.extraheader='Authorization: bearer <token>'` or in-memory credential helper. ClickUp: `869daw4dd`.
2. **`scripts/discord_bot_cloud.py:85`** — Discord bot token written to a `.env` file inside the repo tree. One stray `git add -A` and the token is committed/pushed. Fix: read `DISCORD_BOT_TOKEN` from process env in `discord_bot.py`, drop the `.env` write. ClickUp: `869daw4e8`.

### #daily-brief (silent summary)
**Title**: 🛡️ Security Scan — 2026-05-16 — 2 HIGH, 3 MEDIUM, 1 LOW
**Body**: Saturday weekly scan complete. 9 scripts reviewed (~2,765 LOC), 7 dependencies inventoried. **0 CRITICAL, 2 HIGH** (both cloud-deployment secret hygiene in `discord_bot_cloud.py`), **3 MEDIUM** (user-input → routine prompt-injection in `discord_bot.py`, attacker-controlled `reason` injected into `open_positions.md`, unvalidated symbol/qty in `alpaca_client.py` CLI — no notional ceiling), **1 LOW** (ACTION_LOG unbounded growth). **Positive**: `paper=True` hardcoded in alpaca_client, no live-API codepath exists, `.env` + `discord_config.json` clean in git history, no eval/exec/pickle/shell=True/verify=False anywhere, all httpx calls have timeouts. **CVE flags** (need live-feed re-verification): `httpx>=0.25.0` (CVE-2024-25199, bump to >=0.27), `pandas>=2.0.0` (CVE-2024-9880 <2.2.2). Recommend adding `pip-audit` to weekly routine and pinning upper bounds on `requirements.txt`. Findings posted to ClickUp `risk_and_errors` (3 tasks). No fixes applied — routine is read-only by design.

### Infra fix still needed
1. Provision `memory/discord_config.json` (webhooks) on cloud routine host.
2. Set `DISCORD_BOT_TOKEN` in cloud routine host's `.env`.
3. Install `httpx` in cloud routine host so `notify.py` can run (and re-verify the full `pip install -r requirements.txt` bootstrap including the `ta` workaround).
4. RuFlo MCP unavailable → security findings NOT indexed into `trading-security` namespace. Re-run scan after RuFlo restored if you want regression tracking.

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

---

## 2026-05-18 — Discord Dispatcher (15-min cadence)

`notify.py brief` failed: `memory/discord_config.json` still missing. All queues drained (all empty). `memory/last_dispatch.json` initialized fresh.

### #daily-brief (silent summary)
**Title**: Dispatcher — 2026-05-18
**Body**: All queues empty (run=0, chat=0, knowledge=0, feedback=0). pause_state.json absent → treated active. RuFlo MCP unavailable (permission not granted) — file-only fallback. Dashboard refresh failed: `dashboard.py` crashes when `run_queue.json` is a raw array rather than `{"queue":[...]}` (line ~158, `AttributeError: 'list' object has no attribute 'get'`). Fix: change `read_json(RUN_QUEUE, {"queue":[]}).get("queue",[])` to handle both list and dict formats.

### Bug logged
- **File**: `scripts/dashboard.py` line 158
- **Error**: `AttributeError: 'list' object has no attribute 'get'` when `run_queue.json` contains a raw `[]` array
- **Fix**: `_rq = read_json(RUN_QUEUE, []); state["run_queue"] = _rq if isinstance(_rq, list) else _rq.get("queue", [])`
