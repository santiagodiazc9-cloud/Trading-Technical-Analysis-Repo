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

### 3a. Stale-approval price check (HARD GATE — runs before Approved-YES read)
For each pending setup with `Approved: YES`, verify it hasn't been invalidated by price action since approval. This is the safety net for the case where approval was granted days ago but the entry zone has since been overshot or the stop has been blown.

```bash
python3 scripts/setup_validator.py check <SETUP_ID>
```

Parse the JSON result:
- `valid: true` → proceed to step 4 for this setup.
- `valid: false` → **DO NOT execute**. Post `python3 scripts/notify.py alert high <SYMBOL> 'market-open SKIPPED: stale approval (<reason>, current_price=<n>). Removing Approved flag — setup will be archived by next pre-market sweep.'` and edit `memory/open_positions.md` to remove the `Approved: YES` line under that setup (the next pre-market `archive-invalid` will move it to Expired). Log "skipped: stale approval" and continue to the next setup.
- `valid: true, reason: PRICE_UNAVAILABLE` → permissive: continue to step 4 but log a note that the price check was inconclusive (Alpaca quote fetch failed).

### 4. Check for Approval Before Executing
For each pending setup:
- Read the master pause toggle from `memory/pause_state.json`. If `state` is `paused` or `halted`, do NOT place new trades — log "skipped: paused" and continue. Closes still allowed.
- Check `memory/open_positions.md` for the `Approved: YES` flag under the setup's heading (set by Discord button, `/approve` slash, or direct file edit).
- If the setup has `Denied: YES` or no flag, log "skipped: awaiting approval" / "skipped: denied" and continue.
- Approved setups only: ATR-size, cap at $1,000 or 5% of portfolio, then place order:
  - `python3 scripts/alpaca_client.py buy <SYMBOL> <QTY> market`
  - Verify: `python3 scripts/alpaca_client.py orders`
- After the order is confirmed `filled`, push the fill confirmation to Discord `#fills`:
  - `python3 scripts/notify.py fill <SYMBOL> buy <QTY> <FILL_PRICE> <ORDER_ID>`
- Then place the post-entry trailing stop per CLAUDE.md "Post-Entry Order" rules. If the trailing stop AND fixed-stop fallbacks are BOTH rejected (queued to tomorrow), raise a high-severity Discord alert:
  - `python3 scripts/notify.py alert high <SYMBOL> 'Stop placement rejected — position queued in memory/open_positions.md as STOP_QUEUED. Manual stop required if market moves against position.'`
- Update `memory/open_positions.md` with the executed setup's status (move from "Pending Setups" to "Current Positions" with entry/stop/target). Append the trade record to `memory/trade_log.json`.

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

### 7. Post Summary to Discord `#daily-brief`
At the end of the routine, run:

```bash
python3 scripts/notify.py brief 'Market Open Execution — YYYY-MM-DD' '<summary: # trades placed, # setups skipped (and why), open-position count, account state>'
```

This is silent (no @mention) — for at-a-glance review. Per-fill notifications already went to `#fills` in step 4; per-alert notifications already went to `#risk-alerts` in step 6. If `notify.py` fails, log to `memory/pending_discord_updates.md` and continue.

### 8. Refresh the Dashboard

```bash
python3 scripts/dashboard.py
python3 scripts/notify.py dashboard
```
