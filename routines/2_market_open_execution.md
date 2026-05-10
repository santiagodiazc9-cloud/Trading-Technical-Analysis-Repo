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
- After the order is confirmed `filled`, push the fill confirmation to Discord `#fills`:
  - `python3 scripts/notify.py fill <SYMBOL> buy <QTY> <FILL_PRICE> <ORDER_ID>`
- Then place the post-entry trailing stop per CLAUDE.md "Post-Entry Order" rules. If the trailing stop AND fixed-stop fallbacks are BOTH rejected (queued to tomorrow), raise a high-severity Discord alert:
  - `python3 scripts/notify.py alert high <SYMBOL> 'Stop placement rejected — position queued in memory/open_positions.md as STOP_QUEUED. Manual stop required if market moves against position.'`
- After placing, update the ClickUp pending-setup task: post a comment with execution details, then move the task to `lists.trade_log` using `clickup_move_task`.

### 5. Update Memory
- **`memory/open_positions.md`**: Record new positions with entry price, stop-loss, target
- **`memory/trade_log.json`**: Add trade entry records
- **`journal/YYYY-MM-DD.md`**: Log trades executed and reasoning

### 6. Risk Check
- Count total open positions (max 5)
- Verify no single position exceeds limits
- If daily loss cap is hit, note "NO MORE TRADES TODAY" in open_positions.md AND raise a high-severity Discord alert:
  - `python3 scripts/notify.py alert high portfolio 'Daily loss cap (-2%) hit — no new entries allowed for the rest of today.'`
- If PDT count is at 3/3 and a same-day buy was attempted, raise a medium alert:
  - `python3 scripts/notify.py alert medium portfolio 'PDT day-trade count maxed (3/5 rolling). Same-day entries blocked.'`

### 7. Post Update to ClickUp
Read `memory/clickup_config.json`. Post a brief to `lists.daily_briefs`:
- **name**: `Market Open Execution — YYYY-MM-DD`
- **markdown_description**: trades executed (symbol, qty, entry, stop, target, reasoning), setups skipped and why, current positions and exposure, account state
- **priority**: `high` if any trades placed, else `normal`

For each executed trade, also create a task in `lists.trade_log` with status `to do` (= open trade). When closed later, midday/EOD routines will mark it complete with win/loss tag.

If ClickUp tools unavailable, append to `memory/pending_clickup_updates.md`.

### 8. Post Summary to Discord `#daily-brief`
At the end of the routine, run:

```bash
python3 scripts/notify.py brief 'Market Open Execution — YYYY-MM-DD' '<summary: # trades placed, # setups skipped (and why), open-position count, account state>'
```

This is silent (no @mention) — for at-a-glance review. Per-fill notifications already went to `#fills` in step 4; per-alert notifications already went to `#risk-alerts` in step 6. If `notify.py` fails, log to `memory/pending_clickup_updates.md` and continue.

### 9. Refresh the Dashboard

```bash
python3 scripts/dashboard.py
python3 scripts/notify.py dashboard
```
