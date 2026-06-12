# 🪙 Silver & Gold Price Predictor: Technical Documentation

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)](https://pytorch.org/)
[![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Chart.js](https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white)](https://www.chartjs.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

---

## 📖 1. Executive Summary
The **Silver & Gold Price Predictor** is a sophisticated, industrial-grade analytical platform designed to provide precision forecasting for precious metals. In an era where commodity markets are influenced by complex global factors—from inflation rates to geopolitical tensions—this system provides a quantitative edge by applying state-of-the-art **Deep Learning (LSTM)** to historical price sequences.

The platform serves as a complete ecosystem for traders and analysts. It doesn't just show where the price was; it predicts where it's going. With a focus on high availability, architectural scalability, and a premium "AdminVault" aesthetic, this project represents the intersection of financial expertise and modern AI engineering.

---

## 🏗️ 2. Comprehensive System Architecture

The system is architected using a decoupled **three-tier model**, ensuring that the data processing, machine learning logic, and presentation layers can evolve independently without causing systemic failures.

### 2.1 The Presentation Layer (Frontend)
The frontend is a single-page application (SPA) developed using **Vanilla JavaScript (ES6+)** and **modern CSS3**. 
*   **Dynamic Dashboard**: Utilizing `flexbox` and `grid` layouts for a responsive experience that adapts from 4K monitors to mobile devices.
*   **Visual Engine**: Built on **Chart.js**, featuring custom-rendered line charts with interactive tooltips, crosshair tracking, and multi-series data (Historical vs. Predicted).
*   **Aesthetic System**: The UI follows a "Dark Mode" glassmorphic design system, using semi-transparent backgrounds, vibrant accent colors (Indigo for Silver, Amber for Gold), and subtle micro-animations for a premium feel.

### 2.2 The Application Layer (Backend)
Powered by **FastAPI**, the backend acts as the central nervous system.
*   **Asynchronous Processing**: Every endpoint is `async`, allowing for non-blocking I/O operations. This is critical when multiple users are requesting heavy ML predictions simultaneously.
*   **Background Orchestration**: Integrated `asyncio` tasks handle daily data updates. The system uses a "Lifespan" manager to start and stop background threads gracefully.
*   **Service-Oriented Design**: Business logic is separated into specialized service modules:
    *   `price_service`: Handles disk I/O and CSV parsing.
    *   `lstm_service`: Manages PyTorch model loading and inference.
    *   `calculator_service`: Performs mathematical trade simulations.

### 2.3 The AI Layer (PyTorch Engine)
This is where the complex pattern recognition happens.
*   **Tensor Management**: Utilizing PyTorch for optimized matrix operations, with CUDA support for hardware acceleration when available.
*   **Persistence**: Trained model weights are serialized into `.pth` files, while data scalers are persisted as `.pkl` files via Joblib to ensure identical preprocessing during training and inference.

---

## 📁 3. Directory Structure

```text
Silver/
├── backend/                # FastAPI Application
│   ├── app/                # Core logic package
│   │   ├── services/       # Logic & ML services
│   │   ├── models/         # Pydantic data schemas
│   │   └── main.py         # API Entry point
│   ├── data/               # Historical CSV storage
│   ├── models/             # Saved PyTorch weights (.pth)
│   ├── scripts/            # Training & maintenance scripts
│   └── requirements.txt    # Dependencies
├── frontend/               # Web Interface
│   ├── css/                # Stylesheets (style.css)
│   ├── js/                 # Dashboard logic (app.js)
│   └── index.html          # Main entry
├── docs/                   # Documentation
└── run_all.bat             # Startup script
```

---

## 📊 4. Data Engineering Pipeline

Data is the lifeblood of this system. Our pipeline is designed for robustness, consistency, and "Self-Healing."

### 4.1 Data Acquisition & Storage
The system targets **GC=F (Gold Futures)** and **SI=F (Silver Futures)** from the COMEX exchange.
*   **MongoDB Atlas Engine**: Historical data is stored in a fully-managed MongoDB Atlas cloud cluster. This provides high availability, global scalability, and a flexible document-based structure.
*   **Data Model**: Prices are stored as documents in the `prices` collection, featuring indexed `date` and `asset` fields for sub-millisecond retrieval.
*   **Automated Updates**: A scheduled task in `main.py` runs every day at 01:00 AM. It fetches the latest candles from Yahoo Finance and performs a bulk **Upsert** operation to keep the cloud data fresh.

### 3.2 Resampling & Cleaning (`price_service.py`)
Raw financial data is often "noisy." Our service layer applies several filters:
*   **Handling Gaps**: Financial markets close on weekends. The service handles these gaps using forward-filling (`ffill`) or resampling.
*   **Multi-Timeframe Support**:
    *   **Daily**: Direct retrieval of daily closing prices.
    *   **Weekly**: Resamples daily data to weekly buckets (`df.resample('W').last()`), capturing the weekly settlement price.
    *   **Monthly**: Aggregates data to month-end (`df.resample('ME').last()`) for long-term trend analysis.

---

## 🧠 5. Machine Learning Implementation (Deep Dive)

### 4.1 The Random Forest Architecture
The core model is a **Random Forest Regressor** trained to predict next-period returns. Traditional models often "drift" or "crash" when predicting absolute prices recursively; our system solves this by modeling the *velocity* and *volatility* of the market.

*   **Logic Detail**:
    *   **Returns-Based**: The model learns to predict the percentage change (`Close_t+1 / Close_t - 1`). This ensures the model is stationary and doesn't get "lost" at price levels it hasn't seen before.
    *   **Market Context**: Input features include RSI (14), MACD (Normalized), ATR (Average True Range), and 20-day Rolling Volatility.
    *   **Ensemble Learning**: Uses 500 decision trees to average out noise and provide a stable consensus prediction.

### 4.2 Training Workflow (`train_forecast_rf.py`)
The training script implements a rigorous pipeline:
1.  **Indicator Enrichment**: Computes technical indicators across the entire historical series from MongoDB.
2.  **Chronological Split**: Uses an 80/20 "Walk-Forward" split. It trains on the past and validates on the most recent 20% of data to ensure real-world generalizability.
3.  **USD MAE Evaluation**: Although the model trains on percentage returns, it evaluates performance in **Real USD** to meet strict accuracy targets ($4 for Silver, $10 for Gold).

### 4.3 Multi-Step Path Stability
Generating a forecast requires predicting a path. To prevent the "Unrealistic Crash" behavior common in recursive models:
1.  **Volatility Clipping**: Each step's predicted return is clipped to 2.5 standard deviations of recent market movement.
2.  **Mean Reversion Pressure**: The path is lightly blended toward the 20-day moving average as the horizon increases, representing the natural tendency of markets to consolidate.

---

## 🛠️ 6. Detailed Functional Reference

### 5.1 Backend: `main.py`
The entry point of the application.
*   **`lifespan`**: An async context manager that starts the background data update task when the server boots and cancels it cleanly on shutdown.
*   **`schedule_daily_update()`**: A recursive loop that calculates the time until 1:00 AM and sleeps until then, ensuring data is always fresh.
*   **Endpoints**:
    *   `GET /`: Health check and versioning.
    *   `GET /api/prices/{asset}`: Historical data gateway.
    *   `GET /api/predict/{asset}`: The AI engine trigger.
    *   `POST /api/profit-loss`: The calculator logic.

### 5.2 Backend: `price_service.py`
*   **`get_historical_prices(asset, timeframe)`**:
    *   *Input*: Asset name and period.
    *   *Logic*: Reads CSV from `DATA_DIR`, converts 'Date' column to datetime objects, applies resampling, and returns a sanitized list of dictionaries for JSON serialization.
*   **`get_latest_price(asset)`**: A helper that calls the historical service and returns the tail of the list.

### 5.3 Backend: `calculator_service.py`
*   **`calculate_profit_loss(asset, buy_date, sell_date, qty)`**:
    *   *Logic*: It scans the historical CSV for the exact (or nearest) buy and sell dates.
    *   *Formula*: `Net = (SellPrice - BuyPrice) * Quantity`.
    *   *Percentage*: `((SellPrice / BuyPrice) - 1) * 100`.

### 5.4 Frontend: `app.js`
*   **`renderChart(canvasId, dataList, label, color)`**:
    *   *Destruction Logic*: Before creating a new chart, it checks the `charts` global object. If a chart exists on that canvas, it calls `.destroy()` to prevent "Ghost Charts" (where old data appears on hover).
    *   *Styling*: Applies global chart defaults like hidden legends, indigo-tinted grid lines, and smooth tension (0.1) for lines.
*   **`calculatePL()`**:
    *   Collects values from the HTML inputs.
    *   Performs a `POST` request with a JSON body.
    *   Dynamic Rendering: Clears the result div and injects a "Stat Card" with green (profit) or blue (loss) styling based on the result.

---

## 🎨 7. Design System & Aesthetics
Aesthetics are not an afterthought in this project; they are a core requirement.
*   **Color Palette**:
    *   Background: `#0f172a` (Slate 900)
    *   Cards: `#1e293b` (Slate 800) with subtle borders.
    *   Primary Accent: `#6366f1` (Indigo 500)
    *   Secondary Accent: `#f59e0b` (Amber 500)
*   **Typography**: Uses **Inter** and **Outfit** via Google Fonts for a clean, modern financial look.
*   **Interactivity**: Every button has a `:hover` state with `scale(1.02)`, and every card has an `animate-fade-in` CSS animation to make the page feel "alive" on load.

---

## 📈 8. Technical Justification: Why LSTM?
Traditional statistics (like ARIMA) assume a linear relationship and stationary data. However, Gold prices are non-stationary and influenced by "Black Swan" events.
**LSTM** is the superior choice because:
1.  **Temporal Persistence**: It maintains a "Cell State" that can carry information across hundreds of time steps.
2.  **Non-Linearity**: Through its activation functions, it can model complex, sudden market shifts that simple averages would miss.
3.  **Sequence Learning**: It treats price not as a single point, but as a sequence, learning the "shape" of a bull market versus a bear market.

---

## 🚀 9. Future Roadmap & Scalability
The project is built with "Plugin Architecture" in mind:
*   **Adding Assets**: To add Platinum, simply add `platinum.csv` and the system will automatically handle the rest.
*   **Sentiment Analysis**: A planned update involves scraping financial news (Reuters/CNBC) and feeding the "Sentiment Score" into the LSTM as a second feature.
*   **WebSocket Integration**: For Day Traders, we plan to replace the daily CSV update with a real-time WebSocket stream for second-by-second price action.

---

## 📄 10. Deployment Guide
1.  **Install dependencies**: `pip install -r requirements.txt`
2.  **Prepare Models**: Run the training script for both assets.
3.  **Environment Variables**: Create a `.env` file for API keys if moving away from yfinance.
4.  **Production Server**: Use `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`.

---
**© 2026 Silver & Gold Predictor Team | Premium Market Intelligence**
