from math import sqrt

import numpy as np
import pandas as pd

from utils import deserialize_json


class SingleMarginRateAnalyzer(object):
    def __init__(self, dataSet, issueCodes, dayInput):
        self.priceData = dataSet
        self.issueCodes = issueCodes
        self.dayInput = dayInput
        self.analysisData = {issueCode: self.extract_data(issueCode, self.dayInput) for issueCode in self.issueCodes}

    @staticmethod
    def calculate_ewma_vol(data):
        try:
            cumReturnArray = (1 + data["Change"]).cumprod()
            returnArray = (cumReturnArray.shift(1) - cumReturnArray.shift(3)) / cumReturnArray.shift(3)

            returnEwma = returnArray[250:]

            volEwma = np.zeros_like(data["Change"][250:])
            volEwma[0] = data["Change"][:250].std()

            for rowNum in range(1, len(volEwma)):
                volEwma[rowNum] = sqrt(0.94 * volEwma[rowNum - 1] ** 2 + 0.06 * returnEwma[rowNum] ** 2)

        except KeyError:
            cumReturnArray = (1 + data).cumprod()
            returnArray = (cumReturnArray.shift(1) - cumReturnArray.shift(3)) / cumReturnArray.shift(3)

            returnEwma = returnArray[250:]

            volEwma = np.zeros_like(data[250:])
            volEwma[0] = data[:250].std()

            for rowNum in range(1, len(volEwma)):
                volEwma[rowNum] = sqrt(0.94 * volEwma[rowNum - 1] ** 2 + 0.06 * returnEwma[rowNum] ** 2)

        return pd.Series(volEwma, index=data[250:].index)

    def merge_data(self, issueCode):
        realVol = self.calculate_ewma_vol(self.priceData[issueCode]["InitialData"])
        simulatedVol = self.calculate_ewma_vol(self.priceData[issueCode]["SimulatedData"])

        volMerged = pd.DataFrame({"RealVol": realVol, "SimulatedVol": simulatedVol})

        return pd.concat([self.priceData[issueCode]["InitialData"][["isUpper", "isLower"]], volMerged], axis=1).dropna()

    def extract_data(self, issueCode, dayInput):
        originalData = self.merge_data(issueCode)
        limitDayIndex = originalData.loc[(originalData.isUpper == True) | (originalData.isLower == True)].index

        try:
            extractedData = [originalData.loc[day:][:dayInput] for day in limitDayIndex]

            return pd.concat(extractedData, axis=0)[["RealVol", "SimulatedVol"]].drop_duplicates()

        except ValueError:
            extractedData = []

            return extractedData


if __name__ == "__main__":
    priceData = deserialize_json("../Result/2022-01-12_GibbsSample.json")
    tickersLimit = [ticker for ticker in priceData.keys() if len(priceData[ticker]["SimulatedParams"]) > 1]
    marginRateAnalyzer = SingleMarginRateAnalyzer(priceData, tickersLimit, 20)
