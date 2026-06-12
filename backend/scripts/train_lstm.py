import argparse
import numpy as np
import pandas as pd
import os
import joblib
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from app.services import price_service

# Configuration
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
LOOK_BACK = 60
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Ensure model directory exists
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

class StockDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

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

def create_dataset(dataset, look_back=60):
    X, Y = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        X.append(a)
        Y.append(dataset[i + look_back, 0])
    return np.array(X), np.array(Y)

def train(asset, timeframe='daily', epochs=50, batch_size=32, patience=5):
    print(f"\n{'='*40}")
    print(f"Starting Training: {asset.upper()} ({timeframe})")
    print(f"{'='*40}\n")

    # 1. Load Data
    try:
        data = price_service.get_historical_prices(asset, timeframe)
        print(f"[Data] Loaded {len(data)} records for {asset}")
    except Exception as e:
        print(f"[Error] Failed to load data: {e}")
        return

    df = pd.DataFrame(data)
    prices = df['close'].values.reshape(-1, 1)

    # 2. Preprocessing
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)
    
    # Save Scaler
    scaler_path = os.path.join(MODEL_DIR, f"scaler_torch_{asset}_{timeframe}.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"[Preprocessing] Scaler saved to: {scaler_path}")

    # 3. Create Splits
    # 80% Train, 20% Validation
    train_size = int(len(scaled_prices) * 0.8)
    train_data, val_data = scaled_prices[:train_size], scaled_prices[train_size:]

    X_train, y_train = create_dataset(train_data, LOOK_BACK)
    X_val, y_val = create_dataset(val_data, LOOK_BACK)

    # Convert to Tensors
    X_train = X_train.reshape(-1, LOOK_BACK, 1)
    X_val = X_val.reshape(-1, LOOK_BACK, 1)

    train_dataset = StockDataset(X_train, y_train)
    val_dataset = StockDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    print(f"[Setup] Train Samples: {len(X_train)} | Val Samples: {len(X_val)}")
    print(f"[Setup] Device: {DEVICE}")

    # 4. Model Initialization
    model = LSTMModel().to(DEVICE)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 5. Training Loop
    print("\nStarting Training Loop...")
    best_loss = float('inf')
    # patience passed as argument
    patience_counter = 0

    for epoch in range(epochs):
        # -- Train --
        model.train()
        train_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs.squeeze(), y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        avg_train_loss = train_loss / len(train_loader)

        # -- Validation --
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
                outputs = model(X_batch)
                loss = criterion(outputs.squeeze(), y_batch)
                val_loss += loss.item()
        
        avg_val_loss = val_loss / len(val_loader)

        # -- Log --
        print(f"Epoch {epoch+1}/{epochs} | Loss: {avg_train_loss:.6f} | Val Loss: {avg_val_loss:.6f}")

        # -- Early Stopping --
        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            patience_counter = 0
            # Save Best Model
            model_path = os.path.join(MODEL_DIR, f"lstm_torch_{asset}_{timeframe}.pth")
            torch.save(model.state_dict(), model_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n[Early Stopping] No improvement for {patience} epochs.")
                break

    print(f"\n[Finished] Best Val Loss: {best_loss:.6f}")
    print(f"[Saved] Model saved to: {model_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train LSTM Model for Stock Prediction')
    parser.add_argument('--asset', type=str, required=True, help='Asset symbol (gold/silver)')
    parser.add_argument('--timeframe', type=str, default='daily', help='Timeframe (daily/weekly/monthly)')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--patience', type=int, default=5, help='Patience for early stopping')
    
    args = parser.parse_args()
    
    train(
        asset=args.asset, 
        timeframe=args.timeframe, 
        epochs=args.epochs, 
        batch_size=args.batch_size,
        patience=args.patience
    )
