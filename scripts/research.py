#!/usr/bin/env python3
"""
Market Research & Technical Analysis CLI
Called by Claude Code routines to fetch market data and compute indicators.

Usage:
    python scripts/research.py analyze <symbol>       — Full TA for one symbol
    python scripts/research.py scan                   — Scan all watchlist symbols
    python scripts/research.py market-scan [N]        — Catalyst scan: S&P500 + Nasdaq100 + emerging tech → top N movers with news + earnings
    python scripts/research.py bars <symbol> <tf> <days> — Raw bar data as JSON
    python scripts/research.py indicators <symbol>    — Just the indicator values
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice
from concurrent.futures import ThreadPoolExecutor, as_completed
from alpaca.data.historical import StockHistoricalDataClient, NewsClient
from alpaca.data.requests import StockBarsRequest, StockSnapshotRequest, NewsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed


API_KEY = os.getenv("ALPACA_API_KEY", "")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")

if not API_KEY or not SECRET_KEY:
    print("ERROR: ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env")
    sys.exit(1)

data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
news_client = NewsClient(API_KEY, SECRET_KEY)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_bars(symbol: str, timeframe: str = "1Day", days_back: int = 365) -> pd.DataFrame:
    tf_map = {
        "1Min": TimeFrame(1, TimeFrameUnit.Minute),
        "5Min": TimeFrame(5, TimeFrameUnit.Minute),
        "15Min": TimeFrame(15, TimeFrameUnit.Minute),
        "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
        "1Day": TimeFrame(1, TimeFrameUnit.Day),
    }
    tf = tf_map.get(timeframe, TimeFrame(1, TimeFrameUnit.Day))
    end = datetime.now()
    start = end - timedelta(days=days_back)

    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=tf,
        start=start,
        end=end,
        feed=DataFeed.IEX,
    )
    bars = data_client.get_stock_bars(request)
    df = bars.df

    if isinstance(df.index, pd.MultiIndex):
        df = df.droplevel("symbol")

    df = df.reset_index()
    df.columns = [c.lower() for c in df.columns]
    if "timestamp" in df.columns:
        df = df.rename(columns={"timestamp": "datetime"})
        df["datetime"] = pd.to_datetime(df["datetime"])

    return df


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Moving Averages
    df["sma_20"] = SMAIndicator(close=df["close"], window=20).sma_indicator()
    df["sma_50"] = SMAIndicator(close=df["close"], window=50).sma_indicator()
    df["sma_200"] = SMAIndicator(close=df["close"], window=200).sma_indicator()
    df["ema_9"] = EMAIndicator(close=df["close"], window=9).ema_indicator()
    df["ema_21"] = EMAIndicator(close=df["close"], window=21).ema_indicator()

    # RSI
    df["rsi_14"] = RSIIndicator(close=df["close"], window=14).rsi()

    # MACD
    macd = MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9)
    df["macd_line"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_histogram"] = macd.macd_diff()

    # Bollinger Bands
    bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_middle"] = bb.bollinger_mavg()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_pct"] = bb.bollinger_pband()

    # ATR
    df["atr_14"] = AverageTrueRange(
        high=df["high"], low=df["low"], close=df["close"], window=14
    ).average_true_range()

    # VWAP
    try:
        vwap = VolumeWeightedAveragePrice(
            high=df["high"], low=df["low"], close=df["close"], volume=df["volume"]
        )
        df["vwap"] = vwap.volume_weighted_average_price()
    except Exception:
        df["vwap"] = np.nan

    # Stochastic RSI
    stoch = StochRSIIndicator(close=df["close"], window=14, smooth1=3, smooth2=3)
    df["stoch_k"] = stoch.stochrsi_k() * 100
    df["stoch_d"] = stoch.stochrsi_d() * 100

    return df


def get_signals(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 2:
        return {"error": "Not enough data"}

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    def safe(val):
        if pd.isna(val):
            return None
        return round(float(val), 4)

    signals = {
        "price": safe(latest["close"]),
        "indicators": {
            "rsi_14": safe(latest.get("rsi_14")),
            "macd_line": safe(latest.get("macd_line")),
            "macd_signal": safe(latest.get("macd_signal")),
            "macd_histogram": safe(latest.get("macd_histogram")),
            "sma_20": safe(latest.get("sma_20")),
            "sma_50": safe(latest.get("sma_50")),
            "sma_200": safe(latest.get("sma_200")),
            "ema_9": safe(latest.get("ema_9")),
            "ema_21": safe(latest.get("ema_21")),
            "bb_upper": safe(latest.get("bb_upper")),
            "bb_lower": safe(latest.get("bb_lower")),
            "bb_pct": safe(latest.get("bb_pct")),
            "atr_14": safe(latest.get("atr_14")),
            "vwap": safe(latest.get("vwap")),
            "stoch_k": safe(latest.get("stoch_k")),
            "stoch_d": safe(latest.get("stoch_d")),
        },
        "signals": [],
    }

    # Signal generation
    rsi = latest.get("rsi_14")
    if pd.notna(rsi):
        if rsi < 30:
            signals["signals"].append("RSI OVERSOLD (< 30) — potential BUY")
        elif rsi > 70:
            signals["signals"].append("RSI OVERBOUGHT (> 70) — potential SELL")

    if pd.notna(latest.get("macd_line")) and pd.notna(prev.get("macd_line")):
        if prev["macd_line"] < prev["macd_signal"] and latest["macd_line"] > latest["macd_signal"]:
            signals["signals"].append("MACD BULLISH CROSSOVER — BUY signal")
        elif prev["macd_line"] > prev["macd_signal"] and latest["macd_line"] < latest["macd_signal"]:
            signals["signals"].append("MACD BEARISH CROSSOVER — SELL signal")

    if pd.notna(latest.get("sma_50")) and pd.notna(latest.get("sma_200")):
        if pd.notna(prev.get("sma_50")) and pd.notna(prev.get("sma_200")):
            if prev["sma_50"] < prev["sma_200"] and latest["sma_50"] > latest["sma_200"]:
                signals["signals"].append("GOLDEN CROSS (SMA 50 > 200) — strong BUY")
            elif prev["sma_50"] > prev["sma_200"] and latest["sma_50"] < latest["sma_200"]:
                signals["signals"].append("DEATH CROSS (SMA 50 < 200) — strong SELL")

    if pd.notna(latest.get("ema_9")) and pd.notna(latest.get("ema_21")):
        if pd.notna(prev.get("ema_9")) and pd.notna(prev.get("ema_21")):
            if prev["ema_9"] < prev["ema_21"] and latest["ema_9"] > latest["ema_21"]:
                signals["signals"].append("EMA 9/21 BULLISH CROSSOVER")
            elif prev["ema_9"] > prev["ema_21"] and latest["ema_9"] < latest["ema_21"]:
                signals["signals"].append("EMA 9/21 BEARISH CROSSOVER")

    if pd.notna(latest.get("bb_pct")):
        if latest["bb_pct"] < 0:
            signals["signals"].append("BELOW LOWER BOLLINGER BAND — oversold")
        elif latest["bb_pct"] > 1:
            signals["signals"].append("ABOVE UPPER BOLLINGER BAND — overbought")

    if pd.notna(latest.get("stoch_k")) and pd.notna(latest.get("stoch_d")):
        if latest["stoch_k"] < 20 and latest["stoch_d"] < 20:
            signals["signals"].append("STOCHASTIC OVERSOLD — potential BUY")
        elif latest["stoch_k"] > 80 and latest["stoch_d"] > 80:
            signals["signals"].append("STOCHASTIC OVERBOUGHT — potential SELL")

    if pd.notna(latest.get("vwap")):
        if latest["close"] > latest["vwap"]:
            signals["signals"].append("Price ABOVE VWAP — bullish intraday")
        else:
            signals["signals"].append("Price BELOW VWAP — bearish intraday")

    if pd.notna(latest.get("sma_20")):
        if latest["close"] > latest["sma_20"]:
            signals["signals"].append("Trend: above SMA 20 (short-term uptrend)")
        else:
            signals["signals"].append("Trend: below SMA 20 (short-term downtrend)")

    if pd.notna(latest.get("sma_50")) and pd.notna(latest.get("sma_200")):
        if latest["sma_50"] > latest["sma_200"]:
            signals["signals"].append("Trend: SMA 50 > 200 (long-term bullish)")
        else:
            signals["signals"].append("Trend: SMA 50 < 200 (long-term bearish)")

    return signals


def load_watchlist() -> list[str]:
    wl_path = os.path.join(PROJECT_ROOT, "memory", "watchlist.json")
    try:
        with open(wl_path) as f:
            data = json.load(f)
        return [item["symbol"] for item in data.get("watchlist", [])]
    except Exception:
        return ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL", "AMD", "SPY", "QQQ"]


def load_universe() -> list:
    """Merge S&P 500 + Nasdaq 100 + emerging tech symbol lists, deduplicated."""
    seen = set()
    result = []
    for fname in ("sp500_symbols.json", "nasdaq100_symbols.json", "emerging_tech_symbols.json"):
        path = os.path.join(PROJECT_ROOT, "data", fname)
        try:
            syms = json.load(open(path))
            for s in syms:
                s = s.strip().upper()
                if s and s not in seen:
                    seen.add(s)
                    result.append(s)
        except FileNotFoundError:
            pass
    return result


def fast_premarket_screen(top_n: int = 25) -> list:
    """
    Fetch snapshots for the full universe in batches, filter by volume/price/gap,
    return top_n candidates sorted by volume × |gap%| (momentum score).
    """
    symbols = load_universe()
    candidates = []
    batch_size = 300
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        try:
            req = StockSnapshotRequest(symbol_or_symbols=batch, feed=DataFeed.IEX)
            snapshots = data_client.get_stock_snapshot(req)
        except Exception as e:
            print(f"  snapshot batch {i//batch_size + 1} error: {e}", file=sys.stderr)
            continue
        for sym, snap in snapshots.items():
            try:
                price = float(snap.latest_trade.price) if snap.latest_trade else None
                prev_close = float(snap.prev_daily_bar.close) if snap.prev_daily_bar else None
                volume = int(snap.daily_bar.volume) if snap.daily_bar else 0
                if price is None or prev_close is None or prev_close == 0:
                    continue
                gap_pct = (price - prev_close) / prev_close * 100
                if volume >= 500_000 and price >= 3.0 and abs(gap_pct) >= 1.0:
                    candidates.append({
                        "symbol": sym,
                        "price": round(price, 2),
                        "volume": volume,
                        "gap_pct": round(gap_pct, 2),
                        "momentum_score": volume * abs(gap_pct),
                    })
            except Exception:
                continue
    candidates.sort(key=lambda x: x["momentum_score"], reverse=True)
    return candidates[:top_n]


def get_earnings_soon(symbols: list, days_ahead: int = 7) -> dict:
    """
    Check symbols for upcoming earnings within days_ahead days using yfinance.
    Returns {symbol: earnings_date_str}. Parallelised for speed.
    """
    try:
        import yfinance as yf
    except ImportError:
        return {}

    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)
    result = {}

    def _check(sym):
        try:
            cal = yf.Ticker(sym).calendar
            if cal is None:
                return None
            dates = cal.get("Earnings Date", [])
            if not dates:
                return None
            d = dates[0]
            if hasattr(d, "date"):
                d = d.date()
            elif isinstance(d, str):
                d = datetime.strptime(d[:10], "%Y-%m-%d").date()
            if today <= d <= cutoff:
                return (sym, str(d))
        except Exception:
            pass
        return None

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(_check, s): s for s in symbols}
        for f in as_completed(futures):
            r = f.result()
            if r:
                result[r[0]] = r[1]
    return result


def get_news_for_symbols(symbols: list, limit: int = 3) -> dict:
    """
    Fetch recent news headlines for a list of symbols via Alpaca News API.
    Returns {symbol: [headline, ...]}.
    """
    if not symbols:
        return {}
    result = {s: [] for s in symbols}
    try:
        req = NewsRequest(symbols=",".join(symbols),
                          limit=min(limit * len(symbols), 50),
                          sort="desc", include_content=False)
        resp = news_client.get_news(req)
        # NewsSet iterates as ('data', {'news': [...]}) tuples; items are dicts
        raw_items = []
        for key, val in resp:
            if key == "data" and isinstance(val, dict):
                raw_items = val.get("news", [])
                break
        for item in raw_items:
            syms = item.symbols if hasattr(item, "symbols") else (item.get("symbols") or [])
            headline = item.headline if hasattr(item, "headline") else item.get("headline", "")
            for sym in (syms or []):
                if sym in result and len(result[sym]) < limit:
                    result[sym].append(headline)
    except Exception as e:
        print(f"  news fetch error: {e}", file=sys.stderr)
    return result


_BULLISH_WORDS = {
    "beat", "beats", "upgrade", "raises", "raised", "record", "growth", "strong",
    "outperform", "buy", "bullish", "surge", "rally", "breakout", "accelerate",
    "expansion", "wins", "awarded", "partnership", "breakthrough", "approves",
    "approved", "exceeds", "positive", "profit", "revenue", "gain", "top",
}
_BEARISH_WORDS = {
    "miss", "misses", "downgrade", "cuts", "cut", "weak", "loss", "losses",
    "decline", "sell", "bearish", "drop", "warning", "concern", "risk",
    "struggles", "disappoints", "recall", "investigation", "lawsuit", "lowers",
    "below", "missed", "shortfall", "negative", "charge", "writedown", "layoffs",
}


def compute_sentiment_score(headlines: list) -> float:
    """Score headlines -5 to +5 using financial keyword lists."""
    if not headlines:
        return 0.0
    text = " ".join(headlines).lower()
    words = text.split()
    bullish = sum(1 for w in words if w.strip(".,!?;:\"'") in _BULLISH_WORDS)
    bearish = sum(1 for w in words if w.strip(".,!?;:\"'") in _BEARISH_WORDS)
    total = max(len(words), 1)
    raw = (bullish - bearish) / total * 50
    return round(max(-5.0, min(5.0, raw)), 2)


def get_short_data(symbols: list) -> dict:
    """
    Fetch short interest data for symbols via yfinance.
    Returns {symbol: {"short_pct": float, "short_ratio_days": float}}.
    Parallelised; missing/errored symbols return empty dict.
    """
    try:
        import yfinance as yf
    except ImportError:
        return {}

    result = {}

    def _fetch(sym):
        try:
            info = yf.Ticker(sym).info
            return sym, {
                "short_pct": info.get("shortPercentOfFloat") or 0.0,
                "short_ratio_days": info.get("shortRatio") or 0.0,
            }
        except Exception:
            return sym, {}

    with ThreadPoolExecutor(max_workers=10) as ex:
        for sym, data in ex.map(_fetch, symbols):
            result[sym] = data
    return result


def compute_squeeze_score(gap_pct, volume, news_headlines, short_pct, short_ratio_days) -> int:
    """Score a candidate's short-squeeze potential 0–10."""
    score = 0
    if short_pct and short_pct > 0.15:
        score += 3
    if short_pct and short_pct > 0.25:
        score += 2
    if gap_pct and abs(gap_pct) > 1.0:
        score += 2
    if volume and volume >= 1_000_000:
        score += 2
    if news_headlines:
        score += 1
    return score


def cmd_market_scan(top_n: int = 25):
    """
    Catalyst-driven scan across ~650 symbols with enriched signals:
      1. Gap movers — snapshot screen across full universe
      2. Earnings runners — upcoming earnings in next 7 days
      3. News + sentiment divergence — headlines + contrarian score
      4. Short squeeze score — high short interest + catalyst = explosive potential
      5. Full TA — existing indicator suite on each candidate
    """
    print(f"[market-scan] Pass 1: screening universe for top {top_n} gap movers...", file=sys.stderr)
    candidates = fast_premarket_screen(top_n)
    print(f"[market-scan] Pass 1 complete: {len(candidates)} gap candidates", file=sys.stderr)

    candidate_syms = [c["symbol"] for c in candidates]

    # Earnings: check all candidates + top 50 S&P 500 large-caps for run-up plays
    sp500_large = []
    try:
        sp500_large = json.load(open(os.path.join(PROJECT_ROOT, "data", "sp500_symbols.json")))[:50]
    except Exception:
        pass
    earnings_check = list(set(candidate_syms + sp500_large))
    print(f"[market-scan] Pass 2: checking earnings calendar for {len(earnings_check)} symbols...", file=sys.stderr)
    earnings_map = get_earnings_soon(earnings_check, days_ahead=7)

    # Merge in earnings runners not already in gap candidates
    for sym, edate in earnings_map.items():
        if sym not in candidate_syms and len(candidates) < top_n:
            candidates.append({
                "symbol": sym,
                "price": None,
                "volume": None,
                "gap_pct": None,
                "momentum_score": 0,
                "earnings_runner": True,
            })
            candidate_syms.append(sym)
    candidates = candidates[:top_n]
    candidate_syms = [c["symbol"] for c in candidates]

    print(f"[market-scan] Pass 3: fetching news + short data for {len(candidate_syms)} candidates...", file=sys.stderr)
    # Run news and short-data fetches concurrently
    with ThreadPoolExecutor(max_workers=2) as ex:
        news_future = ex.submit(get_news_for_symbols, candidate_syms, 3)
        short_future = ex.submit(get_short_data, candidate_syms)
    news_map = news_future.result()
    short_map = short_future.result()

    # Load watchlist for context enrichment
    watchlist_map = {}
    try:
        wl = json.load(open(os.path.join(PROJECT_ROOT, "memory", "watchlist.json")))
        watchlist_map = {item["symbol"]: item.get("notes", "") for item in wl.get("watchlist", [])}
    except Exception:
        pass

    results = {}
    for i, c in enumerate(candidates):
        sym = c["symbol"]
        print(f"[market-scan] Pass 4 [{i+1}/{len(candidates)}]: TA for {sym}...", file=sys.stderr)
        headlines = news_map.get(sym, [])
        short = short_map.get(sym, {})
        short_pct = short.get("short_pct", 0.0)
        short_ratio = short.get("short_ratio_days", 0.0)
        gap_pct = c.get("gap_pct")
        volume = c.get("volume")

        sentiment = compute_sentiment_score(headlines)
        if gap_pct is not None and gap_pct > 0 and sentiment < -1:
            divergence = "BULLISH_DIVERGENCE"
        elif gap_pct is not None and gap_pct < 0 and sentiment > 1:
            divergence = "BEARISH_DIVERGENCE"
        else:
            divergence = "ALIGNED"

        squeeze = compute_squeeze_score(gap_pct, volume, headlines, short_pct, short_ratio)

        try:
            df = get_bars(sym, "1Day", 365)
            df = compute_indicators(df)
            signals = get_signals(df)
            signals["symbol"] = sym
            signals["snapshot_gap_pct"] = gap_pct
            signals["snapshot_volume"] = volume
            signals["momentum_score"] = c.get("momentum_score")
            signals["earnings_date"] = earnings_map.get(sym)
            signals["news_headlines"] = headlines
            signals["sentiment_score"] = sentiment
            signals["sentiment_divergence"] = divergence
            signals["short_interest_pct"] = round(short_pct * 100, 1) if short_pct else None
            signals["short_ratio_days"] = short_ratio or None
            signals["squeeze_score"] = squeeze
            signals["squeeze_flag"] = "SQUEEZE_CANDIDATE" if squeeze >= 6 else None
            signals["watchlist_notes"] = watchlist_map.get(sym, "")
            results[sym] = signals
        except Exception as e:
            results[sym] = {"symbol": sym, "error": str(e),
                            "earnings_date": earnings_map.get(sym),
                            "news_headlines": headlines,
                            "sentiment_score": sentiment,
                            "sentiment_divergence": divergence,
                            "short_interest_pct": round(short_pct * 100, 1) if short_pct else None,
                            "squeeze_score": squeeze,
                            "squeeze_flag": "SQUEEZE_CANDIDATE" if squeeze >= 6 else None}
    print(json.dumps(results, indent=2))


def cmd_analyze(symbol: str):
    print(f"Analyzing {symbol}...")
    df = get_bars(symbol, "1Day", 365)
    df = compute_indicators(df)
    signals = get_signals(df)
    signals["symbol"] = symbol
    print(json.dumps(signals, indent=2))


def cmd_scan():
    watchlist = load_watchlist()
    print(f"Scanning {len(watchlist)} symbols...")
    results = {}
    for symbol in watchlist:
        try:
            df = get_bars(symbol, "1Day", 365)
            df = compute_indicators(df)
            signals = get_signals(df)
            signals["symbol"] = symbol
            results[symbol] = signals
        except Exception as e:
            results[symbol] = {"symbol": symbol, "error": str(e)}
    print(json.dumps(results, indent=2))


def cmd_bars(symbol: str, timeframe: str = "1Day", days: int = 60):
    df = get_bars(symbol, timeframe, days)
    # Output last 20 bars as JSON
    recent = df.tail(20).copy()
    if "datetime" in recent.columns:
        recent["datetime"] = recent["datetime"].astype(str)
    print(json.dumps(recent.to_dict(orient="records"), indent=2))


def cmd_indicators(symbol: str):
    df = get_bars(symbol, "1Day", 365)
    df = compute_indicators(df)
    latest = df.iloc[-1]

    def safe(val):
        if pd.isna(val):
            return None
        return round(float(val), 4)

    result = {
        "symbol": symbol,
        "price": safe(latest["close"]),
        "rsi_14": safe(latest.get("rsi_14")),
        "macd_line": safe(latest.get("macd_line")),
        "macd_signal": safe(latest.get("macd_signal")),
        "macd_histogram": safe(latest.get("macd_histogram")),
        "sma_20": safe(latest.get("sma_20")),
        "sma_50": safe(latest.get("sma_50")),
        "sma_200": safe(latest.get("sma_200")),
        "ema_9": safe(latest.get("ema_9")),
        "ema_21": safe(latest.get("ema_21")),
        "bb_upper": safe(latest.get("bb_upper")),
        "bb_lower": safe(latest.get("bb_lower")),
        "bb_pct": safe(latest.get("bb_pct")),
        "atr_14": safe(latest.get("atr_14")),
        "vwap": safe(latest.get("vwap")),
        "stoch_k": safe(latest.get("stoch_k")),
        "stoch_d": safe(latest.get("stoch_d")),
    }
    print(json.dumps(result, indent=2))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    try:
        if cmd == "analyze":
            cmd_analyze(sys.argv[2].upper())
        elif cmd == "scan":
            cmd_scan()
        elif cmd == "market-scan":
            top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 25
            cmd_market_scan(top_n)
        elif cmd == "bars":
            symbol = sys.argv[2].upper()
            tf = sys.argv[3] if len(sys.argv) > 3 else "1Day"
            days = int(sys.argv[4]) if len(sys.argv) > 4 else 60
            cmd_bars(symbol, tf, days)
        elif cmd == "indicators":
            cmd_indicators(sys.argv[2].upper())
        else:
            print(f"Unknown command: {cmd}")
            print(__doc__)
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
