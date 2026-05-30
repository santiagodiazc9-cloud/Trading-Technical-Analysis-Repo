# Routine: Friday Weekly Review
**Schedule**: Friday only, 4:30 PM ET (after market close)

## Instructions

You are running the weekly review routine. This is your most important learning session.

### 0. Ruflo health check (fail loudly, not silently)
This routine writes ADRs and pattern summaries to RuFlo's `trading-adrs` and `trading` namespaces. If RuFlo is silently broken, those writes vanish into a fallback log and future weekly reviews can't query them.

1. Call `mcp__ruflo__system_health`. Expected: healthy/ok.
2. Call `mcp__ruflo__system_info`. Expected: version `3.7.0-alpha.20` (pinned in `.mcp.json`).
3. On failure or version drift:
   ```bash
   python3 scripts/notify.py alert high ruflo 'Ruflo MCP unhealthy or version drift during weekly review — ADR/pattern stores may not persist. Expected v3.7.0-alpha.20.'
   ```
   Continue the routine with file-only memory; ADRs still get written to `docs/adr/`. Note in the weekly journal so the next routine cycle can retry the RuFlo store.

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
Run: `python3 scripts/alpaca_client.py account`

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

### 4a. Write an ADR if strategy changed (RuFlo)
If ANY rule, parameter, or decision criterion was added/changed/removed in step 4, create an Architecture Decision Record:

1. Determine the next ADR number: `ls docs/adr/ | sort -n | tail -1` (or 0001 if directory is empty).
2. Create `docs/adr/<NNNN>-<short-slug>.md` with this template:

```markdown
# ADR-<NNNN>: <decision title>

**Date**: YYYY-MM-DD
**Status**: Accepted
**Supersedes**: <ADR-NNNN if any, else "none">

## Context
What was happening this week that motivated the change. Cite specific trades, journal entries, or memory keys.

## Decision
The exact rule change. Before → after. Be specific about thresholds and conditions.

## Consequences
- Positive: what this prevents or improves
- Negative: what we're giving up or risking
- Neutral: behavior unchanged in these scenarios

## Validation Plan
How we'll know if this was the right call. Concrete metric + timeframe (e.g., "If win rate of trades caught by this rule drops < 40% over next 10 samples, revisit.").

## References
- Memory: <namespace/key>
- Trades: <ticker / date>
- Journal: <YYYY-MM-DD.md>
```

3. Also store the ADR summary in RuFlo memory:
   - `mcp__ruflo__memory_store` with `namespace: "trading-adrs"`, `key: "adr/<NNNN>"`, `value`: the full ADR markdown, `tags: ["adr", "<area-of-change>"]`
4. If this ADR supersedes a prior one, edit the older ADR's frontmatter `Status` to `Superseded by ADR-<NNNN>`.

If NO strategy change happened this week, skip ADR creation. ADRs are for actual rule changes, not weekly housekeeping.

### 5. Tracking List Cleanup + Internet Scan Hit-Rate Review
`memory/watchlist.json` is now posture-proxies-only (7 ETFs) and requires no maintenance. Instead:

**A. Expire stale tracking entries:**
```python
import json, datetime
t = json.load(open('memory/tracking.json'))
today = datetime.date.today().isoformat()
before = len(t['symbols'])
t['symbols'] = [s for s in t['symbols'] if s.get('tracked_until', '') >= today]
t['last_updated'] = today
json.dump(t, open('memory/tracking.json', 'w'), indent=2)
print(f'Expired {before - len(t["symbols"])} entries. {len(t["symbols"])} remain.')
```

**B. Internet-scan hit-rate review:** Look at this week's journal entries. Which symbols appeared in Step 0b (internet-flagged) AND made it through the market-scan debate gate into an approved setup? Note the conversion rate in `journal/YYYY-MM-DD-weekly.md` under "Internet Scan Effectiveness". If conversion < 20% for the week, note what types of web-discovered signals were noise — this informs search query refinement next week.

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

### 9. Update Strategy Library
If any strategy adjustments were made in step 4, append them to `memory/strategy.md` under an "## Adjustments Log" section with date and ADR reference. The strategy file is the canonical strategy library now (Obsidian vault + git history); the prior ClickUp Strategy Library doc is read-only archive.

### 10. Post Weekly Summary to Discord `#daily-brief`
At the end of the routine, run:

```bash
python3 scripts/notify.py brief 'Weekly Review — Week ending YYYY-MM-DD' '<summary: total P&L $/%, # trades, win rate, best/worst trade, ADR # if any rule changed, confidence 1-10, one-line plan for next week>'
```

Silent (no @mention) — for at-a-glance review. If `notify.py` fails, log to `memory/pending_discord_updates.md` and continue.

### 11. Refresh the Dashboard

```bash
python3 scripts/dashboard.py
python3 scripts/notify.py dashboard
```
