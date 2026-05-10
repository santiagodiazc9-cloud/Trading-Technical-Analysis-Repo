#!/usr/bin/env python3
"""
One-shot bootstrap: post + pin a channel-purpose explainer in each Discord channel.

Idempotent: tracks message IDs in memory/channel_explainers.json. Re-running
deletes the previous explainer first, then posts and pins a fresh one. Edit
the EXPLAINERS dict below and re-run to update wording.

Usage:
    python3 scripts/post_channel_explainers.py
    python3 scripts/post_channel_explainers.py --dry-run    # print, don't post
"""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.load(open(ROOT / "memory" / "discord_config.json"))
TRACK = ROOT / "memory" / "channel_explainers.json"

load_dotenv(ROOT / ".env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
if not TOKEN:
    print("DISCORD_BOT_TOKEN missing from .env"); sys.exit(1)

API = "https://discord.com/api/v10"
HEADERS = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}


EXPLAINERS = {
    "approvals": (
        "**📋 #approvals — trade setup approvals**\n\n"
        "The agent posts a card here for every proposed trade setup. Each card has buttons:\n"
        "• **✅ Approve** — authorizes the trade for the next market-open routine\n"
        "• **❌ Deny** — skips the setup and logs the reason\n"
        "• **ℹ️ More info** — shows the full setup details from `memory/open_positions.md`\n\n"
        "**Slash commands here:**\n"
        "• `/approve <setup_id>` — approve by ID instead of button (e.g. `NVDA-2026-05-11`)\n"
        "• `/deny <setup_id> [reason]` — deny with optional reason\n"
        "• `/setups` — show all pending setups inline\n\n"
        "Approvals also work by editing `memory/open_positions.md` directly."
    ),
    "fills": (
        "**🟢 #fills — order fill confirmations**\n\n"
        "Read-only feed. Posted automatically by the agent after every buy/sell completes on Alpaca. "
        "Each post shows symbol, side, qty, fill price, notional, and order ID.\n\n"
        "**Slash commands here:**\n"
        "• `/positions` — current open positions from Alpaca\n"
        "• `/account` — equity, cash, P&L today, PDT count"
    ),
    "risk_alerts": (
        "**⚠️ #risk-alerts — high-priority alerts**\n\n"
        "Tagged @here for **critical** and **high** severity. Triggers include:\n"
        "• -7% manual cut rule fired on a position\n"
        "• Daily loss cap (-2%) hit\n"
        "• PDT day-trade count maxed (3/5 rolling)\n"
        "• Stop-loss order placement rejected by Alpaca\n"
        "• Sector blocklist trip (2 consecutive losses in a sector)\n"
        "• Ruflo MCP unhealthy / version drift\n\n"
        "**Slash commands here:**\n"
        "• `/positions` — see what's at risk right now\n"
        "• `/pause [reason]` — pause new entries (closes still allowed)\n"
        "• `/halt <reason>` — full halt: skip ALL trading routines until `/resume`\n"
        "• `/resume` — resume normal trading"
    ),
    "daily_brief": (
        "**📊 #daily-brief — routine summaries + live dashboard**\n\n"
        "**The other pinned message is the live agent dashboard.** It auto-updates "
        "after every routine — account state, open positions, pending setups, risk state, "
        "recent trades, recent learnings. No notifications when it updates.\n\n"
        "Routine summaries are posted here as silent embeds: pre-market, market-open, midday, "
        "end-of-day, weekly review.\n\n"
        "**Slash commands here:**\n"
        "• `/dashboard` — show the full dashboard inline (ephemeral — only you see it)\n"
        "• `/account`, `/positions` — Alpaca live state\n"
        "• `/setups` — pending setups\n\n"
        "**Master command reference (work in any channel):**\n"
        "Read-only: `/ping` `/dashboard` `/positions` `/account` `/scan <symbol>` `/setups`\n"
        "Approvals: `/approve <id>` `/deny <id> [reason]`\n"
        "State: `/pause [reason]` `/resume` `/halt <reason>`\n"
        "Watchlist: `/watchlist add|remove|show [symbol] [sector] [notes]`\n"
        "Triggers: `/run <pre-market|market-open|midday|eod|weekly|security>`\n"
        "Conversation: `/ask <question>`"
    ),
    "chat": (
        "**💬 #chat — conversational layer**\n\n"
        "The agent posts reflective questions here at end-of-day when something stands out "
        "(e.g. *\"You denied AMD on Tuesday — was that the right call?\"*). Your replies are "
        "picked up by the dispatcher routine (every 15 min) and folded into `memory/learnings.md`.\n\n"
        "Use `/ask <question>` to send a question to the agent. It gets queued and answered "
        "here on the next dispatcher tick.\n\n"
        "**Slash commands here:**\n"
        "• `/ask <question>` — ask the agent anything (queued; ~15 min latency)\n"
        "• `/dashboard` — current state for context\n"
        "• `/scan <symbol>` — quick technical analysis on any ticker"
    ),
    "knowledge_inbox": (
        "**📥 #knowledge-inbox — drop docs, URLs, ideas here**\n\n"
        "Just post. The bot captures every message (text + URLs + attachments) and queues "
        "it for the dispatcher routine, which will:\n"
        "1. Fetch URL contents / read attached docs\n"
        "2. Summarize via a researcher sub-agent\n"
        "3. Append to `memory/learnings.md` under a new dated section\n"
        "4. Store distilled knowledge in RuFlo's `trading` namespace for semantic recall\n\n"
        "Useful for: trading articles, strategy PDFs, market commentary, your own thinking. "
        "No special syntax — just post.\n\n"
        "**Slash commands here:** none specific. Use `/ask` in `#chat` to query what's been ingested."
    ),
    "feedback": (
        "**🗒️ #feedback — one-line course corrections**\n\n"
        "Just post short notes. The bot captures each message and the dispatcher appends them "
        "verbatim to `memory/learnings.md` under a `## Feedback — YYYY-MM-DD` heading.\n\n"
        "Examples:\n"
        "• *\"Don't be cautious about TSLA — it's the most predictable name we trade\"*\n"
        "• *\"R:R 2.0 setups have been too many losers — raise the floor to 2.5\"*\n"
        "• *\"Stop proposing new setups during the first 30 min of market open\"*\n\n"
        "**Slash commands here:** none specific. Just post."
    ),
}


def load_track():
    if TRACK.exists():
        return json.loads(TRACK.read_text())
    return {}


def save_track(data):
    TRACK.write_text(json.dumps(data, indent=2))


def post_and_pin(channel_name: str, channel_id: str, content: str, dry_run: bool):
    print(f"\n--- {channel_name} (channel_id={channel_id}) ---")
    if dry_run:
        print(content)
        return None

    track = load_track()
    prev = track.get(channel_name, {}).get("message_id")

    # Best-effort delete of previous pinned explainer (idempotency).
    if prev:
        d = httpx.delete(f"{API}/channels/{channel_id}/messages/{prev}",
                         headers=HEADERS, timeout=5.0)
        print(f"  delete previous {prev}: HTTP {d.status_code}")

    # Post fresh.
    p = httpx.post(f"{API}/channels/{channel_id}/messages",
                   headers=HEADERS, json={"content": content}, timeout=10.0)
    if p.status_code >= 400:
        print(f"  POST failed: HTTP {p.status_code} — {p.text[:200]}")
        return None
    msg_id = p.json()["id"]
    print(f"  posted: {msg_id}")

    # Pin.
    pin = httpx.put(f"{API}/channels/{channel_id}/pins/{msg_id}",
                    headers=HEADERS, timeout=5.0)
    pinned = pin.status_code in (200, 204)
    print(f"  pin:    HTTP {pin.status_code} ({'ok' if pinned else 'failed'})")

    track[channel_name] = {
        "message_id": msg_id,
        "channel_id": channel_id,
        "pinned": pinned,
    }
    save_track(track)
    return msg_id


def main():
    dry_run = "--dry-run" in sys.argv
    for name, content in EXPLAINERS.items():
        chan = CONFIG["channels"].get(name)
        if not chan or "REPLACE" in str(chan.get("channel_id", "")):
            print(f"\n--- {name} ---  ✗ channel_id missing or placeholder, skipping")
            continue
        post_and_pin(name, chan["channel_id"], content, dry_run)
    print("\nDone.")


if __name__ == "__main__":
    main()
