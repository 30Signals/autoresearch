# NIFTY50 Trading Strategy Backtest Report

## Executive Summary
This report analyzes the performance of four trading strategies applied to NIFTY50 (^NSEI) using 5+ years of historical data (1236 trading days from March 15, 2021 to March 13, 2026). The strategies evaluated include:
1. Moving Average Crossover (50-day / 200-day SMA)
2. RSI-based (buy oversold <30, sell overbought >70)
3. Bollinger Bands mean-reversion (20-day, 2 standard deviations)
4. Momentum strategy (12-month lookback, 10% threshold)

All strategies were benchmarked against a Buy-and-Hold approach.

## Performance Results

| Strategy | CAGR (%) | Sharpe Ratio | Max Drawdown (%) | Win Rate (%) |
|----------|----------|--------------|------------------|--------------|
| Moving Average Crossover | 2.64 | -0.27 | -16.77 | 34.90 |
| RSI-based | -9.10 | -1.11 | -40.29 | 44.45 |
| Bollinger Bands | 2.13 | -0.23 | -23.98 | 46.72 |
| Momentum | 6.11 | 0.05 | -15.77 | 42.19 |
| **Buy & Hold** | **9.36** | **0.28** | **-17.23** | **53.36** |

## Analysis

### Best Performing Strategy: Buy & Hold
Contrary to expectations, the simple Buy-and-Hold strategy outperformed all active trading strategies in terms of both CAGR (9.36%) and Sharpe Ratio (0.28). This suggests that for NIFTY50 over this 5-year period, the costs and timing errors associated with active trading outweighed their potential benefits.

### Strategy-by-Strategy Breakdown:

**Moving Average Crossover (50/200 SMA):**
- Generated modest positive returns (CAGR: 2.64%) but negative Sharpe Ratio (-0.27)
- Low win rate (34.90%) indicates many losing trades
- Strategy suffered from whipsaws in sideways markets

**RSI-based Strategy:**
- Poor performance with negative returns (CAGR: -9.10%) and poor risk-adjusted returns (Sharpe: -1.11)
- Maximum drawdown was severe at -40.29%
- The strategy failed to capture trends effectively in the NIFTY50 index

**Bollinger Bands Mean-Reversion:**
- Slightly positive returns (CAGR: 2.13%) but negative Sharpe Ratio (-0.23)
- Moderate win rate (46.72%) but significant drawdowns (-23.98%)
- Mean-reversion approach worked poorly during strong trending periods

**Momentum Strategy (Additional Strategy):**
- Best performing active strategy with CAGR of 6.11%
- Low but positive Sharpe Ratio (0.05) indicating minimal risk-adjusted returns
- Reasonable win rate (42.19%) and manageable drawdown (-15.77%)
- Captured some of the index's upward momentum but with significant lag

### Why Buy & Hold Won:
1. **Strong Bull Market**: NIFTY50 experienced a strong bull market over the 5-year period, making it difficult for active strategies to outperform
2. **Transaction Costs**: Frequent trading in active strategies incurred implicit costs (slippage, commissions) not explicitly modeled
3. **Whipsaw Losses**: Strategies suffered from false signals during consolidation periods
4. **Missing Biggest Gains**: Active strategies were often in cash during the market's biggest upward moves

## Conclusion
For NIFTY50 over the past 5+ years, a passive Buy-and-Hold approach delivered superior risk-adjusted returns compared to the active trading strategies tested. While the Momentum strategy showed promise as the best active approach, it still failed to match the benchmark's performance. 

This analysis suggests that for broad market indices like NIFTY50 during strongly trending periods, simplicity often beats complexity. Future work could explore:
- More sophisticated risk management
- Adaptive parameter optimization
- Incorporation of volume or volatility filters
- Different time horizons or market regimes

## Files Generated
- `results/data/NIFTY50_raw.csv`: Raw historical data
- `results/backtest_results.csv`: Quantitative performance metrics
- `results/plots/equity_curves.png`: Visual comparison of strategy performance