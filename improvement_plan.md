# Price Prediction Model Improvement Plan

The current price prediction model suffers from instability and "unrealistic" behavior (e.g., sudden market crashes) primarily because it predicts absolute price levels recursively. This approach is sensitive to noise and doesn't handle the non-stationary nature of financial prices well.

## 1. Core Architectural Shift: Return-Based Forecasting
Instead of predicting the next absolute price, the model will predict the **next-period return** (percentage change).

- **Why?** Returns are stationary (mean-reverting), whereas prices are not. This makes the model much more robust to price levels it hasn't seen before.
- **Implementation:** 
    - Change target variable to `next_return = (close_t+1 / close_t) - 1`.
    - Forecast logic: `predicted_price_t+1 = current_price_t * (1 + predicted_return)`.

## 2. Enhanced Feature Engineering
Expand the current technical indicator set to provide more "market context."

- **Volatility:** Add Average True Range (ATR) to measure price volatility in dollar terms.
- **Trend/Momentum:**
    - **MACD (Moving Average Convergence Divergence):** To capture trend shifts.
    - **Exponential Moving Averages (EMA):** Give more weight to recent prices.
- **Relative Strength:** Improve RSI implementation (already in progress).
- **Lagged Returns:** Include returns from the last 1, 3, and 5 days to capture short-term autocorrelation.

## 3. Stability & Multi-Step Path Improvements
Refine the `forecast_service.py` logic to prevent runaway predictions.

- **Dynamic Clipping:** Clip predicted returns based on historical volatility (e.g., 2 standard deviations) rather than using arbitrary dollar caps.
- **Decay Factor:** Gradually dampen the predicted returns as we move further into the future to represent increasing uncertainty.
- **Mean Reversion:** Keep the light blend towards a long-term moving average (e.g., MA50 or MA200) for long horizons, but make it less aggressive.

## 4. Model Training & Evaluation
- **Random Forest Tuning:** Optimize hyperparameters (`n_estimators`, `max_depth`, `min_samples_leaf`) using cross-validation.
- **Chronological Split:** Maintain the existing 80/20 train/test split to ensure no data leakage from the future.
- **MAE Metric:** Implement Mean Absolute Error (MAE) for returns and then convert back to dollar MAE for UI reporting, ensuring we meet the $4 (silver) and $10 (gold) targets.

## 5. Dashboard Separation
Ensure that the prediction service correctly filters and displays data based on the selected asset (Gold vs. Silver) to prevent data crosstalk.
## Phase 2: Advanced Tuning & Precision (Targeting <$10 Gold MAE)

While Phase 1 stabilized the "market crash" behavior, Phase 2 focuses on precision to meet the aggressive $10 target for Gold.

### 1. Advanced Technical Indicators
- **Bollinger Bands**: To capture price volatility relative to the 20-day mean.
- **Stochastic Oscillator**: To identify overbought/oversold conditions more accurately than RSI alone.
- **Log-Returns**: Transition from percentage returns to log-returns for more stable statistical properties.

### 2. Automated Hyperparameter Optimization
- Replace fixed Random Forest parameters with a **Randomized Search** (or a curated grid) to find the optimal `max_depth`, `min_samples_leaf`, and `n_estimators` for each specific asset.

### 3. Model Ensemble / Boosting
- Introduce **Gradient Boosting (XGBoost/LightGBM)** as an alternative to Random Forest. Boosting models are often better at capturing subtle non-linear patterns in financial data.

### 4. Implementation Steps:
1. [ ] Update `forecast_features.py` with Bollinger Bands and Stochastic Oscillator.
2. [ ] Implement `tune_model` logic in `forecast_service.py`.
3. [ ] Update training script to perform hyperparameter search.
4. [ ] Retrain and verify Gold MAE against the $10 target.

---

### Implementation Steps:
1. [ ] Update `forecast_features.py` to include new indicators and return-based targets.
2. [ ] Modify `forecast_service.py` to handle return-to-price conversion and dynamic clipping.
3. [ ] Update `train_forecast_rf.py` to evaluate the model based on return accuracy.
4. [ ] Retrain models and verify the "crash" behavior is resolved.
