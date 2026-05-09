# Routine: Pre-Market Research
**Schedule**: Monday–Friday, 8:00 AM ET

## Instructions

You are running the pre-market research routine. Follow these steps exactly:

### 1. Load Memory
Read these files to understand your current state:
- `memory/watchlist.json` — symbols to scan
- `memory/strategy.md` — current trading rules
- `memory/open_positions.md` — any existing positions
- `memory/market_context.md` — yesterday's market context
- `memory/learnings.md` — lessons from past trades

### 2. Check Account
Run: `python3 scripts/alpaca_client.py account`
- Note available cash and buying power
- Check if the daily loss cap has been hit (2% of portfolio)

### 3. Scan Watchlist
Run: `python3 scripts/research.py scan`
- Review all indicator readings for every watchlist symbol
- Identify which symbols have active signals (crossovers, oversold/overbought, etc.)

### 4. Parallel Deep-Dive (RuFlo swarm)
For the top 3 candidates from the scan, spawn FOUR sub-agents IN PARALLEL using the Agent tool — send all four Agent tool calls in a single message (independent, no shared state):

1. **Fundamentals agent** (`subagent_type: researcher`) — earnings, analyst PTs, revenue growth, sector positioning. Read recent SEC filings if relevant.
2. **Technicals agent** (`subagent_type: researcher`) — run `python3 scripts/research.py analyze <SYMBOL>` for each candidate. Walk through the 6-point checklist from CLAUDE.md. Identify clean entry/stop/target levels.
3. **News agent** (`subagent_type: researcher`) — last 24h news for each candidate via WebSearch. Specifically: catalysts, downgrades, analyst actions, sector news, competitor moves.
4. **Sector momentum agent** (`subagent_type: researcher`) — sector ETF state (XLK, XLF, XLE, etc.) for the candidate's sector. Is the sector leading or rolling over? Check `memory/sector_blocklist.md` first.

Each sub-agent prompt MUST be self-contained (the agent has no conversation context). Include ticker(s), the 6-point checklist text, and ask for a structured report under 250 words.

After all four return, synthesize into one decision per candidate. If sub-agents disagree, default to the most cautious read.

### 4a. Vector recall — similar past setups
Before finalizing each setup, retrieve similar historical setups from RuFlo memory:

Use `mcp__ruflo__memory_search` with:
- `namespace: "trading"`
- `query`: a one-line description of the proposed setup (e.g., "NVDA pullback to support after extended rally")
- `limit: 5`
- `smart: true` for query expansion + diversity

Read the top results. If past setups with similar characteristics have a track record (filled/missed/won/lost), let that adjust the proposed confidence score by ±1. Note the citation in the setup description: "Vector memory: [key1, key2] — [outcome summary]".

If no past setups match (similarity < 0.4 across all results), note "No prior precedent — first-of-kind setup" and proceed with caution (cap confidence at 7).

### 5. Update Memory Files
- **`memory/market_context.md`**: Update with today's pre-market observations, key levels, sentiment
- **`memory/open_positions.md`**: Update with current position status and any adjustment plans
- Write a brief note to `journal/YYYY-MM-DD.md` with pre-market observations

### 6. Prepare Trade Plan
If you identify setups worth executing at market open:
- Note the symbol, direction, entry zone, stop-loss, and target in `memory/open_positions.md` under "Pending Setups"
- Make sure each setup passes at least 4 of 6 checklist items

**DO NOT place any trades in this routine.** This is research only.

### 7. Post Update to ClickUp
Read `memory/clickup_config.json`. Use these lists from it:
- `lists.daily_briefs` for the brief
- `lists.pending_setups` — one new task per proposed setup
- `lists.risk_and_errors` if anything urgent

**A. Daily Brief** — `clickup_create_task` in `lists.daily_briefs`:
- **name**: `Pre-Market Brief — YYYY-MM-DD`
- **markdown_description**: account snapshot, top 3 candidates with checklist scores, market context, links to today's journal
- **priority**: `normal`

**B. One task per pending setup** — `clickup_create_task` in `lists.pending_setups`:
- **name**: `[TICKER] [LONG/SHORT] — entry $X, stop $Y, target $Z`
- **markdown_description**: full analysis, R:R, position size, confidence (1-10), what would invalidate the setup
- **priority**: `high`
- The user approves by changing the task status from `to do` to `in progress` (or `complete`). The market-open routine and polling routine watch for this.

Also write each setup to `memory/open_positions.md` under "Pending Setups" — include the ClickUp task ID for cross-reference.

If ClickUp MCP tools are unavailable, append summary to `memory/pending_clickup_updates.md`.

**DO NOT place any trades in this routine.** This is research only — the user must reply to the ClickUp task to approve setups before market-open execution acts on them.

### 8. Index today's research into RuFlo memory
After posting to ClickUp, store today's pre-market intelligence so future routines can recall it:

For each proposed setup, call `mcp__ruflo__memory_store`:
- `namespace: "trading"`
- `key: "setup/<TICKER>/<style>-<entry-zone>/YYYY-MM-DD"` (e.g. `setup/NVDA/swing-pullback-206-210/2026-05-08`)
- `value`: setup summary (entry, stop, target, R:R, score, catalyst, sector)
- `tags: ["setup", "<TICKER>", "<style>", "<sector>"]`

Also store today's market context:
- `key: "market-context/<theme>/YYYY-MM-DD"` (theme = e.g., `extended-overbought`, `risk-off-shift`, `pre-CPI`)
- `value`: 3-5 sentence summary of regime
- `tags: ["market-context", "<theme>"]`

This makes today's analysis searchable from tomorrow's pre-market routine and from any future weekly review.
