import pandas as pd
import numpy as np
from backtesting import Backtest

class StrategyAnalyzer:
    def __init__(self, results):
        self.results = results
        self.equity = results._equity_curve['Equity']
        self.trades = results._trades
        try:
            self.stats = results._stats
        except AttributeError:
            self.stats = {}
    
    # rest of the class definition...