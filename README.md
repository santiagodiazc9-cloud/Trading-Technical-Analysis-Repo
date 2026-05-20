# Trading Agent

An autonomous AI trading system with two agents — a swing trader and a day trader — controlled from a web dashboard (PWA) and Discord. Runs headlessly via `launchd` and GitHub Actions, with a Next.js dashboard accessible from any device on your network.

## Paper trading only

This agent is configured to use **Alpaca's paper-trading endpoint** (`paper-api.alpaca.markets`). `CLAUDE.md` explicitly forbids live trading. Do not point this at a live brokerage account without redesigning the risk-enforcement layer.

## What it does

**Swing Agent** (scheduled, Claude-powered):
- **Researches** 29 watchlist symbols every morning — fetches bars, computes RSI / MACD / SMA / EMA / Bollinger / ATR / VWAP / StochRSI, spawns parallel sub-agents for fundamentals, news, and sector momentum
- **Classifies market posture** (GREEN / CAUTION / RED / BEAR) from SPY SMA relationships
- **Screens for shorts** as well as longs — flat and declining markets are not "no opportunity"
- **Proposes** setups with full analysis (entry zone, stop, target, R:R, confidence 1–10, catalyst) pushed to Discord `#approvals` as cards with Approve / Deny buttons
- **Executes** orders only after explicit user approval — Discord button, slash command, dashboard button, or direct file edit
- **Manages** open positions — tightens trailing stops as winners run, fires the hard `-7%` cut rule, closes day trades before EOD
- **Reflects** at EOD and weekly — journals decisions, surfaces patterns, writes ADRs when strategy rules change

**Day Trading Agent** (Python engine, runs separately during market hours):
- Polls every 5 minutes (9:35 AM – 3:40 PM ET)
- Three-layer signal stack: **candlestick pattern recognition** (12 patterns) + **statistical mean reversion** (VWAP deviation + intraday Z-score) + **XGBoost ML model** (trained on 180 days of 5-min bars)
- Composite score triggers paper trades when session is approved
- Session approval via dashboard toggle — max trades and max loss budget set per session
- Auto-revokes session at market close

## Architecture

```
              ┌──────────────────────────────────────┐
              │    Dashboard (PWA — localhost:3000)   │  ← phone + desktop
              │    Next.js + TradingView Charts       │
              └──────────────────────────────────────┘
                         │ REST + WebSocket
              ┌──────────▼─────────────────────────────┐
              │    FastAPI Backend (localhost:8000)    │
              └──────────────────────────────────────┘
                         │ reads/writes
              ┌──────────▼─────────────────────────────┐
              │  memory/  +  Dashboard.md              │  ← source of truth (git)
              └──────────────────────────────────────┘
          ┌───┤                                   ├───┐
          ▼   │                                   │   ▼
  ┌──────────────┐                        ┌──────────────────┐
  │ Swing Agent  │                        │ Day Trading Agent │
  │ (launchd +   │                        │ engine.py        │
  │  GHA backup) │                        │ 5-min poll loop  │
  └──────────────┘                        └──────────────────┘
          │                                        │
          └──────────────┬─────────────────────────┘
                         ▼
              ┌──────────────────────────┐
              │   Alpaca Paper API      │
              └──────────────────────────┘

  Discord ← notify.py (fills, alerts, briefs, setup cards)
```

**Key components:**

| Path | Purpose |
|------|---------|
| `scripts/` | Python tooling — Alpaca client, research, Discord bot, notifier, dashboard generator |
| `scripts/daytrader/` | Day trading engine — patterns, mean reversion, ML model, train script |
| `api/` | FastAPI backend for the dashboard |
| `dashboard/` | Next.js PWA — home, swing approvals, day trader, positions, settings |
| `routines/` | Markdown prompts Claude Code executes on schedule |
| `memory/` | File-based agent state — watchlist (29 symbols), strategy, learnings, positions, trade log |
| `journal/` | Date-stamped daily decision logs |
| `docs/adr/` | Architecture Decision Records — every strategy rule change has one |
| `docs/guides/` | Setup, Discord, operations, cloud guides |

## Quick start

```bash
git clone <this-repo>
cd trading-agent
cp .env.example .env        # fill in ALPACA_API_KEY, ALPACA_SECRET_KEY, ANTHROPIC_API_KEY, DISCORD_BOT_TOKEN
pip3 install -r requirements.txt
pip3 install -r requirements-api.txt
python3 scripts/alpaca_client.py account    # smoke test Alpaca connection
```

**Start the dashboard** (both backend + frontend):
```bash
bash scripts/start_dashboard.sh
# Desktop: http://localhost:3000
# Mobile (same WiFi): http://<your-ip>:3000
```

**Train day trading ML models** (run once before first day trading session, then weekly):
```bash
python3 scripts/daytrader/train_all.py
```

**Start the day trading engine** (during market hours):
```bash
python3 scripts/daytrader/engine.py
# Add --dry-run to score symbols without trading
```

For full install (Discord bot, launchd plists, channel setup): see **[docs/guides/SETUP.md](docs/guides/SETUP.md)**.

## Dashboard

Five pages, installable as a PWA (Add to Home Screen on iPhone):

| Page | What it shows |
|------|--------------|
| **Home** | Equity, cash, day P&L, market posture badge, quick nav |
| **Swing** | Pending swing setups with Approve / Deny buttons |
| **Day Trader** | Live 5-min candlestick chart (EMA 9/21 + VWAP), session toggle, score table |
| **Positions** | Open paper positions with unrealized P&L |
| **Settings** | Pause/resume swing agent, market context, watchlist count |

The dashboard reads and writes the same `memory/` files the agents use — no separate database.

## Watchlist (29 symbols)

**Mega-cap tech**: AAPL, MSFT, NVDA, TSLA, AMZN, META, GOOGL, AMD  
**AI infrastructure**: AVGO, TSM, ARM  
**Nuclear / AI power**: CEG, VST, NNE, SMR  
**Sector ETFs**: SPY, QQQ, XLK, XLE, XLV, XLF, XLI  
**Healthcare**: LLY  
**Financials**: JPM, GS  
**Tech (extended)**: CRM, PANW, PLTR  
**Energy**: XOM  

## Hard risk rules

- **Paper only.** Never live.
- **Max 5 open positions** at any time
- **Max 20% of portfolio per position** (cap $20,000 absolute)
- **Max 3 new swing trades per week**
- **-7% hard cut** — closed immediately, no exceptions
- **Real GTC trailing stops** placed immediately after every fill
- **Stop tightens** to 7% trail at +15% gain, 5% trail at +20% gain
- **Daily loss cap -2%** → stop trading for the day
- **Sector blocklist** after 2 consecutive losses in a sector (5-day cooldown)
- **PDT-aware** — sub-$25k accounts limited to 3 day trades per 5 rolling business days
- **No options, no crypto, no margin** — equities only
- **Approval required** before every swing entry
- **Day trading session approval** — explicit per-day budget (max trades + max loss) required before engine trades

## Schedule (all times ET / Madrid in summer is +6h)

| Routine | ET | Madrid |
|---------|-----|--------|
| Pre-market research | 8:00 AM | 2:00 PM |
| Market open execution | 9:35 AM | 3:35 PM |
| Midday scan | 12:30 PM | 6:30 PM |
| End-of-day review | 3:45 PM | 9:45 PM |
| Friday weekly review | 4:30 PM | 10:30 PM |
| Day engine runs | 9:35–3:40 PM | 3:35–9:40 PM |

## Architecture Decision Records

| ADR | Rule |
|-----|------|
| [ADR-0001](docs/adr/0001-rsi-70-no-new-longs.md) | No new longs when RSI > 70 on daily |
| [ADR-0002](docs/adr/0002-approved-setup-2day-staleness.md) | Approved setups auto-stale after 2 trading days |
| [ADR-0003](docs/adr/0003-approval-zone-immutability.md) | Agent cannot mutate entry zone / stop / target intraday |
| [ADR-0004](docs/adr/0004-half-trigger-ledger.md) | Partial re-arm conditions logged and inherited across routines |
| [ADR-0005](docs/adr/0005-day-trading-session-approval.md) | Day trading uses session-level approval instead of per-trade |

## Documentation

| Doc | What it's for |
|-----|---------------|
| **[CLAUDE.md](CLAUDE.md)** | Agent persona, hard risk rules, strategy framework. Loaded as context for every routine. |
| **[docs/guides/SETUP.md](docs/guides/SETUP.md)** | First-time install — Python, Alpaca, Discord bot, launchd, MCP servers |
| **[docs/guides/DISCORD.md](docs/guides/DISCORD.md)** | The 7 channels, 14 slash commands, approval flow, dispatcher loop |
| **[docs/guides/TRADING_GUIDE.md](docs/guides/TRADING_GUIDE.md)** | Day-to-day operations — approve, deny, pause, train, query |
| **[docs/guides/CLOUD_COWORK.md](docs/guides/CLOUD_COWORK.md)** | Mac-off operation via GitHub Actions |
| **[docs/adr/README.md](docs/adr/README.md)** | ADR index |

## License

MIT. Fork freely. No warranties — this is a paper-trading research project, not financial advice.
