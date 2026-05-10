# Routine: Discord Dispatcher
**Schedule**: Every 15 minutes, Mon–Fri, 14:00–22:30 CEST (≈ 8:00 AM–4:30 PM ET)

## Purpose
Drains Discord-driven queue files written by the bot. This routine **replaces** `6_clickup_polling.md` as part of the Discord migration (Phase 2). It bridges between Discord (where Santiago types) and the agent's file system + RuFlo memory.

**This routine never places trades.** It processes user-initiated actions only — approvals already happen in real-time through the bot's button/slash handlers; this routine handles the *async* surfaces (knowledge drops, feedback, queued questions, queued routine triggers).

---

## Inputs (queues drained by this routine)

| Queue file | Source | What this routine does |
|---|---|---|
| `memory/run_queue.json` | `/run <routine>` slash | Execute the named routine inline |
| `memory/discord_chat_queue.json` | `/ask <q>` slash | Answer the question, post reply to `#chat` |
| `memory/knowledge_inbox_queue.json` | Bot's `on_message` in `#knowledge-inbox` | Fetch URL/PDF, summarize, append to learnings + RuFlo |
| `memory/feedback_queue.json` | Bot's `on_message` in `#feedback` | Append to learnings, store in RuFlo |

State carried across runs lives in `memory/last_dispatch.json` (mirrors the old `last_poll.json` shape).

---

## Instructions

### 0. Ruflo health check
Same pattern as routines 1, 5, 7 — call `mcp__ruflo__system_health` + `mcp__ruflo__system_info`. On failure, alert via `notify.py alert high ruflo ...` and continue with file-only fallback (queues still drain; just no semantic-store side effect).

### 1. Load State
Read:
- `memory/pause_state.json` (master toggle)
- `memory/last_dispatch.json` (or initialize empty if missing)
- The four queue files listed above

If any queue file does not exist, treat as `{"queue": []}` and continue.

### 2. Check Pause Toggle FIRST
Read `memory/pause_state.json.state`:
- `active` → ✅ continue normally
- `paused` → ⏸️ skip `run_queue` processing (no auto-runs while paused). Still drain knowledge/feedback/chat queues — those are training, not trading.
- `halted` → 🛑 drain NOTHING. Update `last_dispatch.json` with the timestamp + halted flag and exit. The dispatcher itself stays alive so `/resume` can restart things; halt only suppresses side effects.

### 3. Drain `run_queue.json`
For each queued item NOT in `last_dispatch.processed_run_ids`:

```json
{"routine": "pre-market", "queued_at": "...", "queued_by": "<user_id>"}
```

Map `routine` → routine doc:
- `pre-market` → `routines/1_pre_market_research.md`
- `market-open` → `routines/2_market_open_execution.md`
- `midday` → `routines/3_midday_scan.md`
- `eod` → `routines/4_end_of_day_review.md`
- `weekly` → `routines/5_weekly_review.md`
- `security` → `routines/7_security_scan.md`

Execute the matched routine inline — this is a manual trigger, runs *now* regardless of schedule. After completion:
- Post a brief to `#daily-brief`: `notify.py brief 'Manual run — <routine>' 'Triggered by /run, completed in N min. See journal for output.'`
- Mark the queued_at timestamp in `processed_run_ids`.

Trim the queue file: drop processed items, keep up to 50 unprocessed for retry.

### 4. Drain `discord_chat_queue.json`
For each queued question NOT in `last_dispatch.processed_chat_ids`:

```json
{"question": "...", "queued_at": "...", "queued_by": "<id>", "channel_id": "..."}
```

1. Decide intent (same logic as the old polling routine's chat handler):
   - **Question about a ticker / strategy / past trade** → search `memory/` and RuFlo (`mcp__ruflo__memory_search` with `smart: true`), draft a concise answer (under 200 words).
   - **Instruction to add/remove watchlist symbol** → update `memory/watchlist.json` directly (same shape as `/watchlist` slash).
   - **Strategy-relevant statement** ("don't be cautious about TSLA") → append to `memory/learnings.md` under "## Chat Insights — YYYY-MM-DD", store in RuFlo (`namespace: "trading"`, `key: "chat-insight/YYYY-MM-DD-<msg_id>"`).
   - **Simulation request** → run `python3 scripts/research.py analyze <SYMBOL>`, walk through the hypothetical, return summary.
2. Post the reply via `notify.py send chat '<question excerpt>' '<answer>'`.
3. Add the queued_at timestamp to `processed_chat_ids`.

### 5. Drain `knowledge_inbox_queue.json`
For each queued message NOT in `last_dispatch.processed_knowledge_ids`:

```json
{"message_id": "...", "channel_id": "...", "received_at": "...", "content": "...", "attachments": [...]}
```

1. Determine source content:
   - If `content` contains a URL → `WebFetch` the URL.
   - If `attachments` has a PDF → read the file via the URL.
   - If `content` is plain text without a URL → use the text directly.
2. Spawn an Agent (`subagent_type: researcher`) with this prompt: "Summarize this trading-related document. Extract: (a) any concrete rules/thresholds/setups, (b) the strategy framework category (day trade / swing / risk mgmt), (c) how it differs from current strategy in `memory/strategy.md`. Output under 400 words."
3. Append the summary to `memory/learnings.md` under a new heading: `## Knowledge Inbox — YYYY-MM-DD — <short title>`.
4. Store in RuFlo: `mcp__ruflo__memory_store` with `namespace: "trading"`, `key: "knowledge/<slug>/YYYY-MM-DD"`, `value`: the summary, `tags: ["knowledge", "<category>"]`.
5. Post a confirmation to `#knowledge-inbox`: `notify.py send knowledge_inbox '✅ Processed' '<short title> — appended to learnings.md'`.
6. Add `message_id` to `processed_knowledge_ids`.

### 6. Drain `feedback_queue.json`
For each queued message NOT in `last_dispatch.processed_feedback_ids`:

1. Append the verbatim feedback to `memory/learnings.md` under "## Feedback — YYYY-MM-DD".
2. Store in RuFlo: `namespace: "trading"`, `key: "feedback/YYYY-MM-DD-<msg_id>"`, `value`: feedback content, `tags: ["feedback"]`.
3. Post acknowledgement to `#feedback`: `notify.py send feedback '✅ Recorded' 'Will be reflected in future routines.'`.
4. Add `message_id` to `processed_feedback_ids`.

### 7. Update `last_dispatch.json`
Overwrite with:

```json
{
  "last_dispatch_at": "<ISO timestamp>",
  "last_known_pause_state": "active|paused|halted",
  "processed_run_ids": ["<queued_at>", ...],
  "processed_chat_ids": ["<queued_at>", ...],
  "processed_knowledge_ids": ["<message_id>", ...],
  "processed_feedback_ids": ["<message_id>", ...]
}
```

Trim each `processed_*` array to the most recent 200 entries.

### 8. Refresh Dashboard
After draining the queues:

```bash
python3 scripts/dashboard.py
python3 scripts/notify.py dashboard
```

So Santiago can see the queue drained and any new state on his phone.

### 9. Optional Hourly Heartbeat
At the top of the hour (dispatcher runs at :00, :15, :30, :45 → only :00 fires this):

```bash
python3 scripts/notify.py send daily_brief '💓 Dispatcher alive HH:MM CEST' 'pause=<state>, drained: run=<n> chat=<n> knowledge=<n> feedback=<n>'
```

Skip if all counts are 0. Disable this step if it gets noisy.

---

## Failure Modes

- **Bot offline** (queue files not being written) — dispatcher drains an empty queue and exits cleanly. No alert; the bot's own restart message in `#risk-alerts` is enough signal.
- **Discord webhooks down** — replies/confirmations fail; `notify.py` returns `{"ok": false, ...}`. Log to `memory/pending_discord_updates.md` and continue. The processed_* lists still update so we don't double-process on retry.
- **RuFlo MCP down** — file writes succeed; vector store writes fail. Note in journal. The next dispatcher cycle's health check will alert if it's still down.
- **Routine triggered via `/run` fails partway** — log the error, alert via `notify.py alert high routine '<routine> failed: <error>'`, mark the queued_at as processed (don't re-attempt — Santiago decides whether to retry).

## Key Discipline
- **Idempotent**: re-running on the same state produces no new side effects. The `processed_*` lists in `last_dispatch.json` enforce this.
- **No trades**: this routine NEVER calls `alpaca_client.py buy/sell/close`. The `/run market-open` path *executes* a routine that may trade, but the dispatcher itself doesn't place orders.
- **Pause check first**: step 2 must run before any other action. A halted system drains nothing.
- **ClickUp is read-only** during Phase 2/3 — this routine does NOT write back to ClickUp. The old polling routine's ClickUp-sync logic is intentionally dropped.
