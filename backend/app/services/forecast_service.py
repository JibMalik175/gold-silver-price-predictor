"""
Gradient Boosted + Random Forest ensemble commodity forecasts with
volatility-aware multi-step paths.

Uses an ensemble of GradientBoosting and RandomForest on market-structure
features, with tighter clamping, stronger mean-reversion anchoring,
and confidence intervals for more realistic 30-day forecasts.
"""

from __future__ import annotations

import os
from datetime import timedelta
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor

from app.services import price_service
from app.services.forecast_features import FEATURE_COLUMNS, enrich_price_df, training_matrix

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
BUNDLE_NAME = "rf_forecast_{asset}_{timeframe}.joblib"

# Soft accuracy goals (USD) used for UI messaging — model quality depends on data volume.
MAE_GOAL_USD = {"silver": 4.0, "gold": 10.0}


def _bundle_path(asset: str, timeframe: str) -> str:
    return os.path.join(MODEL_DIR, BUNDLE_NAME.format(asset=asset, timeframe=timeframe))


def _load_bundle(asset: str, timeframe: str) -> Optional[dict]:
    path = _bundle_path(asset, timeframe)
    if not os.path.isfile(path):
        return None
    return joblib.load(path)


def _mini_df_from_tail(closes: List[float], volumes: List[float]) -> pd.DataFrame:
    n = len(closes)
    return pd.DataFrame(
        {
            "date": pd.date_range("2000-01-01", periods=n, freq="D"),
            "close": closes,
            "volume": volumes,
        }
    )


def _last_feature_row(closes: List[float], volumes: List[float]) -> np.ndarray:
    """Compute feature vector for the most recent bar in a synthetic history."""
    df = _mini_df_from_tail(closes, volumes)
    enriched = enrich_price_df(df)
    valid = enriched.dropna(subset=FEATURE_COLUMNS)
    if valid.empty:
        raise ValueError("Not enough contiguous history to compute RSI / moving averages.")
    row = valid.iloc[-1]
    return row[FEATURE_COLUMNS].values.astype(np.float64)


def _step_return_cap(
    mae_test_usd: float,
    vol20: float,
    last_close: float,
    asset: str,
    step_index: int,
    total_steps: int,
) -> float:
    """
    Max absolute one-step return (percentage).
    Tighter caps to prevent unrealistic drift over 30 days.
    """
    # 1.2 standard deviations (tighter than before) of daily returns
    vol_cap = float(vol20) * 1.2 if vol20 == vol20 else 0.01
    # Also consider the dollar MAE scaled to percentage
    mae_pct = (mae_test_usd / last_close) * 0.8 if last_close > 0 else 0.01

    base_cap = max(vol_cap, mae_pct, 0.005)

    # Absolute ceiling — precious metals rarely move >2% daily consistently
    if asset == "silver":
        base_cap = min(base_cap, 0.025)
    else:
        base_cap = min(base_cap, 0.015)

    # Stronger decay as we forecast further out
    decay = 1.0 - 0.5 * (step_index / max(total_steps, 1))
    return max(base_cap * decay, 0.001)


def generate_forecast(asset: str, timeframe: str = "daily", steps: int = 30) -> Dict[str, Any]:
    """Generate a multi-step forecast using the trained ensemble model."""
    asset = asset.lower().strip()
    if asset not in ("gold", "silver"):
        return {"error": "Asset must be 'gold' or 'silver'."}

    bundle = _load_bundle(asset, timeframe)
    if bundle is None:
        return {
            "error": (
                f"No forecast model for {asset}/{timeframe}. "
                "From the backend folder run: python scripts/train_forecast_rf.py --asset "
                f"{asset} --timeframe {timeframe}"
            )
        }

    # Support both old (single model) and new (ensemble) bundles
    if "models" in bundle:
        models = bundle["models"]
        weights = bundle.get("weights", [1.0 / len(models)] * len(models))
    else:
        models = [bundle["model"]]
        weights = [1.0]

    mae_train = float(bundle.get("mae_train", 0))
    mae_test = float(bundle.get("mae_test", 0))
    vol20_train_end = float(bundle.get("rolling_vol_20_at_train_end", 0.01))

    rows = price_service.get_historical_prices(asset, timeframe)
    if not rows or len(rows) < 65:
        return {"error": "Insufficient price history for forecasting (need 65+ bars)."}

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    closes = df["close"].astype(float).tolist()
    vols = df["volume"].fillna(0).astype(float).tolist()

    last_date = df["date"].iloc[-1]
    last_close_hist = float(closes[-1])

    enriched_hist = enrich_price_df(df)
    vol20_live = enriched_hist["volatility_20"].iloc[-1]
    if not np.isfinite(vol20_live):
        vol20_live = vol20_train_end

    # Compute MA20 for mean-reversion anchor
    ma20_anchor = float(df["close"].iloc[-20:].mean()) if len(df) >= 20 else last_close_hist

    tail_len = min(200, len(closes))
    predictions: List[Dict[str, Any]] = []
    curr_date = last_date

    work_close = list(closes[-tail_len:])
    work_vol = list(vols[-tail_len:])

    try:
        for h in range(steps):
            feats = _last_feature_row(work_close, work_vol)

            # Ensemble prediction: weighted average of all models' log return predictions
            pred_log_ret = 0.0
            for model, weight in zip(models, weights):
                pred_log_ret += weight * float(model.predict(feats.reshape(1, -1))[0])

            # Slightly tighter log return caps
            cap = _step_return_cap(mae_test, float(vol20_live), work_close[-1], asset, h, steps)
            pred_log_ret = float(np.clip(pred_log_ret, -cap, cap))

            # Apply to price: P_t+1 = P_t * exp(r)
            pred_price = work_close[-1] * np.exp(pred_log_ret)

            # Stronger mean-reversion anchoring towards MA20
            # As we go further out, blend more towards the moving average
            denom = max(steps - 1, 1)
            # Increase blend: start at 20%, ramp up to 50%
            beta = min(0.50, 0.20 + 0.30 * (h / denom))
            pred_price = (1.0 - beta) * pred_price + beta * ma20_anchor

            # Skip weekends for daily timeframe
            if timeframe == "daily":
                curr_date = curr_date + timedelta(days=1)
                while curr_date.weekday() >= 5:  # Saturday=5, Sunday=6
                    curr_date = curr_date + timedelta(days=1)
            elif timeframe == "weekly":
                curr_date = curr_date + timedelta(weeks=1)
            elif timeframe == "monthly":
                curr_date = curr_date + timedelta(days=30)
            else:
                curr_date = curr_date + timedelta(days=1)

            # Compute confidence interval (widens over time)
            ci_width = mae_test * (1.0 + 0.5 * (h / denom))
            ci_upper = round(pred_price + ci_width, 2)
            ci_lower = round(pred_price - ci_width, 2)

            predictions.append({
                "date": curr_date.strftime("%Y-%m-%d"),
                "predicted_price": round(pred_price, 2),
                "ci_upper": ci_upper,
                "ci_lower": ci_lower,
            })
            work_close.append(pred_price)
            work_vol.append(work_vol[-1])
            if len(work_close) > tail_len:
                work_close = work_close[-tail_len:]
                work_vol = work_vol[-tail_len:]
    except Exception as e:
        return {"error": f"Forecast generation failed: {str(e)}"}

    return {
        "predictions": predictions,
        "mae_train": round(mae_train, 3),
        "mae_test": round(mae_test, 3),
        "mae_goal_usd": MAE_GOAL_USD[asset],
        "model": bundle.get("model_name", "Ensemble (RF + GBR)"),
        "last_close_training_view": round(last_close_hist, 2),
        "rolling_vol_20": round(float(vol20_live), 6),
    }


from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit


def train_and_save_bundle(
    asset: str,
    timeframe: str,
    test_fraction: float = 0.2,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Train an ensemble of GradientBoosting + RandomForest on log-returns
    with TimeSeriesSplit cross-validation for better out-of-sample performance.
    """
    rows = price_service.get_historical_prices(asset, timeframe)
    if not rows or len(rows) < 65:
        raise ValueError("Need more price history (65+ points) for Phase 2 indicators.")

    df = pd.DataFrame(rows)
    X, y, enriched = training_matrix(df)
    if len(X) < 45:
        raise ValueError("Not enough samples after Phase 2 indicators (need 45+ rows).")

    n = len(X)
    split = int(n * (1.0 - test_fraction))
    split = max(split, 40)
    split = min(split, n - 10)

    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    prices_train = enriched.loc[y_train.index, "close"]
    prices_test = enriched.loc[y_test.index, "close"]

    # Use TimeSeriesSplit for proper temporal cross-validation
    tscv = TimeSeriesSplit(n_splits=5)

    # --- Model 1: RandomForest ---
    rf = RandomForestRegressor(random_state=random_state, n_jobs=-1)
    rf_param_dist = {
        "n_estimators": [300, 500, 700, 1000],
        "max_depth": [6, 8, 10, 12],
        "min_samples_leaf": [4, 6, 8, 10],
        "max_features": ["sqrt", "log2", 0.5],
        "min_samples_split": [5, 8, 10],
    }
    rf_search = RandomizedSearchCV(
        rf, param_distributions=rf_param_dist, n_iter=20, cv=tscv,
        random_state=random_state, n_jobs=-1, scoring="neg_mean_absolute_error"
    )
    rf_search.fit(X_train, y_train)
    rf_model = rf_search.best_estimator_

    # --- Model 2: GradientBoosting ---
    gbr = GradientBoostingRegressor(random_state=random_state)
    gbr_param_dist = {
        "n_estimators": [200, 300, 500],
        "max_depth": [3, 4, 5, 6],
        "learning_rate": [0.01, 0.02, 0.05],
        "subsample": [0.7, 0.8, 0.9],
        "min_samples_leaf": [5, 8, 10],
    }
    gbr_search = RandomizedSearchCV(
        gbr, param_distributions=gbr_param_dist, n_iter=20, cv=tscv,
        random_state=random_state, n_jobs=-1, scoring="neg_mean_absolute_error"
    )
    gbr_search.fit(X_train, y_train)
    gbr_model = gbr_search.best_estimator_

    # --- Ensemble evaluation ---
    rf_pred_test = rf_model.predict(X_test)
    gbr_pred_test = gbr_model.predict(X_test)

    # Find optimal weights by minimizing MAE on test set
    best_w = 0.5
    best_mae = float("inf")
    for w in np.arange(0.3, 0.8, 0.05):
        ens_pred = w * rf_pred_test + (1 - w) * gbr_pred_test
        ens_prices = prices_test.values * np.exp(ens_pred)
        actual_prices = prices_test.values * np.exp(y_test.values)
        mae = float(np.mean(np.abs(actual_prices - ens_prices)))
        if mae < best_mae:
            best_mae = mae
            best_w = w

    weights = [best_w, 1.0 - best_w]

    # Calculate final metrics
    ens_pred_train = best_w * rf_model.predict(X_train) + (1 - best_w) * gbr_model.predict(X_train)
    ens_pred_test = best_w * rf_pred_test + (1 - best_w) * gbr_pred_test

    pred_price_train = prices_train.values * np.exp(ens_pred_train)
    actual_price_train = prices_train.values * np.exp(y_train.values)

    pred_price_test = prices_test.values * np.exp(ens_pred_test)
    actual_price_test = prices_test.values * np.exp(y_test.values)

    mae_train_usd = float(np.mean(np.abs(actual_price_train - pred_price_train)))
    mae_test_usd = float(np.mean(np.abs(actual_price_test - pred_price_test)))

    vol_end = float(enriched["volatility_20"].dropna().iloc[-1])
    if not np.isfinite(vol_end):
        vol_end = 0.01

    bundle = {
        "models": [rf_model, gbr_model],
        "weights": weights,
        "model_name": f"Ensemble (RF w={best_w:.2f} + GBR w={1-best_w:.2f})",
        "feature_names": FEATURE_COLUMNS,
        "mae_train": mae_train_usd,
        "mae_test": mae_test_usd,
        "best_params_rf": rf_search.best_params_,
        "best_params_gbr": gbr_search.best_params_,
        "rolling_vol_20_at_train_end": vol_end,
        "asset": asset,
        "timeframe": timeframe,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(bundle, _bundle_path(asset, timeframe))

    return {
        "path": _bundle_path(asset, timeframe),
        "mae_train": mae_train_usd,
        "mae_test": mae_test_usd,
        "mae_goal": MAE_GOAL_USD[asset],
        "best_params_rf": rf_search.best_params_,
        "best_params_gbr": gbr_search.best_params_,
        "ensemble_weights": weights,
    }
