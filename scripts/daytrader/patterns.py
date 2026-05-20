"""
Candlestick pattern detection for 5-min bars.

Each detector returns a directional score:
  +3 = strongly bullish
  +2 = bullish
  +1 = mildly bullish
  -1 = mildly bearish
  -2 = bearish
  -3 = strongly bearish
   0 = no pattern

score_all(df) aggregates all patterns on the latest bars and returns
(composite_score, list_of_detected_pattern_names).
"""

import pandas as pd
import numpy as np


# ── helpers ────────────────────────────────────────────────────────────────

def _body(row) -> float:
    return abs(row["close"] - row["open"])


def _range(row) -> float:
    return row["high"] - row["low"]


def _upper_wick(row) -> float:
    return row["high"] - max(row["open"], row["close"])


def _lower_wick(row) -> float:
    return min(row["open"], row["close"]) - row["low"]


def _is_bullish(row) -> bool:
    return row["close"] > row["open"]


def _is_bearish(row) -> bool:
    return row["close"] < row["open"]


# ── single-candle patterns ─────────────────────────────────────────────────

def doji(c) -> tuple[int, str | None]:
    body = _body(c)
    r = _range(c)
    if r == 0:
        return 0, None
    if body / r < 0.1:
        return 1, "doji"  # slight bullish bias in uptrend context, caller adjusts
    return 0, None


def hammer(c, prev) -> tuple[int, str | None]:
    """Hammer: small body, long lower wick, short upper wick — after decline."""
    body = _body(c)
    lower = _lower_wick(c)
    upper = _upper_wick(c)
    r = _range(c)
    if r == 0:
        return 0, None
    if lower >= 2 * body and upper <= 0.1 * r and _is_bullish(c):
        # Confirm prior downtrend
        if prev["close"] < prev["open"]:
            return 2, "hammer"
    return 0, None


def inverted_hammer(c, prev) -> tuple[int, str | None]:
    body = _body(c)
    upper = _upper_wick(c)
    lower = _lower_wick(c)
    r = _range(c)
    if r == 0:
        return 0, None
    if upper >= 2 * body and lower <= 0.1 * r:
        if prev["close"] < prev["open"]:
            return 1, "inverted_hammer"
    return 0, None


def shooting_star(c, prev) -> tuple[int, str | None]:
    """Shooting star: small body, long upper wick — after advance."""
    body = _body(c)
    upper = _upper_wick(c)
    lower = _lower_wick(c)
    r = _range(c)
    if r == 0:
        return 0, None
    if upper >= 2 * body and lower <= 0.1 * r and _is_bearish(c):
        if prev["close"] > prev["open"]:
            return -2, "shooting_star"
    return 0, None


# ── two-candle patterns ────────────────────────────────────────────────────

def bullish_engulfing(c, prev) -> tuple[int, str | None]:
    if _is_bearish(prev) and _is_bullish(c):
        if c["open"] < prev["close"] and c["close"] > prev["open"]:
            return 3, "bullish_engulfing"
    return 0, None


def bearish_engulfing(c, prev) -> tuple[int, str | None]:
    if _is_bullish(prev) and _is_bearish(c):
        if c["open"] > prev["close"] and c["close"] < prev["open"]:
            return -3, "bearish_engulfing"
    return 0, None


def piercing_line(c, prev) -> tuple[int, str | None]:
    """Bullish reversal: bearish candle followed by bullish that closes above midpoint."""
    if _is_bearish(prev) and _is_bullish(c):
        mid = (prev["open"] + prev["close"]) / 2
        if c["open"] < prev["close"] and c["close"] > mid:
            return 2, "piercing_line"
    return 0, None


def dark_cloud_cover(c, prev) -> tuple[int, str | None]:
    if _is_bullish(prev) and _is_bearish(c):
        mid = (prev["open"] + prev["close"]) / 2
        if c["open"] > prev["close"] and c["close"] < mid:
            return -2, "dark_cloud_cover"
    return 0, None


# ── three-candle patterns ──────────────────────────────────────────────────

def morning_star(c, b, a) -> tuple[int, str | None]:
    """a=oldest, b=middle (small body), c=latest (bullish)."""
    if _is_bearish(a) and _body(b) < 0.3 * _range(a) and _is_bullish(c):
        if c["close"] > (a["open"] + a["close"]) / 2:
            return 3, "morning_star"
    return 0, None


def evening_star(c, b, a) -> tuple[int, str | None]:
    if _is_bullish(a) and _body(b) < 0.3 * _range(a) and _is_bearish(c):
        if c["close"] < (a["open"] + a["close"]) / 2:
            return -3, "evening_star"
    return 0, None


def three_white_soldiers(c, b, a) -> tuple[int, str | None]:
    if all(_is_bullish(x) for x in [a, b, c]):
        if b["close"] > a["close"] and c["close"] > b["close"]:
            if b["open"] > a["open"] and c["open"] > b["open"]:
                return 3, "three_white_soldiers"
    return 0, None


def three_black_crows(c, b, a) -> tuple[int, str | None]:
    if all(_is_bearish(x) for x in [a, b, c]):
        if b["close"] < a["close"] and c["close"] < b["close"]:
            if b["open"] < a["open"] and c["open"] < b["open"]:
                return -3, "three_black_crows"
    return 0, None


# ── aggregator ─────────────────────────────────────────────────────────────

def score_all(df: pd.DataFrame) -> tuple[float, list[str]]:
    """
    Run all pattern detectors on the last 3 candles of df.
    Returns (composite_score_normalized_-1_to_1, list_of_pattern_names).
    composite is the sum of all triggered scores clamped to [-3, 3] then divided by 3.
    """
    if len(df) < 3:
        return 0.0, []

    c = df.iloc[-1]
    b = df.iloc[-2]
    a = df.iloc[-3]

    scores = []
    names = []

    for score, name in [
        doji(c),
        hammer(c, b),
        inverted_hammer(c, b),
        shooting_star(c, b),
        bullish_engulfing(c, b),
        bearish_engulfing(c, b),
        piercing_line(c, b),
        dark_cloud_cover(c, b),
        morning_star(c, b, a),
        evening_star(c, b, a),
        three_white_soldiers(c, b, a),
        three_black_crows(c, b, a),
    ]:
        if name:
            scores.append(score)
            names.append(name)

    if not scores:
        return 0.0, []

    total = sum(scores)
    total = max(-3, min(3, total))
    return round(total / 3.0, 3), names
