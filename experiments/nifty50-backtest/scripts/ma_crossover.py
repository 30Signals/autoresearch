import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load historical data
data = pd.read_csv('results/data/NIFTY50_raw.csv')

# Convert to datetime
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Calculate 50-day and 200-day moving averages
data['SMA_50'] = data['Close'].rolling(window=50).mean()
data['SMA_200'] = data['Close'].rolling(window=200).mean()

# Generate trading signals
# 1 = Buy, -1 = Sell, 0 = No position
data['Signal'] = 0
data.loc[data['SMA_50'] > data['SMA_200'], 'Signal'] = 1
data.loc[data['SMA_50'] < data['SMA_200'], 'Signal'] = -1

# Calculate portfolio performance
initial_capital = 100000
position = 0
portfolio_values = []
for i in range(len(data)):
    if data['Signal'].iloc[i] == 1:  # Buy signal
        position = initial_capital / data['Close'].iloc[i]
    elif data['Signal'].iloc[i] == -1 and position > 0:  # Sell signal
        initial_capital = position * data['Close'].iloc[i]
        position = 0
    portfolio_value = initial_capital + position * data['Close'].iloc[i]
    portfolio_values.append(portfolio_value)

data['Portfolio'] = portfolio_values

# Calculate total return and performance metrics
portfolio_return = (data['Portfolio'].iloc[-1] / data['Portfolio'].iloc[0]) - 1

# Calculate Sharpe Ratio (annualized, 6% risk-free)
annual_risk_free = 0.06
daily_returns = data['Portfolio'].pct_change().dropna()
sharpe_ratio = (daily_returns.mean() - annual_risk_free/252) / daily_returns.std() * np.sqrt(252)

data.to_csv('results/backtest_results.csv')

# Plot equity curve
plt.figure(figsize=(14,7))
plt.plot(data['Portfolio'], label='MA Crossover Strategy')
plt.plot(data['Close'] * 100000 / data['Close'].iloc[0], label='Buy-and-Hold')
plt.title('MA Crossover Strategy Performance')
plt.legend()
plt.savefig('results/plots/ma_crossover_equity.png')