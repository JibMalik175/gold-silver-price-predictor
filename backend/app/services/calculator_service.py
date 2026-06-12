import pandas as pd
from app.services import price_service

def calculate_profit_loss(asset: str, buy_date: str, sell_date: str, quantity: float):
    """
    Calculate profit or loss for a trade (long position: buy then sell).
    P/L = (sell_price - buy_price) * quantity; ROI% = (sell - buy) / buy * 100.
    """
    asset = asset.lower().strip()
    if asset not in ("gold", "silver"):
        raise ValueError("Asset must be 'gold' or 'silver'.")

    prices = price_service.get_historical_prices(asset, "daily")
    df = pd.DataFrame(prices)
    if df.empty:
        raise ValueError("No price history available for this asset. Sync MongoDB data first.")

    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    buy_dt = pd.to_datetime(buy_date).normalize()
    sell_dt = pd.to_datetime(sell_date).normalize()

    if sell_dt < buy_dt:
        raise ValueError("Exit date must be on or after entry date.")

    data_start = df["date"].min()
    data_end = df["date"].max()

    def get_price_on_date(target):
        """Exact session date, else last available close on or before target."""
        match = df[df["date"] == target]
        if not match.empty:
            return float(match.iloc[0]["close"])
        previous = df[df["date"] < target]
        if not previous.empty:
            return float(previous.iloc[-1]["close"])
        if target < data_start:
            raise ValueError(
                f"No price on or before {target.date()}; data starts {data_start.date()}."
            )
        return float(df.iloc[-1]["close"])

    buy_price = get_price_on_date(buy_dt)
    sell_price = get_price_on_date(sell_dt)

    price_change_per_unit = sell_price - buy_price
    profit_loss = price_change_per_unit * quantity
    roi = (price_change_per_unit / buy_price) * 100 if buy_price else 0.0

    return {
        "buy_price": round(buy_price, 2),
        "sell_price": round(sell_price, 2),
        "quantity": quantity,
        "profit_loss": round(profit_loss, 2),
        "roi_percent": round(roi, 2),
        "price_change_per_unit": round(price_change_per_unit, 2),
        "is_gain": profit_loss >= 0,
        "unit": "oz",
        "data_range": {"start": data_start.strftime("%Y-%m-%d"), "end": data_end.strftime("%Y-%m-%d")},
    }
