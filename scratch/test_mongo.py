import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('backend/.env')
uri = os.getenv("MONGODB_URI")
print(f"Connecting to: {uri[:20]}...")

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error: {e}")
