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
- For each close, push to Discord `#fills`:
  - `python3 scripts/notify.py fill <SYMBOL> sell <QTY> <FILL_PRICE> <ORDER_ID>`
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

**Stale-state sweep** — catch silent memory drift (the failure mode where these files freeze for weeks because nothing "noteworthy" happens):
- Check `memory/learnings.md` mtime. If untouched ≥5 trading days, append a one-line entry under "Pattern Notes" summarizing today's market posture (e.g. "2026-05-22: broad market overbought, no setups proposed for 4th day running — patience working as designed"). This keeps the file alive so the weekly review has something to reflect on.
- Check `memory/strategy.md` mtime. If untouched ≥10 trading days, append a one-line `> NOTE:` comment at the top flagging it for the next Friday weekly review — e.g. `> NOTE: strategy.md untouched since 2026-05-08 — Friday review should confirm rules are still right for current regime.` Do NOT change strategy rules here — that's the weekly review's job.

### 7. Prepare for Tomorrow
Update `memory/open_positions.md` with:
- Current swing positions and their status
- Any symbols to watch closely tomorrow
- Notes for tomorrow's pre-market research

### 8. Update the Performance Snapshot
Append today's metrics to `memory/trade_log.json` under `daily_snapshots`:
- date, equity, cash, P&L $/%, trades closed today, wins, losses
- running win rate, running P&L
- confidence-bucket calibration (predicted vs actual outcomes)

The dashboard step below regenerates `Dashboard.md`, which surfaces these stats automatically. No separate dashboard task to update.

### 9. Reflective Question (optional)
If a decision this week stood out (a denied setup that mooned, a series of stop-outs in one sector, etc.), post a single reflective question to Discord `#chat` so Santiago can reply at his own pace:

```bash
python3 scripts/notify.py send chat 'Reflection — YYYY-MM-DD' 'You denied AMD on Tuesday — was that the right call given how it played out?'
```

Skip if nothing notable. Santiago's reply will be picked up by the dispatcher routine and folded into `memory/learnings.md`.

### 10. Post Summary to Discord `#daily-brief`
At the end of the routine, run:

```bash
python3 scripts/notify.py brief 'End-of-Day Review — YYYY-MM-DD' '<summary: daily P&L $/%, # closes, # wins / # losses, swing positions held overnight, top observation>'
```

Silent (no @mention). If the daily loss cap was hit OR a hard rule was violated, ALSO raise a high-severity alert:

```bash
python3 scripts/notify.py alert high portfolio '<one-line description: e.g. "Daily loss cap -2.4% — review tomorrow before any new entries">'
```

If `notify.py` fails, log to `memory/pending_discord_updates.md` and continue.

### 11. Refresh the Dashboard

```bash
python3 scripts/dashboard.py
python3 scripts/notify.py dashboard
```
