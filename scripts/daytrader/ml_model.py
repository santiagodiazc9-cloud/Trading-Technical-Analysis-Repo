"""
XGBoost confidence model for 5-min bar direction prediction.

train(symbol, lookback_days) — fits model on historical data, saves to models/<symbol>.pkl
predict(df) → float probability that the next 3 candles produce >= +0.5% gain
load(symbol) → fitted XGBClassifier or None
"""

import os
import pickle
import sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def _model_path(symbol: str) -> str:
    return os.path.join(MODELS_DIR, f"{symbol}.pkl")


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract feature matrix from an indicator-enriched DataFrame.
    Each row is one bar. NaN rows are dropped.
    """
    feat = pd.DataFrame(index=df.index)

    close = df["close"]
    feat["rsi"] = df.get("rsi_14", np.nan) / 100.0
    feat["macd_hist"] = df.get("macd_histogram", np.nan) / close
    feat["atr_pct"] = df.get("atr_14", np.nan) / close
    feat["bb_pct"] = df.get("bb_pct", np.nan)
    feat["stoch_k"] = df.get("stoch_k", np.nan) / 100.0
    feat["stoch_d"] = df.get("stoch_d", np.nan) / 100.0

    # VWAP deviation
    vwap = df.get("vwap", pd.Series(np.nan, index=df.index))
    feat["vwap_dev"] = (close - vwap) / (df.get("atr_14", close) + 1e-9)

    # Price relative to moving averages
    for ma in ["ema_9", "ema_21", "sma_20"]:
        col = df.get(ma, pd.Series(np.nan, index=df.index))
        feat[f"close_vs_{ma}"] = (close - col) / (close + 1e-9)

    # Momentum: 5-bar return
    feat["mom_5"] = close.pct_change(5)

    # Volume ratio: current vs 20-bar avg
    if "volume" in df.columns:
        vol_avg = df["volume"].rolling(20).mean()
        feat["vol_ratio"] = df["volume"] / (vol_avg + 1e-9)
    else:
        feat["vol_ratio"] = 1.0

    # Candle body ratio
    body = abs(close - df.get("open", close))
    rng = df.get("high", close) - df.get("low", close)
    feat["body_ratio"] = body / (rng + 1e-9)

    return feat


def _build_labels(df: pd.DataFrame, forward_bars: int = 3, threshold: float = 0.005) -> pd.Series:
    """1 if close rises >= threshold% over next forward_bars candles, else 0."""
    future_close = df["close"].shift(-forward_bars)
    return ((future_close - df["close"]) / df["close"] >= threshold).astype(int)


def train(symbol: str, df_with_indicators: pd.DataFrame) -> dict:
    """
    Train and persist an XGBClassifier for symbol.
    df_with_indicators must already have compute_indicators() applied.
    Returns {'symbol': symbol, 'n_samples': int, 'accuracy': float}.
    """
    from xgboost import XGBClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    features = _build_features(df_with_indicators)
    labels = _build_labels(df_with_indicators)

    df_combined = features.copy()
    df_combined["label"] = labels
    df_combined = df_combined.dropna()

    if len(df_combined) < 100:
        return {"symbol": symbol, "n_samples": len(df_combined), "accuracy": None,
                "error": "Not enough data (need >= 100 bars)"}

    X = df_combined.drop(columns=["label"])
    y = df_combined["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        verbosity=0,
    )
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))

    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(_model_path(symbol), "wb") as f:
        pickle.dump({"model": model, "feature_cols": list(X.columns)}, f)

    return {"symbol": symbol, "n_samples": len(df_combined), "accuracy": round(acc, 4)}


def load(symbol: str):
    path = _model_path(symbol)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def predict(symbol: str, df_with_indicators: pd.DataFrame) -> float:
    """
    Return probability (0–1) that the next 3 bars gain >= 0.5%.
    Returns 0.5 (neutral) if no model is trained or data is insufficient.
    """
    payload = load(symbol)
    if payload is None:
        return 0.5

    model = payload["model"]
    feature_cols = payload["feature_cols"]

    features = _build_features(df_with_indicators)
    if features.empty or features.iloc[[-1]].isnull().all(axis=1).any():
        return 0.5

    row = features.iloc[[-1]].reindex(columns=feature_cols, fill_value=0)
    prob = model.predict_proba(row)[0][1]
    return round(float(prob), 4)
