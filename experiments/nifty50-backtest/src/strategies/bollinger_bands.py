import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

class BollingerBandsStrategy(Strategy):
    def init(self):
        # Calculate Bollinger Bands
        close = self.data.Close
        self.sma = self.I(lambda x: pd.Series(x).rolling(window=20).mean(), close)
        self.std = self.I(lambda x: pd.Series(x).rolling(window=20).std(), close)
        self.upper = self.sma + (2 * self.std)
        self.lower = self.sma - (2 * self.std)

    def next(self):
        # Buy when price crosses below lower band
        if self.data.Close[-1] < self.lower[-1] and self.data.Close[-2] >= self.lower[-2]:
            self.buy()
        # Sell when price crosses above upper band
        elif self.data.Close[-1] > self.upper[-1] and self.data.Close[-2] <= self.upper[-2]:
            self.position.close()