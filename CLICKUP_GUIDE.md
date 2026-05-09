# ClickUp Space Guide — How to Use the Trading Agent in ClickUp

This file explains the ClickUp Space we built for managing the trading agent: what each list is for, what to do, what NOT to do.

Open the Space: https://app.clickup.com/90121712391/v/li/901217849070

---

## Quick Reference — Where to do what

| I want to... | Where to go |
|--------------|-------------|
| **Approve a trade** | Daily Operations → Pending Setups → change status to `in progress` |
| **Deny a trade** | Daily Operations → Pending Setups → close the task (status `complete` with deny comment) |
| **See what the agent did today** | Daily Operations → Daily Briefs → today's tasks |
| **Train the agent with a strategy doc** | Agent Training → Knowledge Inbox → new task with link/PDF |
| **Give the agent feedback** | Agent Training → Feedback Log → new task with note |
| **Talk to the agent (chat)** | Agent Training → Feedback Log → "💬 Agent Chat" task → comment |
| **Run a routine right now** | Controls → Run Routines → change status to `in progress` |
| **Add/remove watchlist symbol** | Controls → Watchlist → add or close task |
| **Pause the agent (no new trades)** | Controls → Pause Toggle → "Trading Active" task status `in progress` |
| **Stop the agent fully** | Controls → Pause Toggle → "Trading Active" task status `complete` |
| **See performance** | Daily Operations → Daily Briefs → "Performance Dashboard" (overwritten daily) |
| **See urgent alerts** | Alerts → Risk and Errors |

---

## ONE-TIME SETUP: Custom Statuses (5-minute task)

ClickUp's API doesn't let me create custom status names. The default statuses (`to do`, `in progress`, `complete`) work fine for the polling logic, but you can rename them in the UI for clarity. **Optional — skip this if you're fine with default names.**

For each list below, here's what each default status maps to in our workflow:

### Pending Setups list
- `to do` → Awaiting your approval
- `in progress` → Approved (will execute next market-open routine)
- `complete` → Executed (already filled and moved to Trade Log)

To rename:
1. Open the Pending Setups list.
2. Click the gear icon → "Statuses".
3. Optionally rename each status to: "Awaiting Approval" / "Approved" / "Executed".
4. The polling routine still reads by status order, so renaming is purely cosmetic.

### Run Routines list
- `to do` → Idle
- `in progress` → Run NOW (polling routine will execute and reset back to `to do`)
- `complete` → (don't use)

### Trade Log list
- `to do` → Open trade
- `in progress` → (don't use)
- `complete` → Closed trade (add tag `win` or `loss`)

### Knowledge Inbox list
- `to do` → New, not yet read by agent
- `in progress` → Agent is currently reading
- `complete` → Read and integrated into memory

### Pause Toggle (single "Trading Active" task)
- `to do` → ✅ Trading active
- `in progress` → ⏸️ Paused (no new trades; existing stops still work)
- `complete` → 🛑 Full halt

---

## Daily Workflow (what you do each day)

### Morning (after pre-market routine fires at 14:08 CEST / 8:08 ET)
1. Open ClickUp on your phone.
2. Go to **Daily Briefs** — read today's "Pre-Market Brief" task.
3. Go to **Pending Setups** — review any new setups marked AWAITING APPROVAL.
4. For each setup you want to take:
   - Read the description (catalyst, R:R, score, what would invalidate it).
   - Change task status from `to do` to `in progress` = APPROVED.
5. For each you don't want: leave `to do` (it'll auto-expire after market close) or close as `complete` with a comment "deny: [reason]".

### Midday (after midday-scan fires at 18:34 CEST / 12:34 ET)
1. Check **Daily Briefs** — read "Midday Scan" task.
2. Check **Trade Log** — see how each open trade is performing.
3. New mid-day setups, if any, will appear in **Pending Setups**. Same approve/deny flow.

### After close (after EOD-review fires at 21:51 CEST / 3:51 ET)
1. Check **Daily Briefs** — read today's "End-of-Day Review".
2. Check the **Performance Dashboard** task — week-to-date stats updated.
3. **Agent Chat**: agent may have asked you a reflective question. Reply with your thinking.

### Friday evening
- Friday Weekly Review fires at 22:33 CEST. Read it carefully — it's where strategy adjustments happen.

---

## How to Train the Agent

The agent learns three ways:

### 1. Knowledge Inbox (deepest learning)
**Use for:** structured knowledge — strategy articles, books, methodologies.

How:
1. Open **Agent Training → Knowledge Inbox**.
2. Click "+ New task".
3. Title: short description (e.g. "VWAP reclaim strategy article").
4. Description: paste the full link, or paste content directly, or attach a PDF.
5. Save with status `to do`.

The polling routine (next 15-min pass) will:
- Read your task.
- Follow the link / read the PDF.
- Summarize key takeaways.
- Append rules to `memory/learnings.md`.
- If it's a formal strategy, also update the **Strategy Library** doc.
- Post a summary comment on your task.
- Mark the task `complete`.

### 2. Feedback Log (quick adjustments)
**Use for:** short corrections or preferences — "I want 3:1 R:R minimum", "stop being so cautious about TSLA".

How:
1. Open **Agent Training → Feedback Log**.
2. New task. Title is the feedback in one sentence.
3. Save.

The polling routine integrates the note into `memory/learnings.md` and marks the task complete with a confirmation comment.

### 3. Agent Chat (conversational)
**Use for:** questions, simulations, requests, clarifications. Anything you'd say in plain language.

How:
1. Open the pinned **"💬 Agent Chat"** task in **Feedback Log**.
2. Add a comment with your question.

Examples that work well:
- *"Why did you skip TSLA today?"*
- *"What if I had bought NVDA at $208 last Monday with a $202 stop?"*
- *"Add MU and PLTR to the watchlist."*
- *"Read this article: [link]. What would you change in our strategy?"*
- *"I'm worried about the Tech sector concentration. What do you think?"*

The polling routine reads new comments, replies, and integrates strategy-relevant content into memory.

---

## Important Behaviors to Know

### How fast is "polling"?
Every 15 minutes during 14:00-23:59 CEST Mon-Fri. Outside those hours, no polling — your changes are picked up on the next scheduled routine instead.

### What if the agent doesn't respond?
- Check the polling routine in the Claude desktop app's **Scheduled** sidebar — it should show last successful run.
- If polling looks stuck, open the routine and click "Run now" once.
- If still stuck, the polling logic logs errors into the **Risk and Errors** list — check there.

### Approval is REVERSIBLE until the trade fills
If you change a setup's status to `in progress` (approved) but change your mind:
- Quickly change it back to `to do` OR close as `complete` with comment "deny".
- This works as long as the market-open routine hasn't yet fired.
- After the trade is placed, you'd need to manually close the position via Alpaca app.

### What does `pattern_day_trader: true` mean?
Your account got flagged as PDT after 4+ day trades in 5 business days while balance < $25k. After flagging, you're restricted from day trading until balance is back above $25k. The agent checks `daytrade_count` before placing same-day buy/sell trades.

### Why are some statuses unintuitive?
ClickUp default statuses are limited. The polling routine maps them to our workflow as documented above. If status meaning is confusing, follow this rule: **`to do` = waiting; `in progress` = active/approved; `complete` = done/closed.**

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Trade was approved but didn't execute | Check **Risk and Errors** — likely failed buy gate (e.g., max trades/week hit). Or pause toggle was on. |
| Agent posted nothing to ClickUp | Check `memory/pending_clickup_updates.md` — fallback file for failed posts. |
| Knowledge inbox task not getting read | Confirm status is exactly `to do` (not `in progress`). Polling reads `to do` tasks only. |
| Watchlist out of sync | Polling syncs every run. If still off, manually run the polling routine via "Run now". |
| Don't see push notifications on phone | ClickUp app → Notifications → enable "Tasks created" and "Task assigned to me" |

---

## Visual Reference (mental model)

```
ClickUp Space "Space"
│
├── 📁 Daily Operations
│   ├── 📋 Pending Setups        ← APPROVE TRADES HERE
│   ├── 📋 Trade Log             ← see executed trades
│   └── 📋 Daily Briefs          ← read what agent did
│       └── 📌 Performance Dashboard (always-current task)
│
├── 📁 Agent Training
│   ├── 📋 Knowledge Inbox       ← UPLOAD STRATEGIES HERE
│   ├── 📋 Feedback Log
│   │   └── 📌 💬 Agent Chat     ← TALK TO AGENT HERE
│   └── 📄 Strategy Library      ← agent's current rulebook (doc)
│
├── 📁 Controls
│   ├── 📋 Run Routines          ← TRIGGER ROUTINES HERE
│   ├── 📋 Watchlist             ← MANAGE TICKERS HERE
│   └── 📋 Pause Toggle          ← MASTER KILL SWITCH
│
└── 📁 Alerts
    └── 📋 Risk and Errors       ← URGENT NOTIFICATIONS
```
