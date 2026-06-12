import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.mongodb import get_collection
import pandas as pd

def check_data():
    coll = get_collection('prices')
    docs = list(coll.find({"asset": "silver"}))
    df = pd.DataFrame(docs)
    print("Columns:", df.columns.tolist())
    print("Null counts:\n", df.isnull().sum())
    print("Data types:\n", df.dtypes)
    
    # Check if 'close' exists and is numeric
    if 'close' in df.columns:
        print("Non-numeric 'close' values:", df[pd.to_numeric(df['close'], errors='coerce').isna()]['close'].unique())

if __name__ == "__main__":
    check_data()
