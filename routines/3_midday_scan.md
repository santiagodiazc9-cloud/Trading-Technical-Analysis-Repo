# Routine: Midday Scan
**Schedule**: Monday–Friday, 12:30 PM ET

## Instructions

You are running the midday scan routine. Follow these steps exactly:

### 1. Load Memory
Read:
- `memory/open_positions.md`
- `memory/strategy.md`
- `memory/market_context.md`

### 2. Check Positions
Run: `python3 scripts/alpaca_client.py account`
Run: `python3 scripts/alpaca_client.py positions`
- How is each position performing?
- Has any position hit its stop-loss or target?

### 3. Manage Existing Positions
For each open position:
Run: `python3 scripts/research.py analyze <SYMBOL>`
- **Hit stop-loss?** → Closing a stopped-out position is automatic (risk rule). Close it: `python3 scripts/alpaca_client.py close <SYMBOL>`
- **Hit take-profit target?** → Closing at target is automatic. Close it.
- **Trending well?** → Consider trailing the stop using ATR. Update `memory/open_positions.md`.
- **Thesis broken (no longer matches the setup)?** → Recommend closure in the ClickUp update; **do NOT close on thesis change without user approval**.

### 4. Scan for New Opportunities
Run: `python3 scripts/research.py scan`
- Any new setups emerging that weren't there at open?
- Note them in `memory/open_positions.md` under "Pending Setups" — **do not enter without user approval**.
- Only flag for approval if high-conviction (score 4+ on the checklist).
- Remember: max 5 positions, and respect the daily loss cap.

### 5. Update Memory
- **`memory/open_positions.md`**: Update P&L, adjust stops, note any closes
- **`memory/trade_log.json`**: Log any closed trades with outcome
- **`journal/YYYY-MM-DD.md`**: Add midday observations
- **`memory/market_context.md`**: Update if market conditions have shifted

### 6. Post Update to ClickUp
Read `memory/clickup_config.json`.

**A. Brief** — task in `lists.daily_briefs`:
- **name**: `Midday Scan — YYYY-MM-DD`
- **markdown_description**: position-by-position P&L, management actions, new setups flagged
- **priority**: `high` if anything closed or new setup, else `normal`

**B. New setups** — `clickup_create_task` in `lists.pending_setups` (one per setup), same format as pre-market.

**C. Position updates** — for each position closed, find its task in `lists.trade_log` and add a comment with exit reason and P&L. If you have the task_id from the trade log entry, mark complete and tag `win` or `loss`.

If ClickUp tools unavailable, append to `memory/pending_clickup_updates.md`.
