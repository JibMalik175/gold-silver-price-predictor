import pandas as pd
import os
import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..mongodb import get_collection

ASSETS = {
    "gold": "GC=F",
    "silver": "SI=F"
}

def get_intraday_prices(asset: str) -> List[Dict]:
    """Get hourly prices for the last 24-48 hours using yfinance."""
    if asset.lower() not in ASSETS:
        raise ValueError("Asset must be 'gold' or 'silver'.")
    
    symbol = ASSETS[asset.lower()]
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="2d", interval="1h")
    
    if df.empty:
        return []
        
    df.reset_index(inplace=True)
    
    result = []
    for _, row in df.iterrows():
        # Handle different date column names in yfinance
        date_val = row.get('Datetime') or row.get('Date')
        result.append({
            "date": date_val.strftime('%Y-%m-%d %H:%M'),
            "close": round(row['Close'], 2),
            "open": round(row['Open'], 2),
            "high": round(row['High'], 2),
            "low": round(row['Low'], 2),
            "volume": int(row['Volume'])
        })
    return result

def get_historical_prices(asset: str, timeframe: str = "daily", limit: Optional[int] = None) -> List[Dict]:
    """
    Get historical prices for an asset from MongoDB Atlas.
    
    Args:
        asset: 'gold' or 'silver'
        timeframe: 'daily', 'weekly', 'monthly'
        limit: Number of days to look back
        
    Returns:
        List of dictionaries with date and close price
    """
    collection = get_collection("prices")

    if asset.lower() not in ASSETS:
        raise ValueError("Asset must be 'gold' or 'silver'.")

    query = {"asset": asset.lower()}
    if limit:
        cutoff_date = datetime.now() - timedelta(days=limit)
        query["date"] = {"$gte": cutoff_date}
    
    # Query documents
    cursor = collection.find(
        query,
        {"_id": 0, "date": 1, "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}
    ).sort("date", 1)
    
    docs = list(cursor)
    if not docs:
        return []
        
    # Convert to DataFrame for resampling
    df = pd.DataFrame(docs)
    
    # Ensure Date is datetime object
    # In MongoDB we store dates as ISODate (datetime objects)
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter/Resample based on timeframe
    if timeframe == 'weekly':
        df.set_index('date', inplace=True)
        df = df.resample('W').last().reset_index()
    elif timeframe == 'monthly':
        df.set_index('date', inplace=True)
        df = df.resample('ME').last().reset_index()
            
    # Format data for API
    result = []
    for _, row in df.iterrows():
        result.append({
            "date": row['date'].strftime('%Y-%m-%d'),
            "close": round(row['close'], 2),
            "open": round(row['open'], 2),
            "high": round(row['high'], 2),
            "low": round(row['low'], 2),
            "volume": int(row['volume']) if not pd.isna(row['volume']) else 0
        })
            
    return result

def get_latest_price(asset: str) -> Dict:
    """Get the latest price for an asset from MongoDB."""
    if asset.lower() not in ASSETS:
        raise ValueError("Asset must be 'gold' or 'silver'.")

    collection = get_collection("prices")
    latest = collection.find_one(
        {"asset": asset.lower()},
        {"_id": 0, "date": 1, "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1},
        sort=[("date", -1)]
    )
    
    if not latest:
        return None
            
    return {
        "date": latest['date'].strftime('%Y-%m-%d') if isinstance(latest['date'], datetime) else latest['date'],
        "close": round(latest['close'], 2),
        "open": round(latest['open'], 2),
        "high": round(latest['high'], 2),
        "low": round(latest['low'], 2),
        "volume": int(latest['volume'])
    }

def get_price_for_date(asset: str, target_date: str) -> Optional[Dict]:
    """Retrieve actual price document for a specific date from MongoDB."""
    collection = get_collection("prices")
    try:
        dt = datetime.strptime(target_date, '%Y-%m-%d')
    except:
        return None
        
    doc = collection.find_one({
        "asset": asset.lower(),
        "date": {"$gte": dt, "$lt": dt + timedelta(days=1)}
    })
    
    if not doc:
        return None
        
    return {
        "close": round(doc['close'], 2),
        "date": doc['date'].strftime('%Y-%m-%d')
    }
