import json
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt


def deserialize_json(filePath):
    with open(filePath, "r") as jsonFile:
        sampledData = json.load(jsonFile)

        for paramsData in sampledData.values():
            paramsData["InitialData"] = pd.DataFrame(paramsData["InitialData"])
            paramsData["InitialData"].index = pd.to_datetime(paramsData["InitialData"].index)
            paramsData["SimulatedData"] = pd.Series(paramsData["SimulatedData"])
            paramsData["SimulatedData"].index = pd.to_datetime(paramsData["SimulatedData"].index)

    return sampledData


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


def plot_single_stock_idiosyncratic_vol_distribution(data, ticker):
    idiosyncVol = [100 * params[-1] for params in data[ticker]["SimulatedParams"]]
    volLimited = data[ticker]["InitialParams"][-1] * 100

    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.title("{} Return".format(ticker))
    plt.axvline(volLimited, 0, 1, linewidth=0.7, color="black")
    sns.distplot(idiosyncVol)
    plt.xlabel("Idiosyncratic Volatility (%)")
    plt.show()
