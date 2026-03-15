import pandas as pd
import yfinance as yf

def moving_average_crossover(data): 
    data['50-day SMA'] = data['Close'].rolling(window=50).mean()
    data['200-day SMA'] = data['Close'].rolling(window=200).mean()
    
    data['Signal'] = 0.0
    data.loc[data['50-day SMA'] > data['200-day SMA'], 'Signal'] = 1.0
    data.loc[data['50-day SMA'] < data['200-day SMA'], 'Signal'] = -1.0
    
    return data

if __name__ == '__main__':
    data = pd.read_csv('results/data/NIFTY50_raw.csv', index_col=0)
    data = moving_average_crossover(data)
    data.to_csv('results/data/NIFTY50_MA_crossover.csv')