# Market Context

## Last Updated
2026-06-04 (Market Open Execution, 09:37 ET — Week 5 Day 4 / Thursday — flat book carried over from 6/03 GOOGL cut, no approvals to execute)

## Market Open Update — 2026-06-04 09:37 ET (Market Open Execution)
- **Account**: Equity $98,612.09 | Cash $98,612.09 | Buying power $394,448.36 | Deployed 0% | Day P&L $0.00 (cap headroom full).
- **Positions**: 0/5. Pending setups: 0 (queue empty for 6th consecutive routine; pre-market funnel still dry).
- **Trades placed this routine**: 0 (no Approved-YES setups read — correct no-op).
- **Weekly trade count Week-5**: 0/3 with Thu 6/4 + Fri 6/5 remaining.
- **Daytrade count**: 0/3; PDT inactive.
- **Sector blocklist**: empty. Comm Services still 1/2 toward auto-blocklist; no fresh Comm-Services exposure today.
- **Pause toggle**: `pause_state.json` still missing — treated as active.
- **Market posture inheritance from 6/01 EOD**: 🟢 GREEN (SPY $758.86, SMA 20 $741.22, SMA 50 $705.58) — no fresh SPY read this routine; posture carried forward unchanged.
- **Discord**: notify.py brief + dashboard mirror both failed (config + bot token missing) — logged to pending_discord_updates.md.

## EOD Update — 2026-06-03 15:48 ET (End-of-Day Review)
- **Book flat**: 0 open positions into close (GOOGL closed 12:36 ET on -7% manual cut). No swing positions to manage overnight.
- **Account**: Equity $98,612.11 | Cash $98,612.11 | Buying power $197,224.22 | Deployed 0% | Day P&L -$842.19 (-0.85%, within -2% cap).
- **Trade activity today**: 1 close (GOOGL -$1,387.89 / -7.03% realized), 0 entries, 0 setups proposed. Weekly trade count Week-5: 0/3 (2 sessions left).
- **Sector tally**: Communication Services 1/2 toward blocklist (5-day cooldown if 1 more loss).
- **Confidence calibration first datapoint**: `bucket_5_6` n=1, 0 wins / 1 loss. Other buckets still empty after 5 weeks.
- **Hard rule violations today**: NONE. -7% cut is a rule firing, not a violation.
- **Daily loss cap**: NOT hit (-0.85% vs -2.0% cap).
- **Pre-market funnel**: 5th consecutive scan-less window (cloud routine + Discord-config gap). 0 fresh ideas across pre-market, market-open, and midday.
- **Market posture inheritance from 6/01 EOD**: 🟢 GREEN (SPY $758.86, SMA 20 $741.22, SMA 50 $705.58) — no fresh SPY read this routine; posture carried forward unchanged.

## Mid-day Update — 2026-06-03 12:36 ET (Midday Scan)
- **GOOGL HARD-CUT FIRED**: position closed at $359.8565 (-7.03% realized, -$1,387.89). Trailing stop e0b8fbda cancelled before market-close.
- **Account**: Equity $98,612.11 | Cash $98,612.11 | Deployed 0% (flat) | Day P&L -$842.19 (-0.85%, within -2% cap).
- **Positions**: 0/5. Pending setups: 0. Weekly trade count Week-5: 0/3.
- **Sector tally**: Communication Services 1/2 toward blocklist.
- **Market posture inheritance from 6/01 EOD**: 🟢 GREEN (SPY $758.86, SMA 20 $741.22, SMA 50 $705.58) — no fresh SPY read this midday; posture carried forward.
- **First closed trade after 5 weeks** = -7% loss; confidence-bucket bucket_5_6 now n=1 (0 wins / 1 loss). Calibration data finally exists.

## Market Posture
🟢 GREEN — SPY $758.86 | SMA 20 $741.22 | SMA 50 $705.58 | SMA 200 $681.72
Full trading: new longs AND shorts allowed. **RSI caution: SPY 75.5 (overbought per ADR-0001) — new longs must have strong catalyst, no chasing.** Stoch K 74.1, BB pct 0.94 (upper band) — extension persisting from Week 4 close.

## Snapshot Summary — 2026-06-01 EOD (Week 5 Day 1)
- SPY $758.86 (+0.4% from 5/27 read $750.46). MACD hist barely negative (-0.026) — near MACD bullish cross. EMA 9 ($750.11) above EMA 21 ($739.01).
- Day P&L on account: -$123.93 (-0.12%) — well within daily loss cap (-2%).
- Equity $99,532.84. Cash $80,259.43. Deployed 19.36% (still under-deployed vs 75-85% target).
- Daytrade count: 0/3. Pause toggle: still missing (treated as active).
- Hard rule violations today: NONE. Daily loss cap: NOT hit.
- Trades opened today: 0. Trades closed today: 0. Setups proposed today: 0 (no fresh pre-market scan ran this morning per journal — known cloud-routine gap).
- GOOGL (only open position) intraday round-trip: $374.62 open → $377.91 close (-2.39% → -2.37% unrealized).
- **Microsoft Build 2026 (Day 1 of 2) is tomorrow 6/2.** MSFT live catalyst window opens — if Tuesday pre-market routine fires, scan for post-event re-arm and pre-event extension state.

## Market Summary — Week of May 26, 2026 (Week 4)

### Broad Market (5/27 pre-market scan, daily bars)

| Symbol | Price | RSI | MACD Hist | SMA 20 | SMA 50 | Status |
|--------|-------|-----|-----------|--------|--------|--------|
| SPY | $750.46 | 71.4 | -0.6636 | $733.30 ✓ | $698.39 ✓ | 🟢 GREEN (overbought) |
| QQQ | $730.11 | 75.3 | -0.7091 | $698.15 ✓ | $644.80 ✓ | Extended, overbought |

SPY rallied from ~$741 (5/21) to $750.46 (+1.2%) through Memorial Day weekend. Both SPY and QQQ are near upper Bollinger Bands (bb_pct 0.87 and 0.88). VIX not available in current feed — assume normal (<25) given GREEN posture and risk-on behavior.

### Sector ETFs (5/27 pre-market)
- **XLK (Tech)**: $185.17, RSI 76.7, MACD hist +0.09 (barely positive), +7.8% above SMA 20. LT bearish (SMA50 < SMA200). Overbought.
- **XLE (Energy)**: $57.86, RSI 47.6, below SMA 20 ($58.54). LT bearish (SMA50 < SMA200). No long opportunities.
- **XLV (Healthcare)**: $148.52, RSI 56.7, MACD hist +0.58. Above SMA 20. Stoch 91.9 (overbought). LT bearish (SMA50 < SMA200).
- **XLF (Financials)**: $51.86, RSI 54.8, MACD bullish cross (+0.01). Above SMA 20. LT bearish (SMA50 < SMA200).
- **XLI (Industrials)**: $174.31, RSI 55.7, EMA 9/21 bullish cross. Above SMA 20. LT bullish (SMA50 > SMA200) ✓.

### Individual Names — Key Status

| Symbol | Price | RSI | vs SMA 20 | Key Signal |
|--------|-------|-----|-----------|------------|
| AAPL | 308.33 | 77.5 | +5.8% | OVERBOUGHT — no entry |
| MSFT | 416.09 | 52.4 | -0.03% | Below SMA 20, MACD -0.58, LT bearish. ADR-0004 half-trigger STALED 5/22. Re-arm: Microsoft Build June 2-3. |
| NVDA | 214.79 | 53.2 | +0.06% | ★ AT SMA 20 — post-earnings re-entry zone. SETUP PROPOSED. |
| TSLA | 433.53 | 60.8 | +5.2% | Day-trade only (SMA50 < SMA200). RSI 60.8 — fair |
| AMZN | 265.27 | 56.6 | -0.76% | Below SMA 20, MACD hist -2.05. No entry. |
| META | 612.36 | 46.5 | -0.55% | Short watch: below SMA 20/50/200. RSI 46.5. Stoch K 76.4 (high — bounce risk). Wait for Stoch to reset. |
| GOOGL | 388.91 | 61.1 | +0.39% | Open long 51 shares @ $387.07. Barely above SMA 20. MACD -3.56 (worsening). Stoch 4.47 (still oversold). |
| AMD | 503.95 | 77.1 | +21.6% | Sympathy rally off NVDA beat. Extremely extended — observe only, no entry. |
| LLY | 1066.70 | 68.6 | +8.4% | Extended above SMA 20. Stoch 100. Wait for pullback to SMA 20 (~$984). |
| GS | 994.87 | 65.6 | +5.3% | Near upper BB (bb_pct 0.95). Stoch 95.8 (overbought). Extended. |
| ARM | 321.33 | 78.5 | +39.8% | ABOVE UPPER BB. Extreme extension — potential short reversal watch. Not yet. |
| AVGO | 422.06 | 56.6 | +0.68% | At SMA 20. Stoch 12.8 oversold. MACD -3.62 too deep. Watch for MACD cross. |
| TSM | 412.40 | 58.8 | +2.3% | Above SMA 20, MACD neg. No setup yet. |
| CEG | 301.41 | 55.0 | +2.2% | MACD bullish cross. Below SMA 200 ($323.91) = hard ceiling. PASS for now. |
| VST | 164.50 | 61.0 | +9.0% | Extended 9% above SMA 20. Stoch 94. No entry. |
| PLTR | 136.57 | 47.0 | -0.4% | Below SMA 20/50/200. LT bearish. MACD hist +0.40. Not a short here. |
| XOM | 149.76 | 44.3 | -2.2% | Below SMA 20/50. Energy weak. Not a short here (MACD hist positive). |
| PANW | 256.80 | 79.5 | +18.8% | Extremely extended. No entry. |

## Key Levels (Updated 5/27 pre-market)
- **SPY**: Posture GREEN. SMA 20 $733.30 (support, +2.3% margin). SMA 50 $698.39 (deeper support). RSI 71.4 — overbought but trend intact.
- **NVDA**: $214.79. SMA 20 $214.67 (support = entry zone). SMA 50 $197.49 (next support). **SETUP PENDING APPROVAL.**
- **GOOGL**: $388.91. SMA 20 $387.41 (support — barely holding). MACD -3.56 (deteriorating). Target $415. Trailing stop active.
- **AVGO**: $422.06. SMA 20 $419.21 (support). MACD -3.62 — watch for cross before proposing.
- **ARM**: $321.33. Above upper BB. Potential short reversal candidate — wait for RSI drop below 70 AND close below upper BB ($301.23) before considering.
- **META**: $612.36. Below SMA 20 ($615.79), SMA 50 ($617.81), SMA 200 ($668.68). Stoch K 76.4 — elevated, bounce risk. Better short entry when Stoch resets to 35-50 range.

## Key Events — Week of May 26, 2026
- **Mon 5/26**: Memorial Day — US markets closed.
- **Tue 5/27 (TODAY)**: First trading day Week 4. Pre-market: NVDA setup proposed. Market overbought.
- **Thu 5/29**: End of month — potential rebalancing flows.
- **Fri 5/30**: End of month.
- **Mon Jun 2 / Tue Jun 3**: **Microsoft Build 2026** (San Francisco) — MSFT catalyst window. Re-evaluate MSFT re-arm gate then.

## Sentiment (5/27 pre-market)
- **Posture: 🟢 GREEN** but extended. SPY RSI 71.4 limits new long universe to high-catalyst setups only.
- NVDA post-earnings pullback to SMA 20 is the best-quality re-entry of the week.
- AMD/ARM sympathy rally is overdone — extended names should be observed, not chased.
- META short watch improving but Stoch K too high (76.4) for clean entry today.
- Week 4 capacity: 0/3 trade slots used. GOOGL is 1 open position. Room for 1-2 more.

## Prior Week Summary (Week 3 — 5/19–5/22)
- GOOGL filled 5/20 at $387.07 (51 shares, ~$19,741). Post-NVDA earnings beat strengthened GREEN posture.
- NVDA Q1 FY27 beat AMC 5/20: AI cycle confirmed. NVDA pulled from ~$221 pre-earnings to ~$236 post-beat, then pulled back to $214.79 by 5/27.
- MSFT ADR-0004 half-trigger staled EOD 5/22 (MACD cross never fired during Build 2026 Day 1-3). Re-arm window: Build 2026 June 2-3.
- SPY trip-wire ($736) retired; replaced by SMA-based posture system (strategy.md).
