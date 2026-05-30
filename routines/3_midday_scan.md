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

### 4. Catalyst Check on Open Positions + Internet-Flagged Follow-Up
**For each open position symbol**, run a targeted web search:
```
brave_search: "[SYMBOL] news today catalyst"
```
Note anything that breaks the original setup thesis. If a bearish catalyst emerged (guidance cut, sector downgrade, macro shock), recommend closure in the next step — don't close without user approval unless it's a -7% cut situation.

**Check internet-flagged symbols from morning pre-market**: read `memory/market_context.md` → "## Internet Flagged" section. For any flagged symbol not already in an open position, run:
```bash
python3 scripts/research.py analyze [SYMBOL]
```
If the TA now shows a clean setup (ADX > 25, MACD confirming, RSI in range), propose it as a pending midday setup. Confidence ≥ 7 required for midday proposals (higher bar than pre-market since the day is already underway).

Do not re-run `research.py scan` against the full watchlist — the watchlist is posture-proxies-only (7 ETFs). New setups come from internet-flagged symbols and position management.

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
