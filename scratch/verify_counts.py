import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.mongodb import get_collection

def verify():
    coll = get_collection('prices')
    gold_count = coll.count_documents({"asset": "gold"})
    silver_count = coll.count_documents({"asset": "silver"})
    print(f"Gold: {gold_count}")
    print(f"Silver: {silver_count}")

if __name__ == "__main__":
    verify()
