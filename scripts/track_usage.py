#!/usr/bin/env python3
"""
Append a token usage record to memory/token_usage.json after each routine run.

Usage:
    python3 scripts/track_usage.py <routine_name> <exit_code> [<elapsed_seconds>]

Estimates token usage by routine type since Claude Code CLI in -p mode
doesn't expose raw token counts in a machine-parseable format.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USAGE_FILE = ROOT / "memory" / "token_usage.json"

# Estimated token usage per routine (input + output, based on observed runs)
ROUTINE_ESTIMATES = {
    "1_pre_market_research":   {"input": 110_000, "output": 4_500},
    "2_market_open_execution": {"input":  55_000, "output": 2_000},
    "3_midday_scan":           {"input":  65_000, "output": 2_500},
    "4_end_of_day_review":     {"input":  70_000, "output": 3_000},
    "5_weekly_review":         {"input": 130_000, "output": 5_000},
    "6_discord_dispatcher":    {"input":  20_000, "output":   800},
}

# Anthropic Sonnet 4.6 pricing (USD per token)
INPUT_PRICE  = 3.0  / 1_000_000   # $3/M input
OUTPUT_PRICE = 15.0 / 1_000_000   # $15/M output


def load() -> dict:
    try:
        return json.loads(USAGE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"sessions": [], "totals": {"input_tokens": 0, "output_tokens": 0,
                                           "cost_usd": 0.0, "run_count": 0}}


def save(data: dict) -> None:
    USAGE_FILE.write_text(json.dumps(data, indent=2))


def main():
    routine_path = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    exit_code    = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    elapsed      = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    routine_name = Path(routine_path).stem  # e.g. "1_pre_market_research"
    estimates = ROUTINE_ESTIMATES.get(routine_name,
                                      {"input": 60_000, "output": 2_500})

    input_tok  = estimates["input"]
    output_tok = estimates["output"]
    cost       = input_tok * INPUT_PRICE + output_tok * OUTPUT_PRICE

    record = {
        "timestamp":    datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "routine":      routine_name,
        "status":       "ok" if exit_code == 0 else "failed",
        "input_tokens": input_tok,
        "output_tokens": output_tok,
        "cost_usd":     round(cost, 4),
        "elapsed_s":    elapsed,
        "source":       "estimated",
    }

    data = load()
    data["sessions"].append(record)
    # Keep last 200 sessions
    data["sessions"] = data["sessions"][-200:]

    t = data["totals"]
    t["input_tokens"]  += input_tok
    t["output_tokens"] += output_tok
    t["cost_usd"]       = round(t.get("cost_usd", 0) + cost, 4)
    t["run_count"]      = t.get("run_count", 0) + 1

    save(data)
    print(json.dumps({"ok": True, "cost_usd": round(cost, 4), "routine": routine_name}))


if __name__ == "__main__":
    main()
