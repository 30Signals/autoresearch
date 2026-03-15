import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

class RSIStrategy(Strategy):
    def init(self):
        # Calculate RSI
        close = self.data.Close
        delta = self.I(lambda x: pd.Series(x).diff(), close)
        gain = self.I(lambda x: pd.Series(x).where(lambda y: (y>0), 0).rolling(window=14).mean(), delta)
        loss = self.I(lambda x: pd.Series(x).where(lambda y: (y<0), 0).rolling(window=14).mean().abs(), delta)
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        self.rsi = rsi

    def next(self):
        # Buy when RSI < 30 (oversold)
        if self.rsi[-1] < 30:
            self.buy()
        # Sell when RSI > 70 (overbought)
        elif self.rsi[-1] > 70:
            self.position.close()