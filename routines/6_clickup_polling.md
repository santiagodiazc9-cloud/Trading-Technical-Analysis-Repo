# Routine: ClickUp Polling
**Schedule**: Every 15 minutes, Mon–Fri, 14:00–22:30 CEST (≈ 8:00 AM–4:30 PM ET)

## Purpose
Bridge between Santiago's phone (ClickUp) and the trading agent's local file system. This routine does NOT replace the 5 main trading routines — it only handles user-initiated actions between scheduled runs (approving setups, dropping training docs, sending feedback, manually triggering routines, syncing watchlist, posting chat messages).

**This routine never places trades.** Approvals are recorded; the next market-open or midday routine acts on them.

## Instructions

### 1. Load State
Read these files:
- `memory/clickup_config.json` — all ClickUp IDs
- `memory/last_poll.json` — what was processed in previous runs
- `memory/open_positions.md` — current pending setups
- `memory/watchlist.json` — current watchlist

### 2. Check Master Pause Toggle FIRST
Use `mcp__claude_ai_ClickUp__clickup_get_task` on `control_tasks.trading_active_toggle`.
- Status `to do` → ✅ Trading active. Continue routine.
- Status `in progress` → ⏸️ Paused. Skip pending-setup approval processing. Still process knowledge-inbox / feedback / chat (those are training, not trading).
- Status `complete` → 🛑 Full halt. Skip ALL processing. Update `last_poll.json` with `last_known_pause_status: "complete"` and exit.

Record the current pause status to `last_poll.json` regardless.

### 3. Process Pending-Setup Status Changes
List tasks in `lists.pending_setups` (use `clickup_filter_tasks` if needed).

For each task:
- Compare current status against `last_poll.json.processed_pending_setup_status_changes[task_id]`.
- If status changed since last poll:
  - `to do → in progress` or `to do → complete`: APPROVED. Edit `memory/open_positions.md` to add `Approved: YES` under that setup's entry. Add a comment on the ClickUp task: "✅ Approval recorded — will execute at next market-open routine."
  - `to do → closed/archived` (with deny tag or comment containing "deny"): DENIED. Edit `memory/open_positions.md` to mark setup `Denied: YES` and append the deny reason to `memory/learnings.md` under "Denied Setups". Comment on ClickUp: "❌ Denial recorded — setup removed from queue."
  - any other transition: ignore.
- Save the new status into `processed_pending_setup_status_changes`.

If pause toggle is `in progress`, skip this section entirely (paused = no new approvals processed).

### 4. Process Knowledge Inbox
List tasks in `lists.knowledge_inbox` filtered by status `to do`.

For each task NOT in `last_poll.json.processed_knowledge_inbox_tasks`:
1. Get full task content via `clickup_get_task` with `detail_level: "detailed"`.
2. If the description has a URL, use `WebFetch` to retrieve content. If it has an attached PDF, read it. If it has pasted text, use that.
3. Use the Agent tool with `subagent_type: researcher` to summarize: "Summarize this trading-related document. Extract: (a) any concrete rules/thresholds/setups, (b) the strategy framework category (day trade / swing / risk mgmt), (c) how it differs from current strategy in `memory/strategy.md`. Output under 400 words."
4. Append the summary to `memory/learnings.md` under a new "## Knowledge Inbox — YYYY-MM-DD — <title>" heading.
5. If the document describes a formal strategy, also update the Strategy Library doc: use `clickup_update_document_page` on `documents.strategy_library.active_strategy_page_id`, append a new "Imported from Knowledge Inbox" section.
6. Store distilled knowledge in RuFlo: `mcp__ruflo__memory_store` with `namespace: "trading"`, `key: "knowledge/<slug>/YYYY-MM-DD"`, `value`: the summary, `tags: ["knowledge", "<category>"]`.
7. Comment on the task with the summary, then update task status to `complete`.
8. Add task ID to `processed_knowledge_inbox_tasks`.

### 5. Process Feedback Log
List tasks in `lists.feedback_log` filtered by status `to do`.

For each task NOT in `processed_feedback_log_tasks`:
- IF the task is the pinned `control_tasks.agent_chat` task → skip in this loop, handled in step 6.
- Otherwise: read the task title (one-sentence feedback) and any description.
- Append to `memory/learnings.md` under "## Feedback — YYYY-MM-DD" with the verbatim feedback.
- Store in RuFlo: `namespace: "trading"`, `key: "feedback/YYYY-MM-DD-<task-id-suffix>"`, `value`: the feedback, `tags: ["feedback"]`.
- Post a comment: "✅ Recorded — will be reflected in future routines."
- Update task status to `complete`.
- Add task ID to `processed_feedback_log_tasks`.

### 6. Process Agent Chat Comments
Get the `control_tasks.agent_chat` task. Use `clickup_get_task_comments` to retrieve all comments.

For each comment NOT in `processed_chat_comment_ids` AND NOT authored by the agent itself:
1. Read the comment text. Treat it as a question or instruction.
2. Decide intent:
   - **Question about a ticker / strategy / past trade** → search `memory/` and RuFlo memory (`mcp__ruflo__memory_search` with `smart: true`), draft a concise answer (under 200 words), post via `clickup_create_task_comment`.
   - **Instruction to add/remove watchlist symbol** → update `memory/watchlist.json` accordingly, also update `lists.watchlist` ClickUp tasks. Post confirmation comment.
   - **Strategy-relevant statement** ("don't be cautious about TSLA") → append to `memory/learnings.md` under "## Chat Insights — YYYY-MM-DD", store in RuFlo (`namespace: "trading"`, `key: "chat-insight/YYYY-MM-DD-<comment-id>"`). Post acknowledgement comment.
   - **Simulation request** ("what if I had bought NVDA at $208?") → run analysis via `python3 scripts/research.py analyze NVDA`, walk through hypothetical, post answer.
3. Add the comment ID to `processed_chat_comment_ids`.

### 7. Process Run-Routine Triggers
List tasks in `lists.run_routines`.

For each task with status `in progress`:
- Identify which routine is being triggered by matching against `control_tasks.run_routines.*`:
  - `pre_market_research: 869d7q8q0` → run `routines/1_pre_market_research.md`
  - `market_open_execution: 869d7q8q2` → run `routines/2_market_open_execution.md`
  - `midday_scan: 869d7q8q6` → run `routines/3_midday_scan.md`
  - `end_of_day_review: 869d7q8qa` → run `routines/4_end_of_day_review.md`
  - `weekly_review: 869d7q8qc` → run `routines/5_weekly_review.md`
- Execute the matched routine inline (this is a manual trigger — bypass schedule).
- After completion, post a comment: "✅ Manual run complete — see Daily Briefs for output."
- Reset task status from `in progress` back to `to do`.
- Add task ID + timestamp to `processed_run_routine_triggers`.

### 8. Sync Watchlist
List all open tasks in `lists.watchlist`.

- Build a desired set: every open task name = a ticker.
- Compare against `memory/watchlist.json`.
- If any ticker is in ClickUp but not in JSON → add to JSON.
- If any ticker is in JSON but not in ClickUp (or task is `complete`) → remove from JSON.
- Save `memory/watchlist.json` only if changed. Note the diff in journal.

### 9. Update last_poll.json
Overwrite with:
```json
{
  "last_poll_at": "<ISO timestamp>",
  "processed_pending_setup_status_changes": { "<task_id>": "<status>", ... },
  "processed_run_routine_triggers": { "<task_id>": "<timestamp>", ... },
  "processed_knowledge_inbox_tasks": ["<task_id>", ...],
  "processed_feedback_log_tasks": ["<task_id>", ...],
  "processed_chat_comment_ids": ["<comment_id>", ...],
  "last_known_pause_status": "<to do|in progress|complete>"
}
```

Trim each "processed_*" array to the most recent 200 entries to prevent unbounded growth.

### 10. Log to Memory
Append a one-line summary to `journal/poll-YYYY-MM-DD.md` (create if missing):
```
HH:MM CEST — pause=<status>, pending_changes=<n>, knowledge=<n>, feedback=<n>, chat=<n>, run_triggers=<n>, watchlist_diff=<n>
```

### 11. Commit + Push (if Phase 4 git cowork is active)
If `.git` exists AND environment variable `TRADING_GIT_AUTOCOMMIT=1`:
- `git add -A memory/ journal/`
- `git commit -m "polling: <timestamp> — <one-line summary>"` (skip if nothing changed)
- `git push origin main` (only if remote configured)

If commit fails, log to `memory/pending_clickup_updates.md` and continue. NEVER halt the routine on a git failure.

### 12. Optional: Post a Heartbeat
At top of each hour (poll runs at :00, :15, :30, :45 → only the :00 run does this):
- Post a comment on the `control_tasks.agent_chat` task: "💓 Polling alive at HH:MM CEST. Pause=<status>. Changes processed this hour: <n>." Skip if nothing new.

This is optional — useful for confirming the system is healthy without spamming. Disable by removing this step if too noisy.

## Failure Modes
- **ClickUp MCP down**: skip ClickUp ops, log to `memory/pending_clickup_updates.md`, still update `last_poll.json` with timestamp + error note. Next poll retries.
- **RuFlo MCP down**: skip vector store writes, files still updated. Note in journal.
- **Alpaca API needed but blocked**: only step 6 simulation requests need it; if blocked, post a comment: "Live data unavailable from sandbox — Santiago please run from VS Code." Mark comment as processed anyway (don't re-attempt).

## Key Discipline
- **Idempotent**: Re-running the routine on the same state must produce no new side effects. The `processed_*` lists in `last_poll.json` enforce this.
- **No trades**: This routine NEVER calls `alpaca_client.py buy/sell/close`. Approvals only flow into memory; the next scheduled trading routine acts.
- **Read pause toggle FIRST**: Step 2 must run before any other action. A halted system polls but does nothing.
