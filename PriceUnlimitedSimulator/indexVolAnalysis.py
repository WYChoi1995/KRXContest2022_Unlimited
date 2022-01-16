from FinanceDataReader import DataReader
from utils import deserialize_json
import pandas as pd


class IndexVolAnalyzer(object):
    def __init__(self):
        self.weights = pd.read_csv("../Files/weight.csv", index_col="Ticker").to_dict()["Weight"]
        self.change_key_value()

        self.indexData = DataReader("KS200", "2015-06-15", "2021-12-30")["Change"]
        self.sStockData = deserialize_json("../Result/2022-01-12_GibbsSample.json")

        self.basketData = {issueCode: self.get_value(issueCode, data) for issueCode, data in self.sStockData.items()
                           if issueCode in self.weights.keys() and len(data["InitialData"]) == len(self.indexData)}
        self.add_index_etf("069500")

        self.returnData = self.get_basket_return()

    def change_key_value(self):
        self.weights = {issueCode[1:]: weightValue for issueCode, weightValue in self.weights.items()}

    def get_value(self, issueCode, data):
        return {"RealData": data["InitialData"]["Change"], "SimulatedData": data["SimulatedData"], "Weight": self.weights[issueCode]}

    def add_index_etf(self, issueCode):
        etfWeight = 1

        for weightData in self.basketData.values():
            etfWeight -= weightData["Weight"]

        self.basketData[issueCode] = {"RealData":  DataReader(issueCode, "2015-06-15", "2021-12-30")["Change"],
                                      "SimulatedData": DataReader(issueCode, "2015-06-15", "2021-12-30")["Change"],
                                      "Weight": etfWeight}

    def get_basket_return(self):
        realReturn = 0
        simulatedReturn = 0

        for data in self.basketData.values():
            realReturn += data["RealData"] * data["Weight"]
            simulatedReturn += data["SimulatedData"] * data["Weight"]

        returnData = pd.concat([self.indexData, realReturn, simulatedReturn], axis=1)
        returnData.columns = ["Index", "BasketReal", "BasketSimulated"]
        returnData["Date"] = returnData.index

        returnData = returnData[["Date", "Index", "BasketReal", "BasketSimulated"]]

        return returnData.reset_index(drop=True)


if __name__ == "__main__":
    indexVolAnalyzer = IndexVolAnalyzer()
    indexVolAnalyzer.returnData.to_csv("../Result/indexBasket.csv", index=False)
