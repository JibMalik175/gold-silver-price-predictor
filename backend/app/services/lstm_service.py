import numpy as np
import pandas as pd
import os
import joblib
import torch
import torch.nn as nn
from datetime import timedelta
from app.services import price_service

# Configuration
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
LOOK_BACK = 60
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

def generate_lstm_forecast(asset: str, timeframe: str = 'daily', steps: int = 14):
    asset = asset.lower().strip()
    if asset not in ("gold", "silver"):
        return {"error": "Asset must be 'gold' or 'silver'."}

    model_path = os.path.join(MODEL_DIR, f"lstm_torch_{asset}_{timeframe}.pth")
    scaler_path = os.path.join(MODEL_DIR, f"scaler_torch_{asset}_{timeframe}.pkl")

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        return {
            "error": (
                f"Model not found for {asset}/{timeframe}. "
                f"From the backend folder run: python scripts/train_lstm.py --asset {asset}"
            )
        }
    
    try:
        scaler = joblib.load(scaler_path)
        model = LSTMModel().to(DEVICE)
        model.load_state_dict(torch.load(model_path, map_location=DEVICE))
        model.eval()
    except Exception as e:
        return {"error": f"Failed to load model: {e}"}

    # Prepare Input
    data = price_service.get_historical_prices(asset, timeframe)
    df = pd.DataFrame(data)
    prices = df['close'].values.reshape(-1, 1)
    
    last_60 = prices[-LOOK_BACK:]
    curr_input = scaler.transform(last_60).reshape(1, LOOK_BACK, 1)
    
    future_predictions = []
    
    for _ in range(steps):
        with torch.no_grad():
            curr_tensor = torch.tensor(curr_input, dtype=torch.float32).to(DEVICE)
            pred = model(curr_tensor).cpu().numpy()[0, 0]
        
        future_predictions.append(pred)
        
        # Update window
        pred_reshaped = np.array([[[pred]]])
        curr_input = np.append(curr_input[:, 1:, :], pred_reshaped, axis=1)

    # Helpers
    future_predictions = np.array(future_predictions).reshape(-1, 1)
    future_prices = scaler.inverse_transform(future_predictions)
    
    # Dates
    last_date_str = df.iloc[-1]["date"]
    last_date = pd.to_datetime(last_date_str)
    results = []
    curr_date = last_date
    for i in range(steps):
        if timeframe == 'daily':
            curr_date += timedelta(days=1)
        elif timeframe == 'weekly':
            curr_date += timedelta(weeks=1)
        elif timeframe == 'monthly':
            curr_date += timedelta(days=30)
            
        results.append({
            "date": curr_date.strftime('%Y-%m-%d'),
            "predicted_price": round(float(future_prices[i][0]), 2)
        })
        
    return results
