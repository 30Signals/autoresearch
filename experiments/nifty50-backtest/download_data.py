import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Create results directories
import os
os.makedirs('results/data', exist_ok=True)
os.makedirs('results/plots', exist_ok=True)

# Download NIFTY50 data
print("Downloading NIFTY50 data...")
ticker = "^NSEI"
data = yf.download(ticker, period="5y", interval="1d")

# Save raw data
data.to_csv('results/data/NIFTY50_raw.csv')
print(f"Data downloaded: {len(data)} rows from {data.index[0]} to {data.index[-1]}")

# Display basic info
print("\nData Info:")
print(f"Start Date: {data.index[0]}")
print(f"End Date: {data.index[-1]}")
print(f"Total Days: {len(data)}")
print(f"Price Range: ₹{data['Close'].min():.2f} - ₹{data['Close'].max():.2f}")