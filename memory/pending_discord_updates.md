# Pending Discord Updates

This file is a fallback log. When a routine's `notify.py` call fails (Discord webhook unreachable, network error, bot REST API rejection, etc.), the routine appends its summary here with a timestamp instead of halting.

---

## 2026-06-05 16:38 UTC — Midday Scan brief (notify.py failed: discord_config.json missing)

- **Channel**: #daily-brief (silent)
- **Title**: Midday Scan — 2026-06-05
- **Body**: Book flat (0/5), deployed 0%. No positions to manage. No internet-flagged symbols. 0 setups proposed. POSTURE FLIP 🟢 GREEN → 🟡 CAUTION: SPY $744.26 (-1.6% vs 6/04 midday $756.29) below SMA 20 ($746.59), still above SMA 50 ($713.59) and SMA 200 ($683.94). RSI 55.0 (cooled from 69.4), MACD hist -1.66 (deeper negative), Stoch K 30.3, BB pct 0.43, ATR 6.95. Shallow dip (-0.31% below SMA 20, within 1% trigger), CAUTION-exceptions intact (conf ≥ 8 + sector-ETF-aligned). No VIX, no SPY single-candle >1.5% gap — override not applied. First posture transition since SMA system adopted 2026-05-19. Weekly count Week-5: 0/3 with EOD + Weekly Review remaining.

- **Channel**: #daily-brief (dashboard pin mirror)
- **Action**: `notify.py dashboard` — failed (DISCORD_BOT_TOKEN missing from .env). Dashboard.md regenerated successfully on disk (live=true, positions=0, pending_setups=1 — same parser quirk as prior days reading the `_None._` placeholder; no real pending setup).
- **Reason**: `memory/discord_config.json` still missing in cloud routine host + `DISCORD_BOT_TOKEN` missing from .env. Recurring P0 infra gap — 11th consecutive routine without phone-side delivery. Today's posture-change event is precisely the kind of mid-session signal Discord exists to deliver; only saving grace is that the flat book makes it operationally moot.
- **Action needed Santiago side**: provision `discord_config.json` + `DISCORD_BOT_TOKEN` in cloud workspace.

### 2026-06-05 16:42 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on the first attempt at this midday routine. Identical failure mode as 5/28, 5/29, 6/01, 6/02, 6/03, 6/04 (all routines) and the 6/05 market-open earlier today. Local HEAD is 1 commit ahead of origin/main (the midday commit d82f2dd); falling back to `mcp__github__push_files` to publish the 4 routine-touched files (memory/market_context.md, memory/open_positions.md, memory/pending_discord_updates.md, journal/2026-06-05.md) across 2 sequential API commits (first commit pushed 3 files, this follow-up pushes pending_discord_updates.md). Local commit will be superseded by the API commits; next routine should `git fetch origin && git reset --hard origin/main` to re-sync working tree.
- **Action needed**: Santiago side — local git proxy 403 has now persisted ~16 sessions (5/28 → 6/05 midday). Migrate routine commits to API push as primary path OR investigate proxy auth/credential lifecycle. Friday Weekly Review (later today) is the natural place to land this as a definitive infra rule.

---

## 2026-06-05 13:38 UTC — Market Open Execution brief (notify.py failed: discord_config.json missing)

- **Channel**: #daily-brief (silent)
- **Title**: Market Open Execution — 2026-06-05
- **Body**: 0 trades placed (Approved-YES queue empty for 7th consecutive intraday routine). 0/5 positions; equity $98,612.09; cash $98,612.09; buying power $394,448.36; deployed 0%; day P&L $0.00; daytrade 0/3; PDT false. Posture 🟢 GREEN carried from 6/04 midday (SPY $756.29, full bull SMA stack, RSI 69.4). Weekly count Week-5: 0/3 with Friday remaining. Sector blocklist empty; Comm Services 1/2 toward auto-blocklist. Hard rule violations this routine: none.

- **Channel**: #daily-brief (dashboard pin mirror)
- **Action**: `notify.py dashboard` — failed (DISCORD_BOT_TOKEN missing from .env). Dashboard.md regenerated successfully on disk (live=true, positions=0, pending_setups=1 — same parser quirk as 6/03 + 6/04, reading the `_None._` placeholder; no real pending setup).
- **Reason**: `memory/discord_config.json` still missing in cloud routine host + `DISCORD_BOT_TOKEN` missing from .env. Recurring P0 infra gap — 10th consecutive routine without phone-side delivery. Friday Weekly Review (later today) must land a provisioning plan.
- **Action needed Santiago side**: provision `discord_config.json` + `DISCORD_BOT_TOKEN` in cloud workspace.

### 2026-06-05 13:50 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on the first attempt at this routine. Identical failure mode as 5/28, 5/29, 6/01, 6/02, 6/03, 6/04 (all routines). Local HEAD is 11 commits ahead of origin/main spanning 6/04 market-open → 6/04 EOD plus today's market-open commit; falling back to `mcp__github__push_files` to publish the 7 routine-touched files (memory/market_context.md, memory/open_positions.md, memory/pending_discord_updates.md, memory/learnings.md, memory/trade_log.json, journal/2026-06-04.md, journal/2026-06-05.md) in a single API commit. Local commits will be superseded by the API commit; next routine should `git fetch origin && git reset --hard origin/main` to re-sync working tree.
- **Action needed**: Santiago side — local git proxy 403 has now persisted ~15 sessions (5/28 → 6/05 market-open). Migrate routine commits to API push as primary path OR investigate proxy auth/credential lifecycle. Friday Weekly Review is the natural place to land this as a definitive infra rule.

---

## 2026-06-04 16:36 UTC — Midday Scan brief (notify.py failed: discord_config.json missing)

- **Channel**: #daily-brief (silent)
- **Title**: Midday Scan — 2026-06-04
- **Body**: Book flat (0/5 positions), 7th consecutive routine with nothing to manage. SPY $756.29 — posture 🟢 GREEN intact (price > SMA 20 > SMA 50 > SMA 200). RSI cooled 75.5 → 69.4 (below ADR-0001 caution threshold for the first time this week). MACD hist -0.69, Stoch K 56.8, BB pct 0.81, ATR 6.36. 0 setups proposed (no internet-flagged tickers in market_context.md). 0 management actions (no positions). Week-5 trade count 0/3 with Thu PM + Fri remaining. Daily loss cap headroom full.

- **Channel**: #daily-brief (dashboard pin mirror)
- **Action**: `notify.py dashboard` — failed (DISCORD_BOT_TOKEN missing from .env). Dashboard.md regenerated successfully on disk (live=true, positions=0, pending_setups=1 — same parser quirk as 6/03 + 6/04 09:37 ET, reading the `_None._` placeholder; no real pending setup).
- **Reason**: `memory/discord_config.json` still missing in cloud routine host + `DISCORD_BOT_TOKEN` missing from .env. Recurring P0 infra gap. Friday weekly review must land a fix.
- **Action needed Santiago side**: provision `discord_config.json` + `DISCORD_BOT_TOKEN` in cloud workspace.

### 2026-06-04 16:40 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on 3 attempts with exponential backoff (initial + 2s + 4s). Identical failure mode as 5/28, 5/29, 6/01, 6/02, 6/03, and earlier-today market-open routines. Falling back to `mcp__github__push_files` to publish memory/market_context.md + journal/2026-06-04.md (commit 165c0fb on origin/main). This pending_discord_updates.md follow-up will land in a second API commit. Local commit (bdef46a) is superseded by the API commits; next routine should `git fetch origin && git reset --hard origin/main` to re-sync working tree.
- **Action needed**: Santiago side — local git proxy 403 has persisted ~13 sessions (5/28 → 6/04 midday). Migrate routine commits to API push as primary path OR investigate proxy auth/credential lifecycle.

---

## 2026-06-04 13:38 UTC — Market Open Execution brief (notify.py failed: discord_config.json missing)

- **Channel**: #daily-brief (silent)
- **Title**: Market Open Execution — 2026-06-04
- **Body**: 0 trades placed | 0 setups skipped (empty pending queue, 6th consecutive scan-less window) | 0/5 positions | equity $98,612.09 | cash $98,612.09 | deployed 0% | day P&L $0.00 | daytrade 0/3 | Week-5 trades 0/3 (Thu 6/4, Fri 6/5 remain)

- **Channel**: #daily-brief (dashboard pin mirror)
- **Action**: `notify.py dashboard` — failed (DISCORD_BOT_TOKEN missing from .env). Dashboard.md regenerated successfully on disk (live=true, positions=0, pending_setups=1 — same parser quirk as 6/03, reading the `_None._` placeholder; no real pending setup).
- **Reason**: `memory/discord_config.json` still missing in cloud routine host + `DISCORD_BOT_TOKEN` missing from .env. Recurring P0 infra gap. Friday weekly review must land a fix.
- **Action needed Santiago side**: provision `discord_config.json` + `DISCORD_BOT_TOKEN` in cloud workspace.

### 2026-06-04 13:42 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on 3 attempts with exponential backoff (initial + 2s + 4s). Identical failure mode as 5/28, 5/29, 6/01, 6/02, 6/03 routines. Falling back to `mcp__github__push_files` + `mcp__github__create_or_update_file` to publish the 3 routine-touched files (memory/market_context.md, memory/pending_discord_updates.md, journal/2026-06-04.md) across 2 sequential API commits. Local commit (31ae2fe) is now superseded by API commits on origin/main; next routine should `git fetch origin && git reset --hard origin/main` to re-sync working tree.
- **Action needed**: Santiago side — local git proxy 403 has persisted ~12 sessions (5/28 → 6/04). Migrate routine commits to API push as primary path OR investigate proxy auth/credential lifecycle.

---

## 2026-06-03 19:48 UTC — End-of-Day Review brief (notify.py failed: discord_config.json missing)

- **Channel**: #daily-brief (silent)
- **Title**: End-of-Day Review — 2026-06-03
- **Body**: Daily P&L -$842.19 (-0.85%) | Equity $98,612.11 | 1 close / 0 wins / 1 loss | 0 swings overnight (flat book) | GOOGL -7.03% manual cut at 12:36 ET (rule fired as designed) | Comm Services sector 1/2 toward blocklist | First confidence-calibration sample in bucket_5_6 (n=1, 0W/1L) | No hard-rule violations | Daily loss cap NOT breached.

- **Channel**: #daily-brief (dashboard pin mirror)
- **Action**: `notify.py dashboard` — failed (DISCORD_BOT_TOKEN missing from .env). Dashboard.md regenerated successfully on disk (live=true, positions=0, pending_setups=1 — the "1" is the parser quirk reading the `_None._` placeholder, no real pending setup exists).

- **Channel**: #chat (reflective question — first close after 5 weeks)
- **Title**: Reflection — 2026-06-03
- **Body**: GOOGL was approved at confidence 6/10 on 2026-05-20 — under the usual 7-gate but justified by Stoch K extreme oversold (0.06) inside a full bull SMA stack with the Google I/O catalyst. Today's -7% cut closed it as our first sample in the calibration data. Looking back, was the "lower the gate when oversold + catalyst + bull stack align" framework right to lower the gate here? Or do we need confidence 6 to require an additional confirmation (e.g. MACD positive cross) before approving in the future?

- **Reason**: `memory/discord_config.json` still missing in cloud routine host + `DISCORD_BOT_TOKEN` missing from .env. Same recurring infra gap noted across 5/13–6/03 routines. **First material consequence today**: midday high-severity cut alert never reached Santiago's phone in real time. Friday weekly review must address as P0.
- **Action needed Santiago side**: provision `discord_config.json` + `DISCORD_BOT_TOKEN` in cloud workspace, or install via session secret store.

### 2026-06-03 19:55 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on all 4 attempts with exponential backoff (2s, 4s, 8s, 16s). Identical failure mode as 5/28, 5/29, 6/01, 6/02, and today's earlier market-open + midday routines. Falling back to `mcp__github__push_files` to publish the 7 EOD-touched files (memory/learnings.md, memory/strategy.md, memory/market_context.md, memory/open_positions.md, memory/pending_discord_updates.md, memory/trade_log.json, journal/2026-06-03.md) in a single API commit. The local commit (6ac9337) on detached-HEAD-rebased-to-main will be superseded by the MCP commit on origin/main; next routine should `git fetch origin && git reset --hard origin/main` to re-sync working tree.
- **Action needed**: Santiago side — the local git proxy 403 has now persisted across ~10 sessions (5/28 → 6/03 EOD) and is a fully stable failure. Recommend migrating routine commits to `mcp__github__push_files` as the primary push path, OR investigate the proxy auth/credential lifecycle definitively.

### 2026-06-03 16:36 UTC — HIGH-SEVERITY RISK ALERT (Discord config missing — alert NOT delivered in real-time)
- **Channel**: #risk-alerts (would have tagged @here on phone)
- **Severity**: HIGH
- **Symbol**: GOOGL
- **Body**: "Position at -7.04% — manual cut rule triggered. Closing now. Current $359.83 < cut trigger $359.98."
- **Action taken anyway**: Trailing stop e0b8fbda cancelled; market-close 51 shares executed at $359.8565 (order 990ed249). Realized -$1,387.89 (-7.03%). See trade_log.json for full record.
- **Reason for fallback**: `memory/discord_config.json` still missing in cloud routine host (recurring known gap; bot config is local-only).
- **CONSEQUENCE**: This is the first session where the Discord gap has had a real-world consequence — Santiago did not receive a phone push for an active hard-rule firing. Priority: P0 for Friday weekly review infra discussion.

### 2026-06-03 16:36 UTC — Fill Notification (Discord config missing)
- **Channel**: #fills
- **Body**: "GOOGL sell 51 @ $359.8565 — order 990ed249-5d7b-43cd-8976-a535a7e72fc0 (market). Reason: -7% manual cut rule. Realized -$1,387.89 (-7.03%) on $19,740.57 cost basis."
- **Reason**: same discord_config.json gap.

### 2026-06-03 16:40 UTC — Midday Scan Brief (Discord config missing)
- **Channel**: #daily-brief (silent)
- **Title**: Midday Scan — 2026-06-03
- **Body**: HARD-CUT FIRED on GOOGL at 12:36 ET ($359.83 < $359.98 trigger, -7.04%). Cancelled trailing stop e0b8fbda; market-close 51 shares filled at $359.8565 (order 990ed249). Realized -$1,387.89 (-7.03%). Account now flat: equity $98,612.11, cash $98,612.11, deployed 0%. Day P&L -$842.19 (-0.85%, within -2% cap). Weekly trade count 0/3 (exits don't count). Daytrade 0/3. Sector tally: Communication Services 1/2 toward blocklist (1 loss; not yet blocked). 0 new setups proposed (no internet-flagged candidates in market_context.md, no full-watchlist scan per routine). All position-management actions complete; book is flat. Pause toggle still missing (treated as active).
- **Reason**: `memory/discord_config.json` missing in cloud routine host.
- **Setups to push as cards**: 0.
- **Dashboard mirror**: `Dashboard.md` regenerated by `scripts/dashboard.py`. Pinned-message mirror NOT updated — DISCORD_BOT_TOKEN missing in cloud (`notify.py dashboard` would return `DISCORD_BOT_TOKEN missing from .env`).

### 2026-06-03 17:00 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on 3 attempts with exponential backoff (initial + 4s + 8s). Identical failure mode as 5/28, 5/29, 6/01, 6/02, and earlier-this-day market-open routines. Falling back to `mcp__github__push_files` to publish the 5 routine-touched files (memory/open_positions.md, memory/market_context.md, memory/pending_discord_updates.md, memory/trade_log.json, journal/2026-06-03.md) across 3 sequential API commits. The local commit (3ef98d3) is now superseded by the MCP commits on origin/main; next routine should `git fetch origin && git reset --hard origin/main` to re-sync working tree to the API-pushed state.
- **Action needed**: Santiago side — the local git proxy 403 has now persisted across ~8 sessions (5/28 → 6/03 midday) and is a fully stable failure. Recommend migrating routine commits to `mcp__github__push_files` as the primary push path, OR investigate the proxy auth/credential lifecycle definitively.

---

### 2026-06-03 13:38 UTC — Market Open Execution Brief (Discord config missing in cloud env)
- **Channel**: #daily-brief
- **Title**: Market Open Execution — 2026-06-03
- **Body**: No trades placed — pending setups queue empty (last archived NVDA-2026-05-27 expired 5/30). 1 open position: GOOGL -$1,288.52 (-6.53%) @ $361.81, trailing stop e0b8fbda ACTIVE. Hard-cut trigger $359.98 = $1.83 / 0.51% buffer (second straight routine inside 1% — midday must re-check immediately). Equity $98,721.94 (deployed 18.7%). Day P&L -$732.36 (-0.74%, within -2% cap). Daytrade 0/3. Sector blocklist empty. `pause_state.json` still missing — treated as active.
- **Reason**: `memory/discord_config.json` missing in cloud routine host (recurring known gap; bot config is local-only).
- **Setups to push as cards**: 0.
- **Alerts**: 0 (daily loss cap clear, no -7% cut yet, no hard-rule violations).
- **Dashboard mirror**: `Dashboard.md` regenerated by `scripts/dashboard.py` (live=true, positions=1, pending_setups=1). Pinned-message mirror NOT updated — DISCORD_BOT_TOKEN missing in cloud (`notify.py dashboard` returned `DISCORD_BOT_TOKEN missing from .env`).

### 2026-06-03 13:40 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on 3 attempts with exponential backoff (initial + 2s + 4s). Identical failure mode as 5/28, 5/29, 6/01, and 6/02 routines. Falling back to `mcp__github__push_files` to publish the 3 routine-touched files (memory/open_positions.md, memory/pending_discord_updates.md, journal/2026-06-03.md) across 2 sequential API commits. The local commit (6554b7c) is now superseded by the MCP commit on origin/main; next routine should `git fetch origin && git reset --hard origin/main` to re-sync working tree to the API-pushed state.
- **Action needed**: Santiago side — the local git proxy 403 has now persisted across ~6 sessions (5/28 → 6/03) and is a stable failure (not transient). Recommend migrating routine commits to `mcp__github__push_files` as the primary push path, OR investigate the proxy auth/credential lifecycle definitively. Every routine eating 3–4 retries before falling back wastes ~10–20 seconds and adds noise to the log.

---

### 2026-06-01 19:50 UTC — End-of-Day Review Brief (notify.py failed: discord_config.json missing in cloud env)

- **Channel**: #daily-brief (silent)
- **Title**: End-of-Day Review — 2026-06-01
- **Body**: Day P&L -$123.93 (-0.12%) | Equity $99,532.84 | 0 closes / 0 wins / 0 losses | 1 swing held overnight: GOOGL -$467.16 (-2.37%) — intraday round-trip $374.62 open → $377.91 close, clawed back ~$167 of weekend drift without forced action. 0 setups proposed (no fresh pre-market scan this morning — 3rd Monday pre-market drop in 3 weeks). Posture 🟢 GREEN held (SPY $758.86 RSI 75.5 overbought). Weekly trade count 0/3. Deployed 19.36% (under-deployed). Daytrade count 0/3. No hard-rule violations. Tomorrow's catalyst: Microsoft Build 2026 Day 1 of 2.
- **Channel**: #daily-brief (dashboard pin mirror)
- **Action**: `notify.py dashboard` — failed with `DISCORD_BOT_TOKEN missing from .env`. Dashboard.md regenerated successfully on disk at `/home/user/Trading-Technical-Analysis-Repo/Dashboard.md` (live=true, positions=1, pending_setups=1).
- **Reason**: `memory/discord_config.json` still missing in cloud routine host AND `DISCORD_BOT_TOKEN` still unprovisioned. Recurring known gap — same failure mode as 5/13-5/30 EOD briefs. Santiago side: provision both `discord_config.json` and `.env` in cloud workspace, OR install via session secret store.

### 2026-06-01 19:58 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on 4 attempts with exponential backoff (2s, 4s, 8s, 16s). Identical failure mode as 5/28, 5/29, and the 13:42 UTC market-open routine. Falling back to `mcp__github__push_files` to publish the 7 EOD-touched files (memory/open_positions.md, memory/market_context.md, journal/2026-06-01.md, memory/learnings.md, memory/strategy.md, memory/trade_log.json, memory/pending_discord_updates.md) across multiple sequential API commits. Local main was rebased onto each API push as it landed to keep the working tree clean.
- **Action needed**: Santiago side — the local git proxy 403 has now persisted across ~5 sessions and is a stable failure (not transient). Migrate routine commits to use `mcp__github__push_files` as the primary push path, OR investigate the proxy auth/credential lifecycle definitively. Continuing to use `git push` as the primary path means every routine eats 4 retries before the fallback fires.

### 2026-06-01 13:37 UTC — Market Open Execution Brief (Discord config missing in cloud env)
- **Channel**: #daily-brief
- **Title**: Market Open Execution — 2026-06-01
- **Body**: No trades placed — no `Approved: YES` setups in pending queue. 1 open position (GOOGL -3.22% @ $374.62, trailing stop e0b8fbda ACTIVE on Alpaca). Account equity $99,361.48 (19.22% deployed — under-deployed band). Cash $80,259.43. Day P&L -$295.29 (-0.30%, well within -2% cap). Daytrade count 0/3. Sector blocklist empty. Awaiting fresh Monday pre-market scan to surface Week 5 candidates (MSFT Build Jun 2-3 is the dominant near-term catalyst). `pause_state.json` was missing on disk — treated as active (no pause/halt) per fallback default. Routine no-op confirmed approval gate is holding correctly.
- **Reason**: `memory/discord_config.json` missing in cloud routine host (recurring known gap; bot config is local-only).
- **Setups to push as cards**: 0.
- **Alerts**: 0 (daily loss cap clear, no -7% cut, no hard-rule violations).
- **Dashboard mirror**: `Dashboard.md` regenerated by `scripts/dashboard.py` (1 position, 1 pending-setup row parsed). Pinned-message mirror NOT updated — DISCORD_BOT_TOKEN missing in cloud.

### 2026-06-01 13:42 UTC — Git push failure (HTTP 403 from local proxy, recurring)
- **Channel**: n/a (internal log)
- **Body**: `git push origin main` returned HTTP 403 from the local git proxy on 4 attempts with exponential backoff (2s, 4s, 8s, 16s). Same failure pattern as 2026-05-28/29 logs. Falling back to `mcp__github__push_files` to publish the 3 routine-touched files (memory/open_positions.md, memory/pending_discord_updates.md, journal/2026-06-01.md). Local commit 9220dce will diverge from origin until proxy is fixed or next routine re-syncs.
- **Action needed**: Santiago side — the local git proxy 403 has now persisted across ~5 sessions. Migrate routine commits to `mcp__github__push_files` as the primary push path.

---

### 2026-05-29 19:47 UTC — End-of-Day Review Brief (Discord config missing in cloud env)
[archived — see prior commits for full content]

### 2026-05-28 13:36 UTC — Market Open Execution Brief (Discord config missing in cloud env)
[archived — see prior commits for full content]

### 2026-05-26 13:37 UTC — Market Open Execution Brief (Discord config missing in cloud env)
[archived — see prior commits for full content]

### 2026-05-25 12:13 UTC — Pre-Market Brief (Memorial Day)
[archived — see prior commits for full content]

### 2026-06-02 13:38 UTC — Market Open Execution Brief (notify.py failed: discord_config.json missing in cloud env — recurring)
[archived — see prior commits for full content]

### 2026-06-04 19:46 UTC — End-of-Day Review Brief (notify.py failed: discord_config.json missing in cloud env — recurring)
[archived — see prior commits for full content]
