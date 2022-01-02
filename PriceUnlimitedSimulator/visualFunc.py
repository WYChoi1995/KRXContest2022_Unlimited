import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_factor_performance(plotTitle, data, columnName):
    data.index = pd.to_datetime(data.index)

    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title(plotTitle)
    plt.plot(100 * (1 + data[columnName]).cumprod(), lw=0.7, color="mediumseagreen")
    plt.xlabel("Time")
    plt.ylabel("Performance (Start=100)")
    plt.show()


def plot_single_stock_performance(data, ticker):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title("{} Return".format(ticker))
    plt.plot(100 * data[ticker]["SimulatedData"], lw=0.7, color="mediumseagreen")
    plt.xlabel("Time")
    plt.ylabel("Return (%)")
    plt.axhline(30, 0, 1, linewidth=0.4, color="black")
    plt.axhline(-30, 0, 1, linewidth=0.4, color="black")
    plt.show()


def plot_single_stock_cum_performance(data, ticker):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title("{} Return".format(ticker))
    plt.plot(100 * (1 + data[ticker]["InitialData"]).cumprod(), lw=0.7, color="mediumseagreen")
    plt.plot(100 * (1 + data[ticker]["SimulatedData"]).cumprod(), lw=0.7, color="mediumseagreen")
    plt.xlabel("Time")
    plt.ylabel("Performance (Start=100)")
    plt.show()


def plot_single_stock_return_distribution(data, ticker):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.distplot(data[ticker]["SimulatedData"])
    plt.show()
