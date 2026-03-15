# Success Criteria for NIFTY50 Trading Strategy Backtest

## Data Collection
- [ ] NIFTY50 raw data downloaded and saved as `results/data/NIFTY50_raw.csv`
- [ ] Data contains at least 5 years of daily OHLCV data for ^NSEI

## Strategy Implementation
- [ ] Moving Average Crossover (50-day / 200-day SMA) implemented
- [ ] RSI-based strategy (buy oversold <30, sell overbought >70) implemented
- [ ] Bollinger Bands mean-reversion strategy implemented
- [ ] One additional strategy of choice implemented (Mean Reversion with 20-period Bollinger Bands)

## Metrics Computation
For each strategy, the following metrics computed and saved:
- [ ] Sharpe Ratio (annualized, risk-free rate = 6% for India)
- [ ] Maximum Drawdown (%)
- [ ] CAGR (%)
- [ ] Win Rate (%)
- [ ] Comparison to Buy-and-Hold baseline

## Results Organization
- [ ] All backtest results saved in `results/backtest_results.csv`
- [ ] Equity curves plots saved in `results/plots/` directory
- [ ] Written summary with conclusion saved in `results/report.md`

## Analysis Complete
- [ ] Best-performing strategy identified
- [ ] Explanation provided for why the best strategy works
- [ ] All deliverables completed as specified