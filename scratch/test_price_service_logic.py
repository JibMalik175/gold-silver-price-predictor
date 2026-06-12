import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Mock get_collection
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.mongodb import get_collection

load_dotenv('backend/.env')

def test_silver_prices():
    collection = get_collection("prices")
    query = {"asset": "silver"}
    
    cursor = collection.find(
        query,
        {"_id": 0, "date": 1, "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}
    ).sort("date", 1)
    
    docs = list(cursor)
    print(f"Retrieved {len(docs)} docs")
    
    df = pd.DataFrame(docs)
    df['date'] = pd.to_datetime(df['date'])
    
    print("Iterating and rounding...")
    for i, row in df.iterrows():
        try:
            d = {
                "date": row['date'].strftime('%Y-%m-%d'),
                "close": round(row['close'], 2),
                "open": round(row['open'], 2),
                "high": round(row['high'], 2),
                "low": round(row['low'], 2),
                "volume": int(row['volume']) if not pd.isna(row['volume']) else 0
            }
        except Exception as e:
            print(f"Error at index {i}: {e}")
            print("Row data:", row.to_dict())
            return

    print("Success!")

if __name__ == "__main__":
    test_silver_prices()
