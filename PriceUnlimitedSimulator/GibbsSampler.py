from copy import deepcopy
from datetime import datetime

import numpy as np
import pandas as pd
import json

from FinanceDataReader import DataReader
from investpy import get_bond_historical_data
from statsmodels.regression.linear_model import OLS


class GibbsSampler(object):
    def __init__(self, trialNumInput: int = 5000, collectNumInput: int = 1000, startDate: str = "2015-06-15", endDate: str = "2021-12-30"):
        self.startDate = startDate
        self.endDate = endDate
        self.trialNumInput = trialNumInput
        self.collectionNumInput = collectNumInput

        self.invPyStartDate = datetime.strftime(datetime.strptime(startDate, "%Y-%m-%d"), "%d/%m/%Y")
        self.invPyEndDate = datetime.strftime(datetime.strptime(endDate, "%Y-%m-%d"), "%d/%m/%Y")

        self.riskFreeRate = (get_bond_historical_data("South Korea 3Y", self.invPyStartDate, self.invPyEndDate)["Close"] / 100) / 360
        self.stockFuturesListed = pd.read_csv("./Files/futuresListed.csv", encoding="cp949")

        self.kospiTickers = [kospiTicker[1:] for kospiTicker in self.stockFuturesListed.loc[self.stockFuturesListed["Market"] == "KOSPI"]["Ticker"]]
        self.kosdaqTickers = [kosdaqTicker[1:] for kosdaqTicker in self.stockFuturesListed.loc[self.stockFuturesListed["Market"] == "KOSDAQ"]["Ticker"]]

        self.kospiPriceRange = [0, 1000, 5000, 10000, 50000, 100000, 500000, np.inf]
        self.kospiPriceLabel = np.array([1, 5, 10, 50, 100, 500, 1000])

        self.kosdaqPriceRange = [0, 1000, 5000, 10000, 50000, np.inf]
        self.kosdaqPriceLabel = np.array([1, 5, 10, 50, 100])

        self.kospiIndex = DataReader("KS11", self.startDate, self.endDate)["Change"] - self.riskFreeRate
        self.kosdaqIndex = DataReader("KQ11", self.startDate, self.endDate)["Change"] - self.riskFreeRate

        self.calhartFactors = pd.read_csv("./Files/calhart.csv", index_col="Date")
        self.calhartFactors.index = pd.to_datetime(self.calhartFactors.index)

        self.kospiStockPriceData = {issueCode: self.__call_price_data(issueCode) for issueCode in self.kospiTickers}
        self.kosdaqStockPriceData = {issueCode: self.__call_price_data(issueCode) for issueCode in self.kosdaqTickers}

        self.priceData = {**self.kospiStockPriceData, **self.kosdaqStockPriceData}

        self.gibbsSampleResult = {issueCode: self.__do_gibbs_sampling(codePriceData["Data"], codePriceData["InitialBetaMR"], codePriceData["InitialBetaHML"], codePriceData["InitialBetaSMB"],
                                                                      codePriceData["InitialBetaMMT"], codePriceData["InitialResidSigma"], self.trialNumInput, self.collectionNumInput)
                                  for issueCode, codePriceData in self.priceData.items()}

    def __call_price_data(self, ticker):
        priceData = DataReader(ticker, self.startDate, self.endDate)
        priceData["RiskPremium"] = priceData["Change"] - self.riskFreeRate

        rawUpperLimit = priceData["Close"].shift(1) * 1.3
        rawLowerLimit = priceData["Close"].shift(1) * 0.7

        if ticker in self.kospiTickers:
            adjustedTickUpper = pd.to_numeric(pd.cut(rawUpperLimit, self.kospiPriceRange, labels=self.kospiPriceLabel))
            adjustedTickLower = pd.to_numeric(pd.cut(rawLowerLimit, self.kospiPriceRange, labels=self.kospiPriceLabel))

            priceData["MarketReturn"] = self.kospiIndex
            priceData["HML"] = self.calhartFactors["KSHML"].loc[self.calhartFactors.index >= priceData.index[0]]
            priceData["SMB"] = self.calhartFactors["KSSMB"].loc[self.calhartFactors.index >= priceData.index[0]]
            priceData["MMT"] = self.calhartFactors["KSMMT"].loc[self.calhartFactors.index >= priceData.index[0]]

            priceData.dropna(inplace=True)

            marketModel = OLS(priceData["RiskPremium"], priceData[["MarketReturn", "HML", "SMB", "MMT"]]).fit()
            initialBetaMR = marketModel.params["MarketReturn"]
            initialBetaHML = marketModel.params["HML"]
            initialBetaSMB = marketModel.params["SMB"]
            initialBetaMMT = marketModel.params["MMT"]
            initialSigma = marketModel.mse_resid ** 0.5

        else:
            adjustedTickUpper = pd.to_numeric(pd.cut(rawUpperLimit, self.kosdaqPriceRange, labels=self.kosdaqPriceLabel))
            adjustedTickLower = pd.to_numeric(pd.cut(rawLowerLimit, self.kosdaqPriceRange, labels=self.kosdaqPriceLabel))

            priceData["MarketReturn"] = self.kosdaqIndex
            priceData["HML"] = self.calhartFactors["KQHML"].loc[self.calhartFactors.index >= priceData.index[0]]
            priceData["SMB"] = self.calhartFactors["KQSMB"].loc[self.calhartFactors.index >= priceData.index[0]]
            priceData["MMT"] = self.calhartFactors["KQMMT"].loc[self.calhartFactors.index >= priceData.index[0]]

            priceData.dropna(inplace=True)

            marketModel = OLS(priceData["RiskPremium"], priceData[["MarketReturn", "HML", "SMB", "MMT"]]).fit()
            initialBetaMR = marketModel.params["MarketReturn"]
            initialBetaHML = marketModel.params["HML"]
            initialBetaSMB = marketModel.params["SMB"]
            initialBetaMMT = marketModel.params["MMT"]
            initialSigma = marketModel.mse_resid ** 0.5

        priceData["UpperLimit"] = (rawUpperLimit / adjustedTickUpper).apply(np.floor) * adjustedTickUpper
        priceData["LowerLimit"] = (rawLowerLimit / adjustedTickLower).apply(np.ceil) * adjustedTickLower

        priceData["isUpper"] = (priceData["UpperLimit"] == priceData["Close"])
        priceData["isLower"] = (priceData["LowerLimit"] == priceData["Close"])

        return {"Data": priceData, "InitialBetaMR": initialBetaMR, "InitialBetaHML": initialBetaHML, "InitialBetaSMB": initialBetaSMB,
                "InitialBetaMMT": initialBetaMMT, "InitialResidSigma": initialSigma}

    def __do_gibbs_sampling(self, priceData, initialBetaMR, initialBetaHML, initialBetaSMB, initialBetaMMT, initialSigma, trialNumInput, collectNumInput):
        betaMR = initialBetaMR
        betaHML = initialBetaHML
        betaSMB = initialBetaSMB
        betaMMT = initialBetaMMT
        residSigma = initialSigma

        realReturn = deepcopy(priceData[["Change", "isUpper", "isLower"]])
        realReturn.index = realReturn.index.strftime("%Y-%m-%d")

        trialNum = 0

        gibbsResults = []
        simulatedReturns = []

        isUpperOrLower = len(priceData.loc[(priceData["isUpper"] == True) | (priceData["isLower"] == True)])

        if isUpperOrLower != 0:
            while trialNum <= trialNumInput:
                trialNum += 1
                priceData["GeneratedReturn"] = np.random.normal(betaMR * priceData["Change"] + betaHML * priceData["HML"] + betaSMB * priceData["SMB"] + betaMMT * priceData["MMT"], residSigma)
                priceData["UnlimitedReturn"] = priceData.apply(lambda dataRow: self.__get_real_return(dataRow), axis=1)
                priceData["UnlimitedMp"] = priceData["UnlimitedReturn"] - self.riskFreeRate

                marketModel = OLS(priceData["UnlimitedMp"], priceData[["MarketReturn", "HML", "SMB", "MMT"]]).fit()

                betaMR = marketModel.params["MarketReturn"]
                betaHML = marketModel.params["HML"]
                betaSMB = marketModel.params["SMB"]
                betaMMT = marketModel.params["MMT"]
                residSigma = marketModel.mse_resid ** 0.5

                if trialNum >= collectNumInput:
                    simulatedReturns.append(deepcopy(priceData["UnlimitedReturn"]))
                    gibbsResult = (betaMR, betaHML, betaSMB, betaMMT, residSigma)
                    gibbsResults.append(gibbsResult)

                else:
                    pass

            meanSimulatedReturn = pd.concat(simulatedReturns, axis=1).mean(axis=1)
            meanSimulatedReturn.index = meanSimulatedReturn.index.strftime("%Y-%m-%d")

        else:
            gibbsResult = (betaMR, betaHML, betaSMB, betaMMT, residSigma)
            meanSimulatedReturn = realReturn["Change"]
            gibbsResults.append(gibbsResult)

        return {"InitialData": realReturn.to_dict(), "InitialParams": (initialBetaMR, initialBetaHML, initialBetaSMB, initialBetaMMT, initialSigma),
                "SimulatedData": meanSimulatedReturn.to_dict(), "SimulatedParams": gibbsResults}

    @staticmethod
    def __get_real_return(priceDataRow):
        if priceDataRow["isUpper"] is True:
            return max(priceDataRow["GeneratedReturn"], priceDataRow["Change"])

        elif priceDataRow["isLower"] is True:
            return min(priceDataRow["GeneratedReturn"], priceDataRow["Change"])

        else:
            return priceDataRow["Change"]

    def save_result(self):
        with open("./Result/{}_GibbsSample.json".format(datetime.strftime(datetime.today(), "%Y-%m-%d")), "w") as resultFile:
            jsonResult = json.dumps(self.gibbsSampleResult, indent=4)
            resultFile.write(jsonResult)
