## SUCCESS CRITERIA

## Strategies Implemented
- Moving Average Crossover (50-day / 200-day SMA)
- RSI-based (buy oversold <30, sell overbought >70)
- Bollinger Bands mean-reversion
- Mean Reversion (20-period Bollinger Bands with 2 std dev)

## Data
- NIFTY50_raw.csv downloaded and saved in results/data/
- Backtest results saved in results/backtest_results.csv

## Report
- Written summary with conclusion saved in results/report.md

## Metrics Computed
- Sharpe Ratio (annualized, risk-free rate = 6% for India)
- Maximum Drawdown (%)
- CAGR (%)
- Win Rate (%)
- Comparison to Buy-and-Hold baseline