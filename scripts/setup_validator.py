#!/usr/bin/env python3
"""
Setup validator — price-based expiration check for memory/open_positions.md.

Reads the "Pending Setups" section, parses each setup's entry zone / stop /
target, fetches the current price via scripts/alpaca_client.py, and reports
which setups have become invalid (price has overshot the target without
filling, or blown through the stop without filling).

CLI:
    python3 scripts/setup_validator.py check-all
        → JSON list of all pending setups + verdict for each

    python3 scripts/setup_validator.py check <SETUP_ID_OR_SYMBOL>
        → JSON verdict for a single setup (matched by setup_id or symbol)

    python3 scripts/setup_validator.py archive-invalid
        → mutate memory/open_positions.md to move invalid setups from
          "Pending Setups" to "Expired Setups". Emits JSON describing what
          was archived. The calling routine is responsible for posting a
          Discord risk-alert per archived setup if desired.

Validity rules (current_price vs setup fields):
    LONG:  invalid if current > target_high * 1.02  (TARGET_OVERSHOT)
           invalid if current < stop * 0.95         (STOP_BLOWN)
    SHORT: invalid if current < target_low * 0.98   (TARGET_OVERSHOT)
           invalid if current > stop * 1.05         (STOP_BLOWN)

Missing data is permissive: a setup with no parseable direction/zone returns
valid=True (the human routines remain the authority). The validator only
flags clear-cut staleness.
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSITIONS_PATH = PROJECT_ROOT / "memory" / "open_positions.md"
ALPACA_CLI = PROJECT_ROOT / "scripts" / "alpaca_client.py"

LONG_TARGET_OVERSHOOT_MULT = 1.02
LONG_STOP_BREAK_MULT = 0.95
SHORT_TARGET_OVERSHOOT_MULT = 0.98
SHORT_STOP_BREAK_MULT = 1.05


def latest_close(symbol: str) -> Optional[float]:
    """Fetch latest daily close via alpaca_client.py price <SYMBOL>."""
    try:
        result = subprocess.run(
            [sys.executable, str(ALPACA_CLI), "price", symbol],
            capture_output=True, text=True, timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    close = data.get("close")
    if close is None:
        return None
    try:
        return float(close)
    except (TypeError, ValueError):
        return None


def _parse_money_range(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Extract two dollar values from text like '$206.00–$210.00' or '$206-210'."""
    nums = re.findall(r"(\d+(?:\.\d+)?)", text)
    if not nums:
        return None, None
    if len(nums) == 1:
        v = float(nums[0])
        return v, v
    return float(nums[0]), float(nums[1])


def _parse_money_single(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None


def _parse_setup_block(block: str) -> Optional[dict]:
    """Extract structured fields from one Pending Setup block. Returns None on parse failure."""
    json_match = re.search(r"<!--\s*setup-data:json\s*(\{.*?\})\s*-->", block, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            data["_source"] = "json_block"
            data["approved"] = bool(re.search(r"^-\s*Approved:\s*YES", block, re.MULTILINE))
            data.setdefault("raw_block", block)
            return data
        except json.JSONDecodeError:
            pass

    heading = block.splitlines()[0].lstrip("# ").strip()
    symbol_match = re.search(r"\b([A-Z]{2,5})\b", heading)
    if not symbol_match:
        return None
    symbol = symbol_match.group(1)

    direction_match = re.search(r"^-\s*Direction:\s*(LONG|SHORT)", block, re.MULTILINE | re.IGNORECASE)
    direction = direction_match.group(1).upper() if direction_match else None

    entry_match = re.search(r"^-\s*Entry Zone:\s*([^\n]+)", block, re.MULTILINE)
    entry_low, entry_high = _parse_money_range(entry_match.group(1)) if entry_match else (None, None)

    stop_match = re.search(r"^-\s*Stop-?Loss:\s*([^\n]+)", block, re.MULTILINE)
    stop = _parse_money_single(stop_match.group(1)) if stop_match else None

    target_match = re.search(r"^-\s*Target:\s*([^\n]+)", block, re.MULTILINE)
    target_low, target_high = _parse_money_range(target_match.group(1)) if target_match else (None, None)

    approved = bool(re.search(r"^-\s*Approved:\s*YES", block, re.MULTILINE))

    return {
        "_source": "prose",
        "heading": heading,
        "setup_id": symbol,
        "symbol": symbol,
        "direction": direction,
        "entry_low": entry_low,
        "entry_high": entry_high,
        "stop": stop,
        "target_low": target_low,
        "target_high": target_high,
        "approved": approved,
        "raw_block": block,
    }


def parse_pending_setups(text: str) -> list[dict]:
    """Return list of parsed setup records from the Pending Setups section."""
    m = re.search(r"## Pending Setups\s*(.*?)(?=^## |\Z)", text, re.DOTALL | re.MULTILINE)
    if not m:
        return []
    section = m.group(1)
    setups: list[dict] = []
    for block in re.split(r"\n### ", section):
        block = block.strip()
        if not block:
            continue
        if block.startswith("Watchlist Only"):
            continue
        first_line = block.splitlines()[0].lstrip("# ").strip()
        if first_line.rstrip(".") in ("", "None", "none"):
            continue
        if not block.startswith("### "):
            block = "### " + block
        record = _parse_setup_block(block)
        if record:
            setups.append(record)
    return setups


def validate(setup: dict, current_price: float) -> Tuple[bool, str]:
    direction = (setup.get("direction") or "").upper()
    if direction not in ("LONG", "SHORT"):
        return True, "UNKNOWN_DIRECTION"

    if direction == "LONG":
        target_high = setup.get("target_high")
        stop = setup.get("stop")
        if target_high and current_price > target_high * LONG_TARGET_OVERSHOOT_MULT:
            return False, "TARGET_OVERSHOT"
        if stop and current_price < stop * LONG_STOP_BREAK_MULT:
            return False, "STOP_BLOWN"
    else:
        target_low = setup.get("target_low")
        stop = setup.get("stop")
        if target_low and current_price < target_low * SHORT_TARGET_OVERSHOOT_MULT:
            return False, "TARGET_OVERSHOT"
        if stop and current_price > stop * SHORT_STOP_BREAK_MULT:
            return False, "STOP_BLOWN"

    return True, "OK"


def check_one(setup: dict) -> dict:
    symbol = setup.get("symbol")
    setup_id = setup.get("setup_id", symbol or "unknown")
    if not symbol:
        return {"setup_id": setup_id, "valid": False, "reason": "PARSE_ERROR", "current_price": None}

    price = latest_close(symbol)
    if price is None:
        return {
            "setup_id": setup_id,
            "symbol": symbol,
            "valid": True,
            "reason": "PRICE_UNAVAILABLE",
            "current_price": None,
        }

    valid, reason = validate(setup, price)
    return {
        "setup_id": setup_id,
        "symbol": symbol,
        "direction": setup.get("direction"),
        "approved": setup.get("approved"),
        "valid": valid,
        "reason": reason,
        "current_price": price,
        "source": setup.get("_source"),
    }


def cmd_check_all() -> None:
    text = POSITIONS_PATH.read_text()
    setups = parse_pending_setups(text)
    results = [check_one(s) for s in setups]
    print(json.dumps({"count": len(results), "results": results}, indent=2))


def cmd_check(identifier: str) -> None:
    text = POSITIONS_PATH.read_text()
    setups = parse_pending_setups(text)
    target_symbol = identifier.split("-")[0].upper()
    matches = [
        s for s in setups
        if s.get("setup_id") == identifier or s.get("symbol") == target_symbol
    ]
    if not matches:
        print(json.dumps({"ok": False, "error": f"no pending setup matched {identifier}"}))
        sys.exit(1)
    results = [check_one(s) for s in matches]
    print(json.dumps(results[0] if len(results) == 1 else results, indent=2))


def cmd_archive_invalid() -> None:
    text = POSITIONS_PATH.read_text()
    setups = parse_pending_setups(text)
    archived: list[dict] = []
    new_text = text
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for setup in setups:
        verdict = check_one(setup)
        if verdict["valid"]:
            continue

        raw = setup["raw_block"]
        new_text = new_text.replace("\n" + raw, "", 1)
        expired_lines = raw.splitlines()
        if expired_lines:
            expired_lines[0] = expired_lines[0] + f" — EXPIRED {today}"
        expired_lines.append(
            f"- **Expiration reason**: {verdict['reason']} "
            f"(current_price={verdict['current_price']}; auto-archived by setup_validator)"
        )
        expired_block = "\n".join(expired_lines)

        if "## Expired Setups" in new_text:
            new_text = new_text.replace(
                "## Expired Setups",
                "## Expired Setups\n\n" + expired_block + "\n",
                1,
            )
        else:
            pending_re = re.compile(r"(## Pending Setups[\s\S]*?)(\n## )", re.MULTILINE)
            replacement = r"\1\n## Expired Setups\n\n" + expired_block + r"\n\2"
            new_text, n = pending_re.subn(replacement, new_text, count=1)
            if n == 0:
                new_text += "\n## Expired Setups\n\n" + expired_block + "\n"

        archived.append(verdict)

    if archived:
        POSITIONS_PATH.write_text(new_text)

    print(json.dumps({"archived_count": len(archived), "archived": archived}, indent=2))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "check-all":
        cmd_check_all()
    elif cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: setup_validator.py check <setup_id_or_symbol>", file=sys.stderr)
            sys.exit(1)
        cmd_check(sys.argv[2])
    elif cmd == "archive-invalid":
        cmd_archive_invalid()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
