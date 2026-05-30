#!/usr/bin/env python3
"""
Discord bot — inbound only. Listens for button clicks (Approve/Deny/Info)
on setup approval messages posted by notify.py.

When a button is clicked:
  1. Verify interaction.user.id matches authorized_user_id (only owner can act).
  2. Edit memory/open_positions.md to add Approved: YES (or NO + reason) under
     the matching setup_id.
  3. Append a log line to memory/discord_actions.log.
  4. Reply in-channel confirming the action.

The bot does NOT touch ClickUp directly. The existing polling routine
syncs memory/open_positions.md ↔ ClickUp, so changes propagate naturally.

Run:
    python3 scripts/discord_bot.py

Stop:
    kill the process (or unload launchd plist)
"""

import os
import sys
import json
import re
import logging
import subprocess
from datetime import datetime
from pathlib import Path

import discord
from discord import app_commands
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "memory" / "discord_config.json"
POSITIONS_PATH = ROOT / "memory" / "open_positions.md"
ACTION_LOG = ROOT / "memory" / "discord_actions.log"
WATCHLIST_PATH = ROOT / "memory" / "watchlist.json"
TRACKING_PATH = ROOT / "memory" / "tracking.json"
PAUSE_PATH = ROOT / "memory" / "pause_state.json"
RUN_QUEUE_PATH = ROOT / "memory" / "run_queue.json"
CHAT_QUEUE_PATH = ROOT / "memory" / "discord_chat_queue.json"
KNOWLEDGE_QUEUE_PATH = ROOT / "memory" / "knowledge_inbox_queue.json"
FEEDBACK_QUEUE_PATH = ROOT / "memory" / "feedback_queue.json"
DASHBOARD_PATH = ROOT / "Dashboard.md"
ALPACA_CLI = ROOT / "scripts" / "alpaca_client.py"
RESEARCH_CLI = ROOT / "scripts" / "research.py"
DASHBOARD_SCRIPT = ROOT / "scripts" / "dashboard.py"

VALID_ROUTINES = {"pre-market", "market-open", "midday", "eod", "weekly", "security"}

load_dotenv(ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("discord_bot")


def load_config():
    if not CONFIG_PATH.exists():
        log.error("Missing %s — copy from discord_config.example.json", CONFIG_PATH)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


CONFIG = load_config()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    log.error("DISCORD_BOT_TOKEN missing from .env")
    sys.exit(1)

AUTHORIZED_USER_ID = int(CONFIG["authorized_user_id"])
GUILD_ID = int(CONFIG["guild_id"])
GUILD_OBJ = discord.Object(id=GUILD_ID)
APPROVALS_CHANNEL_ID = int(CONFIG["channels"]["approvals"]["channel_id"])
RISK_CHANNEL_ID = int(CONFIG["channels"]["risk_alerts"]["channel_id"])


def _channel_id_or_none(name: str):
    """Return int channel_id for the named channel, or None if missing/placeholder."""
    chan = CONFIG.get("channels", {}).get(name)
    if not chan:
        return None
    cid = chan.get("channel_id", "")
    if not cid or "REPLACE" in str(cid):
        return None
    try:
        return int(cid)
    except (TypeError, ValueError):
        return None


KNOWLEDGE_INBOX_CHANNEL_ID = _channel_id_or_none("knowledge_inbox")
FEEDBACK_CHANNEL_ID = _channel_id_or_none("feedback")


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def append_action_log(line: str):
    with open(ACTION_LOG, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z  {line}\n")


def update_open_positions(setup_id: str, decision: str, reason: str = "") -> bool:
    """
    Find the setup with footer/marker `setup_id` in open_positions.md and
    add an `Approved: YES|NO` line. Returns True if a setup was matched.

    Matching strategy: setup_id is encoded as `SYMBOL-YYYY-MM-DD[-suffix]`.
    We try a few fallbacks because pre-market routines may format the
    Pending Setups section slightly differently across days.
    """
    if not POSITIONS_PATH.exists():
        log.warning("%s does not exist", POSITIONS_PATH)
        return False

    text = POSITIONS_PATH.read_text()
    symbol = setup_id.split("-")[0]

    flag = "YES" if decision == "approve" else "NO"
    stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%MZ")
    suffix = f" ({reason})" if reason else ""
    new_line = f"- Approved: {flag}  <!-- via Discord {stamp}{suffix} -->"

    # Strategy 1: a heading containing the symbol AND "setup_id={setup_id}" footer
    pattern_id = re.compile(
        rf"(### .*{re.escape(symbol)}.*?)(\n##|\Z)", re.DOTALL
    )

    def inject(match):
        block = match.group(1)
        # Replace existing Approved: line, or append before block end.
        if re.search(r"^- Approved:.*$", block, re.MULTILINE):
            block = re.sub(
                r"^- Approved:.*$",
                new_line,
                block,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            block = block.rstrip() + "\n" + new_line + "\n"
        return block + match.group(2)

    new_text, count = pattern_id.subn(inject, text, count=1)
    if count == 0:
        log.warning("No setup heading matched symbol=%s in open_positions.md", symbol)
        return False

    POSITIONS_PATH.write_text(new_text)
    return True


def authorized(interaction: discord.Interaction) -> bool:
    return interaction.user.id == AUTHORIZED_USER_ID


@client.event
async def on_ready():
    log.info("Logged in as %s (id=%s)", client.user, client.user.id)
    try:
        # Guild-scoped sync = instant. Global sync can take up to 1h.
        tree.copy_global_to(guild=GUILD_OBJ)
        synced = await tree.sync(guild=GUILD_OBJ)
        log.info("Synced %d slash commands to guild %s", len(synced), GUILD_ID)
    except Exception as e:
        log.warning("Slash command sync failed: %s", e)
    # Healthcheck ping so we know the bot came back alive.
    risk_ch = client.get_channel(RISK_CHANNEL_ID)
    if risk_ch:
        try:
            await risk_ch.send("ℹ️ Trading agent bot online.")
        except Exception as e:
            log.warning("Healthcheck post failed: %s", e)


@client.event
async def on_message(message: discord.Message):
    """
    Watch #knowledge-inbox and #feedback for new messages from the authorized
    user. Each match gets enqueued to a memory file for the dispatcher routine
    to drain and process. Bot's own messages and other users are ignored.
    """
    if message.author.id == client.user.id:
        return
    if message.author.id != AUTHORIZED_USER_ID:
        return  # ignore unauthorized users — same gate as slash commands

    payload = {
        "message_id": str(message.id),
        "channel_id": str(message.channel.id),
        "author_id": str(message.author.id),
        "received_at": datetime.utcnow().isoformat() + "Z",
        "content": message.content or "",
        "attachments": [
            {"filename": a.filename, "url": a.url, "size": a.size}
            for a in message.attachments
        ],
    }

    target = None
    if KNOWLEDGE_INBOX_CHANNEL_ID and message.channel.id == KNOWLEDGE_INBOX_CHANNEL_ID:
        target = ("knowledge_inbox", KNOWLEDGE_QUEUE_PATH)
    elif FEEDBACK_CHANNEL_ID and message.channel.id == FEEDBACK_CHANNEL_ID:
        target = ("feedback", FEEDBACK_QUEUE_PATH)

    if not target:
        return

    name, path = target
    try:
        data = json.loads(path.read_text()) if path.exists() else {"queue": []}
    except json.JSONDecodeError:
        data = {"queue": []}
    data.setdefault("queue", []).append(payload)
    path.write_text(json.dumps(data, indent=2))
    append_action_log(f"{name}_msg  msg_id={message.id}  attachments={len(payload['attachments'])}")
    try:
        await message.add_reaction("📥")  # ack so user sees it was queued
    except discord.HTTPException:
        pass


@client.event
async def on_interaction(interaction: discord.Interaction):
    """Handle button clicks. custom_id format: 'approve:SETUP_ID' / 'deny:SETUP_ID' / 'info:SETUP_ID'."""
    if interaction.type != discord.InteractionType.component:
        return

    cid = interaction.data.get("custom_id", "")
    if ":" not in cid:
        return
    action, setup_id = cid.split(":", 1)

    if not authorized(interaction):
        await interaction.response.send_message(
            "Not authorized.", ephemeral=True
        )
        log.warning(
            "Unauthorized click by user_id=%s on %s", interaction.user.id, cid
        )
        return

    if action == "approve":
        ok = update_open_positions(setup_id, "approve")
        msg = (
            f"✅ **Approved** `{setup_id}` — execution routine will pick this up at market open."
            if ok else
            f"⚠️ Approved `{setup_id}` in chat, but no matching setup found in `memory/open_positions.md`. Check the file manually."
        )
        append_action_log(f"approve  {setup_id}  matched={ok}")
        await interaction.response.send_message(msg)
        git_sync_memory(f"approve {setup_id}")

    elif action == "deny":
        ok = update_open_positions(setup_id, "deny", "denied via Discord")
        msg = (
            f"❌ **Denied** `{setup_id}`."
            if ok else
            f"⚠️ Denied `{setup_id}` in chat, but no matching setup found. Check `memory/open_positions.md`."
        )
        append_action_log(f"deny     {setup_id}  matched={ok}")
        await interaction.response.send_message(msg)
        git_sync_memory(f"deny {setup_id}")

    elif action == "info":
        # Pull the relevant section from open_positions.md and reply ephemerally.
        symbol = setup_id.split("-")[0]
        text = POSITIONS_PATH.read_text() if POSITIONS_PATH.exists() else ""
        m = re.search(
            rf"(### .*{re.escape(symbol)}.*?)(\n##|\n###|\Z)", text, re.DOTALL
        )
        snippet = m.group(1) if m else "_No matching section found in open_positions.md._"
        await interaction.response.send_message(
            f"```markdown\n{snippet[:1800]}\n```", ephemeral=True
        )
        append_action_log(f"info     {setup_id}")


@tree.command(name="ping", description="Healthcheck — replies pong if the bot is alive.")
async def ping(interaction: discord.Interaction):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    await interaction.response.send_message("pong", ephemeral=True)


@tree.command(name="approve", description="Approve a setup by ID (alternative to buttons).")
@app_commands.describe(setup_id="e.g. NVDA-2026-05-11")
async def approve_cmd(interaction: discord.Interaction, setup_id: str):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    ok = update_open_positions(setup_id, "approve")
    append_action_log(f"approve  {setup_id}  matched={ok}  (slash)")
    await interaction.response.send_message(
        f"{'✅' if ok else '⚠️'} approve `{setup_id}` (matched={ok})"
    )
    git_sync_memory(f"approve {setup_id} (slash)")


@tree.command(name="deny", description="Deny a setup by ID (alternative to buttons).")
@app_commands.describe(setup_id="e.g. NVDA-2026-05-11", reason="Optional reason")
async def deny_cmd(interaction: discord.Interaction, setup_id: str, reason: str = ""):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    ok = update_open_positions(setup_id, "deny", reason)
    append_action_log(f"deny     {setup_id}  matched={ok}  reason={reason}  (slash)")
    await interaction.response.send_message(
        f"{'❌' if ok else '⚠️'} deny `{setup_id}` (matched={ok})"
    )
    git_sync_memory(f"deny {setup_id} (slash)")


# ---------------------------------------------------------------------------
# Helpers shared by read-only and state-mutating slash commands.
# ---------------------------------------------------------------------------

def shell(*args, timeout: int = 30) -> tuple[int, str]:
    """Run a CLI script, return (rc, stdout). Stderr is folded into stdout."""
    try:
        out = subprocess.run(
            list(args), capture_output=True, text=True,
            timeout=timeout, check=False, cwd=str(ROOT),
        )
        body = (out.stdout or "") + (("\n" + out.stderr) if out.stderr else "")
        return out.returncode, body.strip()
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout}s"


def reply_block(text: str, lang: str = "") -> str:
    """Format text in a Discord code block, capped at 1900 chars."""
    if len(text) > 1900:
        text = text[:1900] + "\n…(truncated)"
    return f"```{lang}\n{text}\n```"


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2))


GIT_SYNC = ROOT / "scripts" / "git_sync.py"


def git_sync_memory(label: str) -> None:
    """Push memory file changes to GitHub so GHA routines see them.

    Only runs if GIT_SYNC script exists and a git remote is reachable.
    Failures are logged but never block the bot response.
    """
    try:
        rc, out = shell(
            sys.executable, str(GIT_SYNC), "sync",
            f"bot(discord): {label}",
            timeout=30,
        )
        if rc != 0:
            log.warning("git_sync failed (rc=%d): %s", rc, out[:200])
        else:
            log.info("git_sync ok: %s", label)
    except Exception as exc:
        log.warning("git_sync exception: %s", exc)


# ---------------------------------------------------------------------------
# Read-only utility commands.
# ---------------------------------------------------------------------------

@tree.command(name="dashboard", description="Show the current trading dashboard.")
async def dashboard_cmd(interaction: discord.Interaction):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)
    rc, _ = shell(sys.executable, str(DASHBOARD_SCRIPT))
    body = DASHBOARD_PATH.read_text() if DASHBOARD_PATH.exists() else "_Dashboard.md not found._"
    append_action_log(f"dashboard  rc={rc}")
    await interaction.followup.send(reply_block(body, "markdown"), ephemeral=True)


@tree.command(name="positions", description="List current open positions from Alpaca.")
async def positions_cmd(interaction: discord.Interaction):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)
    rc, body = shell(sys.executable, str(ALPACA_CLI), "positions")
    append_action_log(f"positions  rc={rc}")
    await interaction.followup.send(reply_block(body, "json"), ephemeral=True)


@tree.command(name="account", description="Show Alpaca account snapshot (equity, cash, P&L today, PDT count).")
async def account_cmd(interaction: discord.Interaction):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)
    rc, body = shell(sys.executable, str(ALPACA_CLI), "account")
    append_action_log(f"account  rc={rc}")
    await interaction.followup.send(reply_block(body, "json"), ephemeral=True)


@tree.command(name="scan", description="Run technical analysis on a single symbol.")
@app_commands.describe(symbol="Ticker, e.g. NVDA")
async def scan_cmd(interaction: discord.Interaction, symbol: str):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    sym = symbol.upper().strip()
    if not re.match(r"^[A-Z.\-]{1,8}$", sym):
        await interaction.response.send_message(f"⚠️ Invalid symbol `{symbol}`.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)
    rc, body = shell(sys.executable, str(RESEARCH_CLI), "analyze", sym, timeout=60)
    append_action_log(f"scan {sym}  rc={rc}")
    await interaction.followup.send(reply_block(body, "json"), ephemeral=True)


@tree.command(name="setups", description="Show pending setups from open_positions.md.")
async def setups_cmd(interaction: discord.Interaction):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    text = POSITIONS_PATH.read_text() if POSITIONS_PATH.exists() else ""
    m = re.search(r"## Pending Setups\s*(.*?)(?=^## |\Z)", text, re.DOTALL | re.MULTILINE)
    body = m.group(1).strip() if m else "_No Pending Setups section found._"
    append_action_log("setups")
    await interaction.response.send_message(reply_block(body, "markdown"), ephemeral=True)


# ---------------------------------------------------------------------------
# State-mutating commands.
# ---------------------------------------------------------------------------

@tree.command(name="pause", description="Pause new trade entries (closes still allowed).")
@app_commands.describe(reason="Optional reason for the pause")
async def pause_cmd(interaction: discord.Interaction, reason: str = ""):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    write_json(PAUSE_PATH, {
        "state": "paused",
        "reason": reason or "manual pause via Discord",
        "set_at": datetime.utcnow().isoformat() + "Z",
    })
    append_action_log(f"pause  reason={reason}")
    await interaction.response.send_message(f"⏸️ Trading paused. Reason: {reason or '(none)'}")
    git_sync_memory("pause")


@tree.command(name="resume", description="Resume normal trading after a pause.")
async def resume_cmd(interaction: discord.Interaction):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    write_json(PAUSE_PATH, {
        "state": "active",
        "reason": "",
        "set_at": datetime.utcnow().isoformat() + "Z",
    })
    append_action_log("resume")
    await interaction.response.send_message("🟢 Trading resumed.")
    git_sync_memory("resume")


@tree.command(name="halt", description="Full halt: skip ALL trading routines until /resume.")
@app_commands.describe(reason="Why the halt — required for the audit trail")
async def halt_cmd(interaction: discord.Interaction, reason: str):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    write_json(PAUSE_PATH, {
        "state": "halted",
        "reason": reason,
        "set_at": datetime.utcnow().isoformat() + "Z",
    })
    append_action_log(f"halt  reason={reason}")
    await interaction.response.send_message(f"🛑 **HALTED** — {reason}")
    git_sync_memory(f"halt reason={reason}")


@tree.command(name="track", description="Pin a symbol for short-term follow-up (5-day expiry). /track add|remove|show")
@app_commands.describe(
    action="add | remove | show",
    symbol="Ticker (required for add/remove)",
    notes="Optional notes about why you're tracking",
)
async def track_cmd(
    interaction: discord.Interaction,
    action: str,
    symbol: str = "",
    notes: str = "",
):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    action = action.lower().strip()
    sym = symbol.upper().strip()
    data = read_json(TRACKING_PATH, {"symbols": [], "last_updated": ""})
    items = data.setdefault("symbols", [])

    if action == "show":
        body = "\n".join(
            f"- {i.get('symbol')} (until {i.get('tracked_until','?')}) — {i.get('notes','')[:80]}"
            for i in items
        )
        await interaction.response.send_message(reply_block(body or "_empty_", "markdown"), ephemeral=True)
        return

    if not sym:
        await interaction.response.send_message("⚠️ symbol required for add/remove.", ephemeral=True)
        return

    if action == "add":
        if any(i.get("symbol") == sym for i in items):
            await interaction.response.send_message(f"`{sym}` already being tracked.", ephemeral=True)
            return
        # 5 trading days ≈ 7 calendar days
        import datetime as _dt
        tracked_until = (_dt.date.today() + _dt.timedelta(days=7)).isoformat()
        items.append({"symbol": sym, "notes": notes, "tracked_until": tracked_until,
                      "added": _dt.date.today().isoformat()})
        data["last_updated"] = _dt.date.today().isoformat()
        write_json(TRACKING_PATH, data)
        append_action_log(f"track add {sym} until={tracked_until}")
        await interaction.response.send_message(f"📌 Tracking `{sym}` until {tracked_until}.")
        git_sync_memory(f"track add {sym}")
        return

    if action == "remove":
        before = len(items)
        data["symbols"] = [i for i in items if i.get("symbol") != sym]
        if len(data["symbols"]) == before:
            await interaction.response.send_message(f"`{sym}` not in tracking list.", ephemeral=True)
            return
        import datetime as _dt
        data["last_updated"] = _dt.date.today().isoformat()
        write_json(TRACKING_PATH, data)
        append_action_log(f"track remove {sym}")
        await interaction.response.send_message(f"🗑️ Removed `{sym}` from tracking.")
        git_sync_memory(f"track remove {sym}")
        return

    await interaction.response.send_message(f"Unknown action `{action}`. Use add | remove | show.", ephemeral=True)


@tree.command(name="run", description="Queue a routine for the next dispatcher tick.")
@app_commands.describe(routine="pre-market | market-open | midday | eod | weekly | security")
async def run_cmd(interaction: discord.Interaction, routine: str):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    r = routine.lower().strip()
    if r not in VALID_ROUTINES:
        await interaction.response.send_message(
            f"⚠️ Unknown routine `{routine}`. Valid: {sorted(VALID_ROUTINES)}", ephemeral=True
        )
        return
    data = read_json(RUN_QUEUE_PATH, {"queue": []})
    data.setdefault("queue", []).append({
        "routine": r,
        "queued_at": datetime.utcnow().isoformat() + "Z",
        "queued_by": str(interaction.user.id),
    })
    write_json(RUN_QUEUE_PATH, data)
    append_action_log(f"run  routine={r}")
    await interaction.response.send_message(
        f"📋 Queued `{r}` — the dispatcher will pick it up on the next tick (≤15 min)."
    )
    git_sync_memory(f"run queue {r}")


@tree.command(name="ask", description="Ask the agent a question (queued; answer arrives in #chat).")
@app_commands.describe(question="Your question")
async def ask_cmd(interaction: discord.Interaction, question: str):
    if not authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    data = read_json(CHAT_QUEUE_PATH, {"queue": []})
    data.setdefault("queue", []).append({
        "question": question,
        "queued_at": datetime.utcnow().isoformat() + "Z",
        "queued_by": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
    })
    write_json(CHAT_QUEUE_PATH, data)
    append_action_log(f"ask  q={question[:80]}")
    await interaction.response.send_message(
        f"📨 Question queued. The next routine cycle will answer in `#chat`.\n> {question[:200]}"
    )
    git_sync_memory(f"ask queue")


def main():
    client.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
