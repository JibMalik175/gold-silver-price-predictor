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

# Status of the most recent update attempt, surfaced via /health
LAST_UPDATE = {"time": None, "ok": None, "error": None}


def _normalize_bar_date(ts: pd.Timestamp) -> datetime:
    """
    Convert a yfinance bar timestamp to a naive midnight datetime.

    yfinance returns tz-aware timestamps while the original CSV migration stored
    naive ones; without normalization the {asset, date} upsert key never matches
    and the same session gets duplicated.
    """
    if ts.tzinfo is not None:
        ts = ts.tz_localize(None)
    return ts.normalize().to_pydatetime()


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

    # Drop the final bar if its session is still in progress: storing a live
    # intraday print as a daily close poisons forecasts. The completed bar is
    # picked up by the next day's update.
    last_ts = df['Date'].iloc[-1]
    now_in_bar_tz = datetime.now(last_ts.tzinfo) if last_ts.tzinfo else datetime.now()
    if last_ts.date() == now_in_bar_tz.date():
        df = df.iloc[:-1]
        if df.empty:
            raise Exception(f"Only an in-progress bar returned for {symbol}; nothing to store")

    collection = get_collection("prices")

    print(f"Updating MongoDB for {asset_key}...")

    operations = []
    for _, row in df.iterrows():
        record_date = _normalize_bar_date(row['Date'])

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
    errors = []
    for asset in ASSETS:
        try:
            # For daily updates, we just need the last month of data to catch gaps
            fetch_data(asset, period="1mo")
        except Exception as e:
            errors.append(f"{asset}: {e}")
            print(f"Error fetching {asset}: {str(e)}")

    LAST_UPDATE["time"] = datetime.now().isoformat(timespec="seconds")
    LAST_UPDATE["ok"] = not errors
    LAST_UPDATE["error"] = "; ".join(errors) if errors else None

if __name__ == "__main__":
    # If run directly, update with full history
    for asset in ASSETS:
        fetch_data(asset, period="max")
