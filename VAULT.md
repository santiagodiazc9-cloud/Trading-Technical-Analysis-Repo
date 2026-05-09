---
type: meta
tags:
  - meta
  - obsidian
---

# Vault — Trading Agent (Obsidian Brain)

Welcome. This project root IS the Obsidian vault.

## How to open

1. Install Obsidian: https://obsidian.md
2. **Open folder as vault** → select this project root.
3. Obsidian will read `.obsidian/` config automatically.

## What lives where

```
/                               ← vault root
├── inbox/                      ← unsorted new notes (default new-note location)
├── journal/YYYY-MM-DD.md       ← daily journal entries (one per trading day)
├── memory/                     ← agent's working memory (active state)
│   ├── strategy.md
│   ├── learnings.md
│   ├── market_context.md
│   ├── open_positions.md
│   ├── sector_blocklist.md
│   ├── pending_clickup_updates.md
│   ├── watchlist.json          ← JSON, not Obsidian-native, but readable
│   ├── trade_log.json
│   ├── clickup_config.json     ← config (don't edit through Obsidian)
│   └── last_poll.json          ← polling state (auto-managed)
├── docs/adr/                   ← Architecture Decision Records
│   ├── README.md
│   └── NNNN-slug.md
├── routines/                   ← agent routine prompts (1-7)
├── scripts/                    ← Python tools (alpaca_client.py, research.py)
├── templates/                  ← Obsidian note templates
└── attachments/                ← (auto-created when you paste images)
```

## Note types and conventions

Every markdown note SHOULD have YAML frontmatter at the top:

```yaml
---
type: setup | journal | lesson | adr | strategy | market-context | rule | learning | meta
date: YYYY-MM-DD
ticker: NVDA          # optional, for setup/lesson/journal
tags: [...]
status: active | archived | superseded | proposed
---
```

This makes Obsidian's properties view + Dataview queries useful.

**Existing files don't all have frontmatter yet.** Add it lazily as you edit each one.

## Tag taxonomy

Use these tags consistently:

- `#setup/<TICKER>` — proposed or executed setup
- `#setup/swing`, `#setup/day-trade` — style
- `#lesson` — observation worth remembering
- `#adr` — architecture decision record
- `#rule` — formal trading rule
- `#journal` — daily journal entry
- `#weekly-review` — weekly summary
- `#market-context` — regime / macro state
- `#feedback` — feedback from user via ClickUp
- `#knowledge` — content imported from Knowledge Inbox
- `#meta` — vault config, README files
- `#deny/<reason>` — denial reasons (e.g., `#deny/overbought`, `#deny/no-catalyst`)

## Linking conventions

- Use `[[wiki-links]]` (configured in `.obsidian/app.json` — `useMarkdownLinks: false`)
- Link aggressively: a journal entry that mentions NVDA → `[[NVDA]]` (or to a specific setup `[[setup-NVDA-2026-05-08]]`)
- Backlinks pane shows reverse: open `learnings.md` and see every note that links to it

## Graph view

Open with `Cmd+G`. Color groups:
- **Blue** — journal entries (story of decisions)
- **Purple** — memory files (current state)
- **Green** — ADRs (durable decisions)
- **Orange** — routines (the agent's instructions)
- **Gray** — inbox (transient)

Useful for spotting orphan notes (no links) and clusters (related ideas).

## Templates

`Cmd+P` → "Insert template" → pick from `templates/`:

- `setup-template.md` — proposing a new trade
- `journal-template.md` — daily journal (the EOD routine uses this format already)
- `adr-template.md` — formal rule change
- `lesson-template.md` — atomic note for a single insight

## Vector recall (RuFlo)

The vault contents are also indexed in RuFlo's vector store under namespace `trading-vault`. Run `scripts/vault_index.py` to refresh after major edits. Then any Claude Code session can do:

```
mcp__ruflo__memory_search namespace="trading-vault" query="..."
```

…to find semantically related notes. Useful for "have I written about this before?" before adding a new note.

## Sync

Vault is a git repo. Push/pull = sync. Cloud trading routines pull on each run, so any note you add in Obsidian shows up in the cloud agent's view from the next routine onward.

For mobile (Obsidian iOS):
- Install [Working Copy](https://workingcopy.app) (git client for iOS) and pair it with Obsidian Mobile via the "External git folder" setting
- Or: use iCloud Drive sync if you're OK without mobile-side commits

## Don't edit through Obsidian

These files are auto-managed and will be overwritten by routines — leave them alone in Obsidian:

- `memory/clickup_config.json`
- `memory/last_poll.json`
- `memory/trade_log.json`
- `memory/watchlist.json` (managed by ClickUp polling routine)
- `.claude-flow/` and `.swarm/` (RuFlo internals — gitignored anyway)
- `ruvector.db` (vector store — gitignored)

If you want to edit one of these, do it in VS Code where you can see what's regenerated automatically.

## What Claude can and can't do with the vault

- ✅ **Local Claude Code (VS Code)**: full read/write, RuFlo vector search, all tools
- ✅ **Cloud routines**: read/write to git-tracked files (commits + pushes back). NO RuFlo (cloud doesn't have the MCP). File-only mode.
- ❌ **Other agent surfaces** (Claude.ai web chat without this project context): no access to the vault unless you paste content in.
