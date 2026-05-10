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
  - Push the close to Discord: `python3 scripts/notify.py fill <SYMBOL> sell <QTY> <FILL_PRICE> <ORDER_ID>`
- **Hit take-profit target?** → Closing at target is automatic. Close it. Same `notify.py fill ...` call.
- **-7% manual cut rule** (CLAUDE.md hard rule): if any position is at unrealized P&L ≤ -7% and not yet stopped out, close it now AND raise a high-severity alert BEFORE closing so the user sees it on phone:
  - `python3 scripts/notify.py alert high <SYMBOL> 'Position at <P&L>% — manual cut rule triggered. Closing now.'`
  - `python3 scripts/alpaca_client.py close <SYMBOL>`
  - `python3 scripts/notify.py fill <SYMBOL> sell <QTY> <FILL_PRICE> <ORDER_ID>`
- **Trending well?** → Consider trailing the stop using ATR. Update `memory/open_positions.md`.
- **Thesis broken (no longer matches the setup)?** → Recommend closure in the `#daily-brief` summary; **do NOT close on thesis change without user approval**.

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

### 6. Push New Setups to Discord
For every new setup proposed in this routine, push to Discord `#approvals` with a unique ID (e.g. `<SYMBOL>-YYYY-MM-DD-midday`):

```bash
python3 scripts/notify.py setup <SETUP_ID> <SYMBOL> <LONG|SHORT> '<entry-zone>' '<stop>' '<target>' '<size>' '<rr>' <confidence-1-10> '<one-line catalyst>'
```

Use the same ID in the `memory/open_positions.md` heading so the bot can match button clicks.

For each position closed, the fill notification in step 3 already documents the exit. The `memory/trade_log.json` update is the durable record.

### 7. Post Summary to Discord `#daily-brief`
At the end of the routine, run:

```bash
python3 scripts/notify.py brief 'Midday Scan — YYYY-MM-DD' '<summary: per-position P&L, management actions taken, # new setups flagged>'
```

Silent (no @mention). Per-fill and per-alert notifications already went to their channels in step 3. If `notify.py` fails, log to `memory/pending_discord_updates.md` and continue.

### 8. Refresh the Dashboard

```bash
python3 scripts/dashboard.py
python3 scripts/notify.py dashboard
```
