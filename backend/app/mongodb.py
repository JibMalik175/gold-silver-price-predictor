from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "silver_gold_db")

# Initialize Client
# We use a global client instance
client = None

def get_mongodb():
    """Get the MongoDB database instance."""
    global client
    if client is None:
        client = MongoClient(MONGODB_URI)
    return client[DB_NAME]

def get_collection(name: str):
    """Get a specific collection."""
    db = get_mongodb()
    return db[name]
