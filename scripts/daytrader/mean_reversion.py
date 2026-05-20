"""
Statistical mean-reversion scoring for intraday bars.

Two models combined:
1. VWAP deviation: (price - VWAP) / ATR — how far from intraday fair value
2. Intraday Z-score: rolling 20-bar z-score of close price

score(df) returns a float in [-1, 1]:
  positive = price ABOVE fair value → bearish mean-reversion signal
  negative = price BELOW fair value → bullish mean-reversion signal

NOTE: sign is inverted from the raw deviation — a stock BELOW VWAP is a
LONG mean-reversion candidate (score will be negative here, but engine
interprets negative mean_reversion score as bullish for a long trade).
The engine uses: composite = pattern_score + (-mean_reversion_score) for long signals.
"""

import numpy as np
import pandas as pd


def vwap_deviation_score(df: pd.DataFrame) -> float:
    """
    Normalise distance from VWAP by ATR.
    Returns raw float; positive = above VWAP, negative = below.
    """
    if "vwap" not in df.columns or "atr_14" not in df.columns:
        return 0.0

    latest = df.iloc[-1]
    price = latest.get("close", np.nan)
    vwap = latest.get("vwap", np.nan)
    atr = latest.get("atr_14", np.nan)

    if any(pd.isna(v) or v == 0 for v in [price, vwap, atr]):
        return 0.0

    raw = (price - vwap) / atr
    return float(np.clip(raw, -3, 3))


def zscore(df: pd.DataFrame, window: int = 20) -> float:
    """Rolling z-score of the close price over the last `window` bars."""
    if len(df) < window:
        return 0.0

    closes = df["close"].tail(window)
    mu = closes.mean()
    sigma = closes.std()
    if sigma == 0:
        return 0.0

    z = (closes.iloc[-1] - mu) / sigma
    return float(np.clip(z, -3, 3))


def score(df: pd.DataFrame) -> float:
    """
    Composite mean-reversion score in [-1, 1].
    Positive → price extended above fair value (bearish lean).
    Negative → price depressed below fair value (bullish lean).
    """
    vwap_score = vwap_deviation_score(df)   # +3 = far above VWAP
    z = zscore(df, window=20)               # +3 = far above rolling mean

    raw = 0.6 * vwap_score + 0.4 * z
    return round(float(np.clip(raw / 3.0, -1.0, 1.0)), 4)
