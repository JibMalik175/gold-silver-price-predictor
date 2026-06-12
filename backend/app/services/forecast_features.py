"""Feature engineering for commodity price forecasting (RSI, SMAs, volatility)."""

from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "log_ret_1",
    "log_ret_3",
    "log_ret_5",
    "volatility_5",
    "volatility_20",
    "rsi_14",
    "close_ma5_ratio",
    "close_ma20_ratio",
    "macd",
    "macd_signal",
    "atr_14_pct",
    "bb_upper_ratio",
    "bb_lower_ratio",
    "stoch_k",
    "stoch_d",
    "hl_range_pct",
    "day_of_week",
]


def rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index (Wilder's smoothing)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50.0)


def enrich_price_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build supervised rows: indicators from OHLCV history.
    Expects columns: date, close, volume (volume optional).
    """
    d = df.copy()
    if "close" not in d.columns:
        raise ValueError("DataFrame must contain 'close'")

    d["close"] = d["close"].astype(float)
    if "volume" not in d.columns:
        d["volume"] = 0.0
    d["volume"] = d["volume"].fillna(0).astype(float)

    c = d["close"]
    if "high" not in d.columns:
        d["high"] = c
    if "low" not in d.columns:
        d["low"] = c
    d["high"] = d["high"].astype(float)
    d["low"] = d["low"].astype(float)

    # Log Returns and Lags
    d["log_ret_1"] = np.log(c / c.shift(1))
    d["log_ret_3"] = np.log(c / c.shift(3))
    d["log_ret_5"] = np.log(c / c.shift(5))

    # Volatility (on log returns)
    d["volatility_5"] = d["log_ret_1"].rolling(5).std()
    d["volatility_20"] = d["log_ret_1"].rolling(20).std()

    # Moving Averages
    ma5 = c.rolling(5, min_periods=1).mean()
    ma20 = c.rolling(20, min_periods=1).mean()

    # Ratios
    d["close_ma5_ratio"] = c / ma5.replace(0, np.nan) - 1.0
    d["close_ma20_ratio"] = c / ma20.replace(0, np.nan) - 1.0

    # RSI
    d["rsi_14"] = rsi_wilder(c, 14)

    # MACD
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    d["macd"] = (ema12 - ema26) / c.replace(0, np.nan)
    d["macd_signal"] = d["macd"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    std20 = c.rolling(20).std()
    bb_upper = ma20 + (std20 * 2)
    bb_lower = ma20 - (std20 * 2)
    d["bb_upper_ratio"] = c / bb_upper.replace(0, np.nan) - 1.0
    d["bb_lower_ratio"] = c / bb_lower.replace(0, np.nan) - 1.0

    # Stochastic Oscillator
    low_14 = d["low"].rolling(14).min()
    high_14 = d["high"].rolling(14).max()
    d["stoch_k"] = 100 * (c - low_14) / (high_14 - low_14).replace(0, np.nan)
    d["stoch_d"] = d["stoch_k"].rolling(3).mean()
    d["stoch_k"] = d["stoch_k"].fillna(50.0)
    d["stoch_d"] = d["stoch_d"].fillna(50.0)

    # ATR
    tr = pd.concat(
        [
            d["high"] - d["low"],
            (d["high"] - c.shift(1)).abs(),
            (d["low"] - c.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    d["atr_14_pct"] = (tr.rolling(14).mean() / c.replace(0, np.nan)).fillna(0.0)
    d["hl_range_pct"] = ((d["high"] - d["low"]) / c.replace(0, np.nan)).fillna(0.0)

    # Seasonal
    if "date" in d.columns:
        d["date"] = pd.to_datetime(d["date"])
        d["day_of_week"] = d["date"].dt.dayofweek / 6.0
    else:
        d["day_of_week"] = 0.0

    # Target: Next period log return
    d["target_next_ret"] = d["log_ret_1"].shift(-1)

    return d


def training_matrix(df: pd.DataFrame):
    """Return X, y, aligned index after dropna."""
    enriched = enrich_price_df(df)
    # We need features and target to be finite
    use = enriched.dropna(subset=FEATURE_COLUMNS + ["target_next_ret"])
    X = use[FEATURE_COLUMNS]
    y = use["target_next_ret"]
    return X, y, enriched
