# Active Strategy

## Current Approach
Starting with a **conservative, paper-trading** approach. Focus on high-probability setups with clear risk/reward.

## Day Trading Rules
- Only trade the first 2 hours and last hour of the session
- Use 5-min chart for entry, 15-min for trend confirmation
- Require EMA 9/21 crossover + RSI confirmation + VWAP alignment
- Max 2 day trades per day
- Close ALL day trades by 3:45 PM ET

## Swing Trading Rules
- Enter on daily chart setups only
- Require SMA 20/50 alignment + MACD crossover
- Hold 2-10 days, never longer without re-evaluation
- Trail stops using ATR once in profit
- Max 3 swing positions at a time

## Setup Lifecycle Rules

These govern how a proposed setup evolves between "proposed → approved → filled → managed → closed".

### Approval Gate (CLAUDE.md hard rule 15 — restated here for visibility)
No entry order is placed without an explicit `Approved: YES` flag in `memory/open_positions.md` for that setup. Buttons / `/approve` / direct file edit are the only routes to flip the flag.

### Approved-Setup Staleness (ADR-0002, 2026-05-15)
Any setup carrying `Approved: YES` that has not filled within **2 trading days** of approval must be re-evaluated against fresh indicators in the next pre-market routine. If the entry zone has been outrun, the catalyst has expired, or the technical structure no longer supports the original thesis, the setup is automatically flipped to `Approved: NO — stale`. A brand-new proposal is required to re-arm. The market-open routine MUST refuse to fill any approved setup whose approval timestamp is more than 2 trading days old without a fresh re-evaluation logged that same session.

### Approval-Zone Immutability (ADR-0003, 2026-05-15)
Once a setup is published with an entry zone, stop-loss, target, and size, **the agent may NOT mutate those parameters intraday**. The agent may re-read indicators and log them, may update "indicator drift" / "R:R if filled now" annotations, and may recommend in `#chat` or journal that Santiago consider re-pricing. The agent may NOT widen or narrow the entry zone, move the stop, move the target, change the size, or self-flip the approval. Only Santiago redefines, or the setup auto-stales (ADR-0002) and a brand-new proposal replaces it.

### Half-Trigger Ledger (ADR-0004, 2026-05-15)
When a multi-condition re-arm gate (set as part of a setup PASS or close-out) has **at least one but not all** of its conditions firing during a routine, the routine MUST log the partial state in (1) `memory/open_positions.md` under the relevant setup's status block as `Half-Trigger — N of M conditions met` with each condition marked MET/NOT YET, and (2) `memory/learnings.md` as a one-line dated entry. Subsequent routines inherit the partial state. A half-trigger does NOT bypass the approval gate; a setup is only re-proposable when ALL gate conditions are firing in the same routine. Half-triggers stale after 5 trading days with no progress and are cleared without re-proposal.

## What's Working
- Discipline: No trades forced during Week 1 (setup week) or Week 2. Overbought conditions identified correctly on AAPL, NVDA, TSLA — decision to pass was correct.
- Watchlist scanner functioning when `ta` package is installable: 10 symbols scanned successfully on 2026-05-15, signals generated cleanly.
- Memory architecture validated: all read/write routines working as intended.
- Approval gate held under live intraday pressure (AMZN-2026-05-15): technicals improved through the day, agent did not mutate parameters or self-approve.
- Staleness rule (informal in Week 2, now ADR-0002) caught the NVDA-2026-05-08 silent-drift case cleanly.

## What's Not Working
- No live trade data yet to evaluate setup quality (still 0 trades through Week 2).
- Cloud routine scheduler unreliable: 4 trading days of Week 2 (5/11–5/14) ran with degraded or missing routines. Only the 5/15 schedule fired fully. Infra audit needed (launchd / cron / GHA workflow).
- Discord webhooks (`memory/discord_config.json`) and bot token still unprovisioned in cloud host — every brief, fill, alert this week logged to `memory/pending_discord_updates.md` instead.
- RuFlo MCP unavailable in cloud env all week — vector recall and pattern storage not running. File-only memory only.

## Adjustments Log
- 2026-05-08: Initial strategy framework established
- 2026-05-08 (Weekly Review): Week 1 was system calibration — no trades taken. Core rules unchanged. Adding emphasis on patience: do NOT enter trades when RSI > 70 on the daily timeframe unless there is a confirmed momentum breakout with volume surge. This rule formalizes the observation that several watchlist names were extended this week. **Formalized as ADR-0001.**
- 2026-05-13 (EOD): Proposed rule for Friday weekly review — **approved-setup staleness check**. Any setup carrying `Approved: YES` that does not fill within 2 trading days must be re-evaluated against fresh indicators in the next pre-market routine. Goal: prevent stale approvals from quietly drifting forward and producing late, low-quality fills.
- 2026-05-14 (EOD): No strategy changes — strategy cannot be meaningfully refined while the data pipeline is down. No scan ran for the 4th straight day. The blocker is infrastructure, not strategy. Holding all rules unchanged until a pre-market routine successfully re-baselines indicators.
- 2026-05-15 (EOD): Two candidate rules tabled for the 2026-05-16 Friday weekly review: (1) **Approval-zone immutability** — once a setup is published with an entry zone, the agent may NOT widen / shift / re-bracket that zone intraday. (2) **Half-trigger ledger** — when a re-arm condition partially fires, log the partial state in `open_positions.md` and `learnings.md` at the routine where it first triggers.
- 2026-05-15 (Friday Weekly Review): **Three new rules formalized via ADRs.**
  - **ADR-0002**: Approved setup auto-stales after 2 trading days without a fill. Re-evaluation required; brand-new proposal needed to re-arm. (Validation case: NVDA-2026-05-08 stale drift caught on 2026-05-15.)
  - **ADR-0003**: Approval-zone immutability. Agent may not mutate entry zone, stop, target, or size of a pending setup intraday. (Validation case: AMZN-2026-05-15 held under improving-technical intraday pressure.)
  - **ADR-0004**: Half-trigger ledger. Partial re-arm conditions are logged in `open_positions.md` and `learnings.md` at the routine where they first fire; subsequent routines inherit the partial state. (Validation case: MSFT SMA 20 reclaim fired and stuck across midday + EOD on 2026-05-15.)

  No changes to the core risk rules (CLAUDE.md hard rules 1–15) or to the strategy framework (day-trade / swing-trade entry signals). All three new rules govern *setup lifecycle*, not entry criteria.
