import pandas as pd
from pathlib import Path
import os
from results.plots import plot_equity_curve
def buy_and_hold_strategy():    current_dir = Path().absolute()
data = pd.read_csv(os.path.join(current_dir, 'data', 'NIFTY50_raw.csv'))
# implement Buy-and-Hold strategy logic here
plot_equity_curve(data)
plt.savefig('results/plots/BUY_HLD_Strat.png', bbox_inches='tight')
    # implement rest of the strategy
buy_and_hold_strategy()