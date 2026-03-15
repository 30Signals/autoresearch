import yfinance as yf
import pandas as pd
import evaluate as evaluate
from datetime import date
import yfinance as yf
import pandas as pd
csv_path = 'results/data/NIFTY50_raw.csv'
raw_data = pd.read_csv(csv_path)

# Implement Moving Average Crossover strategy
nifty50_ma_crossover = evaluate.ma_crossover(raw_data)

# Implement RSI-based strategy
nifty50_rsi = evaluate.rsi_strategy(raw_data)

# Implement Bollinger Bands mean-reversion strategy
nifty50_bollinger = evaluate.bollinger_bands_strategy(raw_data)

# Implement Mean Reversion strategy
nifty50_mean_reversion = evaluate.mean_reversion_strategy(raw_data)

# Save results to csv
nifty50_ma_crossover.to_csv("results/backtest_results_ma_crossover.csv")
nifty50_rsi.to_csv("results/backtest_results_rsi.csv")
nifty50_bollinger.to_csv("results/backtest_results_bollinger.csv")
nifty50_mean_reversion.to_csv("results/backtest_results_mean_reversion.csv")