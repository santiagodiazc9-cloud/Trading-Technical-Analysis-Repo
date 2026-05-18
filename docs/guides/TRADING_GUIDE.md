# Trading Agent — Complete User Guide

This guide is for you, Santiago, when you forget which tool does what (or when you want to know what to do at any given moment).

---

## Part 1 — The Big Picture

You have an autonomous AI trading agent that runs on a paper-trading Alpaca account. It analyzes markets, proposes trades, and (with your approval) executes them. It learns from your feedback and journals every decision.

**There is no single "app" you log into.** Instead, several tools each handle one piece. This guide explains which tool to use for which job.

### The flow in one paragraph

The agent runs on a schedule (5 routines a day, M–F). Each routine reads its memory files in your project folder, fetches data from Alpaca, decides what to do, posts results to **Discord**, and writes a journal entry. You see the proposals on your phone via Discord push notifications, approve or deny with a button tap (or a slash command, or a direct file edit), and the next routine acts on your decision. You can talk to the agent any time via slash commands, Discord channels (`#knowledge-inbox`, `#feedback`, `#chat`), or via Claude Code in VS Code.

---

## Part 2 — The Tools at a Glance

| Tool | Role | When you use it | Where it lives |
|------|------|------------------|-----------------|
| **Discord (web + mobile)** | Your phone-based control surface. Approve trades, see fills, get alerts, train the agent | Many times a day, especially morning + after market close | iPhone / web / Mac app |
| **launchd (Mac background)** | Runs the 4 scheduled jobs: routines, dispatcher, security scan, Discord bot | Set-and-forget. Inspect logs in `launchd_*.log` if something looks off | Mac filesystem |
| **VS Code + Claude Code** | Manual interactive control. Edit memory files, trigger ad-hoc analysis, debug | When you want to dig in, run a one-off scan, fix something | VS Code on Mac |
| **RuFlo MCP** (in Claude Code) | Vector memory + agent swarms — used by routines for "find similar past setups" | Mostly invisible — the routines call it. Pinned to `3.7.0-alpha.20` in `.mcp.json` | Background MCP server |
| **Alpaca Paper Markets (web + mobile app)** | The actual brokerage. Holds positions, executes trades, holds your $100k paper balance | Once a day to verify positions, occasionally to monitor live | iPhone / web |
| **The project folder `~/code/trading-agent/`** | The agent's brain. Memory, journal, scripts, routines, ADRs — all live here | Rarely directly. View through VS Code. Source of truth for everything | Mac filesystem |

**The 80/20 rule:** 80% of your day-to-day happens in **Discord on your phone**. 20% happens in **VS Code** when you want to dig in or fix something. The rest runs invisibly via launchd.

---

## Part 3 — Each Tool in Detail

### 3.1 launchd (background scheduling)

**What it is:** macOS's built-in cron equivalent. Four jobs are loaded:

| Job | What it runs | When |
|---|---|---|
| `com.claude.tradingagent.routines` | Picks the right routine based on time-of-day, runs it via Claude Code | M–F at 08:00, 09:35, 12:30, 15:45 ET + Fri 16:30 ET |
| `com.claude.tradingagent.polling` | Runs the Discord dispatcher (drains `/run`, `/ask`, `#knowledge-inbox`, `#feedback` queues) | Every 15 min, gated 08:00–16:30 ET M–F |
| `com.claude.tradingagent.security` | Runs the Saturday security scan (CVE check, secret leak scan) | Sat 11:00 ET |
| `com.claude.tradingagent.discordbot` | The Discord bot — listens for buttons, slash commands, channel posts | Always on (`KeepAlive=true`) |

**Where to look:**
- Plists: `scripts/claude_*_launchd.plist` (templates) → installed at `~/Library/LaunchAgents/`
- Logs: `launchd_*.log` in the project root
- Status: `launchctl list | grep tradingagent`

**Critical:** routines run **only while your Mac is on**. Closing the laptop = no routines. The eventual fix is Cloud Cowork (see [CLOUD_COWORK.md](CLOUD_COWORK.md)).

### 3.2 VS Code + Claude Code

**What it is:** Your code editor with an AI agent built in. Claude Code in VS Code talks to the same Claude (the one writing this guide), but interactively.

**What you do here:**
- One-off conversations with the agent ("analyze NVDA right now")
- Edit memory files manually (e.g., approve a setup by editing `memory/open_positions.md`)
- Run the project's Python scripts directly (`python3 scripts/research.py scan`)
- Trigger any routine on demand (Cmd+Shift+P → "Run Task" — see [RUN_ROUTINES.md](RUN_ROUTINES.md))

**When to use it:**
- A scheduled routine failed and you want to debug
- You want to ask "what would you do if I bought NVDA at $208?" (simulation)
- You're editing strategy or learnings files directly
- You're testing a new idea before letting the schedule run with it

### 3.3 RuFlo (background MCP)

**What it is:** A Claude Code MCP server. Pinned to `ruflo@3.7.0-alpha.20` in `.mcp.json`.

**What routines actually use:**
- `mcp__ruflo__memory_store` — index proposed setups, strategy decisions, knowledge dumps, security findings into a vector store
- `mcp__ruflo__memory_search` — pre-market routine asks "have we seen a setup like this before?" before finalizing each proposal
- `mcp__ruflo__system_health` — health check at the start of routines 1, 5, 7

**You almost never touch it directly.** Routines fall back to file-only memory if it's down — they alert via `#risk-alerts` so you know.

### 3.4 Discord

**Your phone-based command center.** Detailed walkthrough in **[DISCORD.md](DISCORD.md)**.

**The 5 things you'll do most:**
1. **Approve a trade**: tap **Approve** on the setup card in `#approvals`
2. **Read a brief**: scroll `#daily-brief` — pinned message is the always-current dashboard
3. **Talk to the agent**: type `/ask <question>` in any channel
4. **Train the agent**: post articles/PDFs in `#knowledge-inbox`, one-liners in `#feedback`
5. **Pause everything**: `/pause [reason]` (no new entries) or `/halt <reason>` (full halt)

The full slash command catalog is in DISCORD.md — 14 commands grouped by purpose.

### 3.5 Alpaca Markets

**What it is:** Your actual paper-trading brokerage. The agent places orders here.

**What you do here:**
- Verify the agent's trades actually happened
- See real-time P&L on positions
- See your $100k paper balance
- Check pending orders (especially trailing stops)

**Mobile app**: download "Alpaca: Investing & Trading" from App Store. Log in. Switch to **Paper Trading** mode (top-right toggle).

**Why you need both Alpaca and Discord**: Discord has the agent's *reasoning* (why it bought, what's the catalyst, fill confirmations). Alpaca has the *truth* (current price, order status, real-time P&L). Both are required for a full picture.

---

## Part 4 — Day-to-Day Flow

### Trading day (Monday-Friday)

#### **Morning — 8:00 AM ET / 2:00 PM CEST (before market opens)**
- Phone buzzes: Pre-Market Brief in `#daily-brief`, setup cards in `#approvals` (one per proposed trade).
- Read each card (entry, stop, target, R:R, confidence, catalyst — under 30 sec each).
- For each setup you like: tap **✅ Approve**. That's it.
- For setups you reject: tap **❌ Deny** (reason field optional but useful for training).
- If you want to think: leave it. You can approve later up until ~9:30 AM ET when market-open executes.
- The pinned **Dashboard** in `#daily-brief` shows current account state, pending setups, risk state.

#### **Market open — 9:35 AM ET / 3:35 PM CEST**
- Market-open execution routine fires.
- Approved setups become real Alpaca orders. Trailing stops placed automatically.
- Each fill posts to `#fills` (symbol, qty, price, order ID).
- Any rejection (PDT, stop placement failure, daily loss cap) → high-severity alert in `#risk-alerts` (@here pings phone).
- New brief in `#daily-brief`: "Market Open Execution — YYYY-MM-DD".

#### **Midday — 12:30 PM ET / 6:30 PM CEST**
- Midday Scan fires.
- Reads positions, manages stops, may flag new setups (`<SYMBOL>-YYYY-MM-DD-midday` IDs).
- New approval cards if it found anything.
- Any `-7%` cut closure → `#risk-alerts` first, then `#fills`.

#### **End of trading day — 3:45 PM ET / 9:45 PM CEST**
- EOD Review fires.
- Closes day trades. Updates the trade log + daily snapshot.
- Brief posted to `#daily-brief` (P&L, trades closed, win/loss).
- Dashboard pin updates.
- Occasionally: a reflective question in `#chat` (e.g., "You denied AMD on Tuesday — was that the right call?"). Reply when you have time — your reply gets folded into `memory/learnings.md` by the next dispatcher tick.

#### **Friday evening — 4:30 PM ET / 10:30 PM CEST**
- Weekly Review fires.
- Most important brief of the week. Strategy adjustments happen here. ADRs written if any rules changed.

### Off-day (Saturday-Sunday)
- **Saturday 11:00 AM ET**: security scan fires automatically. Posts findings to `#risk-alerts` (CRITICAL/HIGH) and `#daily-brief` (medium/low summary).
- Otherwise nothing fires. Use the time for:
  - Drop strategy articles into `#knowledge-inbox` — they'll process Monday morning
  - Drop short notes / corrections into `#feedback`
  - Open VS Code, scroll through this week's `journal/*.md` entries

---

## Part 5 — Common Tasks (Step-by-Step)

### "How do I approve a trade?"
- **Phone:** open `#approvals` → tap **✅ Approve** on the setup card. Done.
- **Slash:** type `/approve NVDA-2026-05-11` in any channel.
- **File:** open `memory/open_positions.md` in VS Code → find the `### NVDA-2026-05-11 …` heading → add a line `- Approved: YES` underneath.

All three write to the same flag in the same file. The next market-open routine sees it and trades.

### "How do I deny a trade?"
- **Phone:** tap **❌ Deny** on the card. (Reason input is optional — providing one is better for training.)
- **Slash:** `/deny NVDA-2026-05-11 too overbought`
- **File:** add `- Denied: YES (reason)` under the heading.

### "How do I see my portfolio right now?"
- **Phone:** type `/positions` (Alpaca live) or `/dashboard` (full state) in Discord. Both reply ephemerally — only you see them.
- **Phone (Alpaca app):** open Alpaca → Paper Trading mode → Home tab.
- **VS Code:** `python3 scripts/alpaca_client.py positions`

### "How do I add a stock to the watchlist?"
- **Phone:** `/watchlist add NVDA Tech "AI chip leader"`
- **VS Code:** edit `memory/watchlist.json` directly.

### "How do I remove a stock?"
- **Phone:** `/watchlist remove TSLA`

### "How do I see the current watchlist?"
- **Phone:** `/watchlist show`

### "How do I train the agent on a new strategy I read about?"
1. Find the article URL or download the PDF.
2. Open Discord → `#knowledge-inbox` channel.
3. Paste the URL or attach the PDF. Add a one-line description if you want.
4. Within 15 minutes (during market hours) the dispatcher routine fetches the content, summarizes it via a researcher sub-agent, integrates rules into `memory/learnings.md`, indexes in RuFlo, and posts a confirmation back.

### "How do I tell the agent 'don't be so cautious about TSLA'?"
- **Discord:** post the line in `#feedback`. The dispatcher folds it into `memory/learnings.md` verbatim under `## Feedback — YYYY-MM-DD`.
- **Or** use `/ask` if you want a back-and-forth answer.

### "How do I pause everything for a day?"
- `/pause [optional reason]` — no new entries fire; existing stops still work.
- `/resume` — back to normal.
- `/halt <reason>` — full halt: skip ALL trading actions until `/resume`. Required reason for the audit trail.

### "How do I manually trigger a routine right now?"
- **Discord:** `/run pre-market` (or `market-open` / `midday` / `eod` / `weekly` / `security`). Queues to `memory/run_queue.json`. Next dispatcher tick (every 15 min) runs it.
- **VS Code:** Cmd+Shift+P → "Tasks: Run Task" → "Routine N: Copy Prompt to Clipboard" → paste into Claude Code → Enter.

### "How do I see what the agent is 'thinking'?"
- **Recent reasoning:** journal entries in `journal/YYYY-MM-DD.md`. Open in VS Code.
- **Live in Discord:** `/ask "Walk me through your reasoning on the NVDA setup."` — answer arrives in `#chat` on the next dispatcher tick.
- **Long-term patterns:** `memory/learnings.md`.

### "Something broke / agent stopped responding"
1. Check Discord `#risk-alerts` — agent posts breakage there with @here pings.
2. Check `launchctl list | grep tradingagent` — should show 4 jobs (3 schedule-driven + 1 always-on bot).
3. Check the launchd logs in the project root: `launchd_discord_bot.log`, `launchd_claude_routines.log`, `launchd_claude_polling.log`.
4. Open VS Code → `python3 scripts/alpaca_client.py account`. If this fails, the `.env` keys may have rotated.
5. Check `memory/pending_discord_updates.md` — fallback log if `notify.py` failed during a routine.

---

## Part 6 — Important Things to Know

### About paper trading
- This is **not real money**. You have $100k of fake money to learn with.
- The market data IS real (15-min delayed on free Alpaca tier).
- Trade fills in paper are sometimes more optimistic than real. Don't extrapolate paper performance to live without caution.
- **Stay on paper for at least 30 trading days of clean operation before considering live.**

### About risk rules (NON-NEGOTIABLE — read CLAUDE.md for full list)
- Max 5 open positions at a time
- Max 20% of portfolio per single position
- Max 3 NEW trades per week
- Hard cut at -7% loss on any position (no exceptions)
- 10% trailing stop on every entry (placed as REAL order on Alpaca, not just a note)
- Stop tightens to 7% at +15% gain, 5% at +20% gain
- 75-85% capital deployed when active
- Daily loss cap: -2% → stop trading for the day
- After 2 consecutive losses in a sector: exit all positions in that sector, 5-day cooldown

### About training
- "Training" the agent is NOT fine-tuning the AI model. You can't change Claude itself.
- What you CAN do is grow `memory/learnings.md` and `memory/strategy.md`. Every routine reads these before deciding.
- More feedback = better-tuned agent. Drop a strategy article every week. Comment on every approve/deny. Reply to reflective questions in `#chat`.

### About the dispatcher routine
- It's the bridge between Discord (where you type) and the agent's local file system + RuFlo memory.
- Runs every 15 min during market hours (08:00–16:30 ET M–F).
- Drains 4 queue files: `run_queue.json`, `discord_chat_queue.json`, `knowledge_inbox_queue.json`, `feedback_queue.json`.
- If you post in `#knowledge-inbox` outside market hours, it'll process Monday morning.
- It logs every action in `memory/last_dispatch.json`.

### About .env, configs, and API keys
- `.env` (gitignored) has Alpaca + Discord bot keys.
- `memory/discord_config.json` (gitignored) has Discord webhook URLs and channel IDs.
- Never paste either into a chat or commit them. The `.gitignore` already protects against this — verify with `git ls-files | grep -iE "env|discord_config\.json$"`.
- If keys ever leak, rotate them immediately at the providers' sites.

---

## Part 7 — Where to Look When You're Confused

| Question | Read |
|----------|------|
| What can each Discord channel do? | `DISCORD.md` |
| What are all the slash commands? | `DISCORD.md` |
| How do I run any routine manually? | `RUN_ROUTINES.md` |
| What rules does the agent follow? | `CLAUDE.md` |
| What's the agent's current strategy? | `memory/strategy.md` |
| What did the agent do today? | `journal/YYYY-MM-DD.md` |
| What lessons has the agent learned? | `memory/learnings.md` |
| What setups are pending approval? | `memory/open_positions.md` (or `/setups` in Discord) |
| Did a `notify.py` call fail? | `memory/pending_discord_updates.md` |
| Initial install/setup steps | `SETUP.md` |
| THIS FILE | `TRADING_GUIDE.md` (you are here) |

---

## Part 8 — When to Talk to Me (in this chat)

Open a Claude Code session (in VS Code or this chat) when you want to:
- Add a new feature ("can the agent also analyze options?" — I'd push back: no options per the rules)
- Change a strategy rule ("I want to allow 4 trades/week instead of 3")
- Implement a new RuFlo capability (multi-agent swarms, /remote-control, etc.)
- Migrate to true cloud routines so it runs even with your Mac off (see `CLOUD_COWORK.md`)
- Troubleshoot a deeper issue
- Add or rewire Discord channels / slash commands

Use **Discord on your phone** for daily operations: approvals, fills, alerts, knowledge dumps, feedback, manual routine triggers, conversational questions.

Use **Claude Code in VS Code** when you want to inspect files, run scripts directly, or have a deeper interactive session.

---

## Quick Cheat Sheet (print this)

```
APPROVE TRADE        →  Discord #approvals → tap ✅, OR /approve <id>
DENY TRADE           →  Discord #approvals → tap ❌, OR /deny <id> <reason>
PAUSE AGENT          →  /pause [reason]    (resume with /resume)
FULL HALT            →  /halt <reason>     (resume with /resume)
TRAIN AGENT          →  Drop URL/PDF in #knowledge-inbox
                        OR one-liner in #feedback
SEE BRIEFS           →  Discord #daily-brief (pinned dashboard = live state)
SEE ALERTS           →  Discord #risk-alerts (@here = critical/high)
SEE FILLS            →  Discord #fills
SEE BALANCE          →  /account     OR Alpaca app → Paper Trading
SEE POSITIONS        →  /positions   OR Alpaca app
SCAN A SYMBOL        →  /scan AAPL
ADD TO WATCHLIST     →  /watchlist add NVDA Tech "AI chip leader"
ASK A QUESTION       →  /ask <question>  (answer in #chat ~15min later)
RUN A ROUTINE NOW    →  /run pre-market | market-open | midday | eod | weekly | security
EMERGENCY STOP       →  /halt <reason>
```

That's everything. Welcome aboard.
