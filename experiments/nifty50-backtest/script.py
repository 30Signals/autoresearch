import pandas as pd
from yfinance import download

# Download NIFTY50 raw data
nifty50_raw = download('^NSEI', period='5y', interval='1d')

# Save data to CSV
nifty50_raw.to_csv('results/data/NIFTY50_raw.csv')