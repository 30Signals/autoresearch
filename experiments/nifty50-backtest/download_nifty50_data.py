import yfinance as yf
import pandas as pd
import os

os.makedirs('results/data', exist_ok=True)

def download_nifty50_data():
    data = yf.download("^NSEI", period="5y", interval="1d")
    data.to_csv('results/data/NIFTY50_raw.csv')
    return data

if __name__ == "__main__":
    download_nifty50_data()