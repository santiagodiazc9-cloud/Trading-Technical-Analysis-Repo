#!/usr/bin/env python3
"""
Discord notifier — outbound only, via webhooks.
Stateless HTTP. Works from cloud routines, cron jobs, or local Bash.
The bot (discord_bot.py) is only needed for handling button clicks.

Usage:
    # Free-form message
    python3 scripts/notify.py send <channel> "<title>" "<body>"

    # Pre-formatted helpers
    python3 scripts/notify.py setup <setup_id> <symbol> <direction> <entry> <stop> <target> <size> <rr> <confidence> "<catalyst>"
    python3 scripts/notify.py fill <symbol> <side> <qty> <price> [<order_id>]
    python3 scripts/notify.py alert <severity> <symbol_or_topic> "<message>"
    python3 scripts/notify.py brief <routine> "<summary>"
    python3 scripts/notify.py dashboard          # mirror Dashboard.md to pinned msg in #daily-brief

Channels: approvals | fills | risk_alerts | daily_brief | chat
Severities: critical | high | medium | low
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "memory" / "discord_config.json"
DASHBOARD_PATH = ROOT / "Dashboard.md"
DASHBOARD_MSG_REF = ROOT / "memory" / "dashboard_message.json"
load_dotenv(ROOT / ".env")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")


def load_config():
    if not CONFIG_PATH.exists():
        die(f"Missing {CONFIG_PATH}. Copy discord_config.example.json and fill in.")
    with open(CONFIG_PATH) as f:
        return json.load(f)


def die(msg, code=1):
    print(json.dumps({"ok": False, "error": msg}))
    sys.exit(code)


def post(channel, payload):
    """POST a webhook payload to a channel. Returns dict with ok + status."""
    cfg = load_config()
    chan = cfg["channels"].get(channel)
    if not chan:
        die(f"Unknown channel: {channel}. Valid: {list(cfg['channels'].keys())}")
    url = chan["webhook_url"]
    if "REPLACE" in url:
        die(f"Webhook URL for #{channel} is still a placeholder. Edit {CONFIG_PATH}.")

    try:
        r = httpx.post(url, json=payload, timeout=10.0)
        r.raise_for_status()
    except httpx.HTTPError as e:
        die(f"Discord webhook failed: {e}", code=2)

    print(json.dumps({"ok": True, "channel": channel, "status": r.status_code}))


def post_as_bot(channel, payload):
    """
    POST via the bot's REST API (not webhook). Required when the message has
    interactive components (buttons), because button clicks only route back to
    the bot if the message was sent BY the bot's application.
    """
    if not BOT_TOKEN:
        die("DISCORD_BOT_TOKEN missing from .env — required for bot-sent messages.")
    cfg = load_config()
    chan = cfg["channels"].get(channel)
    if not chan:
        die(f"Unknown channel: {channel}. Valid: {list(cfg['channels'].keys())}")
    channel_id = chan["channel_id"]
    if "REPLACE" in str(channel_id):
        die(f"channel_id for #{channel} is still a placeholder. Edit {CONFIG_PATH}.")

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        r.raise_for_status()
    except httpx.HTTPError as e:
        body = getattr(e, "response", None)
        body = body.text if body is not None else ""
        die(f"Discord bot API failed: {e} body={body[:300]}", code=2)

    print(json.dumps({"ok": True, "channel": channel, "status": r.status_code, "via": "bot"}))


def color_for(channel):
    cfg = load_config()
    colors = cfg.get("colors", {})
    return colors.get({
        "approvals": "approval",
        "fills": "fill",
        "risk_alerts": "alert",
        "daily_brief": "brief",
        "chat": "info",
    }.get(channel, "info"), 10070709)


def cmd_send(channel, title, body):
    """Generic embed send."""
    payload = {
        "embeds": [{
            "title": title,
            "description": body,
            "color": color_for(channel),
            "timestamp": datetime.utcnow().isoformat(),
        }]
    }
    post(channel, payload)


def cmd_setup(setup_id, symbol, direction, entry, stop, target, size, rr, confidence, catalyst):
    """
    Approval-needed setup card. The bot reads setup_id from the message
    when a button is clicked, so this MUST be unique (e.g. NVDA-2026-05-11).
    """
    direction = direction.upper()
    color = color_for("approvals")
    payload = {
        "content": f"@here new setup needs approval: **{symbol}**",
        "embeds": [{
            "title": f"{symbol} — {direction} ({setup_id})",
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {"name": "Entry", "value": str(entry), "inline": True},
                {"name": "Stop", "value": str(stop), "inline": True},
                {"name": "Target", "value": str(target), "inline": True},
                {"name": "Size", "value": str(size), "inline": True},
                {"name": "R:R", "value": str(rr), "inline": True},
                {"name": "Confidence", "value": f"{confidence}/10", "inline": True},
                {"name": "Catalyst", "value": catalyst[:1024], "inline": False},
                {"name": "How to approve", "value": (
                    "Tap a button below, OR reply in #approvals with `approve "
                    f"{setup_id}` / `deny {setup_id} <reason>`, OR edit "
                    "memory/open_positions.md and add `Approved: YES` under this setup."
                ), "inline": False},
            ],
            "footer": {"text": f"setup_id={setup_id}"},
        }],
        # Buttons go in components. The bot listens via custom_id and dispatches.
        "components": [{
            "type": 1,  # action row
            "components": [
                {"type": 2, "style": 3, "label": "Approve",
                 "custom_id": f"approve:{setup_id}"},
                {"type": 2, "style": 4, "label": "Deny",
                 "custom_id": f"deny:{setup_id}"},
                {"type": 2, "style": 2, "label": "More info",
                 "custom_id": f"info:{setup_id}"},
            ],
        }],
    }
    # Setup cards have buttons → MUST go via bot, not webhook,
    # otherwise button clicks won't route back to the bot.
    post_as_bot("approvals", payload)


def cmd_fill(symbol, side, qty, price, order_id=None):
    """Trade fill confirmation."""
    side_emoji = "🟢" if side.lower() == "buy" else "🔴"
    fields = [
        {"name": "Symbol", "value": symbol, "inline": True},
        {"name": "Side", "value": side.upper(), "inline": True},
        {"name": "Qty", "value": str(qty), "inline": True},
        {"name": "Fill price", "value": f"${price}", "inline": True},
        {"name": "Notional", "value": f"${float(qty) * float(price):,.2f}", "inline": True},
    ]
    if order_id:
        fields.append({"name": "Order ID", "value": f"`{order_id}`", "inline": False})
    payload = {
        "embeds": [{
            "title": f"{side_emoji} {side.upper()} filled — {symbol}",
            "color": color_for("fills"),
            "timestamp": datetime.utcnow().isoformat(),
            "fields": fields,
        }]
    }
    post("fills", payload)


def cmd_alert(severity, topic, message):
    """Risk/error alert. Posts to #risk-alerts. Tags @here for high+."""
    sev = severity.lower()
    icons = {"critical": "🚨", "high": "⚠️", "medium": "🔸", "low": "ℹ️"}
    icon = icons.get(sev, "ℹ️")
    content = "@here " if sev in ("critical", "high") else ""
    payload = {
        "content": f"{content}{icon} **{sev.upper()}** — {topic}",
        "embeds": [{
            "description": message,
            "color": color_for("risk_alerts"),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": f"severity={sev}"},
        }]
    }
    post("risk_alerts", payload)


def cmd_brief(routine, summary):
    """Routine summary. Posts to #daily-brief, silent."""
    payload = {
        "embeds": [{
            "title": f"{routine}",
            "description": summary[:4000],
            "color": color_for("daily_brief"),
            "timestamp": datetime.utcnow().isoformat(),
        }]
    }
    post("daily_brief", payload)


def cmd_dashboard():
    """
    Mirror Dashboard.md to a single pinned message in #daily-brief.
    First run: create message, pin it, save its ID. Subsequent runs: PATCH it.

    Discord message bodies cap at 2000 chars. The dashboard rarely exceeds
    that, but if it does we truncate with a pointer to the file in git.
    """
    if not BOT_TOKEN:
        die("DISCORD_BOT_TOKEN missing from .env — required to edit/pin a bot message.")
    if not DASHBOARD_PATH.exists():
        die(f"Dashboard.md not found at {DASHBOARD_PATH}. Run scripts/dashboard.py first.")

    cfg = load_config()
    chan = cfg["channels"].get("daily_brief")
    if not chan or "REPLACE" in str(chan.get("channel_id", "")):
        die("daily_brief channel_id missing or placeholder in discord_config.json")
    channel_id = chan["channel_id"]

    body = DASHBOARD_PATH.read_text()
    if len(body) > 1900:
        body = body[:1900].rsplit("\n", 1)[0] + "\n…\n_(truncated — see `Dashboard.md` in repo)_"
    payload = {"content": body}

    headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}
    api = "https://discord.com/api/v10"
    ref = json.loads(DASHBOARD_MSG_REF.read_text()) if DASHBOARD_MSG_REF.exists() else {}
    msg_id = ref.get("message_id")

    try:
        if msg_id:
            r = httpx.patch(f"{api}/channels/{channel_id}/messages/{msg_id}",
                            headers=headers, json=payload, timeout=10.0)
            if r.status_code == 404:
                msg_id = None  # message was deleted, fall through to recreate
            else:
                r.raise_for_status()
        if not msg_id:
            r = httpx.post(f"{api}/channels/{channel_id}/messages",
                           headers=headers, json=payload, timeout=10.0)
            r.raise_for_status()
            msg_id = r.json()["id"]
            # Pin it so it stays at top of channel.
            pin = httpx.put(f"{api}/channels/{channel_id}/pins/{msg_id}",
                            headers=headers, timeout=10.0)
            # Pinning may fail (max 50 pins per channel); not fatal.
            DASHBOARD_MSG_REF.write_text(json.dumps({
                "message_id": msg_id,
                "channel_id": channel_id,
                "pinned": pin.status_code in (200, 204),
            }, indent=2))
    except httpx.HTTPError as e:
        body = getattr(e, "response", None)
        body = body.text if body is not None else ""
        die(f"Dashboard mirror failed: {e} body={body[:300]}", code=2)

    print(json.dumps({"ok": True, "channel": "daily_brief", "message_id": msg_id, "via": "bot"}))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    a = sys.argv[2:]

    try:
        if cmd == "send":
            cmd_send(a[0], a[1], a[2])
        elif cmd == "setup":
            cmd_setup(*a[:10])
        elif cmd == "fill":
            cmd_fill(a[0], a[1], a[2], a[3], a[4] if len(a) > 4 else None)
        elif cmd == "alert":
            cmd_alert(a[0], a[1], a[2])
        elif cmd == "brief":
            cmd_brief(a[0], a[1])
        elif cmd == "dashboard":
            cmd_dashboard()
        else:
            print(f"Unknown command: {cmd}")
            print(__doc__)
            sys.exit(1)
    except IndexError:
        print(f"Missing arguments for `{cmd}`.")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
