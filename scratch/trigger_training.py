import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.forecast_service import train_and_save_bundle

def train_all():
    assets = ["gold", "silver"]
    timeframes = ["daily", "weekly"]
    
    for asset in assets:
        for tf in timeframes:
            print(f"Training {asset} {tf}...")
            try:
                out = train_and_save_bundle(asset, tf)
                print(f"  Success! Path: {out['path']}")
                print(f"  MAE Train: {out['mae_train']:.4f}, MAE Test: {out['mae_test']:.4f}")
            except Exception as e:
                print(f"  Failed {asset} {tf}: {e}")

if __name__ == "__main__":
    load_dotenv("backend/.env")
    train_all()
