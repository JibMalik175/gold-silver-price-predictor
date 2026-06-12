import os
import pandas as pd
import sys
from datetime import datetime
from pymongo import UpdateOne

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.mongodb import get_collection

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def migrate():
    """Migrate data from CSV to MongoDB Atlas."""
    collection = get_collection("prices")
    
    # Create Index for performance
    print("Creating indexes...")
    collection.create_index([("asset", 1), ("date", 1)], unique=True)
    collection.create_index([("date", -1)])
    
    for asset in ["gold", "silver"]:
        csv_path = os.path.join(DATA_DIR, f"{asset}.csv")
        if not os.path.exists(csv_path):
            print(f"Skipping {asset}: CSV not found at {csv_path}")
            continue
            
        print(f"Reading CSV for {asset}...")
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'])
        
        print(f"Migrating {len(df)} records for {asset} to MongoDB Atlas...")
        
        operations = []
        for _, row in df.iterrows():
            record_date = row['Date'].to_pydatetime()
            operations.append(UpdateOne(
                {"asset": asset, "date": record_date},
                {"$set": {
                    "asset": asset,
                    "date": record_date,
                    "open": row['Open'],
                    "high": row['High'],
                    "low": row['Low'],
                    "close": row['Close'],
                    "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
                }},
                upsert=True
            ))
            
            # Batch updates in chunks of 1000
            if len(operations) >= 1000:
                collection.bulk_write(operations)
                operations = []
                
        if operations:
            collection.bulk_write(operations)
            
        print(f"Finished migration for {asset}.")

if __name__ == "__main__":
    migrate()
