import os
import matplotlib.pyplot as plt
def plot_equity_curve(data):    plt.plot(data)
def plot_closing_price(data):    plt.plot(data)
def plot_volume(data):    plt.plot(data)
def main():    data = read_file('results/data/NIFTY50_raw.csv')    plot_equity_curve(data)
if __name__ == '__main__':    main()