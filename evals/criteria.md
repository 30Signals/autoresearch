# Success Criteria for NIFTY50 Trading Strategy Backtest
## Metrics Computed
- Sharpe Ratio (annualized, risk-free rate = 6% for India)
- Maximum Drawdown (%)
- CAGR (%)
- Win Rate (%)
- Comparison to Buy-and-Hold baseline
## Strategies Implemented
- Moving Average Crossover (50-day / 200-day SMA)
- RSI-based (buy oversold <30, sell overbought >70)
- Bollinger Bands mean-reversion
- One additional strategy of choice (to be determined)
## Data
- NIFTY50_raw.csv downloaded and saved in results/data/
- Backtest results saved in results/backtest_results.csv
- Equity curves plotted and saved in results/plots/
## Report
- Written summary with conclusion saved in results/report.md