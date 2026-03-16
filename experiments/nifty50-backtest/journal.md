### Round 1: Setup and Data Download
- Created success criteria file with 10 deliverables
- Ready to start downloading NIFTY50 data and implementing strategies

### Round 2: Data Download and Strategy Implementation
- Downloaded 5+ years of NIFTY50 historical data (1236 days from 2021-03-15 to 2026-03-13)
- Implemented Moving Average Crossover strategy (SMA50/SMA200)
- Implemented RSI-based strategy (window=14, oversold=30, overbought=70)
- Implemented Bollinger Bands mean-reversion strategy (window=20, std=2)
- Implemented one additional strategy: Momentum strategy (lookback=252, threshold=0.1)
- Computed Sharpe Ratio, Maximum Drawdown, CAGR, and Win Rate for each strategy
- Compared each strategy to Buy-and-Hold baseline
- Saved results to results/data/NIFTY50_raw.csv, results/backtest_results.csv, and results/plots/
- Created equity curves plot for visual comparison

### Round 3: Results Analysis and Reporting
- Analyzed backtest results showing Buy & Hold outperformed all active strategies
- Momentum strategy was best performing active strategy (CAGR: 6.11%, Sharpe: 0.05)
- Buy & Hold achieved CAGR: 9.36%, Sharpe Ratio: 0.28
- Identified that strong bull market and transaction costs favored passive approach
- Generated comprehensive report in results/report.md
- All deliverables completed successfully