# Gold & Silver Price Predictor System
## Complete System Design Document

---

**Document Version:** 1.0  
**Date:** February 4, 2026  
**Project Name:** Gold & Silver Price Predictor  
**Document Type:** System Design Document (SDD)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Scope and Objectives](#3-scope-and-objectives)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Technology Stack](#6-technology-stack)
7. [System Architecture](#7-system-architecture)
8. [Data Strategy](#8-data-strategy)
9. [Machine Learning Models](#9-machine-learning-models)
10. [Technical Indicators](#10-technical-indicators)
11. [Use Cases](#11-use-cases)
12. [API Design](#12-api-design)
13. [Frontend Design](#13-frontend-design)
14. [Evaluation Metrics](#14-evaluation-metrics)
15. [Deployment Strategy](#15-deployment-strategy)
16. [Testing Strategy](#16-testing-strategy)
17. [Future Enhancements](#17-future-enhancements)
18. [Glossary](#18-glossary)

---

## 1. Executive Summary

### 1.1 Purpose

This document provides a comprehensive technical specification for the **Gold & Silver Price Predictor System**—a multi-horizon forecasting application designed to predict precious metal prices across daily, weekly, and monthly timeframes.

### 1.2 Project Overview

The system combines traditional time-series forecasting methods (ARIMA, SARIMA) with modern machine learning approaches (LSTM, Random Forest, Prophet) to deliver accurate price predictions for gold and silver commodities in the international market (USD).

### 1.3 Key Features

| Feature | Description |
|---------|-------------|
| Multi-Horizon Forecasting | Daily, weekly, and monthly predictions |
| Historical Price Charts | Interactive visualization with technical indicators |
| Profit/Loss Calculator | Calculate returns on hypothetical trades |
| Technical Analysis | RSI, MACD, Moving Averages, Bollinger Bands |
| Model Transparency | MAE/RMSE metrics displayed to users |
| Separate Asset Models | Independent models for Gold and Silver |

### 1.4 Target Users

- Individual investors analyzing precious metals
- Financial analysts researching commodity trends
- Students learning about time-series forecasting
- Portfolio managers assessing gold/silver allocation

---

## 2. System Overview

### 2.1 System Description

The Gold & Silver Price Predictor is a web-based application that:

1. **Collects** historical price data from Yahoo Finance
2. **Processes** data into multiple timeframes (daily/weekly/monthly)
3. **Calculates** technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
4. **Trains** separate ML models for each asset and timeframe
5. **Predicts** future prices with confidence intervals
6. **Displays** results through an interactive dashboard

### 2.2 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌──────────┐  ┌───────────────┐  ┌─────────────────────────┐  │
│  │  Charts  │  │ P/L Calculator│  │  Prediction Dashboard   │  │
│  └────┬─────┘  └───────┬───────┘  └────────────┬────────────┘  │
└───────┼────────────────┼───────────────────────┼────────────────┘
        │                │                       │
        └────────────────┼───────────────────────┘
                         │
                    ┌────▼────┐
                    │   API   │
                    │ Server  │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
   │  Data   │     │   ML    │     │Indicator│
   │ Service │     │ Models  │     │ Engine  │
   └────┬────┘     └────┬────┘     └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                    ┌────▼────┐
                    │ Yahoo   │
                    │ Finance │
                    └─────────┘
```

### 2.3 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                           │
│   Dashboard │ Charts │ P/L Calculator │ Predictions │ Indicators    │
└─────────────────────────────────────────────────────────────────────┬┘
                                                                      │
                               REST API                               │
                                                                      │
┌─────────────────────────────────────────────────────────────────────▼┐
│                        BACKEND (Python/FastAPI)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────────┐   │
│  │ Data Layer  │  │ ML Pipeline  │  │ Indicator Calculator      │   │
│  │             │  │              │  │                           │   │
│  │ • Fetcher   │  │ • ARIMA      │  │ • SMA/EMA                 │   │
│  │ • Cleaner   │  │ • SARIMA     │  │ • RSI                     │   │
│  │ • Resampler │  │ • LSTM       │  │ • MACD                    │   │
│  │ • Storage   │  │ • Prophet    │  │ • Bollinger Bands         │   │
│  │             │  │ • RandomForest│ │ • Gold-Silver Ratio       │   │
│  └─────────────┘  └──────────────┘  └───────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      DATA SOURCES         │
                    │  Yahoo Finance (GC=F,SI=F)│
                    └───────────────────────────┘
```

---

## 3. Scope and Objectives

### 3.1 In Scope (Version 1.0)

| Category | Items Included |
|----------|----------------|
| **Assets** | Gold (GC=F), Silver (SI=F) |
| **Market** | International (USD) |
| **Timeframes** | Daily, Weekly, Monthly |
| **Features** | Price charts, P/L calculator, predictions, indicators |
| **Models** | ARIMA, SARIMA, LSTM, Prophet, Random Forest |
| **Metrics** | MAE, RMSE, Directional Accuracy |

### 3.2 Out of Scope (Future Versions)

- Pakistani market (PKR prices)
- Real-time streaming prices
- Trading execution/integration
- Mobile application (React Native)
- Multi-currency support
- Alert/notification system

### 3.3 Project Objectives

1. **Accuracy**: Achieve MAE < $25 for daily gold predictions
2. **Usability**: Intuitive interface requiring no financial expertise
3. **Transparency**: Display model performance metrics prominently
4. **Scalability**: Architecture ready for additional assets/markets
5. **Performance**: API response time < 500ms for predictions

---

## 4. Functional Requirements

### 4.1 Data Management (FR-DM)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DM-01 | System shall fetch historical prices from Yahoo Finance | High |
| FR-DM-02 | System shall store daily OHLCV data for gold and silver | High |
| FR-DM-03 | System shall resample daily data into weekly and monthly | High |
| FR-DM-04 | System shall update prices daily via scheduled job | Medium |
| FR-DM-05 | System shall handle missing data through forward-fill | Medium |

### 4.2 Price Visualization (FR-PV)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PV-01 | System shall display line charts for historical prices | High |
| FR-PV-02 | System shall support daily, weekly, monthly chart views | High |
| FR-PV-03 | System shall overlay technical indicators on charts | High |
| FR-PV-04 | System shall allow users to toggle indicators on/off | Medium |
| FR-PV-05 | System shall display candlestick charts (optional view) | Low |

### 4.3 Profit/Loss Calculator (FR-PL)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PL-01 | User shall select asset (gold/silver) | High |
| FR-PL-02 | User shall input buy date and sell date | High |
| FR-PL-03 | System shall auto-populate prices from historical data | High |
| FR-PL-04 | User shall input quantity (ounces or grams) | High |
| FR-PL-05 | System shall calculate P/L: (Sell - Buy) × Quantity | High |
| FR-PL-06 | System shall calculate ROI: ((Sell-Buy)/Buy) × 100 | High |
| FR-PL-07 | System shall mark buy/sell points on chart | Medium |

### 4.4 Price Prediction (FR-PP)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PP-01 | System shall train separate models for gold and silver | High |
| FR-PP-02 | System shall train separate models per timeframe | High |
| FR-PP-03 | System shall provide daily predictions (next 1-5 days) | High |
| FR-PP-04 | System shall provide weekly predictions (next 1-4 weeks) | High |
| FR-PP-05 | System shall provide monthly predictions (next 1-3 months) | High |
| FR-PP-06 | System shall display prediction confidence intervals | High |
| FR-PP-07 | System shall retrain models weekly | Medium |

### 4.5 Model Evaluation (FR-ME)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ME-01 | System shall calculate MAE for each model | High |
| FR-ME-02 | System shall calculate RMSE for each model | High |
| FR-ME-03 | System shall calculate directional accuracy (%) | High |
| FR-ME-04 | System shall display metrics in Model Performance panel | High |
| FR-ME-05 | System shall show rolling 30/60/90 day MAE | Medium |

### 4.6 Technical Indicators (FR-TI)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TI-01 | System shall calculate SMA (20, 50, 200 periods) | High |
| FR-TI-02 | System shall calculate EMA (9, 21 periods) | High |
| FR-TI-03 | System shall calculate RSI (14 periods) | High |
| FR-TI-04 | System shall calculate MACD (12, 26, 9) | High |
| FR-TI-05 | System shall calculate Bollinger Bands (20, 2σ) | High |
| FR-TI-06 | System shall calculate Gold-Silver Ratio | High |
| FR-TI-07 | System shall display RSI/MACD as sub-charts | Medium |

---

## 5. Non-Functional Requirements

### 5.1 Performance (NFR-P)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-P-01 | API response time for predictions | < 500ms |
| NFR-P-02 | Chart rendering time | < 1 second |
| NFR-P-03 | Model training time (daily) | < 5 minutes |
| NFR-P-04 | Concurrent users supported | 100+ |

### 5.2 Reliability (NFR-R)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-R-01 | System uptime | 99.5% |
| NFR-R-02 | Data fetch success rate | 99% |
| NFR-R-03 | Model prediction success rate | 99.9% |
| NFR-R-04 | Automatic recovery from failures | Yes |

### 5.3 Usability (NFR-U)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-U-01 | Learning curve for new users | < 5 minutes |
| NFR-U-02 | Mobile-responsive design | Yes |
| NFR-U-03 | Accessibility (WCAG 2.1 AA) | Compliant |

### 5.4 Security (NFR-S)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-S-01 | HTTPS encryption | Required |
| NFR-S-02 | API rate limiting | 100 req/min |
| NFR-S-03 | Input validation | All endpoints |

### 5.5 Maintainability (NFR-M)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-M-01 | Code test coverage | > 80% |
| NFR-M-02 | Modular architecture | Yes |
| NFR-M-03 | Documentation coverage | All public APIs |

---

## 6. Technology Stack

### 6.1 Backend

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Language** | Python 3.11+ | Best ML/data science ecosystem |
| **Framework** | FastAPI | Modern, async, auto-documentation |
| **ML Libraries** | scikit-learn, statsmodels, prophet, tensorflow | Industry standards |
| **Data Processing** | pandas, numpy | Efficient data manipulation |
| **Data Fetching** | yfinance | Free Yahoo Finance API |
| **Task Scheduling** | APScheduler / Celery | Daily data updates & model retraining |

### 6.2 Frontend

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Framework** | React 18+ | Component-based, large ecosystem |
| **State Management** | Redux Toolkit | Predictable state, dev tools |
| **Charting** | TradingView Lightweight Charts | Professional financial charts |
| **Styling** | Tailwind CSS or CSS Modules | Rapid UI development |
| **HTTP Client** | Axios | Promise-based, interceptors |

### 6.3 Infrastructure

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Database** | SQLite (dev) / PostgreSQL (prod) | Simple to complex scaling |
| **Caching** | Redis | Fast prediction caching |
| **Containerization** | Docker | Consistent environments |
| **Orchestration** | Docker Compose | Multi-container management |
| **Hosting** | AWS / Render / Railway | Flexible deployment options |

### 6.4 Development Tools

| Tool | Purpose |
|------|---------|
| Git + GitHub | Version control |
| pytest | Python testing |
| Jest + React Testing Library | Frontend testing |
| Swagger/OpenAPI | API documentation |
| Jupyter Notebooks | Model experimentation |

---

## 7. System Architecture

### 7.1 Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                         │
│                                                                     │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────────────────┐ │
│  │   Dashboard   │ │    Charts     │ │   Prediction Panel        │ │
│  │   Component   │ │   Component   │ │   Component               │ │
│  └───────────────┘ └───────────────┘ └───────────────────────────┘ │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────────────────┐ │
│  │  P/L Calculator│ │  Indicators  │ │   Model Performance       │ │
│  │   Component   │ │   Panel      │ │   Component               │ │
│  └───────────────┘ └───────────────┘ └───────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┬──┘
                                                                   │
                              REST API                             │
                                                                   │
┌──────────────────────────────────────────────────────────────────▼──┐
│                          APPLICATION LAYER                          │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     API Controllers                          │   │
│  │  /prices  │  /predictions  │  /indicators  │  /profit-loss  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                       Services                               │   │
│  │  PriceService │ PredictionService │ IndicatorService │ PLSvc │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┬──┘
                                                                   │
┌──────────────────────────────────────────────────────────────────▼──┐
│                           DOMAIN LAYER                              │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   Data Module    │  │   ML Module      │  │ Indicator Module │  │
│  │                  │  │                  │  │                  │  │
│  │ • DataFetcher    │  │ • ARIMA Model    │  │ • SMACalculator  │  │
│  │ • DataCleaner    │  │ • SARIMA Model   │  │ • EMACalculator  │  │
│  │ • DataResampler  │  │ • LSTM Model     │  │ • RSICalculator  │  │
│  │ • DataStorage    │  │ • Prophet Model  │  │ • MACDCalculator │  │
│  │                  │  │ • RF Model       │  │ • BollingerCalc  │  │
│  │                  │  │ • ModelEvaluator │  │ • RatioCalculator│  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────────────────┬──┘
                                                                   │
┌──────────────────────────────────────────────────────────────────▼──┐
│                       INFRASTRUCTURE LAYER                          │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │     Database     │  │      Cache       │  │  External APIs   │  │
│  │   (PostgreSQL)   │  │     (Redis)      │  │  (Yahoo Finance) │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Data Flow Diagram

```
                     ┌─────────────────┐
                     │  Yahoo Finance  │
                     │    GC=F, SI=F   │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │  Data Fetcher   │
                     │  (yfinance)     │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │  Data Cleaner   │
                     │  (handle NaN)   │
                     └────────┬────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
       ┌──────────┐    ┌──────────┐    ┌──────────┐
       │  Daily   │    │  Weekly  │    │ Monthly  │
       │  Data    │    │  Resample│    │ Resample │
       └────┬─────┘    └────┬─────┘    └────┬─────┘
            │               │               │
            │    ┌──────────┴──────────┐    │
            │    │                     │    │
            ▼    ▼                     ▼    ▼
       ┌──────────────┐          ┌──────────────┐
       │   Technical  │          │     ML       │
       │  Indicators  │          │   Models     │
       └──────┬───────┘          └──────┬───────┘
              │                         │
              │    ┌────────────────────┘
              │    │
              ▼    ▼
       ┌──────────────┐
       │     API      │
       │   Response   │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │   Frontend   │
       │  Dashboard   │
       └──────────────┘
```

### 7.3 Model Training Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│                      ML TRAINING PIPELINE                          │
└────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Raw Prices  │────▶│ Feature     │────▶│ Train/Test  │
│ (10+ years) │     │ Engineering │     │ Split (80/20│
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┴───────────────────┐
                    │                                              │
                    ▼                                              ▼
             ┌─────────────┐                                ┌─────────────┐
             │ Training    │                                │ Testing     │
             │ Set (80%)   │                                │ Set (20%)   │
             └──────┬──────┘                                └──────┬──────┘
                    │                                              │
     ┌──────────────┼──────────────┐                               │
     │              │              │                               │
     ▼              ▼              ▼                               │
┌─────────┐   ┌─────────┐   ┌─────────┐                           │
│ ARIMA   │   │  LSTM   │   │ Prophet │                           │
│ Model   │   │  Model  │   │ Model   │                           │
└────┬────┘   └────┬────┘   └────┬────┘                           │
     │             │             │                                 │
     └─────────────┴─────────────┘                                 │
                    │                                              │
                    ▼                                              │
             ┌─────────────┐                                       │
             │ Predictions │◀──────────────────────────────────────┘
             │ on Test Set │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │ Evaluation  │
             │ MAE / RMSE  │
             │ Dir. Acc.   │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │ Save Best   │
             │ Model       │
             └─────────────┘
```

---

## 8. Data Strategy

### 8.1 Data Source

| Attribute | Value |
|-----------|-------|
| **Source** | Yahoo Finance |
| **Gold Symbol** | GC=F (COMEX Gold Futures) |
| **Silver Symbol** | SI=F (COMEX Silver Futures) |
| **Unit** | USD per troy ounce |
| **History** | 2000-01-01 to present |
| **Frequency** | Daily |

### 8.2 Data Fields

| Field | Description | Used For |
|-------|-------------|----------|
| Date | Trading date | X-axis, indexing |
| Open | Opening price | Candlestick charts |
| High | Highest price of day | Candlestick, ATR |
| Low | Lowest price of day | Candlestick, ATR |
| Close | Closing price | **Primary price**, all calculations |
| Volume | Trading volume | Volume indicators |

### 8.3 Data Preprocessing

```python
# Pseudocode for data preprocessing

def preprocess_data(raw_df):
    # 1. Handle missing values
    df = raw_df.ffill()  # Forward fill
    
    # 2. Remove weekends/holidays (already excluded)
    df = df[df['Volume'] > 0]
    
    # 3. Create resampled versions
    daily = df.copy()
    weekly = df.resample('W').last()
    monthly = df.resample('M').last()
    
    return daily, weekly, monthly
```

### 8.4 Data Storage Schema

**Table: prices**

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| asset | VARCHAR(10) | 'gold' or 'silver' |
| date | DATE | Trading date |
| open | DECIMAL(10,2) | Opening price |
| high | DECIMAL(10,2) | High price |
| low | DECIMAL(10,2) | Low price |
| close | DECIMAL(10,2) | Closing price |
| volume | BIGINT | Trading volume |
| created_at | TIMESTAMP | Record creation time |

**Table: predictions**

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| asset | VARCHAR(10) | 'gold' or 'silver' |
| timeframe | VARCHAR(10) | 'daily', 'weekly', 'monthly' |
| prediction_date | DATE | Date prediction was made |
| target_date | DATE | Date being predicted |
| predicted_price | DECIMAL(10,2) | Predicted price |
| actual_price | DECIMAL(10,2) | Actual price (filled later) |
| model_name | VARCHAR(50) | Model used |
| created_at | TIMESTAMP | Record creation time |

---

## 9. Machine Learning Models

### 9.1 Model Overview

| Model | Use Case | Timeframe | Strengths |
|-------|----------|-----------|-----------|
| **ARIMA** | Baseline daily | Daily | Simple, interpretable |
| **SARIMA** | Seasonal patterns | Weekly/Monthly | Handles seasonality |
| **LSTM** | Complex patterns | Daily/Weekly | Captures non-linear relationships |
| **Prophet** | Long-term trends | Monthly | Easy tuning, handles holidays |
| **Random Forest** | Feature-based | All | Uses technical indicators |

### 9.2 Model Details

#### 9.2.1 ARIMA (AutoRegressive Integrated Moving Average)

**Purpose:** Baseline model for daily predictions

**Parameters:**
- p (AR order): 5
- d (differencing): 1
- q (MA order): 2

**Implementation:**
```python
from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(train_data, order=(5, 1, 2))
fitted = model.fit()
forecast = fitted.forecast(steps=5)
```

#### 9.2.2 SARIMA (Seasonal ARIMA)

**Purpose:** Weekly and monthly predictions with seasonal patterns

**Parameters:**
- Order: (1, 1, 1)
- Seasonal Order: (1, 1, 1, 52) for weekly / (1, 1, 1, 12) for monthly

#### 9.2.3 LSTM (Long Short-Term Memory)

**Purpose:** Capture complex, non-linear price patterns

**Architecture:**
```
Input Layer (60 timesteps)
    ↓
LSTM Layer (50 units)
    ↓
Dropout (0.2)
    ↓
LSTM Layer (50 units)
    ↓
Dropout (0.2)
    ↓
Dense Layer (1 unit)
    ↓
Output (Predicted Price)
```

**Hyperparameters:**
- Sequence length: 60 days
- LSTM units: 50
- Dropout: 0.2
- Optimizer: Adam
- Loss: MSE
- Epochs: 100
- Batch size: 32

#### 9.2.4 Facebook Prophet

**Purpose:** Long-term trend and seasonality modeling

**Configuration:**
```python
from prophet import Prophet

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.05
)
```

#### 9.2.5 Random Forest Regressor

**Purpose:** Multi-feature regression using technical indicators

**Features Used:**
- Lagged prices: Close_t-1, Close_t-2, ..., Close_t-10
- Moving averages: SMA20, SMA50, EMA9, EMA21
- Momentum: RSI14
- MACD values
- Day of week, Month

**Hyperparameters:**
- n_estimators: 100
- max_depth: 15
- min_samples_split: 5
- random_state: 42

### 9.3 Training Configuration

**Total Models:** 6 (2 assets × 3 timeframes)

| Asset | Timeframe | Primary Model | Fallback Model |
|-------|-----------|---------------|----------------|
| Gold | Daily | LSTM | ARIMA |
| Gold | Weekly | SARIMA | Random Forest |
| Gold | Monthly | Prophet | SARIMA |
| Silver | Daily | LSTM | ARIMA |
| Silver | Weekly | SARIMA | Random Forest |
| Silver | Monthly | Prophet | SARIMA |

### 9.4 Training Schedule

| Task | Frequency | Time |
|------|-----------|------|
| Data update | Daily | 00:30 UTC |
| Daily model retrain | Weekly | Sunday 01:00 UTC |
| Weekly model retrain | Monthly | 1st of month |
| Monthly model retrain | Quarterly | 1st of quarter |

---

## 10. Technical Indicators

### 10.1 Moving Averages

#### Simple Moving Average (SMA)

**Formula:**
```
SMA(n) = (P1 + P2 + ... + Pn) / n
```

**Periods used:** 20, 50, 200

**Implementation:**
```python
def calculate_sma(series, period):
    return series.rolling(window=period).mean()
```

#### Exponential Moving Average (EMA)

**Formula:**
```
EMA_today = (Price_today × k) + (EMA_yesterday × (1 - k))
where k = 2 / (n + 1)
```

**Periods used:** 9, 21

### 10.2 Relative Strength Index (RSI)

**Formula:**
```
RS = Average Gain / Average Loss
RSI = 100 - (100 / (1 + RS))
```

**Period:** 14

**Interpretation:**
- RSI > 70: Overbought
- RSI < 30: Oversold

**Implementation:**
```python
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

### 10.3 MACD (Moving Average Convergence Divergence)

**Components:**
- MACD Line: EMA(12) - EMA(26)
- Signal Line: EMA(9) of MACD Line
- Histogram: MACD Line - Signal Line

**Implementation:**
```python
def calculate_macd(series):
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram
```

### 10.4 Bollinger Bands

**Components:**
- Middle Band: SMA(20)
- Upper Band: SMA(20) + 2σ
- Lower Band: SMA(20) - 2σ

**Implementation:**
```python
def calculate_bollinger(series, period=20, std_dev=2):
    middle = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return upper, middle, lower
```

### 10.5 Gold-Silver Ratio

**Formula:**
```
Ratio = Gold Price / Silver Price
```

**Interpretation:**
- High ratio (>80): Silver undervalued relative to gold
- Low ratio (<60): Gold undervalued relative to silver
- Historical average: ~65-70

---

## 11. Use Cases

### 11.1 Use Case Diagram

```
                    ┌─────────────────────────────────┐
                    │       Price Predictor System    │
                    │                                 │
     ┌──────┐       │  ┌──────────────────────────┐  │
     │      │       │  │   UC1: View Price Chart  │  │
     │      │───────┼─▶│                          │  │
     │      │       │  └──────────────────────────┘  │
     │      │       │                                 │
     │      │       │  ┌──────────────────────────┐  │
     │ User │───────┼─▶│  UC2: Calculate P/L      │  │
     │      │       │  └──────────────────────────┘  │
     │      │       │                                 │
     │      │       │  ┌──────────────────────────┐  │
     │      │───────┼─▶│  UC3: View Predictions   │  │
     │      │       │  └──────────────────────────┘  │
     │      │       │                                 │
     │      │       │  ┌──────────────────────────┐  │
     │      │───────┼─▶│  UC4: Analyze Indicators │  │
     │      │       │  └──────────────────────────┘  │
     │      │       │                                 │
     │      │       │  ┌──────────────────────────┐  │
     │      │───────┼─▶│  UC5: View Model Metrics │  │
     └──────┘       │  └──────────────────────────┘  │
                    │                                 │
                    └─────────────────────────────────┘
```

### 11.2 Use Case Descriptions

#### UC1: View Price Chart

| Attribute | Description |
|-----------|-------------|
| **Actor** | User |
| **Precondition** | Historical data is available |
| **Main Flow** | 1. User selects asset (Gold/Silver)<br>2. User selects timeframe (Daily/Weekly/Monthly)<br>3. System displays price chart<br>4. User optionally enables indicators |
| **Postcondition** | Chart is displayed with selected options |
| **Alternative Flow** | If data unavailable, show error message |

#### UC2: Calculate Profit/Loss

| Attribute | Description |
|-----------|-------------|
| **Actor** | User |
| **Precondition** | Historical data is available |
| **Main Flow** | 1. User selects asset<br>2. User enters buy date<br>3. System auto-fills buy price<br>4. User enters sell date<br>5. System auto-fills sell price<br>6. User enters quantity<br>7. System calculates P/L and ROI<br>8. System marks points on chart |
| **Postcondition** | P/L result displayed |
| **Alternative Flow** | If date not in dataset, prompt manual entry |

#### UC3: View Predictions

| Attribute | Description |
|-----------|-------------|
| **Actor** | User |
| **Precondition** | Models are trained |
| **Main Flow** | 1. User selects asset<br>2. User selects prediction horizon<br>3. System displays predicted price<br>4. System shows confidence interval<br>5. System shows model performance metrics |
| **Postcondition** | Prediction displayed with context |

#### UC4: Analyze Indicators

| Attribute | Description |
|-----------|-------------|
| **Actor** | User |
| **Precondition** | Chart is displayed |
| **Main Flow** | 1. User opens indicator panel<br>2. User toggles desired indicators<br>3. System calculates and overlays indicators<br>4. User interprets signals |
| **Postcondition** | Indicators displayed on chart |

#### UC5: View Model Metrics

| Attribute | Description |
|-----------|-------------|
| **Actor** | User |
| **Precondition** | Models are trained and evaluated |
| **Main Flow** | 1. User opens Model Performance panel<br>2. System displays MAE, RMSE per model<br>3. System displays directional accuracy<br>4. User compares model reliability |
| **Postcondition** | Metrics displayed |

---

## 12. API Design

### 12.1 API Endpoints

#### Prices API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/prices/{asset}` | Get historical prices |
| GET | `/api/prices/{asset}/latest` | Get latest price |

**GET /api/prices/{asset}**

Query Parameters:
- `timeframe`: daily | weekly | monthly
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

Response:
```json
{
  "asset": "gold",
  "timeframe": "daily",
  "data": [
    {"date": "2024-01-15", "close": 2032.50},
    {"date": "2024-01-16", "close": 2028.30}
  ]
}
```

#### Predictions API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/predictions/{asset}` | Get predictions |

**GET /api/predictions/{asset}**

Query Parameters:
- `horizon`: daily | weekly | monthly

Response:
```json
{
  "asset": "gold",
  "horizon": "daily",
  "predictions": [
    {
      "date": "2024-01-17",
      "predicted_price": 2045.20,
      "lower_bound": 2020.00,
      "upper_bound": 2070.00
    }
  ],
  "model": "LSTM",
  "mae": 18.40,
  "rmse": 24.10,
  "accuracy": 0.62
}
```

#### Indicators API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/indicators/{asset}` | Get technical indicators |

**GET /api/indicators/{asset}**

Query Parameters:
- `indicators`: sma,ema,rsi,macd,bollinger (comma-separated)
- `timeframe`: daily | weekly | monthly

Response:
```json
{
  "asset": "gold",
  "timeframe": "daily",
  "indicators": {
    "sma": {"sma20": [...], "sma50": [...], "sma200": [...]},
    "rsi": {"rsi14": [...]},
    "macd": {"line": [...], "signal": [...], "histogram": [...]}
  }
}
```

#### Profit/Loss API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/profit-loss` | Calculate P/L |

**POST /api/profit-loss**

Request:
```json
{
  "asset": "gold",
  "buy_date": "2023-01-15",
  "sell_date": "2024-01-15",
  "quantity": 2.5,
  "unit": "oz"
}
```

Response:
```json
{
  "buy_price": 1920.50,
  "sell_price": 2032.30,
  "quantity": 2.5,
  "profit_loss": 279.50,
  "roi_percent": 5.82,
  "holding_days": 366
}
```

#### Model Metrics API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/models/metrics` | Get model performance |

Response:
```json
{
  "models": [
    {
      "asset": "gold",
      "horizon": "daily",
      "model_name": "LSTM",
      "mae": 18.40,
      "rmse": 24.10,
      "directional_accuracy": 0.62,
      "last_trained": "2024-01-14T01:00:00Z"
    }
  ]
}
```

---

## 13. Frontend Design

### 13.1 Page Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                           HEADER                                    │
│  Logo │ Gold │ Silver │ Compare │ About           [Theme Toggle]   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        MAIN DASHBOARD                               │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PRICE CHART                               │   │
│  │  [Daily] [Weekly] [Monthly]     [1M] [6M] [1Y] [5Y] [Max]   │   │
│  │                                                              │   │
│  │     ████████████████████████████████████████████            │   │
│  │    █                                              █          │   │
│  │   █                                                █         │   │
│  │  █████████████████████████████████████████████████          │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌───────────────────────┐  ┌───────────────────────────────────┐  │
│  │    RSI SUB-CHART      │  │      MACD SUB-CHART               │  │
│  │  ────────70────────   │  │  ═══════════════════════════════  │  │
│  │  ────────30────────   │  │                                   │  │
│  └───────────────────────┘  └───────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────────────┐  │
│  │   PREDICTION PANEL      │  │    P/L CALCULATOR               │  │
│  │                         │  │                                 │  │
│  │   Daily:  $2,045.20    │  │   Asset:    [Gold ▼]            │  │
│  │   Weekly: $2,080.50    │  │   Buy Date: [2023-01-15]        │  │
│  │   Monthly: $2,150.00   │  │   Sell Date:[2024-01-15]        │  │
│  │                         │  │   Quantity: [2.5] [oz ▼]      │  │
│  │   MAE: $18.40          │  │                                 │  │
│  │   Accuracy: 62%        │  │   Profit: +$279.50 (+5.82%)    │  │
│  └─────────────────────────┘  └─────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   INDICATOR TOGGLES                          │   │
│  │  [✓] SMA 20  [✓] SMA 50  [ ] SMA 200  [✓] EMA 9  [ ] EMA 21 │   │
│  │  [✓] RSI     [✓] MACD    [ ] Bollinger                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 13.2 Component Hierarchy

```
App
├── Header
│   ├── Logo
│   ├── Navigation
│   └── ThemeToggle
├── Dashboard
│   ├── AssetSelector
│   ├── TimeframeSelector
│   ├── PriceChart
│   │   ├── MainChart
│   │   ├── RSISubChart
│   │   └── MACDSubChart
│   ├── PredictionPanel
│   │   ├── DailyPrediction
│   │   ├── WeeklyPrediction
│   │   ├── MonthlyPrediction
│   │   └── ModelMetrics
│   ├── ProfitLossCalculator
│   │   ├── AssetInput
│   │   ├── DateInputs
│   │   ├── QuantityInput
│   │   └── ResultDisplay
│   └── IndicatorPanel
│       └── IndicatorToggles
└── Footer
```

### 13.3 Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, stacked panels |
| Tablet | 640px - 1024px | Two columns |
| Desktop | > 1024px | Full layout as shown |

---

## 14. Evaluation Metrics

### 14.1 Model Evaluation Metrics

#### Mean Absolute Error (MAE)

**Formula:**
```
MAE = (1/n) × Σ |Actual - Predicted|
```

**Interpretation:** Average dollar error per prediction

**Target:** 
- Daily: < $25
- Weekly: < $60
- Monthly: < $120

#### Root Mean Squared Error (RMSE)

**Formula:**
```
RMSE = √[(1/n) × Σ (Actual - Predicted)²]
```

**Interpretation:** Penalizes large errors more heavily

#### Directional Accuracy

**Formula:**
```
Accuracy = (Correct Direction Predictions / Total Predictions) × 100
```

**Target:** > 55% (better than random)

### 14.2 Metric Calculation Per Model

| Asset | Horizon | Target MAE | Target RMSE | Target Accuracy |
|-------|---------|------------|-------------|-----------------|
| Gold | Daily | < $25 | < $35 | > 55% |
| Gold | Weekly | < $60 | < $80 | > 58% |
| Gold | Monthly | < $120 | < $150 | > 60% |
| Silver | Daily | < $0.50 | < $0.70 | > 55% |
| Silver | Weekly | < $1.00 | < $1.40 | > 58% |
| Silver | Monthly | < $2.00 | < $2.80 | > 60% |

### 14.3 Rolling Evaluation Windows

Display metrics for multiple windows:
- Last 30 days
- Last 60 days
- Last 90 days

This shows model stability over time.

---

## 15. Deployment Strategy

### 15.1 Environment Setup

| Environment | Purpose | URL |
|-------------|---------|-----|
| Development | Local testing | localhost:3000 / localhost:8000 |
| Staging | Pre-production testing | staging.predictor.example.com |
| Production | Live system | predictor.example.com |

### 15.2 Docker Configuration

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/predictor
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=predictor
  
  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### 15.3 CI/CD Pipeline

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Push   │────▶│  Build  │────▶│  Test   │────▶│ Deploy  │
│  Code   │     │  Docker │     │  Suite  │     │Staging  │
└─────────┘     └─────────┘     └─────────┘     └────┬────┘
                                                     │
                                                     ▼
                                               ┌─────────┐
                                               │ Manual  │
                                               │ Approval│
                                               └────┬────┘
                                                    │
                                                    ▼
                                               ┌─────────┐
                                               │ Deploy  │
                                               │  Prod   │
                                               └─────────┘
```

---

## 16. Testing Strategy

### 16.1 Testing Pyramid

```
                    /\
                   /  \
                  / E2E \
                 /  Tests \
                /──────────\
               /            \
              / Integration  \
             /    Tests       \
            /──────────────────\
           /                    \
          /     Unit Tests       \
         /________________________\
```

### 16.2 Test Coverage Requirements

| Test Type | Coverage Target | Tools |
|-----------|-----------------|-------|
| Unit Tests | > 80% | pytest, Jest |
| Integration Tests | > 60% | pytest, Supertest |
| E2E Tests | Critical paths | Playwright |

### 16.3 Test Categories

#### Backend Unit Tests
- Data fetching and cleaning
- Indicator calculations
- Model prediction logic
- P/L calculations

#### Frontend Unit Tests
- Component rendering
- State management
- Utility functions

#### Integration Tests
- API endpoint responses
- Database operations
- Cache invalidation

#### E2E Tests
- User flow: View chart → Add indicators
- User flow: Calculate P/L
- User flow: View predictions

---

## 17. Future Enhancements

### Phase 2 (v2.0)
- [ ] Pakistani market (PKR prices)
- [ ] Real-time price streaming
- [ ] Price alerts / notifications
- [ ] User accounts and saved watchlists

### Phase 3 (v3.0)
- [ ] Mobile app (React Native)
- [ ] Additional commodities (Platinum, Copper)
- [ ] News sentiment integration
- [ ] Portfolio tracking

### Phase 4 (v4.0)
- [ ] Social features (share predictions)
- [ ] API for third-party integration
- [ ] Advanced backtesting engine
- [ ] Custom model upload

---

## 18. Glossary

| Term | Definition |
|------|------------|
| **ARIMA** | AutoRegressive Integrated Moving Average - statistical model for time series |
| **Bollinger Bands** | Volatility indicator with upper/lower bands around a moving average |
| **EMA** | Exponential Moving Average - weighted average giving more weight to recent prices |
| **LSTM** | Long Short-Term Memory - type of recurrent neural network for sequences |
| **MAE** | Mean Absolute Error - average absolute difference between predicted and actual |
| **MACD** | Moving Average Convergence Divergence - trend-following momentum indicator |
| **OHLCV** | Open, High, Low, Close, Volume - standard price data format |
| **Prophet** | Facebook's time series forecasting library |
| **RMSE** | Root Mean Squared Error - square root of average squared errors |
| **RSI** | Relative Strength Index - momentum oscillator measuring speed of price changes |
| **SARIMA** | Seasonal ARIMA - ARIMA with seasonal components |
| **SMA** | Simple Moving Average - unweighted average of last n prices |
| **Troy Ounce** | Unit of measurement for precious metals (31.1 grams) |

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-04 | System | Initial document |

---

**End of Document**
