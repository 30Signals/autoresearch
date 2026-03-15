import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import os

# Create directories
os.makedirs('results/data', exist_ok=True)
os.makedirs('results/plots', exist_ok=True)

# Download data
print("Downloading NIFTY50 data...")
data = yf.download("^NSEI", period="5y", interval="1d")
data.to_csv('results/data/NIFTY50_raw.csv')
print(f"Data downloaded. Shape: {data.shape}")

# Load data for backtest
df = data.copy()

# Calculate daily returns
df['Returns'] = df['Close'].pct_change()

# ========== Strategy 1: Moving Average Crossover (50/200) ==========
print("Processing Moving Average Crossover...")
df['MA50'] = df['Close'].rolling(window=50).mean()
df['MA200'] = df['Close'].rolling(window=200).mean()
df['MA_Signal'] = np.where(df['MA50'] > df['MA200'], 1, 0)  # 1 for long, 0 for no position
df['MA_Signal'] = df['MA_Signal'].diff()  # To get entry/exit signals
# We'll hold the position until the signal changes
df['MA_Position'] = df['MA_Signal'].ffill().fillna(0)
df['MA_Strategy_Return'] = df['MA_Position'].shift(1) * df['Returns']
df['MA_Equity'] = (1 + df['MA_Strategy_Return']).cumprod()

# ========== Strategy 2: RSI-based ==========
print("Processing RSI...")
delta = df['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))
df['RSI_Signal'] = np.where(df['RSI'] < 30, 1, np.where(df['RSI'] > 70, -1, 0))  # 1 for buy, -1 for sell, 0 for hold
# We'll convert to position: when we get a buy signal, we go long until a sell signal
df['RSI_Position'] = df['RSI_Signal'].ffill().fillna(0)
# If we start with a sell signal, we remain flat (0)
df['RSI_Strategy_Return'] = df['RSI_Position'].shift(1) * df['Returns']
df['RSI_Equity'] = (1 + df['RSI_Strategy_Return']).cumprod()

# ========== Strategy 3: Bollinger Bands ==========
print("Processing Bollinger Bands...")
df['BB_Middle'] = df['Close'].rolling(window=20).mean()
df['BB_Std'] = df['Close'].rolling(window=20).std()
df['BB_Upper'] = df['BB_Middle'] + 2 * df['BB_Std']
df['BB_Lower'] = df['BB_Middle'] - 2 * df['BB_Std']
# Ensure we're working with Series that have the same index
bb_signal = np.where(df['Close'] < df['BB_Lower'], 1, np.where(df['Close'] > df['BB_Upper'], -1, 0))
df['BB_Signal'] = bb_signal
df['BB_Position'] = df['BB_Signal'].ffill().fillna(0)
df['BB_Strategy_Return'] = df['BB_Position'].shift(1) * df['Returns']
df['BB_Equity'] = (1 + df['BB_Strategy_Return']).cumprod()

# ========== Strategy 4: Momentum (12-period ROC) ==========
print("Processing Momentum...")
df['ROC'] = df['Close'].pct_change(periods=12)
df['Mom_Signal'] = np.where(df['ROC'] > 0, 1, 0)  # Long when ROC positive
df['Mom_Position'] = df['Mom_Signal'].ffill().fillna(0)
df['Mom_Strategy_Return'] = df['Mom_Position'].shift(1) * df['Returns']
df['Mom_Equity'] = (1 + df['Mom_Strategy_Return']).cumprod()

# ========== Buy and Hold ==========
df['BuyHold_Return'] = df['Returns']
df['BuyHold_Equity'] = (1 + df['BuyHold_Return']).cumprod()

# ========== Performance Metrics ==========
def calculate_metrics(returns, risk_free_rate=0.06):
    """Calculate Sharpe Ratio, Max Drawdown, CAGR, Win Rate"""
    # Daily risk-free rate
    daily_rf = (1 + risk_free_rate) ** (1/252) - 1
    
    # Excess returns
    excess_returns = returns - daily_rf
    
    # Sharpe Ratio (annualized)
    sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0
    
    # Cumulative returns
    cum_returns = (1 + returns).cumprod()
    
    # Maximum Drawdown
    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    # CAGR
    n_years = len(returns) / 252
    cagr = (cum_returns.iloc[-1]) ** (1/n_years) - 1 if n_years > 0 else 0
    
    # Win Rate (percentage of positive returns)
    win_rate = (returns > 0).sum() / len(returns)
    
    return {
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_drawdown,
        'CAGR': cagr,
        'Win Rate': win_rate
    }

# Calculate metrics for each strategy
strategies = {
    'Moving Average Crossover': df['MA_Strategy_Return'].dropna(),
    'RSI': df['RSI_Strategy_Return'].dropna(),
    'Bollinger Bands': df['BB_Strategy_Return'].dropna(),
    'Momentum': df['Mom_Strategy_Return'].dropna(),
    'Buy and Hold': df['BuyHold_Return'].dropna()
}

results = {}
for name, returns in strategies.items():
    results[name] = calculate_metrics(returns)

# Convert results to DataFrame
results_df = pd.DataFrame(results).T
results_df.to_csv('results/backtest_results.csv')
print("Backtest results saved to results/backtest_results.csv")

# ========== Plotting ==========
plt.figure(figsize=(14, 8))
plt.plot(df.index, df['MA_Equity'], label='Moving Average Crossover')
plt.plot(df.index, df['RSI_Equity'], label='RSI')
plt.plot(df.index, df['BB_Equity'], label='Bollinger Bands')
plt.plot(df.index, df['Mom_Equity'], label='Momentum')
plt.plot(df.index, df['BuyHold_Equity'], label='Buy and Hold')
plt.title('Equity Curves of Trading Strategies')
plt.xlabel('Date')
plt.ylabel('Equity')
plt.legend()
plt.grid(True)
plt.savefig('results/plots/equity_curves.png')
plt.close()

# ========== Summary Report ==========
with open('results/report.md', 'w') as f:
    f.write("# NIFTY50 Trading Strategy Backtest Report\n\n")
    f.write("## Summary of Performance Metrics\n\n")
    f.write(results_df.to_markdown() + "\n\n")
    
    # Find best strategy based on Sharpe Ratio
    best_strategy = results_df['Sharpe Ratio'].idxmax()
    best_sharpe = results_df['Sharpe Ratio'].max()
    
    f.write(f"## Best Strategy: {best_strategy}\n\n")
    f.write(f"The best performing strategy based on Sharpe Ratio is **{best_strategy}** with a Sharpe Ratio of {best_sharpe:.3f}.\n\n")
    
    f.write("### Why this strategy works:\n\n")
    if best_strategy == 'Moving Average Crossover':
        f.write("The Moving Average Crossover strategy captures trends by going long when the short-term average exceeds the long-term average. "
                "This works well in trending markets where prices tend to persist in one direction.\n")
    elif best_strategy == 'RSI':
        f.write("The RSI strategy exploits mean-reversion by buying when the asset is oversold (RSI<30) and selling when overbought (RSI>70). "
                "This works well in ranging markets where prices revert to a mean.\n")
    elif best_strategy == 'Bollinger Bands':
        f.write("The Bollinger Bands strategy also exploits mean-reversion, buying when prices touch the lower band and selling when they touch the upper band. "
                "It works well during periods of low volatility when prices tend to stay within the bands.\n")
    elif best_strategy == 'Momentum':
        f.write("The Momentum strategy buys when the rate of change is positive, capitalizing on the tendency of assets to continue in the same direction. "
                "This works well when there is strong upward momentum in the market.\n")
    else:
        f.write("Buy and Hold serves as a baseline, representing passive investment in the index.\n")
    
    f.write("\n## Comparison to Buy and Hold\n\n")
    for strategy in ['Moving Average Crossover', 'RSI', 'Bollinger Bands', 'Momentum']:
        sharpe_diff = results_df.loc[strategy, 'Sharpe Ratio'] - results_df.loc['Buy and Hold', 'Sharpe Ratio']
        cagr_diff = results_df.loc[strategy, 'CAGR'] - results_df.loc['Buy and Hold', 'CAGR']
        f.write(f"### {strategy} vs Buy and Hold\n")
        f.write(f"- Sharpe Ratio Difference: {sharpe_diff:.3f}\n")
        f.write(f"- CAGR Difference: {cagr_diff:.3f}\n\n")

print("Report saved to results/report.md")

# Also save the processed data with signals for inspection
df.to_csv('results/data/NIFTY50_with_signals.csv')
print("Data with signals saved to results/data/NIFTY50_with_signals.csv")