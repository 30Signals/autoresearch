import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from backtesting import Backtest
from strategies.ma_crossover import MACrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.macd_crossover import MACDCrossoverStrategy
from strategy_analyzer import StrategyAnalyzer

def run_backtest():
    # Load data
    data_path = 'results/data/NIFTY50_raw.csv'
    # Skip the first two rows (header and ticker) and then use the third row as column names
    df = pd.read_csv(data_path, skiprows=2)
    # The third row is actually the column names for the data, but it's empty for the first column
    # Let's set the column names manually
    df.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    # Now set the index to Date and convert to datetime
    df.set_index('Date', inplace=True)
    df.index = pd.to_datetime(df.index)
    
    # Drop rows with NaN in OHLC columns
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
    
    # Ensure required columns exist
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    
    # Convert to numeric
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
    
    # Strategies to test
    strategies = [
        ('Moving Average Crossover', MACrossover),
        ('RSI-Based', RSIStrategy),
        ('Bollinger Bands', BollingerBandsStrategy),
        ('MACD Crossover', MACDCrossoverStrategy)
    ]
    
    results_list = []
    
    # Create plots directory
    os.makedirs('results/plots', exist_ok=True)
    
    for name, strategy_class in strategies:
        print(f"Running backtest for {name}...")
        bt = Backtest(df, strategy_class, cash=100000, commission=0.002, finalize_trades=True)
        results = bt.run()
        
        # Calculate metrics using the results object
        analyzer = StrategyAnalyzer(results)
        metrics = analyzer.get_metrics()
        metrics['Strategy'] = name
        
        # Buy-and-hold baseline for comparison
        bh_returns = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
        bh_years = len(df) / 252
        bh_cagr = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) ** (1 / bh_years) - 1) * 100 if bh_years > 0 else 0
        
        metrics['BuyHold_CAGR'] = bh_cagr
        metrics['BuyHold_Return_%'] = bh_returns
        
        results_list.append(metrics)
        
        # Plot equity curve
        plt.figure(figsize=(12, 6))
        plt.plot(results._equity_curve['Equity'], label=name)
        plt.title(f'Equity Curve: {name}')
        plt.xlabel('Trading Days')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'results/plots/{name.replace(" ", "_").lower()}_equity.png')
        plt.close()
    
    # Create results DataFrame
    results_df = pd.DataFrame(results_list)
    cols = ['Strategy', 'Sharpe Ratio', 'Max Drawdown (%)', 'CAGR (%)', 'Win Rate (%)', 'BuyHold_CAGR', 'BuyHold_Return_%']
    results_df = results_df[cols]
    
    # Save to CSV
    results_df.to_csv('results/backtest_results.csv', index=False)
    print("Backtest results saved to results/backtest_results.csv")
    
    # Also save the raw data for reference (already done)
    print("All done!")

if __name__ == '__main__':
    run_backtest()