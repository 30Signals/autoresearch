# Research Goal: NIFTY50 Trading Strategy Backtest

## Objective
Research and backtest multiple trading strategies on NIFTY50 (^NSEI) using 5+ years
of historical data. Identify the best-performing strategy and explain why it works.
Find new strategies basis example strategies shown below.

## Example Strategies
1. Moving Average Crossover (50-day / 200-day SMA)
2. RSI-based (buy oversold <30, sell overbought >70)
3. Bollinger Bands mean-reversion
4. One additional strategy of your choice

## Required Metrics (per strategy)
- Sharpe Ratio (annualized, risk-free rate = 6% for India)
- Maximum Drawdown (%)
- CAGR (%)
- Win Rate (%)
- Comparison to Buy-and-Hold baseline

## Deliverables
- results/data/NIFTY50_raw.csv
- results/backtest_results.csv
- results/plots/ — equity curves
- results/report.md — written summary with conclusion

## Data
Use: yf.download("^NSEI", period="5y", interval="1d")

## Success Criteria
- [ ] Implement Moving Average Crossover strategy
- [ ] Implement RSI-based strategy
- [ ] Implement Bollinger Bands strategy
- [ ] Implement additional strategy (MACD crossover)
- [ ] Compute Sharpe Ratio for all strategies
- [ ] Compute Maximum Drawdown for all strategies
- [ ] Compute CAGR for all strategies
- [ ] Compute Win Rate for all strategies
- [ ] Compare strategies to Buy-and-Hold baseline
- [ ] Generate results/backtest_results.csv
- [ ] Generate results/plots/ — equity curves
- [ ] Write results/report.md — summary with conclusion