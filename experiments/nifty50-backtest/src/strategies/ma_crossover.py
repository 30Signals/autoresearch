import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

class MACrossover(Strategy):
    def init(self):
        # Calculate 50 and 200 day SMAs
        close = self.data.Close
        self.sma50 = self.I(lambda x: pd.Series(x).rolling(50).mean(), close)
        self.sma200 = self.I(lambda x: pd.Series(x).rolling(200).mean(), close)

    def next(self):
        # Buy when 50 crosses above 200
        if self.sma50[-1] > self.sma200[-1] and self.sma50[-2] <= self.sma200[-2]:
            self.buy()
        # Sell when 50 crosses below 200
        elif self.sma50[-1] < self.sma200[-1] and self.sma50[-2] >= self.sma200[-2]:
            self.position.close()