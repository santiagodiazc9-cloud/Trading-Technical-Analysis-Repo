# Trading Agent — Complete User Guide

This guide is for you, Santiago, when you forget which tool does what (or when you want to know what to do at any given moment).

---

## Part 1 — The Big Picture

You have an autonomous AI trading agent that runs on a paper-trading Alpaca account. It analyzes markets, proposes trades, and (with your approval) executes them. It learns from your feedback and journals every decision.

**There is no single "app" you log into.** Instead, several tools each handle one piece. This guide explains which tool to use for which job.

### The flow in one paragraph

The agent runs on a schedule (5 routines a day). Each routine reads its memory files in your project folder, fetches data from Alpaca, decides what to do, posts results to ClickUp, and writes a journal entry. You see the proposals on your phone via ClickUp, approve or deny with a tap, and the next routine acts on your decision. You can also talk to the agent any time via Claude Code in VS Code or via ClickUp's Agent Chat.

---

## Part 2 — The Tools at a Glance

| Tool | Role | When you use it | Where it lives |
|------|------|------------------|-----------------|
| **Claude Desktop App (Cowork)** | Runs scheduled routines, hosts ClickUp connector, runs polling routine | Set-and-forget mostly. Open to manage schedule, pause/resume routines, see logs | Mac app |
| **VS Code + Claude Code** | Manual interactive control of the agent. Edit memory files, trigger ad-hoc analysis | When you want to ask questions, run a one-off scan, fix something | VS Code in Mac |
| **RuFlo (in Claude Code)** | Optional power-user enhancement: vector memory, agent swarms, ADRs | Advanced — covered in Part 7. Skip until you've used the basics for a few days | VS Code terminal |
| **ClickUp (web + mobile app)** | Your phone-based control surface. Approve trades, train agent, see briefs | Many times a day, especially morning + after market close | iPhone/web |
| **Alpaca Markets (web + mobile app)** | The actual brokerage. Holds positions, executes trades, holds your $100k paper balance | Once a day to verify positions, occasionally to monitor live | iPhone/web |
| **The project folder in `/Users/santiagodiaz/Documents/Claude/Projects/...`** | The agent's brain. Memory, journal, scripts, routines — all live here | Rarely directly. View through VS Code | Mac filesystem |

**The 80/20 rule:** 80% of your day-to-day happens in **ClickUp on your phone**. 20% happens in **VS Code** when you want to dig in or fix something. The rest runs invisibly.

---

## Part 3 — Each Tool in Detail

### 3.1 Claude Desktop App (Cowork)

**What it is:** The Mac app where we have these chat conversations. It also hosts the agent's automatic schedule and the ClickUp integration.

**What runs here:**
- 5 scheduled trading routines (Mon-Fri)
- 1 polling routine (every 15 min during market hours)
- All ClickUp posts to your phone

**When to open it:**
- To pause a routine for a day
- To trigger a "Run now" on a specific routine
- To see the last-run timestamp and verify schedules are firing
- To have a free-form conversation about what to build/change in the project (which is what we're doing now)

**Where things are:**
- Left sidebar → **Scheduled** section: your 6 routines
- Click any routine → opens detail view → "Run now" button + last-run logs

**Critical thing to know:** Cowork routines **only run while your Mac is on and the app is running** (or in the background). If you close your Mac for the weekend, no routines fire. The PDF you read uses Claude Cloud Routines which run even when your Mac is off — that's a future upgrade.

---

### 3.2 VS Code + Claude Code

**What it is:** Your code editor with an AI agent built in. The Claude Code extension talks to Claude (the same AI) but interactively.

**What you do here:**
- Have one-off conversations with the agent ("analyze NVDA right now")
- Edit memory files manually (e.g., approve a setup by editing `memory/open_positions.md`)
- Run the project's Python scripts (`python3 scripts/research.py scan`)
- Check the project structure
- Trigger any routine on demand (Cmd+Shift+P → "Run Task")

**When to use it:**
- You want to dig into the agent's reasoning at a deeper level
- A scheduled routine failed and you want to debug
- You want to ask "what would you do if I bought NVDA at $208?" (simulation)
- You're editing strategy or learnings files directly
- You're testing a new idea before letting the schedule run with it

**Tasks shortcut:** Cmd+Shift+P → "Tasks: Run Task" → pick from the 12 trading tasks (see RUN_ROUTINES.md).

---

### 3.3 RuFlo (advanced)

**What it is:** A Claude Code workflow plugin you installed. Adds power features like vector memory, multi-agent swarms, architecture decision records, and remote phone control.

**Skip this section if you're new** — the basics work without it. Come back when you want to enhance:
- **Vector memory**: agent retrieves "similar past setups" before deciding
- **Swarm**: parallel sub-agents for fundamentals/technicals/news/sector research
- **ADR**: long-term log of strategy changes (why we changed each rule)
- **/remote-control**: control the trading session from your phone via voice/text
- **CVE scanning**: security audit the Python code

We have a build plan for integrating it — just say "approved" and we'll wire steps 1-3 in.

---

### 3.4 ClickUp

**Your phone-based command center.** Detailed walkthrough in **CLICKUP_GUIDE.md**.

**The 5 things you'll do most:**
1. **Approve a trade**: Pending Setups → tap setup → change status to "in progress"
2. **Read a brief**: Daily Briefs → tap today's task → read the markdown
3. **Talk to the agent**: 💬 Agent Chat task → add a comment → wait ~15 min for reply
4. **Train the agent**: Knowledge Inbox → new task with link or PDF → wait for summary
5. **Pause everything**: Pause Toggle → "Trading Active" task → status "in progress" or "complete"

---

### 3.5 Alpaca Markets

**What it is:** Your actual paper-trading brokerage. The agent places orders here.

**What you do here:**
- Verify the agent's trades actually happened
- See real-time P&L on positions
- See your $100k paper balance
- Check pending orders (especially trailing stops)

**Mobile app**: download "Alpaca: Investing & Trading" from App Store. Log in. Switch to **Paper Trading** mode (top-right toggle). You'll see exactly what the agent sees.

**Why you need both Alpaca and ClickUp**: ClickUp has the agent's *reasoning* (why it bought, what's the catalyst). Alpaca has the *truth* (did the order actually fill, what's the current price). Both are required for a full picture.

---

## Part 4 — Day-to-Day Flow

### Trading day (Monday-Friday)

#### **Morning — 8:00 AM CEST (before market opens)**
- Open phone. ClickUp app should have a notification: today's Pre-Market Brief.
- Read the brief (3-5 minute read).
- Open Pending Setups list. Review any new setups.
- For each setup you like: tap → change status `to do` → `in progress`. That's an APPROVAL.
- If you want to think more: leave it. You can approve later up until ~3:30 PM CEST when market-open executes.
- **Optional**: open Alpaca app to verify $100k starting balance, no surprise positions.

#### **Late morning — 3:30 PM CEST (market just opened)**
- Market-open execution routine fires at 3:35 PM CEST.
- Approved setups become real orders.
- New ClickUp task posted: "Market Open Execution — YYYY-MM-DD".
- Open Alpaca app, verify orders filled at expected prices.

#### **Midday — 6:30 PM CEST (mid-trading-day)**
- Midday Scan fires at 6:34 PM CEST.
- Reads positions, manages stops, may flag new setups.
- Review the new "Midday Scan" brief. If new setups, approve same way.

#### **End of trading day — 9:51 PM CEST**
- EOD Review fires.
- Reads "End-of-Day Review" brief — daily P&L, trades, lessons.
- Check the **Performance Dashboard** task — week-to-date metrics updated.
- Agent may post a reflective question on Agent Chat. Reply with your thinking — that's how it learns.

#### **Friday evening — 10:33 PM CEST**
- Weekly Review fires.
- Most important brief of the week. Strategy adjustments happen here.

### Off-day (Saturday-Sunday)
- Nothing fires automatically.
- Optional: open VS Code, scroll through this week's journal entries (`journal/*.md`), reflect on whether the agent's reasoning aligned with what actually played out.
- Drop strategy articles you read this week into the Knowledge Inbox — they'll process Monday morning.

---

## Part 5 — Common Tasks (Step-by-Step)

### "How do I approve a trade?"
1. ClickUp app → Pending Setups list.
2. Tap the setup task (named like "NVDA LONG — entry $208, stop $202.50, target $220").
3. Read the description (catalyst, R:R, score, what would invalidate).
4. Top of screen → status dropdown → change `to do` → `in progress`.
5. That's it. The next market-open routine will execute it.

### "How do I deny a trade?"
1. ClickUp → Pending Setups → tap the task.
2. Either:
   - Status `complete` + comment "deny: too overbought" — explicit deny
   - Or just leave `to do` and the setup expires when market closes — implicit deny
3. Explicit deny with a reason is BETTER for training the agent.

### "How do I see my portfolio right now?"
- **Phone:** Alpaca app → Paper Trading mode → Home tab. Shows balance + positions.
- **VS Code:** Cmd+Shift+P → "Tasks: Run Task" → "Trading: Show Open Positions"
- **Quick check on ClickUp:** Daily Briefs → most recent brief → read "Account state" section
- **Right now (instant):** ask Claude Code directly: *"Show me my current Alpaca positions and P&L."*

### "How do I add a stock to the watchlist?"
- ClickUp → Controls → Watchlist → "+ New task". Title = ticker. Description = strategy + notes.
- The polling routine syncs `memory/watchlist.json` automatically.

### "How do I remove a stock?"
- Open the ticker's task → close as `complete`. Polling will remove it from the JSON.

### "How do I train the agent on a new strategy I read about?"
1. Find the article URL or download the PDF.
2. ClickUp → Agent Training → Knowledge Inbox → "+ New task".
3. Title: 5 words ("VWAP reclaim breakout strategy").
4. Description: paste link OR attach PDF.
5. Save with status `to do`.
6. Within 15 minutes (during market hours) the polling routine reads it, summarizes, integrates rules into `memory/learnings.md`, and posts a comment back.

### "How do I tell the agent 'don't be so cautious about TSLA'?"
- ClickUp → Agent Training → Feedback Log → "+ New task" → write that as the title → save.
- Or: open Agent Chat task → add a comment → save.
- Either works. The polling routine integrates feedback into `memory/learnings.md`.

### "How do I pause everything for a day?"
- ClickUp → Controls → Pause Toggle → "Trading Active" task → status `in progress`. No new trades fire; existing stops still work.
- To resume: change status back to `to do`.
- For full halt: status `complete`. No trading actions of any kind.

### "How do I manually trigger a routine right now?"
- **From ClickUp:** Run Routines list → the routine's task → status `in progress`. Polling will catch it within 15 min.
- **From VS Code:** Cmd+Shift+P → "Tasks: Run Task" → "Routine 1 (Pre-Market): Copy Prompt to Clipboard" → paste into Claude Code and Enter.
- **From the desktop app:** Scheduled sidebar → click the routine → "Run now".

### "How do I see what the agent is 'thinking'?"
- **Recent reasoning:** journal entries in `journal/YYYY-MM-DD.md`. Open in VS Code.
- **Live**: Claude Code in VS Code — ask *"Walk me through your reasoning on the NVDA setup."*
- **Long-term patterns:** `memory/learnings.md`.

### "Something broke / agent stopped responding"
1. Check **ClickUp → Alerts → Risk and Errors** — agent posts breakage there.
2. Check the desktop app's Scheduled sidebar — any routines disabled or failing?
3. Open VS Code → Cmd+Shift+P → Tasks: "Trading: Test Alpaca Connection". If this fails, the .env keys may have rotated.
4. Open VS Code → Cmd+Shift+P → "Tasks: Run Task" → "Trading: Show Pending ClickUp Updates" — fallback log if ClickUp posts failed.

---

## Part 6 — Important Things to Know

### About paper trading
- This is **not real money**. You have $100k of fake money to learn with.
- The market data IS real (delayed by 15 min on free Alpaca tier).
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
- More feedback = better-tuned agent. Drop a strategy article every week. Comment on every approve/deny. Reply to reflective questions.

### About the polling routine
- It's the bridge between ClickUp and the agent's local file system.
- Runs every 15 min during market hours (14:00-23:59 CEST Mon-Fri).
- If you change a status outside market hours, it'll be picked up by the next scheduled routine.
- It logs every action it takes; check `memory/last_poll.json` for state.

### About .env and API keys
- `.env` file is in your project folder, gitignored. It has your Alpaca + Anthropic + ClickUp keys.
- Never paste this into a chat or commit it to git.
- If keys ever leak, rotate them immediately at the providers' sites.

---

## Part 7 — Where to Look When You're Confused

| Question | Read |
|----------|------|
| What does each ClickUp list do? | `CLICKUP_GUIDE.md` |
| How do I run any routine manually? | `RUN_ROUTINES.md` |
| What rules does the agent follow? | `CLAUDE.md` |
| What's the agent's current strategy? | `memory/strategy.md` |
| What did the agent do today? | `journal/YYYY-MM-DD.md` (the most recent dated file) |
| What lessons has the agent learned? | `memory/learnings.md` |
| What setups are pending approval? | `memory/open_positions.md` |
| Did the agent fail to post to ClickUp? | `memory/pending_clickup_updates.md` |
| Initial install/setup steps | `SETUP.md` |
| THIS FILE | `TRADING_GUIDE.md` (you are here) |

---

## Part 8 — When to Talk to Me (in this Cowork chat)

Open this Claude desktop app and chat with me when you want to:
- Add a new feature ("can the agent also analyze options?" — I'd push back: no options per the rules)
- Change a strategy rule ("I want to allow 4 trades/week instead of 3")
- Implement RuFlo features (vector memory, swarm, ADRs)
- Migrate to true cloud routines (Claude Code Cloud Routines instead of Cowork) so it runs even with your Mac off
- Troubleshoot a deeper issue
- Build a phone PWA dashboard (alternative to ClickUp)

Use **Claude Code in VS Code** for everything else — running scripts, asking questions about specific tickers, editing files. Cowork is for big-picture changes; Claude Code is for daily operations.

---

## Quick Cheat Sheet (print this)

```
APPROVE TRADE  →  ClickUp app → Pending Setups → status `in progress`
DENY TRADE    →  same, close as `complete`
PAUSE AGENT   →  Controls → Pause Toggle → `in progress` or `complete`
TRAIN AGENT   →  Knowledge Inbox (deep) or Agent Chat (quick)
SEE BRIEFS    →  Daily Briefs list
SEE ALERTS    →  Risk and Errors list
SEE BALANCE   →  Alpaca app, Paper Trading mode
ASK A QUESTION →  Agent Chat task in ClickUp, OR Claude Code in VS Code
EMERGENCY STOP →  Pause Toggle → `complete` (full halt)
```

That's everything. Welcome aboard.
