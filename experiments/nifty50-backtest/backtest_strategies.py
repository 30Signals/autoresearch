import pandas as pd
import yfinance as yf
from datetime import datetime
import numpy as np

def load_data():
    data_path = 'results/data/NIFTY50_raw.csv'
    data = pd.read_csv(data_path, index_col='Date', parse_dates=True)
    data = data.rename(columns={'Adj Close': 'Adj_Close'})
    for col in ['Open', 'High', 'Low', 'Close', 'Adj_Close', 'Volume']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    return data.dropna()

def moving_average_crossover(data):
    data['SMA_50'] = data['Adj_Close'].rolling(50).mean()
    data['SMA_200'] = data['Adj_Close'].rolling(200).mean()
    data['Signal'] = 0
    data.loc[data.index[50:], 'Signal'] = np.where(data['SMA_50'][50:].values > data['SMA_200'][50:].values, 1, -1)
    return data

def run_backtest():
    data = load_data()
    data = moving_average_crossover(data)
    # Add other strategies here
    data.to_csv('results/data/backtest_data.csv')

if __name__ == '__main__':
    run_backtest()