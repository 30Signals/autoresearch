import pandas as pd
import numpy as np
def calculate_sharpe_ratio(strategy_returns):    risk_free_rate = 0.06
return (strategy_returns.mean() - risk_free_rate) / strategy_returns.std()
# implement rest of the function
