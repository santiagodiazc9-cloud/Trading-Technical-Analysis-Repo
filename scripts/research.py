#!/usr/bin/env python3
"""
Market Research & Technical Analysis CLI
Called by Claude Code routines to fetch market data and compute indicators.

Usage:
    python scripts/research.py analyze <symbol>       — Full TA for one symbol
    python scripts/research.py scan                   — Scan all watchlist symbols
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
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed


API_KEY = os.getenv("ALPACA_API_KEY", "")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")

if not API_KEY or not SECRET_KEY:
    print("ERROR: ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env")
    sys.exit(1)

data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

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
