# Discord — User Interface Guide

Discord is the **primary user interface** for the trading agent. Everything time-sensitive (approvals, fills, alerts) and everything async (knowledge dumps, feedback, conversational `/ask`) happens here. The file system (`memory/*` + `Dashboard.md`) remains the source of truth — Discord is a view onto it, the bot is the bridge.

This file is the single reference for: which channel does what, what every slash command does, and how the end-to-end flows look.

---

## How Discord fits into the system

```
                   ┌──────────────────────────────────────┐
                   │   YOU (phone, web, desktop Discord)  │
                   └──────────────────────────────────────┘
                          │ tap button / type slash / post msg
                          ▼
                   ┌──────────────────────────────────────┐
                   │   DISCORD BOT (always-on, launchd)   │
                   │   scripts/discord_bot.py             │
                   └──────────────────────────────────────┘
                          │ writes
                          ▼
                   ┌──────────────────────────────────────┐
                   │   memory/*.{md,json}                 │
                   │   (open_positions, queues, watchlist)│
                   └──────────────────────────────────────┘
                          │ read by
                          ▼
                   ┌──────────────────────────────────────┐
                   │   ROUTINES + DISPATCHER (launchd)    │
                   │   1–5 trading + 6 dispatcher + 7 sec │
                   └──────────────────────────────────────┘
                          │ post via notify.py + dashboard.py
                          ▼
                   ┌──────────────────────────────────────┐
                   │   DISCORD CHANNELS                   │
                   │   #approvals, #fills, #risk-alerts,  │
                   │   #daily-brief, #chat                │
                   └──────────────────────────────────────┘
```

**Two key principles:**
1. The bot **only writes to files**. It never touches Alpaca, never executes routines, never makes trade decisions.
2. Routines **only read from files** to discover user intent (Approved flags, queue files, pause state). They never call Discord directly except via `notify.py`.

This separation means the bot can crash and routines still run; routines can fail and the bot keeps responding.

---

## The 7 channels

Each channel has a **pinned explainer message** posted by `scripts/post_channel_explainers.py`. Re-run that script (after editing the `EXPLAINERS` dict) to update wording — it deletes the old pin and posts/pins fresh.

### `#approvals` — trade setup approvals
**What gets posted here:** A setup card for every proposed trade, posted by routines 1 and 3 via `notify.py setup ...`. Each card is sent **as the bot** (not via webhook) so its Approve/Deny/More info buttons route back to the bot.

**Bot behavior:** Listens for button clicks. Clicks are gated to the `authorized_user_id` in `memory/discord_config.json`. On click, the bot edits `memory/open_positions.md` to set `Approved: YES` (Approve) or `Denied: YES` (Deny) under the matching `<SYMBOL>-YYYY-MM-DD` heading.

**Slash commands here:** `/approve`, `/deny`, `/setups`, `/info` (button)

**Sample card content:** `**NVDA — LONG (NVDA-2026-05-11)** | Entry $206-210 | Stop $202 | Target $220 | Size 4 shares | R:R 2.2:1 | Confidence 7/10 | Catalyst: AI cycle intact`

### `#fills` — order fill confirmations
**What gets posted here:** Read-only feed posted by routines 2, 3, 4 via `notify.py fill ...` after every buy/sell completes on Alpaca.

**Bot behavior:** None. Webhook-only channel.

**Slash commands here:** `/positions`, `/account` (most relevant)

**Sample post:** `🟢 BUY filled — NVDA | 4 shares @ $207.45 | Notional $829.80 | Order ID abc123-…`

### `#risk-alerts` — high-priority alerts
**What gets posted here:** `notify.py alert <severity> ...` calls. Severities: `critical`, `high`, `medium`, `low`. Critical and high tag `@here` so phone notifications fire.

**Triggers:**
- `-7%` manual cut rule fired on a position (routine 3)
- Daily loss cap (-2%) hit (routine 2 / 4)
- PDT day-trade count maxed at 3/5 (routine 2)
- Stop-loss order placement rejected by Alpaca (routine 2)
- Sector blocklist trip (routine 1 or 4)
- Ruflo MCP unhealthy / version drift (routines 1, 5, 7)
- Bot startup ping after launchd restart

**Bot behavior:** Posts an "ℹ️ Trading agent bot online" message on every restart so you know it came back.

**Slash commands here:** `/positions`, `/pause`, `/halt`, `/resume`

### `#daily-brief` — routine summaries + pinned dashboard
**What's pinned:**
1. **The live agent dashboard** (`Dashboard.md` content). Auto-updated after every routine via `notify.py dashboard` which PATCHes the same message ID stored in `memory/dashboard_message.json`. No notification noise on update.
2. **The channel explainer** (master command reference + channel purpose).

**What gets posted here:** Silent embeds via `notify.py brief 'Routine name — date' '<one-paragraph summary>'` at the end of every routine.

**Bot behavior:** None on incoming messages.

**Slash commands here:** `/dashboard` (full inline render, ephemeral)

### `#chat` — conversational layer
**What gets posted here:**
- Reflective questions from the agent at end-of-day when something noteworthy happened (`notify.py send chat ...`). Examples: "You denied AMD on Tuesday — was that the right call?"
- Answers to your `/ask` questions, posted by the Discord dispatcher routine.

**Bot behavior:** None on incoming user messages — they're not currently scraped (use `/ask` to queue questions explicitly).

**Slash commands here:** `/ask`, `/dashboard`, `/scan <symbol>`

### `#knowledge-inbox` — drop URLs / docs / ideas
**What you do:** Just post. Plain text, URLs (Substack articles, SEC filings, strategy PDFs), or attachments. No special syntax.

**Bot behavior:** `on_message` handler (gated on author == authorized_user_id) writes the message + attachments to `memory/knowledge_inbox_queue.json`.

**Dispatcher behavior:** On the next 15-min tick, the dispatcher routine (`routines/6_discord_dispatcher.md` step 5) drains the queue:
1. Fetches URL content / reads attached docs
2. Spawns a `researcher` sub-agent to summarize (under 400 words)
3. Appends summary to `memory/learnings.md` under `## Knowledge Inbox — YYYY-MM-DD — <title>`
4. Stores distilled knowledge in RuFlo's `trading` namespace under `key: knowledge/<slug>/YYYY-MM-DD`
5. Posts a confirmation back to `#knowledge-inbox`

### `#feedback` — one-line course corrections
**What you do:** Post short one-line notes. Examples:
- "Don't be cautious about TSLA — it's the most predictable name we trade"
- "R:R 2.0 setups have been too many losers — raise the floor to 2.5"
- "Stop proposing new setups during the first 30 min of market open"

**Bot behavior:** Same `on_message` pattern — writes to `memory/feedback_queue.json`.

**Dispatcher behavior:** Drains queue (step 6), appends each entry verbatim to `memory/learnings.md` under `## Feedback — YYYY-MM-DD`, stores in RuFlo, posts ack.

---

## The 14 slash commands

All commands are gated to `authorized_user_id`. All except read-only commands log to `memory/discord_actions.log` for audit. Slash commands work in **any** channel — the channel is just where the response appears.

### Read-only

| Command | Args | What it does | Output |
|---|---|---|---|
| `/ping` | none | Healthcheck. | "pong" (ephemeral) |
| `/dashboard` | none | Regenerates `Dashboard.md` and renders inline. | Full dashboard markdown (ephemeral) |
| `/positions` | none | Shells out to `alpaca_client.py positions`. | JSON of open positions (ephemeral) |
| `/account` | none | Shells out to `alpaca_client.py account`. | JSON of equity/cash/PDT (ephemeral) |
| `/scan <symbol>` | symbol (e.g. `NVDA`) | Shells out to `research.py analyze SYMBOL`. | Full TA report (ephemeral, ~30 sec) |
| `/setups` | none | Reads "Pending Setups" section from `memory/open_positions.md`. | Markdown block (ephemeral) |

### Approval

| Command | Args | What it does | Output |
|---|---|---|---|
| `/approve <setup_id>` | setup_id (e.g. `NVDA-2026-05-11`) | Edits `memory/open_positions.md` to set `Approved: YES`. | Public confirmation in channel |
| `/deny <setup_id> [reason]` | setup_id + optional reason | Edits `memory/open_positions.md` to set `Denied: YES (reason)`. | Public confirmation |

### State

| Command | Args | What it does | Output |
|---|---|---|---|
| `/pause [reason]` | optional reason | Sets `memory/pause_state.json.state = "paused"`. Routines skip new entries; closes still allowed. | Public ack |
| `/resume` | none | Sets `state = "active"`. | Public ack |
| `/halt <reason>` | required reason | Sets `state = "halted"`. Routines skip ALL trading actions. | Public ack |

### Watchlist

| Command | Args | What it does | Output |
|---|---|---|---|
| `/watchlist add <symbol> [sector] [notes]` | symbol + optional fields | Appends to `memory/watchlist.json`. | Public ack |
| `/watchlist remove <symbol>` | symbol | Removes from `memory/watchlist.json`. | Public ack |
| `/watchlist show` | none | Lists current watchlist. | Markdown block (ephemeral) |

### Triggers + conversation

| Command | Args | What it does | Output |
|---|---|---|---|
| `/run <routine>` | one of `pre-market`, `market-open`, `midday`, `eod`, `weekly`, `security` | Queues to `memory/run_queue.json`. Next dispatcher tick runs it. | Public ack ("📋 Queued …") |
| `/ask <question>` | free-form | Queues to `memory/discord_chat_queue.json`. Next dispatcher tick answers in `#chat`. | Public ack with question excerpt |

---

## Approval flow (end to end)

```
1. Routine 1 (08:00 ET) proposes a setup
   ├─ Writes to memory/open_positions.md under "Pending Setups"
   │   with heading "### NVDA-2026-05-11 — LONG"
   └─ Calls: notify.py setup NVDA-2026-05-11 NVDA LONG '$206-210' '$202' '$220' …

2. Bot posts a setup card to #approvals via REST API
   └─ Card has Approve / Deny / More info buttons (custom_id includes setup_id)

3. You see the push notification on your phone
   ├─ Option A: tap Approve button       → bot writes Approved: YES to file
   ├─ Option B: type /approve NVDA-2026-05-11 → same result via slash
   └─ Option C: edit memory/open_positions.md directly (manual fallback)

4. Market-open routine fires at 09:35 ET
   ├─ Reads memory/open_positions.md
   ├─ Sees "Approved: YES" under the NVDA-2026-05-11 heading
   ├─ Runs the pre-trade buy gate (CLAUDE.md hard rules)
   ├─ Places order via alpaca_client.py buy
   └─ Calls: notify.py fill NVDA buy 4 207.45 <order_id>

5. Bot posts fill to #fills (webhook, no buttons)

6. Dashboard regenerates, pinned message in #daily-brief updates
```

If you do nothing, the setup expires when market-open routine sees no `Approved: YES` flag and skips it with "skipped: awaiting approval" logged.

---

## Knowledge / feedback flow

```
1. You post in #knowledge-inbox: "https://substack.com/p/vwap-strategy"
   OR drop a PDF
   OR just paste raw text

2. Bot's on_message handler (gated to your user_id)
   └─ Writes to memory/knowledge_inbox_queue.json:
      { message_id, channel_id, author_id, received_at, content, attachments }

3. Next 15-min dispatcher tick (08:00–16:30 ET)
   ├─ Reads the queue
   ├─ For each message:
   │   ├─ If URL → WebFetch to get content
   │   ├─ If PDF attachment → read content
   │   ├─ Spawns researcher sub-agent for summary
   │   ├─ Appends to memory/learnings.md under ## Knowledge Inbox — YYYY-MM-DD
   │   ├─ Stores in RuFlo trading namespace
   │   └─ Posts ✅ confirmation back to #knowledge-inbox
   └─ Updates last_dispatch.json with processed message_ids
```

`#feedback` works identically but skips the URL/PDF/sub-agent step — feedback gets appended verbatim to `memory/learnings.md` under `## Feedback — YYYY-MM-DD`.

---

## Dashboard mirror

`Dashboard.md` (at the vault root) is the agent's single source of truth for "current state". It contains:
- Account snapshot (equity, cash, P&L today, PDT count)
- Open positions table
- Pending setups (with approval status)
- Risk state (sector blocklist, daily loss cap status, weekly trade count)
- Recent trades
- Recent learnings
- Run queue

**Generation:** `python3 scripts/dashboard.py` reads Alpaca live + `memory/*` files and writes `Dashboard.md`.

**Mirror:** `python3 scripts/notify.py dashboard` reads `Dashboard.md` and PATCHes a single pinned message in `#daily-brief`. The message ID is tracked in `memory/dashboard_message.json` so subsequent calls update the same message instead of posting new ones.

**When refreshed:** Every routine (1–5 + dispatcher) calls both commands at the end. Manual refresh: run the two commands.

If you ever delete the pinned message in Discord, `notify.py dashboard` will detect the 404 and post + pin a fresh one.

---

## Operations

### Restart the bot
After editing `scripts/discord_bot.py`:
```bash
launchctl unload ~/Library/LaunchAgents/com.claude.tradingagent.discordbot.plist
launchctl load   ~/Library/LaunchAgents/com.claude.tradingagent.discordbot.plist
```
Within ~5 seconds you should see "ℹ️ Trading agent bot online." in `#risk-alerts`.

### Update channel explainer wording
1. Edit the `EXPLAINERS` dict at the top of `scripts/post_channel_explainers.py`
2. Run: `python3 scripts/post_channel_explainers.py`
3. The script deletes the old pinned message and posts/pins a fresh one. The tracker `memory/channel_explainers.json` keeps message IDs.

### Add a new channel
1. Create the channel in Discord
2. Copy the channel ID (right-click → Copy Channel ID, requires Developer Mode)
3. Create a webhook (channel settings → Integrations → Webhooks → New)
4. Add a slot to `memory/discord_config.json` under `channels`
5. If the bot should listen there: edit `discord_bot.py` to add a constant + `on_message` filter, then restart bot
6. If you want a pinned explainer: add an entry to `EXPLAINERS` in `post_channel_explainers.py` and run it

### Grant the bot extra permissions
Server Settings → Roles → `Trading Agent Bot` → Permissions. Currently it needs:
- Send Messages, Embed Links, Attach Files (basic)
- Manage Messages (for pinning the dashboard)
- Use Application Commands (for slash commands)
- Add Reactions (future use)

---

## Troubleshooting

**Bot offline / shows as offline in Discord member list**
- Check `launchd_discord_bot.log` for stack traces
- Verify `DISCORD_BOT_TOKEN` in `.env` is current
- Verify `memory/discord_config.json` has no `REPLACE_WITH_*` placeholders
- `launchctl list | grep discordbot` should show a PID; if it shows `-`, it crashed — load the plist again

**Slash commands don't appear in the picker**
- After restart, sync takes ~5–60 seconds. Type `/` in any channel and wait.
- Check the bot's startup log for `Synced N slash commands to guild …` (N should be 14)
- If N < 14, the bot crashed mid-sync — check log

**Webhook posts fail (`notify.py` returns `{"ok": false, ...}`)**
- Webhook URL might be revoked. Get a new one (channel → Integrations → Webhooks) and update `memory/discord_config.json`
- Discord rate-limited (rare for this volume) — `notify.py` will fail with HTTP 429

**Dashboard pinned message not updating**
- Check `memory/dashboard_message.json` exists with `message_id` and `pinned: true`
- Manually run `python3 scripts/notify.py dashboard` and check log
- If it returns HTTP 404, the message was deleted — `notify.py` will recreate on next run

**Channel listener (`#knowledge-inbox` / `#feedback`) not firing**
- Check `memory/discord_actions.log` — should show `knowledge_inbox_msg msg_id=…` per post
- If empty: check the bot's `_channel_id_or_none()` resolution at startup (log)
- Most common: channel_id in `discord_config.json` is still a placeholder

**Subprocess inside bot fails with `ModuleNotFoundError`**
- The bot uses `sys.executable` for subprocess to avoid launchd-PATH issues. If you see this, verify the patch is still in place: `grep "sys.executable" scripts/discord_bot.py` should return 4 hits.

**"@here" not pinging your phone**
- Open Discord on phone → server settings → notification settings → "All messages" or at least "@mentions"
- iOS / Android focus modes can also block

---

## Reference

- **Bot code:** `scripts/discord_bot.py`
- **Notification sender:** `scripts/notify.py`
- **Dashboard generator:** `scripts/dashboard.py`
- **Channel explainer bootstrap:** `scripts/post_channel_explainers.py`
- **Bot launchd plist:** `scripts/discord_bot_launchd.plist`
- **Dispatcher routine:** `routines/6_discord_dispatcher.md`
- **Bot runbook:** `routines/discord_bot_runner.md`
- **Real config (gitignored):** `memory/discord_config.json`
- **Template config:** `memory/discord_config.example.json`
