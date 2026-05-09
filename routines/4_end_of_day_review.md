# Routine: End-of-Day Review
**Schedule**: Monday–Friday, 3:45 PM ET

## Instructions

You are running the end-of-day review routine. Follow these steps exactly:

### 1. Load Memory
Read:
- `memory/open_positions.md`
- `memory/strategy.md`
- `memory/trade_log.json`

### 2. Close Day Trades
Run: `python3 scripts/alpaca_client.py positions`
- Identify any positions tagged as "day_trade" in open_positions.md
- Close ALL day trade positions: `python3 scripts/alpaca_client.py close <SYMBOL>`
- Log each close in trade_log.json with P&L

### 3. Review Swing Positions
For remaining (swing) positions:
Run: `python3 scripts/research.py analyze <SYMBOL>`
- Update stop-losses if trailing
- Note if any swing position needs attention tomorrow
- Update `memory/open_positions.md` with current state

### 4. Daily Performance Review
Run: `python3 scripts/alpaca_client.py account`
- Record today's P&L
- Calculate win/loss ratio for the day
- Update the summary section of `memory/trade_log.json`

### 5. Write Daily Journal
Create/update `journal/YYYY-MM-DD.md` with the full journal entry format:
- Market conditions summary
- All trades taken today (entries and exits with reasoning)
- Open positions and their current P&L
- Key observations
- Lessons learned

### 6. Update Learnings
- Did any patterns emerge today?
- Did any rules get violated? (Note them!)
- Any strategy adjustments warranted?
- Update `memory/learnings.md` with new insights
- Update `memory/market_context.md` with end-of-day state

### 7. Prepare for Tomorrow
Update `memory/open_positions.md` with:
- Current swing positions and their status
- Any symbols to watch closely tomorrow
- Notes for tomorrow's pre-market research

### 8. Post Update to ClickUp
Read `memory/clickup_config.json`.

**A. Brief** — task in `lists.daily_briefs`:
- **name**: `End-of-Day Review — YYYY-MM-DD`
- **markdown_description**: daily P&L $/% , trades closed (entry/exit/outcome), day-trade win rate, swing positions and P&L, top 1-3 observations, notes for tomorrow
- **priority**: `high` if daily loss cap hit or rule violated, else `normal`

**B. Performance Dashboard** — UPDATE the existing task at `control_tasks.performance_dashboard` (don't create a new one). Use `clickup_update_task` to overwrite the markdown_description with current metrics:
- This Week: trades, win rate, avg win/loss, best/worst
- All-time: starting bal $100k, current equity, total P&L
- Confidence calibration: predicted vs actual outcomes by confidence bucket

**C. Trade Log updates** — for each trade closed today, find its task in `lists.trade_log` and mark complete with outcome.

**D. Daily Reflective Question** — also post a comment on the `control_tasks.agent_chat` task asking the user 1 question to reflect on (e.g. "You denied AMD on Tuesday — was that the right call given how it played out?"). Skip if no decisions were notable.

If ClickUp tools unavailable, append to `memory/pending_clickup_updates.md`.
