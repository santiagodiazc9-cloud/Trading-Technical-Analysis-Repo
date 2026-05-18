# Running the Trading Agent — Cheat Sheet

Pin this file as a tab in VS Code so it's always one click away.

---

## Three ways routines run

| Mode | Where | When | What it does |
|------|-------|------|--------------|
| **Automatic (launchd)** | macOS background, 4 jobs loaded via `launchctl` | Per-job schedule | All routines fire at the right times, post to Discord, refresh the dashboard |
| **Discord-driven** | `/run <routine>` slash command | Anytime; processed by next 15-min dispatcher tick | Queues to `memory/run_queue.json`, dispatcher picks it up, runs the routine |
| **Manual from VS Code** | Cmd+Shift+P → Run Task, or paste prompt into Claude Code | Anytime you trigger it | You run any routine on demand, full control |

All three modes read/write the same `memory/` and `journal/` files, so they stay in sync.

---

## Manual runs from VS Code — three options

### Option A: VS Code Tasks (fastest)
Press **Cmd+Shift+P** → type **"Run Task"** → press Enter → pick one from the list.

The tasks I set up:

**Quick checks (run a script directly, no Claude needed):**
- `Trading: Test Alpaca Connection` — confirms keys work
- `Trading: Show Open Positions` — what's in your account right now
- `Trading: Show Recent Orders` — last orders placed
- `Trading: Market Clock` — is the market open?
- `Trading: Scan Watchlist` — full TA scan of every watchlist symbol
- `Trading: Analyze Symbol` — pops a prompt for a ticker, runs full analysis

**Run a full routine via Claude Code (copies prompt to clipboard, you paste it in):**
- `Routine 1 (Pre-Market): Copy Prompt to Clipboard`
- `Routine 2 (Market Open): Copy Prompt to Clipboard`
- `Routine 3 (Midday): Copy Prompt to Clipboard`
- `Routine 4 (End-of-Day): Copy Prompt to Clipboard`
- `Routine 5 (Weekly Review): Copy Prompt to Clipboard`

**How the routine tasks work:** clicking one copies a one-line prompt onto your clipboard. Then click into Claude Code (the chat box at the bottom of VS Code) and press **Cmd+V** + Enter.

**Other useful:**
- `Trading: Show Pending Notification Failures` — if a routine couldn't reach Discord, the summary lands in `memory/pending_discord_updates.md`. This task prints it.

### Option B: Type the prompt directly into Claude Code

If you don't want to use Tasks, just paste any of these into the Claude Code chat box:

```
Run the pre-market research routine — read routines/1_pre_market_research.md and follow every step exactly.
```
```
Run the market open execution routine — read routines/2_market_open_execution.md and follow every step exactly. Only place trades for setups explicitly approved in memory/open_positions.md.
```
```
Run the midday scan routine — read routines/3_midday_scan.md and follow every step exactly.
```
```
Run the end-of-day review routine — read routines/4_end_of_day_review.md and follow every step exactly.
```
```
Run the Friday weekly review routine — read routines/5_weekly_review.md and follow every step exactly.
```

### Option C: Quick one-liners (no routine, just info)

```
Show me my account status and current positions.
```
```
Analyze NVDA — run the research script and tell me if there's a trade setup.
```
```
What's in memory/open_positions.md right now? Are there setups awaiting approval?
```

---

## From Discord (phone-friendly)

Use the `/run` slash command in any channel:

```
/run pre-market
/run market-open
/run midday
/run eod
/run weekly
/run security
```

This queues the request to `memory/run_queue.json`. The dispatcher routine (which fires every 15 min during market hours) drains the queue and executes the named routine. So expect up to 15-min latency before it actually fires. Confirmation appears in `#daily-brief` after completion.

---

## Approving a trade

The agent never trades without your OK. When a routine flags a setup, it lands in two places:
1. **A setup card in Discord `#approvals`** with Approve / Deny / More info buttons
2. **`memory/open_positions.md`** under "Pending Setups" with a `<SYMBOL>-YYYY-MM-DD` heading

To approve, do **any** of:
- Tap **✅ Approve** on the Discord card
- Type `/approve NVDA-2026-05-11` in any Discord channel
- Open `memory/open_positions.md` in VS Code and add `- Approved: YES` under the setup's heading

The next market-open execution run will see that flag and trade it.

---

## What runs automatically

Four launchd jobs, all loaded at boot via `~/Library/LaunchAgents/com.claude.tradingagent.*.plist`:

| Job | Routine | Schedule (ET) | Schedule (CEST) |
|---------|---------|-----------|-----|
| routines | Pre-Market Research | 08:00 M–F | 14:00 |
| routines | Market Open Execution | 09:35 M–F | 15:35 |
| routines | Midday Scan | 12:30 M–F | 18:30 |
| routines | End-of-Day Review | 15:45 M–F | 21:45 |
| routines | Friday Weekly Review | 16:30 Fri | 22:30 |
| polling | Discord Dispatcher | every 15 min, gated 08:00–16:30 M–F | 14:00–22:30 |
| security | Saturday Security Scan | 11:00 Sat | 17:00 Sat |
| discordbot | Discord bot (always-on) | continuous, restart on crash | continuous |

To pause, edit, or trigger them:
- **Inspect:** `launchctl list | grep tradingagent`
- **Disable a job:** `launchctl unload ~/Library/LaunchAgents/com.claude.tradingagent.<name>.plist`
- **Re-enable:** `launchctl load ~/Library/LaunchAgents/com.claude.tradingagent.<name>.plist`
- **Logs:** `tail -f launchd_*.log` in the project root

The Mac must be on for routines to fire — closing the laptop = no routines. Future-state: Cloud Cowork (see `CLOUD_COWORK.md`).

---

## Where to look for results

- **Live notifications** → Discord push notifications on your phone
- **Setup approval cards** → Discord `#approvals`
- **Order fills** → Discord `#fills`
- **High-priority alerts** → Discord `#risk-alerts` (@here pings phone)
- **Routine summaries + pinned live dashboard** → Discord `#daily-brief`
- **Conversational answers / reflective questions** → Discord `#chat`
- **Account & positions** → Alpaca Paper Trading app, or `/account` `/positions` in Discord
- **Decisions & reasoning** → `journal/YYYY-MM-DD.md` (today's journal)
- **Open positions** → `memory/open_positions.md`
- **Lessons over time** → `memory/learnings.md`
- **Trade history** → `memory/trade_log.json`
- **Fallback log when `notify.py` fails** → `memory/pending_discord_updates.md`

Full Discord channel + slash command catalog: see `DISCORD.md`.
