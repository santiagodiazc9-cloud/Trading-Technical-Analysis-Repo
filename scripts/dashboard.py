#!/usr/bin/env python3
"""
Dashboard generator — single source-of-truth view of the trading agent's state.

Renders Dashboard.md at the vault root. Reads Alpaca (live) + memory/* (files).
Called by every routine at end-of-run; also callable on demand via
`/dashboard` slash command (which renders this same file inline).

Usage:
    python3 scripts/dashboard.py            # regenerate Dashboard.md
    python3 scripts/dashboard.py --stdout   # also print to stdout
    python3 scripts/dashboard.py --json     # emit a JSON payload (for scripting)

If Alpaca is unreachable (sandbox / network blocked), the dashboard still
renders from local files and notes the gap in a "Live data unavailable"
section.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_PATH = ROOT / "Dashboard.md"
ALPACA_CLI = ROOT / "scripts" / "alpaca_client.py"

MEMORY = ROOT / "memory"
TRADE_LOG = MEMORY / "trade_log.json"
OPEN_POSITIONS = MEMORY / "open_positions.md"
SECTOR_BLOCKLIST = MEMORY / "sector_blocklist.md"
LEARNINGS = MEMORY / "learnings.md"
WATCHLIST = MEMORY / "watchlist.json"
PAUSE_STATE = MEMORY / "pause_state.json"
RUN_QUEUE = MEMORY / "run_queue.json"


def run_alpaca(*args):
    """Call alpaca_client.py and parse JSON stdout. Returns None on failure."""
    try:
        out = subprocess.run(
            ["python3", str(ALPACA_CLI), *args],
            capture_output=True, text=True, timeout=15, check=False,
        )
        if out.returncode != 0:
            return None
        return json.loads(out.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def read_text(path: Path, default=""):
    try:
        return path.read_text()
    except FileNotFoundError:
        return default


def parse_pending_setups(positions_md: str):
    """Extract Pending Setups section as a list of dicts (heading + Approved flag)."""
    m = re.search(r"## Pending Setups\s*(.*?)(?=^## |\Z)", positions_md, re.DOTALL | re.MULTILINE)
    if not m:
        return []
    section = m.group(1)
    setups = []
    for block in re.split(r"\n### ", section):
        block = block.strip()
        if not block or block.startswith("Watchlist Only"):
            continue
        first_line = block.splitlines()[0].lstrip("# ").strip()
        approved = "YES" if re.search(r"^- ?Approved:\s*YES", block, re.MULTILINE) else (
            "NO" if re.search(r"^- ?Denied:\s*YES", block, re.MULTILINE) else "AWAITING"
        )
        setups.append({"heading": first_line, "approved": approved})
    return setups


def parse_blocked_sectors(blocklist_md: str):
    m = re.search(r"## Currently Blocked\s*(.*?)(?=^## |\Z)", blocklist_md, re.DOTALL | re.MULTILINE)
    if not m:
        return []
    body = m.group(1).strip()
    if not body or "_None._" in body:
        return []
    return [line.strip("- ").strip() for line in body.splitlines() if line.strip().startswith("-")]


def tail_learnings(learnings_md: str, n: int = 3) -> list[str]:
    """Most recent date-stamped learnings sections, newest first."""
    sections = re.split(r"^## ", learnings_md, flags=re.MULTILINE)
    dated = [s for s in sections if re.match(r"\d{4}-\d{2}-\d{2}", s.lstrip())]
    dated.sort(key=lambda s: s.lstrip()[:10], reverse=True)
    out = []
    for s in dated[:n]:
        line = s.strip().splitlines()[0]
        out.append(line[:120])
    return out


def format_money(x) -> str:
    if x is None:
        return "—"
    try:
        return f"${float(x):,.2f}"
    except (TypeError, ValueError):
        return str(x)


def format_pct(x) -> str:
    if x is None:
        return "—"
    try:
        return f"{float(x):+.2f}%"
    except (TypeError, ValueError):
        return str(x)


def collect_state() -> dict:
    """Pull together everything needed to render the dashboard."""
    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "live_data_available": True,
    }

    account = run_alpaca("account")
    positions = run_alpaca("positions")
    clock = run_alpaca("clock")
    if account is None or positions is None:
        state["live_data_available"] = False
    state["account"] = account or {}
    state["positions"] = positions or []
    state["clock"] = clock or {}

    trade_log = read_json(TRADE_LOG, {})
    state["trade_log"] = trade_log
    state["weekly_trade_count"] = trade_log.get("weekly_trade_count", {})
    state["summary"] = trade_log.get("summary", {})
    state["recent_trades"] = trade_log.get("trades", [])[-5:]

    state["pending_setups"] = parse_pending_setups(read_text(OPEN_POSITIONS))
    state["blocked_sectors"] = parse_blocked_sectors(read_text(SECTOR_BLOCKLIST))
    state["recent_learnings"] = tail_learnings(read_text(LEARNINGS))

    state["watchlist"] = read_json(WATCHLIST, {}).get("watchlist", [])
    state["pause"] = read_json(PAUSE_STATE, {"state": "active"})
    state["run_queue"] = read_json(RUN_QUEUE, {"queue": []}).get("queue", [])

    return state


def render(state: dict) -> str:
    lines = []
    push = lines.append

    push("# Trading Agent Dashboard")
    push(f"_Generated {state['generated_at']} — auto-regenerated by every routine; rebuild on demand with `/dashboard`._")
    push("")

    pause = state["pause"].get("state", "active")
    pause_emoji = {"active": "🟢", "paused": "⏸️", "halted": "🛑"}.get(pause, "❓")
    push(f"**Status**: {pause_emoji} `{pause}`")
    if state["clock"]:
        push(f"**Market**: {'OPEN' if state['clock'].get('is_open') else 'CLOSED'} (next open: {state['clock'].get('next_open', '—')})")
    if not state["live_data_available"]:
        push("> ⚠️ **Live Alpaca data unavailable** — values below are from local files only.")
    push("")

    acct = state["account"]
    push("## Account")
    if acct:
        equity = acct.get("equity")
        cash = acct.get("cash")
        deployed = acct.get("deployed_pct")
        pnl_today = acct.get("pnl_today")
        dt_count = acct.get("daytrade_count")
        push("| Metric | Value |")
        push("|---|---|")
        push(f"| Equity | {format_money(equity)} |")
        push(f"| Cash | {format_money(cash)} |")
        push(f"| Buying Power | {format_money(acct.get('buying_power'))} |")
        push(f"| Deployed | {deployed}% (target 75–85%) |")
        push(f"| P&L today | {format_money(pnl_today)} |")
        push(f"| Day-trade count | {dt_count}/3 (PDT 5-day rolling) |")
    else:
        push("_No live account data._")
    push("")

    push("## Open Positions")
    if state["positions"]:
        push("| Symbol | Side | Qty | Entry | Now | Unrealized $ | Unrealized % |")
        push("|---|---|---|---|---|---|---|")
        for p in state["positions"]:
            push(
                f"| {p['symbol']} | {p['side']} | {p['qty']} | "
                f"{format_money(p['avg_entry'])} | {format_money(p['current_price'])} | "
                f"{format_money(p['unrealized_pnl'])} | {format_pct(p['unrealized_pnl_pct'])} |"
            )
    else:
        push("_No open positions._")
    push("")

    push("## Pending Setups")
    if state["pending_setups"]:
        for s in state["pending_setups"]:
            badge = {"YES": "✅ APPROVED", "NO": "❌ DENIED", "AWAITING": "⏳ AWAITING"}[s["approved"]]
            push(f"- {badge} — {s['heading']}")
    else:
        push("_No pending setups._")
    push("")

    push("## Risk State")
    weekly = {k: v for k, v in state["weekly_trade_count"].items() if not k.startswith("_")}
    week_summary = ", ".join(f"{k}={v}" for k, v in weekly.items()) or "none"
    push(f"- Trades this week: {week_summary} (max 3/wk)")
    blocked = state["blocked_sectors"]
    push(f"- Blocked sectors: {', '.join(blocked) if blocked else 'none'}")
    push(f"- Daily loss cap: -2% of equity (live equity {format_money((acct or {}).get('equity'))})")
    if state["pause"].get("reason"):
        push(f"- Pause reason: {state['pause']['reason']}")
    push("")

    push("## Recent Trades (last 5)")
    if state["recent_trades"]:
        for t in state["recent_trades"]:
            push(f"- {t}")
    else:
        push("_No trades logged yet._")
    push("")

    push("## Recent Learnings")
    if state["recent_learnings"]:
        for line in state["recent_learnings"]:
            push(f"- {line}")
    else:
        push("_No learnings yet._")
    push("")

    push("## Run Queue")
    if state["run_queue"]:
        for item in state["run_queue"][-5:]:
            push(f"- {item}")
    else:
        push("_Empty._")
    push("")

    summary = state["summary"]
    if summary:
        push("## All-Time Summary")
        push(f"- Total trades: {summary.get('total_trades', 0)}")
        push(f"- Wins / Losses: {summary.get('wins', 0)} / {summary.get('losses', 0)}")
        push(f"- Win rate: {summary.get('win_rate', '—')}")
        push(f"- Phase P&L: {format_money(summary.get('phase_pnl'))} ({summary.get('phase_pnl_pct', 0)}%)")
        push(f"- Current equity: {format_money(summary.get('current_equity'))}")
        push("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    args = set(sys.argv[1:])
    state = collect_state()

    if "--json" in args:
        print(json.dumps(state, indent=2, default=str))
        return

    md = render(state)
    DASHBOARD_PATH.write_text(md)

    if "--stdout" in args:
        sys.stdout.write(md)

    print(json.dumps({
        "ok": True,
        "path": str(DASHBOARD_PATH),
        "live": state["live_data_available"],
        "positions": len(state["positions"]),
        "pending_setups": len(state["pending_setups"]),
    }))


if __name__ == "__main__":
    main()
