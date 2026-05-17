# Trading Agent

An autonomous AI trading agent that researches the U.S. equity market, proposes trade setups, executes orders with explicit user approval, and journals every decision. Runs on a personal Mac via `launchd` schedules with GitHub Actions as a cloud failsafe — controlled from a phone via Discord.

## ⚠️ Paper trading only

This agent is configured to use **Alpaca's paper-trading endpoint** (`paper-api.alpaca.markets`) and CLAUDE.md explicitly forbids live trading. Do not point this at a live brokerage account without first redesigning the risk-enforcement layer for real-money consequences.

## What it does

- **Researches** the watchlist every morning before market open — fetches bars, computes RSI / MACD / SMA / EMA / Bollinger / ATR / VWAP / StochRSI, scans for crossovers and squeezes, spawns parallel sub-agents for fundamentals + news + sector momentum
- **Proposes** trade setups with full analysis (entry zone, stop, target, R:R, position size, confidence score 1–10, catalyst) and pushes them to Discord as approval cards with buttons
- **Executes** orders only after explicit user approval (Discord button tap, slash command, or direct file edit)
- **Manages** open positions throughout the day — tightens trailing stops as winners run, fires the hard `-7%` manual cut rule, closes day trades before EOD
- **Reflects** at end of day and end of week — journals decisions, surfaces patterns, asks reflective questions, writes ADRs when strategy rules change
- **Learns** from your feedback — drop articles in `#knowledge-inbox`, post one-liners in `#feedback`; the dispatcher folds them into the agent's memory and RuFlo's vector store

## Architecture

```
                  ┌─────────────────────────────┐
                  │    YOU (Discord on phone)   │
                  └─────────────────────────────┘
                       │ ▲
                       ▼ │
                  ┌─────────────────────────────┐
                  │   Discord Bot (always-on)   │ ← Mac only (launchd KeepAlive)
                  └─────────────────────────────┘
                       │ writes to / reads from
                       ▼
                  ┌─────────────────────────────┐
                  │   memory/  +  Dashboard.md  │ ← single source of truth (git)
                  └─────────────────────────────┘
                    │ ▲                    │ ▲
                    ▼ │                    ▼ │
          ┌──────────────────┐  ┌───────────────────────┐
          │  Mac (primary)   │  │  GitHub Actions       │
          │  launchd cron    │  │  cloud failsafe       │
          │  subscription    │  │  API key, fires +15m  │
          └──────────────────┘  └───────────────────────┘
                       │
                       ▼
                  ┌─────────────────────────────┐
                  │   Alpaca Paper API          │
                  └─────────────────────────────┘
```

**Key components:**
- `scripts/` — Python tooling (Alpaca client, technical research, Discord bot, notification sender, dashboard generator)
- `routines/` — Markdown prompts that Claude Code executes on schedule. Each routine = a self-contained set of instructions for the agent
- `memory/` — File-based agent memory: watchlist, strategy, learnings, open positions, trade log, queue files
- `journal/` — Daily decision logs (date-stamped)
- `docs/adr/` — Architecture Decision Records (every strategy rule change has one)
- 4 launchd jobs orchestrate it all: routines (5 trading + Saturday security), polling (dispatcher every 15min), bot (always on)

## Quick start

```bash
git clone <this-repo>
cd trading-agent
cp .env.example .env             # then fill in ALPACA_API_KEY, ALPACA_SECRET_KEY, DISCORD_BOT_TOKEN
pip3 install -r requirements.txt
python3 scripts/alpaca_client.py account     # smoke test
```

For the full install (Discord bot setup, launchd plists, channel creation), see **[SETUP.md](SETUP.md)**.

To enable the GitHub Actions cloud failsafe, see **[.github/SECRETS.md](.github/SECRETS.md)**.

## Documentation

| Doc | What it's for |
|---|---|
| **[CLAUDE.md](CLAUDE.md)** | Agent persona, hard risk rules, strategy framework, decision checklist. Loaded as system context for every routine. |
| **[SETUP.md](SETUP.md)** | First-time install guide (Python, Alpaca account, Discord bot, launchd, MCP servers). |
| **[DISCORD.md](DISCORD.md)** | The 7 channels, 14 slash commands, approval flow, dispatcher loop. The reference if you're using or maintaining the Discord layer. |
| **[TRADING_GUIDE.md](TRADING_GUIDE.md)** | Day-to-day operations from the user's perspective: how to approve, deny, pause, train, query. |
| **[RUN_ROUTINES.md](RUN_ROUTINES.md)** | Manual routine triggers from VS Code or Discord. |
| **[VAULT.md](VAULT.md)** | Obsidian vault conventions (this repo doubles as a knowledge vault). |
| **[CLOUD_COWORK.md](CLOUD_COWORK.md)** | Future direction: running routines off-Mac via Claude Cloud Routines or GitHub Actions. |

## Hard risk rules (the non-negotiables)

Reproduced from CLAUDE.md so they're in the README too:

- **Paper only.** Never live.
- **Max 5 open positions** at any time
- **Max 20% of portfolio per single position** (cap $20,000 absolute)
- **Max 3 NEW trades per week** (closes don't count)
- **-7% hard cut** on any position — no averaging down, no exceptions
- **Real GTC trailing stops** placed via Alpaca on every entry (not a note in memory)
- **Stop tightens** to 7% trail at +15% gain, 5% at +20% gain
- **75–85% capital deployed** when active
- **Daily loss cap -2%** → stop trading for the day
- **Sector blocklist** kicks in after 2 consecutive losing trades in a sector (5-day cooldown)
- **PDT-aware** — accounts under $25k limited to 3 day trades per 5 rolling business days
- **No options, no crypto, no margin** — equities only

## Status

| Phase | What | Status |
|---|---|---|
| 1 | Foundation: Discord bot, slash commands, dashboard, channel webhooks, routines wiring | ✅ Done |
| 2 | Replace ClickUp polling with Discord dispatcher; bot listeners for `#knowledge-inbox` and `#feedback` | ✅ Done |
| 3 | Strip ClickUp writes from all routines; ClickUp now read-only archive | ✅ Done |
| 4 | Delete ClickUp emergency-fallback artifacts; stable on Discord for one full trading week | ✅ Done |
| 5 | GitHub Actions cloud failsafe; hybrid Mac-primary / GHA-backup scheduler with lockfile guard | ✅ Done |

**Active surfaces:** Discord (primary UI), Alpaca Paper (broker), GitHub Actions (cloud failsafe), RuFlo MCP (`3.7.0-alpha.20`).
**Archived surfaces:** ClickUp (read-only archive; see git history pre-`a201388`).

## License

MIT. Fork freely. No warranties — this is a paper-trading research project, not financial advice.
