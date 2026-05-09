# Running the Trading Agent — Cheat Sheet

Pin this file as a tab in VS Code so it's always one click away.

---

## Two ways routines run

| Mode | Where | When | What it does |
|------|-------|------|--------------|
| **Automatic** | Claude desktop app (Cowork mode) | Mon-Fri on schedule | All 5 routines fire at the right time, post to ClickUp |
| **Manual** | VS Code → Claude Code | Anytime you trigger it | You run any routine on demand |

The two modes are not in conflict — they read/write the same `memory/` and `journal/` files, so manual runs and scheduled runs stay in sync.

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
- `Trading: Analyze Symbol` — pops a prompt for a ticker, runs full analysis on it

**Run a full routine via Claude Code (copies prompt to clipboard, you paste it in):**
- `Routine 1 (Pre-Market): Copy Prompt to Clipboard`
- `Routine 2 (Market Open): Copy Prompt to Clipboard`
- `Routine 3 (Midday): Copy Prompt to Clipboard`
- `Routine 4 (End-of-Day): Copy Prompt to Clipboard`
- `Routine 5 (Weekly Review): Copy Prompt to Clipboard`

**How the routine tasks work:** clicking one copies a one-line prompt onto your clipboard. Then click into Claude Code (the chat box at the bottom of VS Code) and press **Cmd+V** + Enter.

**Other useful:**
- `Trading: Show Pending ClickUp Updates` — if a routine couldn't reach ClickUp, the summary lands in `memory/pending_clickup_updates.md`. This task prints it.

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

## Approving a trade

The agent never trades without your OK. When a routine flags a setup, it lands in two places:
1. **A ClickUp task** marked `AWAITING APPROVAL`
2. **`memory/open_positions.md`** under "Pending Setups"

To approve, do **either** of:
- Reply "approve" in the ClickUp task's comments
- Open `memory/open_positions.md` in VS Code and add a line `Approved: YES` under the setup

The next market-open execution run will see that flag and trade it.

---

## What runs automatically (no action needed)

These are already scheduled in the Claude desktop app:

| Routine | Time (CEST) | Time (ET) |
|---------|-------------|-----------|
| Pre-Market Research | 2:08 PM | 8:08 AM |
| Market Open Execution | 3:44 PM | 9:44 AM |
| Midday Scan | 6:34 PM | 12:34 PM |
| End-of-Day Review | 9:51 PM | 3:51 PM |
| Friday Weekly Review | 10:33 PM Fri | 4:33 PM ET Fri |

Times have a few minutes of jitter built in to balance load. To pause, edit, or trigger them, open the Claude desktop app → **Scheduled** sidebar.

---

## Where to look for results

- **Live notifications** → ClickUp app (your "Trading Agent" list)
- **Account & positions** → Alpaca Paper Trading dashboard or app
- **Decisions & reasoning** → `journal/YYYY-MM-DD.md` (today's journal)
- **Open positions** → `memory/open_positions.md`
- **Lessons over time** → `memory/learnings.md`
- **Trade history** → `memory/trade_log.json`
