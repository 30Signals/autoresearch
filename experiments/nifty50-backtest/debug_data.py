import pandas as pd

data = pd.read_csv('results/data/NIFTY50_raw.csv')
print("Shape:", data.shape)
print("Columns:", data.columns.tolist())
print("First few rows:")
print(data.head())
print("Data types:")
print(data.dtypes)