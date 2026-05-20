#!/usr/bin/env python3
"""
Train XGBoost models for all day-tradeable symbols in memory/watchlist.json.
Run once before the first day trading session; re-run weekly.

Usage:
    python3 scripts/daytrader/train_all.py
    python3 scripts/daytrader/train_all.py --symbol AAPL   # single symbol
"""

import sys
import os
import json
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from scripts.research import get_bars, compute_indicators
from scripts.daytrader import ml_model


def get_day_symbols() -> list[str]:
    wl_path = os.path.join(ROOT, "memory", "watchlist.json")
    with open(wl_path) as f:
        wl = json.load(f)
    return [
        s["symbol"] for s in wl["watchlist"]
        if s.get("strategy") in ("day", "both")
    ]


def train_symbol(symbol: str) -> dict:
    print(f"  [{symbol}] fetching 180 days of 5-min bars...", end=" ", flush=True)
    try:
        df = get_bars(symbol, "5Min", days_back=180)
        if df.empty or len(df) < 200:
            print(f"SKIP — only {len(df)} bars")
            return {"symbol": symbol, "error": "insufficient data"}
        df = compute_indicators(df)
        result = ml_model.train(symbol, df)
        if result.get("error"):
            print(f"SKIP — {result['error']}")
        else:
            print(f"OK  accuracy={result['accuracy']:.3f}  n={result['n_samples']}")
        return result
    except Exception as e:
        print(f"ERROR — {e}")
        return {"symbol": symbol, "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", help="Train a single symbol instead of all")
    args = parser.parse_args()

    symbols = [args.symbol.upper()] if args.symbol else get_day_symbols()
    print(f"Training {len(symbols)} symbol(s): {symbols}\n")

    results = []
    for sym in symbols:
        results.append(train_symbol(sym))

    ok = [r for r in results if not r.get("error")]
    print(f"\nDone. {len(ok)}/{len(results)} models trained successfully.")
    if ok:
        accs = [r["accuracy"] for r in ok if r.get("accuracy") is not None]
        if accs:
            print(f"Mean accuracy: {sum(accs)/len(accs):.3f}  (range {min(accs):.3f}–{max(accs):.3f})")


if __name__ == "__main__":
    main()
