from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from app.services import forecast_service
from app.services import data_fetcher
from app.services import price_service
from app.services import reality_check_service
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

async def schedule_daily_update():
    while True:
        try:
            print(f"[{datetime.now()}] Running scheduled data update...")
            # Run synchronous update in thread pool
            await asyncio.to_thread(data_fetcher.update_all_data)
            print(f"[{datetime.now()}] Data update completed successfully.")
        except Exception as e:
            print(f"[{datetime.now()}] Error updating data: {e}")
            
        # Calculate time until next 01:00 AM
        now = datetime.now()
        next_run = now.replace(hour=1, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
            
        seconds_to_wait = (next_run - now).total_seconds()
        print(f"Next update scheduled for {next_run} (in {seconds_to_wait / 3600:.2f} hours)")
        await asyncio.sleep(seconds_to_wait)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run initial update to ensure database is consistent
    print("Performing initial data synchronization...")
    try:
        await asyncio.to_thread(data_fetcher.update_all_data)
    except Exception as e:
        print(f"Initial sync failed: {e}")
        
    # Start background task for subsequent daily updates
    task = asyncio.create_task(schedule_daily_update())
    yield
    # Shutdown: cancel task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Gold & Silver Price Predictor API",
    description="API for multi-horizon price forecasting of precious metals",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/api/predict/{asset}")
async def predict_prices(asset: str, timeframe: str = "daily"):
    """
    Price path forecast: Random Forest on RSI, moving averages, and volatility,
    with volatility-aware caps (replaces recursive LSTM to avoid runaway paths).
    """
    steps_map = {"daily": 30, "weekly": 4, "monthly": 1}
    steps = steps_map.get(timeframe, 30)

    asset_key = asset.lower().strip()
    if asset_key not in ("gold", "silver"):
        raise HTTPException(status_code=400, detail="Asset must be 'gold' or 'silver'.")

    try:
        result = forecast_service.generate_forecast(asset_key, timeframe, steps)

        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])

        latest = price_service.get_latest_price(asset_key)
        last_close = float(latest["close"]) if latest and latest.get("close") is not None else None

        return {
            "asset": asset_key,
            "timeframe": timeframe,
            "model": result.get("model", "RandomForest"),
            "last_close": last_close,
            "predictions": result["predictions"],
            "mean_absolute_error_train": result.get("mae_train"),
            "mean_absolute_error_test": result.get("mae_test"),
            "mae_goal_usd": result.get("mae_goal_usd"),
            "rolling_volatility_20": result.get("rolling_vol_20"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.models import ProfitLossRequest, SavePredictionRequest
from app.services import calculator_service

@app.post("/api/profit-loss")
async def calculate_pl(request: ProfitLossRequest):
    """Calculate profit/loss for a hypothetical trade."""
    try:
        result = calculator_service.calculate_profit_loss(
            request.asset.lower().strip(),
            request.buy_date,
            request.sell_date,
            request.quantity,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predictions/save")
async def save_predictions(request: SavePredictionRequest):
    """Save a forecast path for future reality check."""
    try:
        count = await reality_check_service.save_predictions(
            request.asset, 
            request.timeframe, 
            [p.dict() for p in request.predictions]
        )
        return {"status": "success", "saved_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predictions/history")
async def get_prediction_history(asset: Optional[str] = None):
    """Retrieve saved predictions and compare with reality."""
    try:
        data = await reality_check_service.get_reality_checks(asset)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@app.get("/health")
async def health_check():
    return {"status": "healthy", "last_data_update": data_fetcher.LAST_UPDATE}

def _normalize_asset(asset: str) -> str:
    key = asset.lower().strip()
    if key not in ("gold", "silver"):
        raise HTTPException(status_code=400, detail="Asset must be 'gold' or 'silver'.")
    return key

@app.get("/api/prices/{asset}")
async def get_prices(asset: str, timeframe: str = "daily", range: str = "all"):
    """
    Get historical prices for an asset (gold/silver).
    Timeframe: daily, weekly, monthly
    Range: all, monthly, weekly, daily (hours)
    """
    asset_key = _normalize_asset(asset)
    try:
        if range == "daily":
            data = price_service.get_intraday_prices(asset_key)
        else:
            limit = None
            if range == "weekly":
                limit = 7
            elif range == "monthly":
                limit = 30

            data = price_service.get_historical_prices(asset_key, timeframe, limit)

        return {"asset": asset_key, "timeframe": timeframe, "range": range, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prices/{asset}/latest")
async def get_latest_price(asset: str):
    """Get the latest available price."""
    asset_key = _normalize_asset(asset)
    try:
        data = price_service.get_latest_price(asset_key)
        return {"asset": asset_key, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount the frontend directory at the root
# Structure: backend/app/main.py -> backend/ -> project_root/ -> frontend/
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Gold & Silver Price Predictor API (Frontend not found)",
            "status": "active",
            "version": "1.0.0"
        }

