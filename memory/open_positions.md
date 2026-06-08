# Open Positions

## Current Positions
_None. GOOGL closed 2026-06-03 12:36 ET at $359.8565 — -7% manual cut rule triggered. Book flat through 2026-06-08 09:37 ET market-open (11th consecutive intraday routine on a flat book; 6th consecutive trading day post-cut, first session of Week 6). 5/5 position slots open. Posture carried from 6/05 EOD: 🟡 CAUTION sustained with **exception window CLOSED** (SPY -1.10% below SMA 20 at last read). Pre-market 6/08 had not produced a fresh SPY re-baseline by 09:37 ET routine entry — posture treated as unchanged until midday refresh. Operationally moot at zero exposure._

## Pending Orders
None.

## Pending Setups
_None at 2026-06-08 09:37 ET market-open. Pre-market pipeline empty for 10th consecutive scan-less or scan-empty window — extended from 6/05 EOD into Week 6 Day 1 (Mon 6/08 pre-market either dropped its slot or produced no candidates; will resolve at midday). 5/5 position slots open; weekly trade count Week-6 (2026-06-08 start): **0/3**. No setup IDs to validate via `setup_validator.py`; `Approved: YES` queue empty; trades placed = 0; trades skipped due to "awaiting approval" = 0._

_(Carried context from 6/05 EOD)_ _None. Pre-market pipeline empty for 9th consecutive scan-less or scan-empty window into 2026-06-05 EOD (Mon 5/27 → Fri 6/5 with documented gaps). 5/5 position slots open; weekly trade count Week-5: **0/3 (FINAL)** — EOD is the last new-entry-eligible routine today; Weekly Review at ~16:30 ET does not place trades. Today's four routine reads (market-open, midday × 2, EOD) all executed as no-ops (no positions to manage, no Internet-Flagged symbols to evaluate, no pending setups in queue). Posture 🟡 CAUTION sustained with exception window CLOSED at EOD — for any new long under CAUTION, the path-to-eligibility now requires SMA 20 reclaim AS WELL AS confidence ≥ 8 + sector-ETF-above-SMA-20 (the within-1% exception path is no longer available). Friday Weekly Review (later today) will resolve (a) the empty 6/05 pre-market funnel — scheduler drop vs genuine zero-candidate scan, (b) the first live SMA-posture-system intraday trajectory (GREEN → CAUTION → CAUTION-sustained → CAUTION-exception-closed) and its attribution (rule worked / whipsaw / rotation), (c) the duplicate/late midday cron fire as a distinct infra symptom, and (d) the SPY ATR-widening observation (+18.6% in one trading day without a >1.5% single-candle shock) as a candidate "volatility expanding" flag._

## Sector Watch (carried, refreshed 2026-06-05 EOD)
- **Communication Services**: 1 consecutive loss (GOOGL-2026-05-20). 1 more loss = auto-blocklist for 5 trading days per CLAUDE.md hard rule #10. Elevated scrutiny on any GOOGL / META / Comm-Services-tagged proposal for the next 4 trading sessions (Mon 6/8, Tue 6/9, Wed 6/10, Thu 6/11 — clears Fri 6/12 if no fresh Comm-Services loss). No fresh Comm-Services exposure today; tally unchanged from 6/03.

---

## Watchlist Updates (as of 2026-05-27)

### Re-arm / Watch Notes
- **NVDA**: Last pre-identified re-entry zone setup (NVDA-2026-05-27) expired 5/30 below $213. Re-arm only on SMA 20 reclaim + MACD hist > 0 in same scan.
- **AVGO**: At SMA 20 ($419.21), Stoch K 12.8 oversold. MACD hist -3.62 TOO DEEP for entry — rejected at 6/10. Re-arm: wait for MACD hist to turn positive (histogram cross). Same AI semiconductor thesis as NVDA.
- **ARM**: $321.33, +39% above SMA 20, above upper BB. POTENTIAL SHORT on reversal. Watch for: RSI drops below 70 AND close below upper BB ($301.23). Do not short into momentum.
- **META**: $612.36, below SMA 20/50/200. Stoch K 76.4 (too high for short entry — bounce risk). Re-arm: wait for Stoch K to reset to 35-50 range, then confirm MACD histogram deepening negative.
- **MSFT**: $416.09, barely below SMA 20 ($416.18), MACD hist -0.58. ADR-0004 half-trigger CLEARED 5/22 (staled). New re-arm window: Microsoft Build 2026 June 2-3 (NOW LIVE — Day 2). Re-arm conditions: SMA 20 reclaim AND MACD histogram positive cross in same pre-market routine.
- **CEG**: $301.41, MACD bullish cross (+0.39). Rejected today (SMA 200 ceiling at $323.91 = 1.3:1 R:R only). Re-arm: SMA 200 ($323.91) needs to be breached convincingly before proposing.
- **AMZN**: $265.27, below SMA 20. MACD hist -2.05 (deeply negative). No re-arm trigger visible.

## Expired / Archived Setups
- **NVDA-2026-05-08**: Expired 2026-05-16. Price ran through target without filling entry.
- **AMZN-2026-05-15**: Archived 2026-05-19. Thesis broken, below entry zone.
- **GOOGL-2026-05-20**: Filled 2026-05-20 @ $387.07. **CLOSED 2026-06-03 12:36 ET @ $359.8565 — -7% manual cut rule triggered.** Realized -$1,387.89 (-7.03%) over 10 trading sessions. Order 990ed249-5d7b-43cd-8976-a535a7e72fc0 (sell market 51 shares). Trailing stop e0b8fbda CANCELLED before close. Sector: Communication Services (1 loss; not yet blocklist-eligible — needs 2 consecutive). Approved: YES via Discord 2026-05-27 12:03Z (legacy entry).
- **NVDA-2026-05-27**: EXPIRED 2026-05-30. Price broke below entry zone floor ($213) to $211.15. SMA 20 ($215.46) failed as support — original thesis required it. Re-arm only on SMA 20 reclaim + MACD hist > 0 in same scan.