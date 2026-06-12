import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv("backend/.env")

async def check_db():
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "silver_gold_db")
    print(f"Connecting to {uri} / {db_name}")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]
    
    for collection_name in ["prices"]:
        coll = db[collection_name]
        count = await coll.count_documents({})
        print(f"Collection {collection_name}: {count} records")
        if count > 0:
            sample = await coll.find_one()
            print(f"Sample record: {sample}")

if __name__ == "__main__":
    asyncio.run(check_db())
