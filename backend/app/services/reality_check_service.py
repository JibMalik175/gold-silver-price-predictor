from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from app.services import price_service

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "silver_gold_db")
COLLECTION_NAME = "reality_checks"

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

async def save_predictions(asset: str, timeframe: str, predictions: List[Dict[str, Any]]):
    """
    Save a list of prediction points to the reality_checks collection.
    Each point: { "date": "YYYY-MM-DD", "predicted_price": 123.45 }
    """
    created_at = datetime.utcnow()
    docs = []
    for p in predictions:
        docs.append({
            "asset": asset.lower(),
            "timeframe": timeframe.lower(),
            "predicted_for_date": p["date"],
            "predicted_price": float(p["predicted_price"]),
            "made_at": created_at,
            "status": "pending"
        })
    
    if docs:
        await collection.insert_many(docs)
    return len(docs)

async def get_reality_checks(asset: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve saved predictions and join with actual prices if available.
    """
    query = {}
    if asset:
        query["asset"] = asset.lower()
    
    cursor = collection.find(query).sort("predicted_for_date", -1).limit(100)
    history = await cursor.to_list(length=100)
    
    # Enrich with actual prices
    results = []
    for item in history:
        # Convert BSON to dict
        item["_id"] = str(item["_id"])
        item["made_at"] = item["made_at"].strftime("%Y-%m-%d %H:%M")
        
        # Try to find actual price for that date
        actual = price_service.get_price_for_date(item["asset"], item["predicted_for_date"])
        if actual:
            item["actual_price"] = actual["close"]
            item["error_abs"] = abs(item["actual_price"] - item["predicted_price"])
            item["error_pct"] = (item["error_abs"] / item["actual_price"]) * 100
            item["status"] = "completed"
        else:
            item["actual_price"] = None
            item["error_abs"] = None
            item["error_pct"] = None
            item["status"] = "pending"
            
        results.append(item)
        
    return results
