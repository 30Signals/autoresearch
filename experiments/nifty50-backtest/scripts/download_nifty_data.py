import yfinance as yf

# Download NIFTY50 data
nifty50_data = yf.download("^NSEI", period="5y", interval="1d")

# Save to CSV
nifty50_data.to_csv('results/data/NIFTY50_raw.csv')