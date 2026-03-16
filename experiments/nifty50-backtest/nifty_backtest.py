import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Create results directories
import os
os.makedirs('results/data', exist_ok=True)
os.makedirs('results/plots', exist_ok=True)

def download_nifty_data():
    """Download 5+ years of NIFTY50 historical data"""
    print("Downloading NIFTY50 data...")
    nifty = yf.download("^NSEI", period="5y", interval="1d")
    nifty.to_csv('results/data/NIFTY50_raw.csv')
    print(f"Downloaded {len(nifty)} days of data from {nifty.index[0].date()} to {nifty.index[-1].date()}")
    return nifty

def calculate_returns(prices):
    """Calculate daily returns"""
    return prices.pct_change().dropna()

def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate"""
    return ((end_value / start_value) ** (1/years) - 1) * 100

def calculate_sharpe_ratio(returns, risk_free_rate=0.06):
    """Calculate Sharpe Ratio (annualized)"""
    excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_max_drawdown(equity_curve):
    """Calculate Maximum Drawdown"""
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    return drawdown.min() * 100

def calculate_win_rate(returns):
    """Calculate Win Rate"""
    return (returns > 0).mean() * 100

def moving_average_crossover_strategy(data, short_window=50, long_window=200):
    """Moving Average Crossover Strategy"""
    print(f"Implementing Moving Average Crossover strategy (SMA{short_window}/SMA{long_window})...")
    
    # Calculate moving averages
    data[f'MA_{short_window}'] = data['Close'].rolling(window=short_window).mean()
    data[f'MA_{long_window}'] = data['Close'].rolling(window=long_window).mean()
    
    # Generate signals
    data['MA_Signal'] = 0
    data.loc[data.index[short_window:], 'MA_Signal'] = np.where(
        data[f'MA_{short_window}'][short_window:] > data[f'MA_{long_window}'][short_window:], 1, 0
    )
    
    # Calculate strategy returns
    data['MA_Returns'] = data['Close'].pct_change()
    data['MA_Strategy_Returns'] = data['MA_Signal'].shift(1) * data['MA_Returns']
    
    return data

def rsi_strategy(data, rsi_window=14, oversold=30, overbought=70):
    """RSI-based Strategy"""
    print(f"Implementing RSI strategy (window={rsi_window}, oversold={oversold}, overbought={overbought})...")
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Generate signals
    data['RSI_Signal'] = 0
    data.loc[data['RSI'] < oversold, 'RSI_Signal'] = 1  # Buy
    data.loc[data['RSI'] > overbought, 'RSI_Signal'] = -1  # Sell
    
    # Hold position until opposite signal
    data['RSI_Position'] = data['RSI_Signal'].replace(0, np.nan).fillna(method='ffill').fillna(0)
    
    # Calculate strategy returns
    data['RSI_Returns'] = data['Close'].pct_change()
    data['RSI_Strategy_Returns'] = data['RSI_Position'].shift(1) * data['RSI_Returns']
    
    return data

def bollinger_bands_strategy(data, window=20, num_std=2):
    """Bollinger Bands Mean Reversion Strategy"""
    print(f"Implementing Bollinger Bands strategy (window={window}, std={num_std})...")
    
    # Calculate Bollinger Bands
    data['MA'] = data['Close'].rolling(window=window).mean()
    data['STD'] = data['Close'].rolling(window=window).std()
    data['Upper_Band'] = data['MA'] + (num_std * data['STD'])
    data['Lower_Band'] = data['MA'] - (num_std * data['STD'])
    
    # Generate signals (mean reversion) - using numpy to avoid alignment issues
    close_values = data['Close'].values
    upper_band_values = data['Upper_Band'].values
    lower_band_values = data['Lower_Band'].values
    
    # Initialize signal array
    signals = np.zeros(len(data))
    
    # Generate signals where we have valid band values
    for i in range(len(data)):
        if not np.isnan(lower_band_values[i]) and not np.isnan(upper_band_values[i]):
            if close_values[i] < lower_band_values[i]:
                signals[i] = 1  # Buy oversold
            elif close_values[i] > upper_band_values[i]:
                signals[i] = -1  # Sell overbought
    
    data['BB_Signal'] = signals
    
    # Hold position until opposite signal
    data['BB_Position'] = data['BB_Signal'].replace(0, np.nan).fillna(method='ffill').fillna(0)
    
    # Calculate strategy returns
    data['BB_Returns'] = data['Close'].pct_change()
    data['BB_Strategy_Returns'] = data['BB_Position'].shift(1) * data['BB_Returns']
    
    return data

def momentum_strategy(data, lookback=252, momentum_threshold=0.1):
    """Momentum Strategy - Additional strategy"""
    print(f"Implementing Momentum strategy (lookback={lookback}, threshold={momentum_threshold})...")
    
    # Calculate momentum (12-month return)
    data['Momentum'] = data['Close'].pct_change(periods=lookback)
    
    # Generate signals
    data['Momentum_Signal'] = 0
    data.loc[data['Momentum'] > momentum_threshold, 'Momentum_Signal'] = 1  # Buy strong momentum
    data.loc[data['Momentum'] < -momentum_threshold, 'Momentum_Signal'] = -1  # Sell weak momentum
    
    # Hold position until opposite signal
    data['Momentum_Position'] = data['Momentum_Signal'].replace(0, np.nan).fillna(method='ffill').fillna(0)
    
    # Calculate strategy returns
    data['Momentum_Returns'] = data['Close'].pct_change()
    data['Momentum_Strategy_Returns'] = data['Momentum_Position'].shift(1) * data['Momentum_Returns']
    
    return data

def backtest_strategy(data, strategy_returns_col, initial_capital=100000):
    """Backtest a strategy and calculate metrics"""
    strategy_returns = data[strategy_returns_col].dropna()
    
    # Calculate equity curve
    equity_curve = initial_capital * (1 + strategy_returns).cumprod()
    
    # Calculate metrics
    years = len(strategy_returns) / 252
    final_value = equity_curve.iloc[-1]
    
    metrics = {
        'Total_Returns': float((final_value - initial_capital) / initial_capital * 100),
        'CAGR': float(calculate_cagr(initial_capital, final_value, years)),
        'Sharpe_Ratio': float(calculate_sharpe_ratio(strategy_returns)),
        'Max_Drawdown': float(calculate_max_drawdown(equity_curve)),
        'Win_Rate': float(calculate_win_rate(strategy_returns))
    }
    
    return metrics, equity_curve

def buy_and_hold_benchmark(data, initial_capital=100000):
    """Buy and Hold benchmark"""
    buy_hold_returns = data['Close'].pct_change().dropna()
    equity_curve = initial_capital * (1 + buy_hold_returns).cumprod()
    
    years = len(buy_hold_returns) / 252
    final_value = equity_curve.iloc[-1]
    
    metrics = {
        'Total_Returns': float((final_value - initial_capital) / initial_capital * 100),
        'CAGR': float(calculate_cagr(initial_capital, final_value, years)),
        'Sharpe_Ratio': float(calculate_sharpe_ratio(buy_hold_returns)),
        'Max_Drawdown': float(calculate_max_drawdown(equity_curve)),
        'Win_Rate': float(calculate_win_rate(buy_hold_returns))
    }
    
    return metrics, equity_curve

def plot_equity_curves(results, buy_hold_curve):
    """Plot equity curves for all strategies"""
    plt.figure(figsize=(12, 8))
    
    for strategy_name, equity_curve in results.items():
        plt.plot(equity_curve.index, equity_curve.values, label=strategy_name, linewidth=2)
    
    plt.plot(buy_hold_curve.index, buy_hold_curve.values, label='Buy & Hold', linewidth=2, linestyle='--', alpha=0.7)
    
    plt.title('NIFTY50 Trading Strategies - Equity Curves', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Portfolio Value (₹)', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/plots/equity_curves.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main function to run the backtest"""
    print("="*60)
    print("NIFTY50 Trading Strategy Backtest")
    print("="*60)
    
    # Download data
    nifty_data = download_nifty_data()
    
    # Apply all strategies
    nifty_data = moving_average_crossover_strategy(nifty_data)
    nifty_data = rsi_strategy(nifty_data)
    nifty_data = bollinger_bands_strategy(nifty_data)
    nifty_data = momentum_strategy(nifty_data)
    
    # Backtest each strategy
    results = {}
    equity_curves = {}
    
    strategies = [
        ('MA Strategy', 'MA_Strategy_Returns'),
        ('RSI Strategy', 'RSI_Strategy_Returns'),
        ('Bollinger Bands Strategy', 'BB_Strategy_Returns'),
        ('Momentum Strategy', 'Momentum_Strategy_Returns')
    ]
    
    for strategy_name, returns_col in strategies:
        print(f"\nBacktesting {strategy_name}...")
        metrics, equity_curve = backtest_strategy(nifty_data, returns_col)
        results[strategy_name] = metrics
        equity_curves[strategy_name] = equity_curve
        print(f"  CAGR: {metrics['CAGR']:.2f}%")
        print(f"  Sharpe Ratio: {metrics['Sharpe_Ratio']:.2f}")
        print(f"  Max Drawdown: {metrics['Max_Drawdown']:.2f}%")
        print(f"  Win Rate: {metrics['Win_Rate']:.2f}%")
    
    # Buy and Hold benchmark
    print(f"\nBacktesting Buy & Hold...")
    bh_metrics, bh_equity_curve = buy_and_hold_benchmark(nifty_data)
    results['Buy & Hold'] = bh_metrics
    equity_curves['Buy & Hold'] = bh_equity_curve
    print(f"  CAGR: {bh_metrics['CAGR']:.2f}%")
    print(f"  Sharpe Ratio: {bh_metrics['Sharpe_Ratio']:.2f}")
    print(f"  Max Drawdown: {bh_metrics['Max_Drawdown']:.2f}%")
    print(f"  Win Rate: {bh_metrics['Win_Rate']:.2f}%")
    
    # Create results DataFrame
    results_df = pd.DataFrame(results).T
    results_df.to_csv('results/backtest_results.csv')
    print(f"\nResults saved to results/backtest_results.csv")
    
    # Plot equity curves
    plot_equity_curves(equity_curves, bh_equity_curve)
    print("Equity curves plotted and saved to results/plots/equity_curves.png")
    
    # Identify best strategy (based on Sharpe Ratio)
    best_strategy = results_df['Sharpe_Ratio'].idxmax()
    print(f"\nBest performing strategy: {best_strategy}")
    print(f"Sharpe Ratio: {results_df.loc[best_strategy, 'Sharpe_Ratio']:.2f}")
    
    return results_df, best_strategy

if __name__ == "__main__":
    results_df, best_strategy = main()