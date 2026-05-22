# Open Positions

_Last refreshed: 2026-05-22 Friday Weekly Review (live Alpaca state + 5/22 close scan). Daily routine logs live in `journal/YYYY-MM-DD.md` — this file holds current state only._

## Current Positions

### GOOGL — LONG (filled 2026-05-20)
- **Entry**: $387.07 | 51 shares | Cost basis: $19,740.57
- **Current** (5/22 close): $383.23 | Market value $19,544.69
- **Unrealized P&L**: -$195.88 (-0.99%)
- **Stop**: 10% GTC trailing stop — order `e0b8fbda-b5e5-44d4-86d2-14523e6b4b7c` (status: new / untriggered). Current implied floor ~$348.
- **-7% manual cut trigger**: $359.98 — close immediately if hit (CLAUDE.md Rule 5)
- **Target**: $415.00 | R:R ~2.3:1
- **Stop-tighten ladder**: at +15% ($445.13) → re-place 7% trail; at +20% ($464.48) → 5% trail
- **Catalyst**: Google I/O 2026 (Gemini models, AI Mode in Search)
- **Sector**: Communication Services
- **Setup ID**: GOOGL-2026-05-20 | **Confidence**: 6/10 | **Week 3 trade count**: 1/3
- **Status note (5/22)**: Below SMA 20 ($385.48), MACD histogram -3.53 (deteriorating), Stoch K 0.9 (extreme oversold). The I/O "sell the news" continued past entry — the oversold-bounce thesis is not yet confirmed. No action required: -1.0% is far from the -7% cut and the trailing stop. Watch at the 5/26 pre-market for either an SMA 20 reclaim (thesis confirms) or a break toward $376 (stop into range).

## Pending Orders
- GOOGL 10% trailing stop, order `e0b8fbda` — GTC, untriggered.

## Pending Setups

None.

## Watchlist Alerts (refreshed 2026-05-22 close)
- **NVDA** ($215.34): Post-earnings (5/20 AMC). In the $215–$220 watch zone, RSI 53.7 (< 65), SMA 20 $214.75 just reclaimed. Best fresh-setup candidate for Week 4 — re-baseline fully at 5/26 pre-market (post-earnings reaction was never journaled).
- **AVGO** ($414.01): Oversold within a long-term uptrend (Stoch K 8.5), lagged the post-NVDA semi rally. MACD hist -4.18 — needs a turn before a setup forms. Watch.
- **META** ($610.42): SHORT WATCH (ADR-0007). Below SMA 20/50/200, RSI 45.4. No short here — chasing. Entry only on a failed bounce to the $617–$619 SMA confluence with RSI holding above 40.
- **MSFT** ($418.50): Half-trigger STALED (see below). Holding SMA 20; no setup. Re-watch into the real Microsoft Build window (June 2-3).
- **AAPL / AMD / ARM / QQQ**: All RSI > 72 — overbought. No chase. Wait for pullbacks toward SMA 20.
- **TSLA** ($425.95): Day-trade only — SMA 50 ($388.31) < SMA 200 ($410.00), long-term bearish.

## MSFT Half-Trigger Status (ADR-0004) — STALED 2026-05-22

**Setup #2 — MSFT Mean-Reversion / Trend-Follow — CLEARED, no re-proposal.**
- Re-arm gate required both, in the same routine: (1) SMA 20 reclaim, (2) MACD positive cross (histogram > 0).
- Condition 1 (SMA 20 reclaim): held the entire window.
- Condition 2 (MACD positive cross): **never fired.** Histogram progression across the 5-day window: -1.31 → -0.97 → -0.55 → -0.54 → -0.56 → -0.37. It approached zero but never crossed positive.
- **Stale-by 2026-05-22 EOD reached** (5 trading days from 2026-05-15). Per ADR-0004 the half-trigger is cleared without re-proposal.
- MSFT remains on the watchlist. A *fresh* setup (not a re-arm) is required — likely framed against the real Microsoft Build conference (June 2-3, San Francisco; earlier notes had the wrong dates).

## Expired / Archived Setups

### GOOGL-2026-05-20 — FILLED (now an open position)
- Swing long, entry zone $387–$391, stop $376, target $415, 51 shares, R:R ~2.3:1, confidence 6/10.
- Proposed 2026-05-20 pre-market; approved via Discord 2026-05-20 13:28Z; filled ~09:51 ET 2026-05-20 at $387.07.
- **Status**: FILLED → see "Current Positions" above. Logged to `trade_log.json` in the 2026-05-22 weekly review (the EOD routine that normally logs trades had misfired).

### MSFT Setup #2 — Mean-Reversion / Trend-Follow — STALED 2026-05-22
- Re-arm gate never completed (MACD cross never fired). Cleared per ADR-0004. See "MSFT Half-Trigger Status" above.

### AMZN-2026-05-15 — ARCHIVED (ADR-0002, 2026-05-19)
- Swing long, entry $264.00–$265.50, stop $260.00, target $278–$280, ~74 shares, checklist 3/6, never approved.
- Archived 2026-05-19 midday: 2 trading days since proposal with no fill, thesis broken (price had fallen to $256.71, MACD deeply negative). Price has since recovered to ~$266 but MACD is still negative — no re-proposal warranted.

### NVDA Swing Long (Setup #1) — EXPIRED 2026-05-16
- Entry zone $206–$210 (never filled). NVDA ran well above the zone; setup expired. NVDA is now tracked fresh post-earnings — see Watchlist Alerts.
