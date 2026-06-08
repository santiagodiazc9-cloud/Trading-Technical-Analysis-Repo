# Market Context

## Last Updated
2026-06-08 09:37 ET (Market Open Execution, Week 6 Day 1 / Monday — routine fired into a flat book + empty Approved queue; no fresh SPY re-baseline available pre-market, so posture inherited from 6/05 EOD 🟡 CAUTION sustained / exception window CLOSED; no trades placed, no trades skipped due to approval; weekly count reset to Week-6 0/3; Discord notify.py still failing — discord_config.json missing in cloud host, 14th consecutive routine; 6th consecutive trading day post-GOOGL-cut on a flat book)

## Market Open Update — 2026-06-08 09:37 ET (Market Open Execution)
- **Routine fire**: clean 09:37 ET (≈2 min after nominal 09:35 ET trigger). Market clock confirmed OPEN (next close 2026-06-08 16:00 ET); first trading session of Week 6.
- **POSTURE inherited (no fresh SPY read)**: 🟡 CAUTION sustained, exception window CLOSED (carried from 6/05 EOD: SPY $738.05, -1.10% below SMA 20 $746.27, beyond the 1% threshold). No pre-market routine produced a 6/08 SPY re-baseline before this routine entered — same gap pattern logged on Friday 6/05 09:37 ET. Posture will be re-evaluated at midday with the first live 6/08 SPY indicator pull.
- **Book**: Flat (0/5 positions). Pending orders: 0 (confirmed via `alpaca_client.py orders` → `[]`). Day-trade close step no-op. Swing-position review step no-op. Per-position management routine reduced to a no-op for the **11th consecutive intraday routine** (6th consecutive trading day post-GOOGL-cut).
- **Account**: Equity $98,612.09 | Cash $98,612.09 | Buying power $394,448.36 | Deployed 0% | Day P&L $0.00 (cap headroom full at -$1,972.24 to trip -2%). Daytrade count 0/3; PDT inactive.
- **Pending setups & approvals**: `memory/open_positions.md` "Pending Setups" empty; no setup IDs → `setup_validator.py` not invoked; no `Approved: YES` flags to read. Trades placed = 0. Trades skipped due to "awaiting approval" = 0. Trades skipped due to "paused" = 0.
- **Pause toggle**: `pause_state.json` still missing — treated as active per project convention. No `/pause` or `/halt` in effect.
- **Hard rule violations this routine**: NONE. Daily loss cap NOT hit ($0.00 vs -$1,972 trigger). PDT count well under cap.
- **Weekly trade count Week-6** (week_starting_2026-06-08): **0/3** at routine exit. Three subsequent new-entry-eligible routines remain today (midday × 1, EOD × 1; Weekly Review is not new-entry-eligible) and four more trading days this week.
- **Sector blocklist**: empty. Communication Services still 1/2 toward auto-blocklist (carried from GOOGL-2026-05-20 loss); no fresh Comm-Services exposure this routine. Elevated scrutiny on GOOGL / META / Comm-Services-tagged proposals through Thu 6/11; auto-clear Fri 6/12 if no fresh Comm-Services loss.
- **Confidence calibration**: unchanged. bucket_5_6 n=1 (GOOGL 0W/1L); bucket_7_8 and bucket_9_10 still n=0 after 5 weeks live.
- **Discord**: `notify.py brief` failed with `discord_config.json missing` — 14th consecutive routine without phone-side delivery. Logged to `memory/pending_discord_updates.md`. `dashboard.py` refreshed on disk (live=true, positions=0, pending_setups=1 same parser quirk reading the `_None._` placeholder, not a real setup). `notify.py dashboard` not attempted — same config-missing failure mode.
- **Stale-state sweep**: `memory/open_positions.md` carries no Pending Setups → no stale-approval check needed. `learnings.md` last touched 6/05 EOD (1 trading day old); `strategy.md` last touched 2026-06-04 (2 trading days old); no stale-file flags needed.
- **First Week-6 entry into Week 6**: Week 5 closed at 0 entries / 1 closed trade (GOOGL -7% cut on 6/03). Week 6 enters with the same flat book that has now persisted for ≈3 calendar days + 1 trading session. Friday Weekly Review (6/05) outputs not yet folded into market_context (Weekly Review didn't write a fresh section into this file) — referencing 6/05 EOD's pending Weekly-Review questions (a)-(d) is the latest checkpoint.



## EOD Update — 2026-06-05 15:46 ET (End-of-Day Review)
- **POSTURE: 🟡 CAUTION sustained, exception window CLOSED**. SPY $738.05 at EOD read — drifted -$5.78 / -0.78% from the 14:05 ET late-midday read of $743.83. Now **-1.10% below SMA 20 ($746.27)** — beyond the 1% CAUTION-exception threshold for the first time since the SMA-based posture system was adopted 2026-05-19. Long-term bull stack intact: SMA 50 $713.47 > SMA 200 $683.90; SPY +3.4% / $24.58 above SMA 50 (no RED transition). For any hypothetical new long under CAUTION, the path-to-eligibility now requires the SMA 20 reclaim itself, not just the confidence-8 + sector-ETF overlay.
- **Indicator drift through the session**: RSI 49.85 (cooled from 54.6 at 14:05 ET; first sub-50 read since pre-GOOGL-entry window in May). MACD hist -2.05 (deeper from -1.69). Stoch K 30.32 unchanged. BB pct 0.24 (lower half, off the lower band). **ATR 14 = 7.54** (continued widening from 6.36 → 6.95 → 7.05 → 7.54 across the day's reads = +18.6% in one trading day, without a single-candle >1.5% shock). EMA 9 ($750.24) > EMA 21 ($742.92), still bullish but converging.
- **Volatility override**: VIX still unavailable in feed. No SPY single-candle >1.5% gap observed — drift continued, not a shock. Override condition NOT met → posture stays CAUTION (not forced RED). ATR-widening is logged as a separate candidate observation (>15% single-day ATR rise without single-candle shock), provisional for Weekly Review.
- **Today's posture path (full intraday trajectory)**: 🟢 GREEN (inherited at 09:37 ET market-open) → 🟡 CAUTION (12:36 ET flip on in-arrears midday cron) → 🟡 CAUTION sustained (14:05 ET late-cron midday re-check) → 🟡 CAUTION + exception window CLOSED (15:46 ET EOD). Within-1% threshold held at both midday reads (-0.31%, -0.37%) and broke at EOD (-1.10%). First sustained-with-exception-closure intraday trajectory the SMA-system has produced.
- **Book**: Flat (0/5 positions). Pending orders: 0 (confirmed via `alpaca_client.py orders`). Day-trade close step no-op (step 2). Swing-position review step no-op (step 3). Per-position management routine reduced to a no-op for the 10th consecutive intraday routine (5th consecutive trading day post-GOOGL-cut).
- **Account**: Equity $98,612.09 | Cash $98,612.09 | Buying power $394,448.36 | Deployed 0% | Day P&L $0.00 (cap headroom full at -$1,972.24 to trip -2%). Daytrade count 0/3; PDT inactive.
- **Setups proposed this routine**: 0. `memory/market_context.md` still has no "Internet Flagged" section to seed — pre-market funnel was empty for Week 5 Day 5. CAUTION posture's tightened exception (now requires SMA 20 reclaim) makes the gate-floor effectively confidence ≥ 8 + sector-aligned + price > SMA 20 — three stacked conditions.
- **Weekly trade count Week-5: 0/3 (FINAL)**. EOD is the last new-entry-eligible routine; Weekly Review at ~16:30 ET does not place trades. Week 5 closes alongside Weeks 1, 2, 4 at zero entries — but unlike those weeks Week 5 had one closed trade (GOOGL -7% cut on 6/03).
- **Sector blocklist**: empty. Communication Services still 1/2 toward auto-blocklist; no fresh Comm-Services exposure today. 4 trading sessions of elevated scrutiny remaining before 6/12 clear (Mon 6/8, Tue 6/9, Wed 6/10, Thu 6/11).
- **Pause toggle**: `pause_state.json` still missing — treated as active.
- **Hard rule violations this routine**: NONE.
- **Daily loss cap**: NOT hit ($0.00 vs -$1,972 trigger).
- **Confidence calibration**: unchanged. bucket_5_6 n=1 (GOOGL 0W/1L); bucket_7_8 and bucket_9_10 still n=0 after 5 weeks live.
- **Discord**: notify.py brief + dashboard pin both expected to fail (config + bot token still unprovisioned in cloud host); will be logged to `memory/pending_discord_updates.md`. **13th consecutive routine** without phone-side delivery if today's brief fails as expected.
- **Stale-state sweep**: learnings.md and market_context.md both modified within this routine; strategy.md modified 2026-06-04 12:05 UTC (1 trading day old). No stale-file flags needed.
- **Trigger-vs-policy reconciliation**: today's external EOD trigger said "ClickUp MCP IS available — use for posting EOD brief…" but CLAUDE.md Phase 4 (2026-05-16) retired ClickUp writes; `routines/4_end_of_day_review.md` does not reference ClickUp. Following project policy (CLAUDE.md overrides default behavior): Discord + Dashboard cover audit/visibility; no ClickUp writes performed. Logged for Weekly Review attention.
- **First SMA-posture-system live state-change is now codified for Weekly Review attribution.** Today (6/05) produced a full intraday trajectory: GREEN inherited → CAUTION flip at 12:36 → CAUTION sustained at 14:05 → exception window CLOSED at 15:46. Three discrete confirmations of the same regime change. Tonight's Weekly Review must answer: (a) was this the rule working as designed (catching rotation early on an SMA-relationship break), or (b) is it a same-week round-trip with Monday open ready to recover above SMA 20? Either outcome is informative.



## Late Midday Re-baseline — 2026-06-05 14:05 ET (Midday Scan, late fire)
- **Cron fired ~95 min after its scheduled 12:30 ET slot.** Prior in-arrears 12:36 ET midday entry (below) was written by a routine completing at 14:02 ET; this routine fired immediately after at 14:04 ET. Two midday-class executions back-to-back, both against an identical flat book. No-op for management, no-op for ideas, same posture verdict — logged here for audit clarity and de-duplicated against the 12:36 ET section.
- **SPY $743.83** (down a further $0.43 / -0.06% from the 12:36 ET read of $744.26). Still BELOW SMA 20 ($746.56) by 0.37%, above SMA 50 ($713.59), above SMA 200 ($683.93). RSI 54.6 (essentially unchanged from 55.0). MACD hist -1.69 (marginally more negative from -1.66 — momentum still cooling). EMA 9 ($751.40) > EMA 21 ($743.45) — short-term EMA cross still bullish but converging. Stoch K 30.3 unchanged. BB pct 0.41 (mid-band). ATR 14 = 7.05 (up from 6.95 — volatility tick continues). Price BELOW VWAP ($748.81) intraday.
- **Posture verdict: 🟡 CAUTION sustained.** No reversal toward GREEN, no deepening toward RED. SPY is still within 1% of SMA 20 (-0.37% vs -1% threshold), so CAUTION-exception eligibility remains intact for any hypothetical confidence-8+ setup with sector-ETF-above-SMA-20 confirmation. No volatility shock (no SPY single-candle >1.5% gap observed, VIX still unavailable in feed). Override conditions not met.
- **Book**: Flat (0/5 positions). 0 open orders. No stops to ratchet, no winners to tighten, no -7% cuts to fire, no thesis-break recommendations to surface. Per-position management routine reduced to a no-op for the 9th consecutive intraday routine (counting the 12:36 ET fire from this same cron cycle).
- **Account**: Equity $98,612.09 | Cash $98,612.09 | Buying power $394,448.36 | Deployed 0% | Day P&L $0.00 (cap headroom full at -$1,972.24 to trip -2%). Daytrade count 0/3; PDT inactive.
- **Setups proposed this routine**: 0. `memory/market_context.md` has no "Internet Flagged" section to seed from — pre-market funnel still dry into Week 5 Day 5. CAUTION posture would still gate any candidate above confidence ≥ 8 + sector-ETF-aligned.
- **Catalyst check on open positions**: skipped (0 open positions). No tavily queries fired.
- **Weekly trade count Week-5**: 0/3 entering EOD with one routine remaining today + Friday Weekly Review. Week-5 will close with 0 entries.
- **Sector blocklist**: empty. Comm Services still 1/2 toward auto-blocklist; no fresh Comm-Services exposure today.
- **Pause toggle**: `pause_state.json` still missing — treated as active.
- **Hard rule violations this routine**: NONE.
- **Discord**: notify.py brief + dashboard pin both expected to fail (config + bot token still unprovisioned in cloud host); will be logged to `memory/pending_discord_updates.md`. 12th consecutive routine without phone-side delivery if today's brief fails as expected.
- **Stale-state sweep**: `memory/open_positions.md` carries no Pending Setups; no stale-approval check needed; setup_validator.py not invoked (no setup IDs to validate).
- **Late-fire pattern note for Friday Weekly Review**: A scheduler firing two midday routines within ~30 minutes of each other (12:36 ET in-arrears + 14:04 ET nominal) is a new infra artifact — not the same as the Wed-only full-day drops or the pre-market scheduler gaps logged Weeks 2-4. Worth flagging in tonight's Weekly Review as a distinct symptom: not a drop, but a duplicate/late fire. Operationally moot today (both routines saw an identical flat book), but if it recurred on a busy day each routine could attempt independent re-baselines or, worse, duplicate setup proposals.

## Mid-day Update — 2026-06-05 12:36 ET (Midday Scan)
- **POSTURE CHANGE 🟢 → 🟡 CAUTION**: SPY $744.26 (down from $756.29 at 6/04 midday → -1.59% over ~24h trading). Now BELOW SMA 20 ($746.59) by 0.31% but above SMA 50 ($713.59) and SMA 200 ($683.94). First posture change in 2+ weeks. Shallow dip — within 1% of SMA 20 trigger (-0.31% vs -1% threshold), so CAUTION-exceptions for high-confidence longs remain available IF an 8+ setup with sector-ETF-above-SMA-20 confirmation surfaces.
- **SPY indicators (12:36 read)**: RSI 14 = 55.0 (cooled from 69.4 / no longer overbought). MACD hist -1.66 (turning more negative from -0.69). EMA 9 ($751.48) > EMA 21 ($743.48) — short-term EMA crossover still bullish. Stoch K 30.3 (mid-range, room to fall). BB pct 0.43 (mid-band, off the upper rail). ATR 14 = 6.95 (up from 6.36 — volatility ticking higher). Price BELOW VWAP ($748.89) — bearish intraday tone.
- **Volatility override**: VIX unavailable in current feed. No SPY single-candle >1.5% gap observed (intraday move was a steady drift, not a shock). Override conditions NOT met — posture stays CAUTION, not forced RED.
- **Book**: Flat (0/5 positions). No stops to ratchet, no winners to tighten, no -7% cuts to fire, no thesis-break recommendations to surface. Per-position management routine reduced to a no-op for the 8th consecutive intraday routine (5 weekday routines × 4 trading days + this one — though some books had GOOGL through 6/03 12:36).
- **Account**: Equity $98,612.09 | Cash $98,612.09 | Buying power $394,448.36 | Deployed 0% | Day P&L $0.00 (cap headroom full at -$1,972.24 to trip -2%). Daytrade count 0/3; PDT inactive.
- **Setups proposed this routine**: 0. `memory/market_context.md` has no "Internet Flagged" section to seed from — pre-market funnel still dry into Week 5 Day 5. CAUTION posture would have raised the bar (confidence ≥ 8 required) even if a candidate had surfaced.
- **Weekly trade count Week-5**: 0/3 entering EOD with one routine remaining today + Friday Weekly Review. Week-5 will close with 0 or 1 entries.
- **Sector blocklist**: empty. Comm Services still 1/2 toward auto-blocklist; no fresh Comm-Services exposure today.
- **Pause toggle**: `pause_state.json` still missing — treated as active (would have permitted entries had any been approved).
- **Hard rule violations this routine**: NONE.
- **Discord**: notify.py brief + dashboard pin both expected to fail (config + bot token still unprovisioned in cloud host); will be logged to `memory/pending_discord_updates.md`. 11th consecutive routine without phone-side delivery if today's brief fails as expected.
- **Stale-state sweep**: `memory/open_positions.md` carries no Pending Setups; no stale-approval check needed; setup_validator.py not invoked (no setup IDs to validate).
- **Posture-change implication for Friday Weekly Review**: This is the first posture transition since the SMA-based posture system was adopted (2026-05-19). Operationally a no-op today (flat book), but worth flagging in tomorrow's weekly review as the system's first live state change. If posture recovers to GREEN by EOD or Monday pre-market, the rule worked as designed (transient CAUTION). If it deepens to RED, the rule will have flagged the rotation early relative to a fixed price-level trip-wire.

## Market Open Update — 2026-06-05 09:37 ET (Market Open Execution)
- **Account**: Equity $98,612.09 | Cash $98,612.09 | Buying power $394,448.36 | Deployed 0% | Day P&L $0.00 (cap headroom full at -$1,972.24 to trip -2%).
- **Positions**: 0/5. Pending setups: 0 (queue empty for 7th consecutive intraday routine; pre-market funnel still dry going into Week 5 close).
- **Trades placed this routine**: 0 (no Approved-YES setups read — correct no-op). No-trade is a valid outcome per CLAUDE.md rule 14.
- **Weekly trade count Week-5**: 0/3 entering Friday — single session remaining to either propose+approve+fill or close Week 5 with 0 entries (would tie Weeks 1, 2, 4 for zero-activity weeks).
- **Daytrade count**: 0/3; PDT inactive (`pattern_day_trader: false`).
- **Sector blocklist**: empty. Comm Services still 1/2 toward auto-blocklist; no fresh Comm-Services exposure today.
- **Pause toggle**: `pause_state.json` still missing — treated as active (would have permitted entries had any been approved).
- **Market clock**: open (next_close 16:00:00-04:00). Routine fired inside its scheduled window.
- **Market posture inheritance from 6/04 midday**: 🟢 GREEN (SPY $756.29, SMA 20 $745.92, SMA 50 $711.83, SMA 200 $683.41, RSI 69.4) — no fresh SPY read this routine; posture carried forward unchanged. Will be re-baselined at midday or by Friday pre-market if that scheduler slot fires.
- **Pre-market 6/05 funnel**: per memory state at routine entry, no Approved setups present in `open_positions.md`. Two interpretations: (a) pre-market scheduler dropped its 6/05 slot (continuing the Wed/Fri infra pattern), or (b) pre-market fired but produced no candidates (5 in a row before today). Either way, market-open executes 0 trades — distinction is for the Friday Weekly Review.
- **Discord**: notify.py brief + dashboard pin both expected to fail (config + bot token still unprovisioned in cloud host); will be logged to `memory/pending_discord_updates.md`. 10th consecutive routine without phone-side delivery if today's brief fails as expected.
- **Stale-state sweep**: `memory/open_positions.md` carries no Pending Setups; no stale-approval check needed; setup_validator.py not invoked (no setup IDs to validate).
- **Hard rule violations this routine**: NONE.

## EOD Update — 2026-06-04 15:46 ET (End-of-Day Review)
- **Book flat**: 0 open positions into close (unchanged from 6/03 close after GOOGL -7% cut). 5/5 slots open going into Friday.
- **Account**: Equity $98,612.09 | Cash $98,612.09 | Buying power $394,448.36 | Deployed 0% | Day P&L $0.00 (-$0.02 nominal vs 6/03 EOD = zero on a cash book; full -2% cap headroom).
- **Trade activity today**: 0 entries, 0 closes, 0 setups proposed across all 4 intraday routines. Weekly trade count Week-5: 0/3 with 1 session remaining (Fri 6/5).
- **Sector tally**: Communication Services 1/2 toward auto-blocklist (carried from 6/03 GOOGL loss). No fresh Comm-Services exposure today.
- **Confidence calibration**: unchanged. bucket_5_6 n=1 (0 wins / 1 loss); bucket_7_8 and bucket_9_10 still empty after 5 weeks live.
- **Hard rule violations today**: NONE.
- **Daily loss cap**: NOT hit ($0.00 vs -$1,972 trigger).
- **Pre-market funnel**: 5th consecutive scan-less window. 0 fresh candidates across pre-market + market-open + midday + EOD.
- **Market posture**: 🟢 GREEN carried from 6/04 midday (SPY $756.29, full bull SMA stack, RSI 69.4 cooled below ADR-0001 caution threshold). No fresh EOD SPY read this routine.
- **Stale-state sweep**: clean — learnings.md and strategy.md both modified 6/04 12:05 UTC; no stale-file flags needed.
- **MSFT post-Build re-arm gate**: NOT re-evaluated against fresh data since 5/27. Tomorrow's pre-market is the natural first read after Microsoft Build 2026 wrap (6/03).
- **Discord**: notify.py brief + dashboard pin both expected to fail (config + bot token missing); will be logged to pending_discord_updates.md. 9th consecutive routine without phone delivery if today's brief fails as expected.

## Mid-day Update — 2026-06-04 12:35 ET (Midday Scan)
- **Book**: Flat (0/5 positions). 4 slots open. No stops to ratchet, no winners to tighten, no -7% cuts to fire. Per-position management routine reduced to a no-op.
- **Account**: Equity $98,612.09 | Cash $98,612.09 | Buying power $394,448.36 | Deployed 0% | Day P&L $0.00 (cap headroom full).
- **Setups proposed this routine**: 0. `memory/market_context.md` had no "Internet Flagged" section to seed from — pre-market funnel still dry into Week 5 Day 4 (7th consecutive routine without fresh ideas; pre-market itself is 5 in a row).
- **Weekly trade count Week-5**: 0/3 with Thu 6/4 PM + Fri 6/5 remaining.
- **Daytrade count**: 0/3; PDT inactive.
- **Sector blocklist**: empty. Comm Services still 1/2 toward auto-blocklist; no fresh Comm-Services exposure today.
- **Pause toggle**: `pause_state.json` still missing — treated as active.
- **SPY snapshot**: $756.29 — posture **🟢 GREEN unchanged**. Price above SMA 20 ($745.92) above SMA 50 ($711.83) above SMA 200 ($683.41). RSI 69.4 (cooled from 75.5 at pre-market — no longer extreme overbought per ADR-0001 trigger). MACD hist -0.69 (slightly negative, momentum cooling). EMA 9 ($753.15) > EMA 21 ($743.35). Stoch K 56.8 (mid-range). BB pct 0.81 (upper half but off the band). ATR 6.36. Price ABOVE VWAP ($748.07) intraday — bullish.
- **Posture verdict**: No change. SPY drifted ~$2.50 lower from 6/01 EOD read ($758.86 → $756.29), but every SMA relationship still aligned bullish. No volatility shock signal (no SPY single-candle >1.5% gap, no VIX read available but no risk-off price action). Override conditions not met.
- **Discord**: notify.py brief + dashboard pin both failed (config + bot token missing) — logged to pending_discord_updates.md. 7th consecutive routine without phone-side delivery.

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
🟡 CAUTION + **exception window CLOSED** — SPY $738.05 | SMA 20 $746.27 | SMA 50 $713.47 | SMA 200 $683.90 (refreshed 6/05 15:46 ET EOD — CAUTION sustained from 12:36 ET flip; SPY now -1.10% below SMA 20, beyond the 1% exception threshold for the first time since SMA-system adoption 2026-05-19)
Reduced trading: new longs require SMA 20 reclaim in same routine AS WELL AS confidence ≥ 8 AND sector ETF above its own SMA 20 (the within-1% exception path is now closed at the EOD reading). Prefer shorts over new longs at the margin. RSI 49.85 (first sub-50 read since pre-GOOGL-entry window in May). MACD hist -2.05 (deeper from -1.69). Stoch K 30.32 unchanged. **ATR 14 = 7.54** (sustained widening 6.36 → 6.95 → 7.05 → 7.54 = +18.6% in one trading day, without single-candle >1.5% shock — separate observation candidate for Weekly Review). No VIX read available; no override applied. First posture transition since SMA-based posture system adopted 2026-05-19 — now confirmed across three intraday reads with exception-window closure at EOD. Operationally moot today (flat book, no setups in queue). Long-term bull stack intact (SPY +3.4% above SMA 50, no RED transition). Friday Weekly Review (later today, ~16:30 ET) to attribute the transition (rule worked as designed / Monday-recovery whipsaw / rotation-starting) and to log the multi-symptom infra slate (duplicate-midday-fire, Monday pre-market pattern, Discord-config gap, ATR widening).

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
