import pandas as pd
from pathlib import Path
import os
from results.plots import plot_equity_curve
# implement Bollinger Bands strategy here
def bollinger_bands_strategy():    current_dir = Path().absolute()
data = pd.read_csv(os.path.join(current_dir, 'data', 'NIFTY50_raw.csv'))
# implement strategy logic here
plot_equity_curve(data)
plt.savefig('results/plots/Bollinger_Strat.png', bbox_inches='tight')
bollinger_bands_strategy()