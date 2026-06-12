import yfinance as yf
import pandas as pd
import os
from datetime import datetime
from ..mongodb import get_collection
from pymongo import UpdateOne

ASSETS = {
    "gold": "GC=F",
    "silver": "SI=F"
}

def fetch_data(asset_key: str, period: str = "max"):
    """
    Fetch historical data and save to MongoDB Atlas.
    """
    if asset_key not in ASSETS:
        raise ValueError(f"Invalid asset. Choose from {list(ASSETS.keys())}")
    
    symbol = ASSETS[asset_key]
    print(f"Fetching data for {asset_key} ({symbol})...")
    
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    
    if df.empty:
        raise Exception(f"No data found for {symbol}")
    
    # Reset index to make Date a column
    df.reset_index(inplace=True)
    
    collection = get_collection("prices")
    
    print(f"Updating MongoDB for {asset_key}...")
    
    operations = []
    for _, row in df.iterrows():
        # MongoDB handles native datetime objects well
        record_date = row['Date'].to_pydatetime()
        
        # Prepare an Upsert operation
        operations.append(UpdateOne(
            {"asset": asset_key, "date": record_date},
            {"$set": {
                "asset": asset_key,
                "date": record_date,
                "open": row['Open'],
                "high": row['High'],
                "low": row['Low'],
                "close": row['Close'],
                "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0,
                "updated_at": datetime.now()
            }},
            upsert=True
        ))
    
    if operations:
        # Bulk write for efficiency
        result = collection.bulk_write(operations)
        print(f"Successfully processed {len(operations)} records for {asset_key} (Modified: {result.modified_count}, Upserted: {result.upserted_count})")
    
    return df

def update_all_data():
    """Fetch and update data for all assets."""
    for asset in ASSETS:
        try:
            # For daily updates, we just need the last month of data to catch gaps
            fetch_data(asset, period="1mo")
        except Exception as e:
            print(f"Error fetching {asset}: {str(e)}")

if __name__ == "__main__":
    # If run directly, update with full history
    for asset in ASSETS:
        fetch_data(asset, period="max")
