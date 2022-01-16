import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


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
    plt.axhline(30, 0, 1, linewidth=0.7, color="black")
    plt.axhline(-30, 0, 1, linewidth=0.7, color="black")
    plt.show()


def plot_single_stock_cum_performance(data, ticker):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title("{} Return".format(ticker))
    plt.plot(100 * (1 + data[ticker]["InitialData"]["Change"]).cumprod(), lw=0.5, color="black")
    plt.plot(100 * (1 + data[ticker]["SimulatedData"]).cumprod(), lw=0.7, color="mediumseagreen")
    plt.xlabel("Time")
    plt.ylabel("Performance (Start=100)")
    plt.show()


def plot_single_stock_return_distribution(data, ticker):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title("{} Return".format(ticker))
    sns.histplot(100 * data[ticker]["SimulatedData"])
    plt.xlabel("Return (%)")
    plt.show()


def plot_index_performance(originalData, comparedData, label):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title("Performance")
    plt.plot(100 * (1 + originalData).cumprod(), lw=0.5, color="black", label=label[0])
    plt.plot(100 * (1 + comparedData).cumprod(), lw=0.7, color="mediumseagreen", label=label[1])
    plt.xlabel("Time")
    plt.ylabel("Performance (Start=100)")
    plt.legend()
    plt.show()


def plot_index_tracking_error(originalData, comparedData):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title("Tracking Error")
    plt.plot(100 * (originalData - comparedData), lw=0.5, color="mediumseagreen", label="KOSPI 200 - Basket")
    plt.xlabel("Time")
    plt.ylabel("Spread (%)")
    plt.legend()
    plt.show()


def plot_single_stock_idiosyncratic_vol_distribution(data, ticker):
    idiosyncVol = [100 * params[-1] for params in data[ticker]["SimulatedParams"]]
    volLimited = data[ticker]["InitialParams"][-1] * 100

    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title("{} Vol distribution".format(ticker))
    plt.axvline(volLimited, 0, 1, linewidth=0.7, color="black", label="Real Vol")
    sns.distplot(idiosyncVol)
    plt.xlabel("Idiosyncratic Volatility (%)")
    plt.legend()
    plt.show()
