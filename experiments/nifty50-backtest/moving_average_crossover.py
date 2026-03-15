import pandas as pd
import yfinance as yf
import numpy as np

# Download data
data = yf.download('^NSEI', period='5y', interval='1d')

# Calculate moving averages
data['50-day SMA'] = data['Close'].rolling(window=50).mean()
data['200-day SMA'] = data['Close'].rolling(window=200).mean()

# Generate signals
data['Signal'] = np.where(data['50-day SMA'] > data['200-day SMA'], 1, 0)

# Generate buy and sell signals
buy_signals = data[data['Signal'] == 1]
sell_signals = data[data['Signal'] == 0]

# Plot the results
import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))
plt.plot(data['Close'], label='Close Price')
plt.plot(data['50-day SMA'], label='50-day SMA')
plt.plot(data['200-day SMA'], label='200-day SMA')
plt.scatter(buy_signals.index, buy_signals['Close'], label='Buy', marker='^', color='g')
plt.scatter(sell_signals.index, sell_signals['Close'], label='Sell', marker='v', color='r')
plt.legend(loc='upper left')
plt.show()