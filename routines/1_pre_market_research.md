# Routine: Pre-Market Research
**Schedule**: Monday–Friday, 8:00 AM ET

## Instructions

You are running the pre-market research routine. Follow these steps exactly:

### 1. Load Memory
Read these files to understand your current state:
- `memory/watchlist.json` — symbols to scan
- `memory/strategy.md` — current trading rules
- `memory/open_positions.md` — any existing positions
- `memory/market_context.md` — yesterday's market context
- `memory/learnings.md` — lessons from past trades

### 2. Check Account
Run: `python scripts/alpaca_client.py account`
- Note available cash and buying power
- Check if the daily loss cap has been hit (2% of portfolio)

### 3. Scan Watchlist
Run: `python scripts/research.py scan`
- Review all indicator readings for every watchlist symbol
- Identify which symbols have active signals (crossovers, oversold/overbought, etc.)

### 4. Deep-Dive Top Candidates
For the top 3 most interesting symbols from the scan:
Run: `python scripts/research.py analyze <SYMBOL>`
- Evaluate trend alignment, momentum, and volatility
- Run through the 6-point decision checklist from CLAUDE.md

### 5. Update Memory Files
- **`memory/market_context.md`**: Update with today's pre-market observations, key levels, sentiment
- **`memory/open_positions.md`**: Update with current position status and any adjustment plans
- Write a brief note to `journal/YYYY-MM-DD.md` with pre-market observations

### 6. Prepare Trade Plan
If you identify setups worth executing at market open:
- Note the symbol, direction, entry zone, stop-loss, and target in `memory/open_positions.md` under "Pending Setups"
- Make sure each setup passes at least 4 of 6 checklist items

**DO NOT place any trades in this routine.** This is research only.

### 7. Post Update to ClickUp
Read `memory/clickup_config.json`. Use these lists from it:
- `lists.daily_briefs` for the brief
- `lists.pending_setups` — one new task per proposed setup
- `lists.risk_and_errors` if anything urgent

**A. Daily Brief** — `clickup_create_task` in `lists.daily_briefs`:
- **name**: `Pre-Market Brief — YYYY-MM-DD`
- **markdown_description**: account snapshot, top 3 candidates with checklist scores, market context, links to today's journal
- **priority**: `normal`

**B. One task per pending setup** — `clickup_create_task` in `lists.pending_setups`:
- **name**: `[TICKER] [LONG/SHORT] — entry $X, stop $Y, target $Z`
- **markdown_description**: full analysis, R:R, position size, confidence (1-10), what would invalidate the setup
- **priority**: `high`
- The user approves by changing the task status from `to do` to `in progress` (or `complete`). The market-open routine and polling routine watch for this.

Also write each setup to `memory/open_positions.md` under "Pending Setups" — include the ClickUp task ID for cross-reference.

If ClickUp MCP tools are unavailable, append summary to `memory/pending_clickup_updates.md`.

**DO NOT place any trades in this routine.** This is research only — the user must reply to the ClickUp task to approve setups before market-open execution acts on them.
