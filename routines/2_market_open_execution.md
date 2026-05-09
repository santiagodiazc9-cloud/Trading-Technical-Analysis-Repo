# Routine: Market Open Execution
**Schedule**: Monday–Friday, 9:35 AM ET (5 minutes after open for initial volatility to settle)

## Instructions

You are running the market-open execution routine. Follow these steps exactly:

### 1. Load Memory
Read these files:
- `memory/open_positions.md` — check for pending setups from pre-market research
- `memory/strategy.md` — review rules
- `memory/market_context.md` — today's context

### 2. Check Current State
Run: `python3 scripts/alpaca_client.py account`
Run: `python3 scripts/alpaca_client.py positions`
Run: `python3 scripts/alpaca_client.py clock`
- Verify market is open
- Note current equity and open positions

### 3. Validate Pre-Market Setups
For each pending setup identified in pre-market research:
Run: `python3 scripts/research.py analyze <SYMBOL>`
- Are the signals still valid? Has the stock gapped in a way that changes the thesis?
- Is the entry zone still reachable?
- Re-run the 6-point checklist with current data

### 4. Check for Approval Before Executing
For each pending setup:
- Read the corresponding task in ClickUp `lists.pending_setups`. Use `clickup_get_task`.
- A setup is **approved** if the task's status is `in progress` or `complete`.
- A setup is **denied** if the task is closed/archived OR has a comment containing `deny` from the user.
- A setup is **awaiting** if status is still `to do`.
- ALSO check `memory/open_positions.md` for `Approved: YES` flag (legacy fallback).
- ALSO check that the master pause toggle (`control_tasks.trading_active_toggle`) status is `to do` — if it's anything else, do not place new trades.
- If not approved, log "skipped: awaiting approval" and continue.
- Approved setups only: ATR-size, cap at $1,000 or 5% of portfolio, then place order:
  - `python3 scripts/alpaca_client.py buy <SYMBOL> <QTY> market`
  - Verify: `python3 scripts/alpaca_client.py orders`
- After placing, update the ClickUp pending-setup task: post a comment with execution details, then move the task to `lists.trade_log` using `clickup_move_task`.

### 5. Update Memory
- **`memory/open_positions.md`**: Record new positions with entry price, stop-loss, target
- **`memory/trade_log.json`**: Add trade entry records
- **`journal/YYYY-MM-DD.md`**: Log trades executed and reasoning

### 6. Risk Check
- Count total open positions (max 5)
- Verify no single position exceeds limits
- If daily loss cap is hit, note "NO MORE TRADES TODAY" in open_positions.md

### 7. Post Update to ClickUp
Read `memory/clickup_config.json`. Post a brief to `lists.daily_briefs`:
- **name**: `Market Open Execution — YYYY-MM-DD`
- **markdown_description**: trades executed (symbol, qty, entry, stop, target, reasoning), setups skipped and why, current positions and exposure, account state
- **priority**: `high` if any trades placed, else `normal`

For each executed trade, also create a task in `lists.trade_log` with status `to do` (= open trade). When closed later, midday/EOD routines will mark it complete with win/loss tag.

If ClickUp tools unavailable, append to `memory/pending_clickup_updates.md`.
