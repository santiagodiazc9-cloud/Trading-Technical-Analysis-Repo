---
type: meta
tags:
  - meta
---

# Inbox

Where unsorted notes land. New notes created via Obsidian's "New note" go here by default (configured in `.obsidian/app.json`).

## Workflow
1. Drop a thought, link, or quick observation here.
2. When you have a few minutes (or during the Saturday cleanup window), promote each note to its proper home:
   - **Trade idea / setup** → use the setup template, store under… well, anywhere — the vault doesn't care about folders, just frontmatter and tags. Convention: keep proposed setups in `inbox/` until they post to ClickUp, then archive into `journal/YYYY-MM-DD-setup-TICKER.md` or similar.
   - **Lesson / observation** → use the lesson template. Move to `memory/learnings.md` (append) OR keep as a standalone note linked from `learnings.md`.
   - **Strategy article you read** → drop the link or PDF into the **Knowledge Inbox** in ClickUp instead — the polling routine handles it (summarizes, integrates, deletes from inbox).
   - **Decision / rule change** → use ADR template, save under `docs/adr/NNNN-slug.md`. Increment NNNN.
   - **Random thought / journal entry** → use journal template, save under `journal/YYYY-MM-DD.md` (or append to today's).

## Don't store here long-term
This folder should never have more than ~10 notes at any time. If it does, you're behind on processing.

The Saturday Security Scan routine (and a future "Vault Cleanup" routine) will eventually surface stale inbox notes.
