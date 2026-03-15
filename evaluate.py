import yfinance as yf
def moving_average_crossover(df):
    # Calculate 50-day and 200-day SMA
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()

    # Create a new column for the crossover signal
    df['Signal'] = 0.0
    df.loc[(df['SMA_50'] > df['SMA_200']), 'Signal'] = 1
    df.loc[(df['SMA_50'] < df['SMA_200']), 'Signal'] = -1

    return df