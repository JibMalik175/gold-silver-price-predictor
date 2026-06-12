from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class ProfitLossRequest(BaseModel):
    asset: Literal["gold", "silver"]
    buy_date: str
    sell_date: str
    quantity: float = Field(gt=0)
    unit: str = "oz"

    @field_validator("asset", mode="before")
    @classmethod
    def normalize_asset(cls, v: str) -> str:
        if isinstance(v, str):
            key = v.lower().strip()
            if key in ("gold", "silver"):
                return key
        raise ValueError("Asset must be 'gold' or 'silver'.")

    @field_validator("buy_date", "sell_date")
    @classmethod
    def date_non_empty(cls, v: str) -> str:
        if not v or not str(v).strip():
            raise ValueError("Dates must be non-empty (YYYY-MM-DD).")
        return str(v).strip()


class ProfitLossResponse(BaseModel):
    buy_price: float
    sell_price: float
    quantity: float
    profit_loss: float
    roi_percent: float
    price_change_per_unit: float
    is_gain: bool
    unit: str
    data_range: Optional[dict] = None

class PredictionPoint(BaseModel):
    date: str
    predicted_price: float

class SavePredictionRequest(BaseModel):
    asset: Literal["gold", "silver"]
    timeframe: str
    predictions: list[PredictionPoint]
