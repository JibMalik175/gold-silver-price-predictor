from app.mongodb import get_collection
from datetime import datetime

def check():
    collection = get_collection("prices")
    latest = collection.find_one(sort=[("updated_at", -1)])
    if latest:
        print(f"Latest update: {latest.get('updated_at')}")
    else:
        print("No records with updated_at found.")

if __name__ == "__main__":
    check()
