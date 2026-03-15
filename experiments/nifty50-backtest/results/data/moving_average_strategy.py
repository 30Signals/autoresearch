import pandas as pd
from pathlib import Path
import os
from results.plots import plot_equity_curve
current_dir = Path().absolute()
data = pd.read_csv(os.path.join(current_dir, 'data', 'NIFTY50_raw.csv'))
def moving_average_strategy():    # implement Moving Average strategy here
current_dir.mkdir(exist_ok=True)
    plt_file = current_dir / 'Moving_Avg_Strat.png'
plot_equity_curve(data)
plt.savefig(plt_file, bbox_inches='tight')
    # implement rest of the strategy
moving_average_strategy()