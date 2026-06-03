# Active Strategy

## Current Approach
Starting with a **conservative, paper-trading** approach. Focus on high-probability setups with clear risk/reward.

## Indicator Suite
| Indicator | Parameters | Purpose |
|---|---|---|
| EMA | 9, 21 | Trend direction, intraday crossovers |
| SMA | 20, 50, 200 | Trend identification, support/resistance |
| ADX | 14 | Trend strength gate — require >25 before entry |
| RSI | 14 | Momentum, overbought/oversold, divergence |
| MACD | 12/26/9 | Momentum confirmation |
| Bollinger Bands | 20, 2σ | Volatility, mean reversion setups |
| ATR | 14 | Dynamic stop sizing, volatility measurement |
| VWAP | intraday | Intraday fair value |
| Fibonacci | 38.2%, 61.8% | Preferred pullback entry zones on swing setups |
| Stochastic RSI | 14/3/3 | Momentum extremes |

## Day Trading Rules
- Only trade the first 2 hours and last hour of the session
- Use 5-min chart for entry, 15-min for trend confirmation
- Require EMA 9/21 crossover + RSI confirmation + VWAP alignment
- **ADX must be > 25** — skip day trades in choppy, trendless tape
- Max 2 day trades per day
- Close ALL day trades by 3:45 PM ET
- Preferred entries: pullbacks to VWAP or EMA 21, not breakout chases

## Swing Trading Rules
- Enter on daily chart setups only
- Require SMA 20/50 alignment + MACD crossover
- **ADX must be > 25** on the daily — no swing trades in sideways markets
- **Preferred entry zones**: Fibonacci 38.2%–61.8% pullback from the prior impulse leg, or a retest of the SMA 20
- Hold 2-10 days, never longer without re-evaluation
- Trail stops using ATR once in profit
- Max 3 swing positions at a time
- **RSI divergence**: if price makes a new high but RSI does not, treat as a caution signal — tighten target or skip

## Market Posture System (added 2026-05-19, replaces price-level trip-wire)

Every pre-market routine classifies the current market posture based on SPY's position relative to its moving averages. This replaces the old hard price-level trip-wire ($736), which became stale and context-free.

**Posture classification (check in order — first match wins):**

| Posture | Condition | Trading stance |
|---|---|---|
| 🟢 GREEN | SPY above SMA 20 AND SMA 20 above SMA 50 | Full — new longs AND shorts allowed |
| 🟡 CAUTION | SPY below SMA 20 but above SMA 50 | Reduced — only setups with confidence ≥ 8; prefer shorts over new longs |
| 🔴 RED | SPY below SMA 50 | Shorts only — no new long entries |
| ⚫ BEAR | SPY below SMA 200 | Aggressive short bias; no new longs; reduce all long exposure |

**Volatility override:** If VIX > 25, treat posture as CAUTION regardless of SMA readings (fear spikes invalidate setups). If VIX > 35, treat as RED.

**CAUTION exceptions (new long still allowed if ALL apply):**
- Confidence score ≥ 8/10
- SPY is within 1% of SMA 20 (shallow dip, not a breakdown)
- Setup's own sector ETF is still above its SMA 20

**Posture logging:** The pre-market routine logs the classified posture to `memory/market_context.md` under "Market Posture" so subsequent routines (midday, EOD) inherit it without re-running the full SPY analysis.

**Why this replaces the old trip-wire:** A fixed price level ($736) has no relationship to market health after the market moves significantly. A $734 SPY in an uptrend is a buying opportunity; a $737 SPY after a -15% crash is a dead-cat bounce. The SMA relationship captures this correctly in both cases.

## Short Selling Rules (added 2026-05-19)

Short setups are allowed and actively scanned in every pre-market routine. The mirror of the long rules applies. Shorts unlock opportunity in sideways and bearish markets.

### Short swing entry criteria (all required)
1. **Trend**: Price below SMA 20 AND SMA 20 is declining (slope negative over 5 sessions)
2. **Strength**: ADX > 25 — do not short into choppy, trendless tape
3. **Momentum**: MACD histogram negative AND deepening (more negative than prior session)
4. **RSI range**: RSI between 40–65 and declining — confirms momentum shift without capitulation. Do NOT short RSI < 35 (bounce risk)
5. **Entry zone**: Failed bounce to SMA 20 (rejection candle), Fibonacci 61.8% retracement of prior decline that fails to hold, or break below consolidation support with volume confirmation
6. **Sector confirmation**: Sector ETF (XLK, XLE, XLV, XLF, XLI, or XLY) also bearish — below SMA 20 with MACD negative. No counter-trend shorts against a ripping sector.

### Short-specific hard rules
- **No shorting within 2 trading days of earnings** — short squeeze risk. Cover open shorts the session before earnings.
- **No shorting into SMA 200** without a prior confirmed breach. The 200 is a magnet for bounces.
- **7% cut rule applies symmetrically** — if a short moves 7% against you (i.e., the stock rises 7% above your entry), cover immediately per CLAUDE.md Rule 5.
- **No shorting on ex-dividend dates** — price artificially drops on ex-div, distorts the setup.
- **Cover trigger**: If RSI drops below 30, cover at least half the position — extreme oversold conditions produce violent reversals.
- **Gap-up risk**: If a shorted stock gaps up >3% at open, assess whether the thesis is broken before averaging. Default: cover and reassess.

### Short day trade entry (5-min / 15-min)
- EMA 9 crosses below EMA 21 on 5-min chart
- Price below VWAP and VWAP is declining
- RSI < 50 and falling
- First 90 minutes or last 60 minutes of session only
- Cover by 3:45 PM ET (same as long day trades)

## Economic Calendar Rules (added 2026-05-16)
- Before every pre-market routine, check for scheduled high-impact events that day (NFP, CPI, FOMC, rate decisions, earnings)
- **Hard rule**: Do not open a NEW position within 30 minutes of a high-impact news event
- **Hard rule**: Do not hold a swing position through scheduled high-impact macro news unless already profitable with a stop above breakeven
- If an unscheduled event causes a >1.5% gap in SPY within a single candle, flag as potential black swan — halt new entries and log to `#risk-alerts`
- Low-impact events (PMI, housing data) are noted but do not trigger a halt

## Confluence Requirements (added 2026-05-16)
Every setup must satisfy ALL of the following before being proposed:
1. Trend alignment (SMA or EMA direction)
2. Trend strength (ADX > 25)
3. Momentum confirmation (RSI in range, MACD aligned)
4. Valid entry zone (Fib pullback, VWAP retest, or BB mean reversion — not a chase)
5. R:R ≥ 2:1 with stop defined before entry
6. Specific catalyst documented

Fewer than all 6 = **no proposal**. Note in journal as "partial confluence, passed."

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
- Discipline: No trades forced through Weeks 1, 2, or 4. Overbought conditions identified correctly on AAPL, NVDA, TSLA, AMD, ARM, LLY, PANW — decision to pass was correct.
- Watchlist scanner functioning when `ta` package is installable: 29 symbols scanned successfully through Week 4 (with the documented setuptools-upgrade workaround).
- Memory architecture validated: all read/write routines working as intended across 4 weeks.
- Approval gate held under live intraday pressure (AMZN-2026-05-15): technicals improved through the day, agent did not mutate parameters or self-approve.
- Staleness rule (informal in Week 2, now ADR-0002) caught the NVDA-2026-05-08 silent-drift case cleanly.
- **Week 4: Half-trigger framework + chase rule worked as a redundant safety net.** AVGO 2026-05-28 PASS at 6/10 (confluence gate) was followed 24 hours later by a full-trigger 3/3 firing — but the chase rule (CLAUDE.md #12) and ADR-0003 immutability concern (tentative entry zone outrun by $22+) jointly blocked the proposal. Two independent rules concurring is the design. Codified into ADR-0006 to remove the routine-ordering dependency.
- **Week 4: Position-management framework held under a two-session round-trip swing.** GOOGL ran +1.10% best mark → -1.41% in two days (-2.51 pp). 20% concentration sizing + 10% trailing stop absorbed the swing without forcing a decision; -7% cut buffer remains ~5.7%, SMA 50 break (the real thesis-break signal) ~8.9% away.

## What's Not Working
- **Still 0 closed trades after 4 weeks.** Single position (GOOGL) is 9 sessions old, mark currently -1.74% (live). The confidence-calibration buckets in `trade_log.json` remain empty — no win-rate or per-bucket performance data to validate the 5/6 ≥ 5 confluence gate or the confidence scoring scale.
- **Cloud routine scheduler still dropping slots intermittently.** Week 4 scheduler gaps: 5/27 Wed (no routine fired all day) and 5/29 Fri pre-market (midday re-baselined independently). This is the second pre-market drop in two weeks, and the Wed full-day miss is the second full-day infra failure in 4 weeks. Pattern is "mostly working with occasional drops" rather than the Week 2 "mostly broken" — but a Wed-only miss is not catchable from the EOD-only fallback the way Week 2 gaps were.
- **Discord webhooks (`memory/discord_config.json`) still unprovisioned in cloud host.** Every brief, fill, alert this week logged to `memory/pending_discord_updates.md` instead. This is the limiting factor for approval flow under any kind of distress (e.g., if -7% cut fires intraday, the alert won't reach Santiago).
- **RuFlo MCP unavailable in cloud env across the full 4 weeks.** Vector recall (pre-market step 4a) and indexing (step 8 + this routine's step 4a sub-bullet) both skipped. File-only memory has been sufficient for this volume of setups, but the moment Santiago wants "find prior similar setups" the gap will bite.
- **No fresh sectors entering the watchlist since 2026-05-20.** The AI-infrastructure / nuclear-power additions caught the Week 3 theme. Week 4's leading themes (XLK leadership, AAPL/AMD/ARM/PANW extension) are tech-heavy — the watchlist needs a defensive name or two for rotational protection. Tabled for Week 5 watchlist maintenance.

## Adjustments Log
- 2026-05-16: Upgraded strategy framework. Added: ADX (14) > 25 trend strength gate on all entries (day + swing), Fibonacci 38.2%/61.8% as preferred pullback entry zones, RSI divergence as caution signal, economic calendar hard rules (no new entries within 30min of high-impact news, no holding swings through macro events), explicit confluence checklist (all 6 required to propose). Forex-specific concepts (session hours, spreads, SMC order blocks) not applied — equities only. Core risk rules in CLAUDE.md unchanged.
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
- 2026-06-01 (EOD, Week 5 Day 1): **No rule changes.** Today produced no setups proposed, no entries, no closes. GOOGL intraday round-trip (-3.22% open → -2.37% close) absorbed cleanly by the existing trailing-stop / -7%-cut / 20%-concentration stack — second consecutive single-position swing where the passive exit framework required no decision. Day's lessons (Monday pre-market scheduler-failure pattern, empty confidence-bucket data after 5 weeks, single-session-inside-1×ATR non-event codification candidate) appended to `memory/learnings.md`. None rise to a strategy-rule change at EOD; queued for Friday weekly review (Week 5 close) to evaluate whether (a) the Monday scheduler audit warrants an explicit infra-fallback rule and (b) the "single-session inside 1×ATR = no action, no log" pattern is a formal codification candidate.
- 2026-06-03 (EOD, Week 5 Day 3): **No rule changes today — three candidates queued for Friday weekly review (Week 5 close).** GOOGL closed at -7.03% on the -7% manual cut at 12:36 ET — first closed trade after 5 weeks. Risk machinery validated (rule fired, position closed, account drag contained to -1.39% under the 20%-concentration ceiling of -1.40%). Manual cut governed before broker trailing stop by ~3 pp — dual-stop design validated. Three candidate rules queued for Friday's weekly review without being adopted today (no rule changes at EOD per the standing protocol):
  1. **Confidence-6 entry add-on**: at confidence 6/10 (the gate floor), require explicit MACD-positive confirmation (histogram > 0 OR crossing positive in same routine) before proposing, even when Stoch K extreme oversold + bull SMA stack + catalyst align. Trigger: GOOGL was proposed at confidence 6 on Stoch + bull stack + catalyst with worsening MACD, and that was the marginal element that broke. One sample is not signal — flag the question, do not adopt yet.
  2. **Catalyst-staleness annotation**: surface a "thesis-decay" annotation on positions where the catalyst event passed N sessions ago without sustained move above entry zone. Manual-cut adjunct, not a replacement. Trigger: GOOGL Google I/O catalyst was 14 calendar days stale at exit, MACD worsening for 5+ sessions, but no annotation surfaced in management routines.
  3. **Discord-config provisioning as P0 infra**: today's midday high-severity alert never reached Santiago's phone because `memory/discord_config.json` + `DISCORD_BOT_TOKEN` remain unprovisioned in the cloud routine host. Until 6/03 this was a silent gap (no live alerts to fire); now it's blocked real-time risk delivery. Not a strategy rule per se — an infrastructure rule with strategy implications.

  No changes to core risk rules (CLAUDE.md hard rules 1-15), entry criteria, position sizing, stop-loss methodology, or sector discipline. Day's lessons appended to `memory/learnings.md` with rules-of-thumb framing where appropriate (provisional, not adopted).
- 2026-05-29 (Friday Weekly Review): **One new rule formalized via ADR-0006.**
  - **ADR-0006**: Chase rule and confluence gate must be evaluated in the same routine. A confluence full-trigger firing concurrent with any of (a) >3% same-session move, (b) tentative entry zone outrun by >50% of its own width, or (c) price > SMA 20 + 2 × ATR (longs) / < SMA 20 − 2 × ATR (shorts) is an **automatic PASS** for that routine — no proposal generated, no card sent. The auto-PASS reason MUST be logged in `open_positions.md` and the journal entry. Tightens CLAUDE.md rule 12 from a post-proposal audit into a precondition on the gate itself, and extends ADR-0003's published-zone immutability to pre-publish tentative zones. (Validation case: AVGO 2026-05-28 → 2026-05-29 — half-trigger 2/3 Thu midday/EOD → full-trigger 3/3 Fri midday concurrent with +3.1% intraday and tentative zone $414–$418 outrun by $22+. All three rules concurred PASS; this ADR makes the joint check mechanical instead of routine-ordering-dependent.)

  No changes to the core risk rules (CLAUDE.md hard rules 1–15), to position sizing, stop-loss methodology, or sector discipline. The new rule governs *setup lifecycle* and the *confluence-gate firing condition*, not entry criteria themselves.
