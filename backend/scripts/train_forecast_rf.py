"""
Train Random Forest forecast models (RSI, SMAs, volatility) with chronological test split.

Usage (from backend directory, with MongoDB env configured):
  python scripts/train_forecast_rf.py --asset silver --timeframe daily
  python scripts/train_forecast_rf.py --asset gold --timeframe weekly
"""

import argparse
import os
import sys

# Allow running as script: python scripts/train_forecast_rf.py
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from app.services.forecast_service import MAE_GOAL_USD, train_and_save_bundle  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Train RF forecast bundle for gold/silver")
    parser.add_argument("--asset", type=str, required=True, choices=("gold", "silver"))
    parser.add_argument("--timeframe", type=str, default="daily", choices=("daily", "weekly", "monthly"))
    parser.add_argument("--test-fraction", type=float, default=0.2, help="Hold-out tail fraction for MAE")
    args = parser.parse_args()

    out = train_and_save_bundle(args.asset, args.timeframe, test_fraction=args.test_fraction)
    goal = MAE_GOAL_USD[args.asset]
    print(f"\nSaved bundle: {out['path']}")
    print(f"MAE train (USD): {out['mae_train']:.4f}")
    print(f"MAE test  (USD): {out['mae_test']:.4f}  (goal <= ${goal:.0f} for {args.asset})")
    if out["mae_test"] > goal:
        print(
            f"Note: test MAE is above the soft goal. Try more history in MongoDB, "
            f"different timeframe, or tune hyperparameters in forecast_service.py."
        )


if __name__ == "__main__":
    main()
