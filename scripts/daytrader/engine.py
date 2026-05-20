#!/usr/bin/env python3
"""
Day trading engine. Polls every 5 minutes during market hours (9:35–3:40 ET).
Combines candlestick patterns, mean-reversion, and ML confidence into a composite
score; places paper trades when score exceeds threshold AND session is approved.

Usage:
    python3 scripts/daytrader/engine.py              # live paper trading
    python3 scripts/daytrader/engine.py --dry-run    # score without trading
    python3 scripts/daytrader/engine.py --once       # single poll then exit
"""

import sys
import os
import json
import time
import argparse
import subprocess
from datetime import datetime, timezone

import pytz

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from scripts.research import get_bars, compute_indicators
from scripts.daytrader import patterns, mean_reversion, ml_model

ET = pytz.timezone("America/New_York")

SESSION_FILE = os.path.join(ROOT, "memory", "daytrader_session.json")
POSITIONS_FILE = os.path.join(ROOT, "memory", "open_positions.md")

LONG_THRESHOLD = 0.55   # composite score > this → consider long
SHORT_THRESHOLD = -0.55  # composite score < this → consider short
POLL_INTERVAL_SEC = 300  # 5 minutes


# ── session state ───────────────────────────────────────────────────────────

def load_session() -> dict:
    if not os.path.exists(SESSION_FILE):
        return {"session_approved": False, "max_trades": 2,
                "max_loss_usd": 500, "trades_taken": 0, "loss_usd": 0.0}
    with open(SESSION_FILE) as f:
        return json.load(f)


def save_session(state: dict):
    with open(SESSION_FILE, "w") as f:
        json.dump(state, f, indent=2)


def session_budget_ok(session: dict) -> bool:
    return (
        session.get("session_approved", False)
        and session.get("trades_taken", 0) < session.get("max_trades", 2)
        and session.get("loss_usd", 0.0) < session.get("max_loss_usd", 500)
    )


# ── market hours ────────────────────────────────────────────────────────────

def market_is_open() -> bool:
    now_et = datetime.now(ET)
    if now_et.weekday() >= 5:
        return False
    open_t = now_et.replace(hour=9, minute=35, second=0, microsecond=0)
    close_t = now_et.replace(hour=15, minute=40, second=0, microsecond=0)
    return open_t <= now_et <= close_t


# ── watchlist ───────────────────────────────────────────────────────────────

def get_day_symbols() -> list[str]:
    wl_path = os.path.join(ROOT, "memory", "watchlist.json")
    with open(wl_path) as f:
        wl = json.load(f)
    return [
        s["symbol"] for s in wl["watchlist"]
        if s.get("strategy") in ("day", "both")
    ]


# ── score one symbol ─────────────────────────────────────────────────────────

def score_symbol(symbol: str) -> dict:
    """
    Returns dict with keys: symbol, composite, direction, pattern_score,
    mr_score, ml_prob, pattern_names, error.
    """
    try:
        df = get_bars(symbol, "5Min", days_back=5)
        if df.empty or len(df) < 30:
            return {"symbol": symbol, "error": f"only {len(df)} bars"}

        df = compute_indicators(df)

        pattern_score, pattern_names = patterns.score_all(df)
        mr_score = mean_reversion.score(df)
        ml_prob = ml_model.predict(symbol, df)

        # mean_reversion score: positive = above VWAP (bearish lean)
        # We invert it so positive = bullish mean-reversion signal
        mr_bullish = -mr_score

        # ML prob: 0.5 = neutral; map to [-0.5, 0.5] then scale
        ml_signal = (ml_prob - 0.5) * 2.0  # [-1, 1]

        composite = (0.35 * pattern_score) + (0.30 * mr_bullish) + (0.35 * ml_signal)
        composite = round(composite, 4)

        direction = "LONG" if composite > LONG_THRESHOLD else (
            "SHORT" if composite < SHORT_THRESHOLD else "NEUTRAL"
        )

        return {
            "symbol": symbol,
            "composite": composite,
            "direction": direction,
            "pattern_score": pattern_score,
            "mr_score": mr_score,
            "ml_prob": ml_prob,
            "pattern_names": pattern_names,
            "price": round(float(df.iloc[-1]["close"]), 2),
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


# ── order helpers ────────────────────────────────────────────────────────────

def get_open_positions() -> set[str]:
    """Return symbols currently held (read from Alpaca)."""
    try:
        result = subprocess.run(
            ["python3", os.path.join(ROOT, "scripts", "alpaca_client.py"), "positions"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        if isinstance(data, list):
            return {p["symbol"] for p in data}
        return set()
    except Exception:
        return set()


def place_order(symbol: str, direction: str, price: float, dry_run: bool = False) -> dict:
    """Size a market order at 10% of ~$100k notional ($10k per trade, capped at $20k)."""
    account_equity = 100_000
    size_pct = 0.10
    notional = min(account_equity * size_pct, 20_000)
    qty = max(1, int(notional / price))

    action = "buy" if direction == "LONG" else "sell_short"

    if dry_run:
        return {"dry_run": True, "symbol": symbol, "action": action, "qty": qty, "price": price}

    result = subprocess.run(
        ["python3", os.path.join(ROOT, "scripts", "alpaca_client.py"),
         action, symbol, str(qty), "market"],
        capture_output=True, text=True, timeout=20
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"error": result.stderr or result.stdout}


def post_discord_fill(symbol: str, direction: str, qty: int, price: float):
    try:
        setup_id = f"{symbol}-{datetime.now(ET).strftime('%Y-%m-%d')}-daytrade"
        action = "buy" if direction == "LONG" else "sell_short"
        subprocess.run(
            ["python3", os.path.join(ROOT, "scripts", "notify.py"),
             "fill", symbol, action, str(qty), str(price), setup_id],
            timeout=10, capture_output=True
        )
    except Exception:
        pass


# ── main poll loop ────────────────────────────────────────────────────────────

def poll(dry_run: bool = False) -> list[dict]:
    symbols = get_day_symbols()
    open_positions = get_open_positions()
    session = load_session()
    results = []

    ts = datetime.now(ET).strftime("%H:%M ET")
    print(f"\n[{ts}] Polling {len(symbols)} symbols | "
          f"session_approved={session.get('session_approved')} | "
          f"trades_taken={session.get('trades_taken')}/{session.get('max_trades')}")

    for symbol in symbols:
        s = score_symbol(symbol)
        if s.get("error"):
            print(f"  {symbol}: ERROR — {s['error']}")
            continue

        direction = s["direction"]
        composite = s["composite"]
        patterns_hit = ", ".join(s["pattern_names"]) if s["pattern_names"] else "none"

        print(f"  {symbol}: {direction:7s} composite={composite:+.3f} "
              f"pattern={s['pattern_score']:+.2f} mr={s['mr_score']:+.2f} "
              f"ml={s['ml_prob']:.2f}  patterns=[{patterns_hit}]  price=${s['price']}")

        results.append(s)

        # Trade gate
        if direction == "NEUTRAL":
            continue
        if symbol in open_positions:
            continue
        if not session_budget_ok(session):
            if not session.get("session_approved"):
                pass  # silently skip — session not approved
            else:
                print(f"    → budget exhausted, skipping {symbol}")
            continue

        # Execute
        order = place_order(symbol, direction, s["price"], dry_run=dry_run)
        if order.get("dry_run"):
            print(f"    → DRY RUN: would {direction} {order['qty']} shares @ ${s['price']}")
        elif order.get("error"):
            print(f"    → ORDER ERROR: {order['error']}")
        else:
            qty = order.get("qty", "?")
            fill_price = order.get("filled_avg_price", s["price"])
            print(f"    → FILLED: {direction} {qty} {symbol} @ ${fill_price}")
            post_discord_fill(symbol, direction, qty, fill_price)
            session["trades_taken"] = session.get("trades_taken", 0) + 1
            save_session(session)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Score symbols and print signals without placing orders")
    parser.add_argument("--once", action="store_true",
                        help="Run a single poll loop then exit")
    args = parser.parse_args()

    if args.once or args.dry_run:
        poll(dry_run=args.dry_run or True if args.once else args.dry_run)
        return

    print("Day trading engine started. Polling every 5 min during market hours.")
    print("Set memory/daytrader_session.json {session_approved: true} to enable trading.\n")

    was_open = False
    while True:
        now_open = market_is_open()

        if now_open:
            was_open = True
            poll(dry_run=False)
        else:
            if was_open:
                # Market just closed — revoke session automatically
                session = load_session()
                if session.get("session_approved"):
                    session["session_approved"] = False
                    save_session(session)
                    print(f"[{datetime.now(ET).strftime('%H:%M ET')}] Market closed — session revoked automatically.")
                was_open = False
            else:
                print(f"[{datetime.now(ET).strftime('%H:%M ET')}] Market closed — sleeping.")

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()
