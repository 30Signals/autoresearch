import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

class MACDCrossoverStrategy(Strategy):
    def init(self):
        # Calculate MACD and signal
        close = self.data.Close
        # Fast EMA (12), Slow EMA (26)
        ema_fast = self.I(lambda x: pd.Series(x).ewm(span=12, adjust=False).mean(), close)
        ema_slow = self.I(lambda x: pd.Series(x).ewm(span=26, adjust=False).mean(), close)
        macd = ema_fast - ema_slow
        # Signal line (9-period EMA of MACD)
        signal = self.I(lambda x: pd.Series(x).ewm(span=9, adjust=False).mean(), macd)
        self.macd = macd
        self.signal = signal

    def next(self):
        # Buy when MACD crosses above signal
        if self.macd[-1] > self.signal[-1] and self.macd[-2] <= self.signal[-2]:
            self.buy()
        # Sell when MACD crosses below signal
        elif self.macd[-1] < self.signal[-1] and self.macd[-2] >= self.signal[-2]:
            self.position.close()