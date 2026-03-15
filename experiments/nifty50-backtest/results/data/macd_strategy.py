import pandas as pd
from pathlib import Path
import os
from results.plots import plot_equity_curve
def macd_strategy():    current_dir = Path().absolute()
data = pd.read_csv(os.path.join(current_dir, 'data', 'NIFTY50_raw.csv'))
# implement MACD strategy here
plot_equity_curve(data)
plt.savefig('results/plots/MACD_Strat.png', bbox_inches='tight')
    # implement rest of the strategy
macd_strategy()