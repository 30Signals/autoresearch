import yfinance as yf
import pandas as pd
import os

os.makedirs('results/data', exist_ok=True)

# Download and save raw data
data = yf.download("^NSEI", period="5y", interval="1d")
data.to_csv('results/data/NIFTY50_raw.csv')
print("Raw data saved. Shape:", data.shape)