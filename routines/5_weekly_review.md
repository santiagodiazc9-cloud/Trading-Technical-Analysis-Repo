# Routine: Friday Weekly Review
**Schedule**: Friday only, 4:30 PM ET (after market close)

## Instructions

You are running the weekly review routine. This is your most important learning session.

### 1. Load Memory
Read ALL memory files:
- `memory/trade_log.json`
- `memory/strategy.md`
- `memory/learnings.md`
- `memory/watchlist.json`
- `memory/market_context.md`
- `memory/open_positions.md`
- All journal entries from this week (`journal/YYYY-MM-DD.md`)

### 2. Weekly Performance Analysis
Run: `python scripts/alpaca_client.py account`

Calculate and report:
- Total P&L for the week
- Number of trades taken
- Win rate (wins / total trades)
- Average win size vs average loss size
- Best trade of the week (and why it worked)
- Worst trade of the week (and why it failed)
- Risk-adjusted return (P&L relative to max drawdown)

### 3. Strategy Review
Analyze the week's trades against the strategy rules:
- Which setups produced the best results?
- Which indicator signals were most reliable?
- Were there any false signals that cost money?
- Did position sizing rules work well?
- Were there missed opportunities?

### 4. Update Strategy
Based on the analysis:
- Update `memory/strategy.md` with any refinements
- Move confirmed lessons from observations → rules
- Note in the "Adjustments Log" what changed and why

### 5. Watchlist Maintenance
- Remove symbols that have gone stale (no signals for 2+ weeks)
- Consider adding symbols that showed up in sector rotation
- Update notes on existing watchlist items
- Save changes to `memory/watchlist.json`

### 6. Update Learnings
Write a comprehensive weekly summary to `memory/learnings.md`:
- What patterns repeated this week?
- What mistakes were made? How to prevent them?
- What new rules or adjustments are needed?

### 7. Write Weekly Journal
Create `journal/YYYY-MM-DD-weekly.md` with:
- Week-in-review performance summary
- Strategy effectiveness analysis
- Key market themes
- Plan for next week
- Confidence level in current approach (1-10)

### 8. Next Week Prep
Update `memory/market_context.md` with:
- Expected events next week (earnings, economic data, FOMC, etc.)
- Key levels to watch on SPY/QQQ
- Sector rotation themes to monitor

### 9. Post Weekly Review to ClickUp
Read `memory/clickup_config.json`.

**A. Weekly Brief** — task in `lists.daily_briefs`:
- **name**: `Weekly Review — Week ending YYYY-MM-DD`
- **markdown_description**: total P&L ($/%), # trades, win rate, avg win/loss, best/worst trade, strategy effectiveness, adjustments made, confidence 1-10, plan for next week
- **priority**: `high`

**B. Performance Dashboard** — UPDATE `control_tasks.performance_dashboard` with full weekly + all-time metrics.

**C. Strategy Library** — if any strategy adjustments were made, also update the `documents.strategy_library.active_strategy_page_id` page using `clickup_update_document_page`. Append the change to the "Adjustments Log" section.

If ClickUp tools unavailable, append summary to `memory/pending_clickup_updates.md`.
