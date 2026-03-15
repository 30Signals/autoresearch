import pandas as pd
from pathlib import Path
import os
from results.plots import plot_equity_curve
# implement RSI strategy here
def rsi_strategy():
    current_dir = Path().absolute()
data = pd.read_csv(os.path.join(current_dir, 'data', 'NIFTY50_raw.csv'))
# implement strategy logic here
plot_equity_curve(data)
plt.savefig('results/plots/RSI_Strat.png', bbox_inches='tight')
    # implement rest of the strategy
rsi_strategy()
