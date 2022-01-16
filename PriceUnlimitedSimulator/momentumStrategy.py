import re

import pandas as pd
from FinanceDataReader import DataReader


class MomentumStrategy(object):
    def __init__(self):
        self.investPool = pd.read_csv("../Files/mmtPool.csv")
        self.marketCodes = ["KS" + str(year) for year in range(2015, 2022)] + ["KQ" + str(year) for year in range(2015, 2022)]

        self.investPool = {marketCode:
                               {"Long": [issueCode[1:] for issueCode in self.investPool[marketCode + "Long"].values],
                                "Short": [issueCode[1:] for issueCode in self.investPool[marketCode + "Short"].values]} for marketCode in self.marketCodes}

        self.mmtData = self.get_return()

    def get_return(self):
        longShortReturns = {}

        for marketCode, portfolio in self.investPool.items():
            longPortfolio = {issueCode: DataReader(issueCode, re.sub(r'[^0-9]', "", marketCode), str(int(re.sub(r'[^0-9]', "", marketCode)) + 1)) for issueCode in portfolio["Long"]}
            shortPortfolio = {issueCode: DataReader(issueCode, re.sub(r'[^0-9]', "", marketCode), str(int(re.sub(r'[^0-9]', "", marketCode)) + 1)) for issueCode in portfolio["Short"]}

            longShortReturns[marketCode] = pd.concat([longReturn["Change"] for longReturn in longPortfolio.values()], axis=1).mean(axis=1) - \
                                       pd.concat([shortReturn["Change"] for shortReturn in shortPortfolio.values()], axis=1).mean(axis=1)

        kospiReturn = pd.concat([longShortReturns[marketCode] for marketCode in self.marketCodes if "KS" in marketCode], axis=0)
        kosdaqReturn = pd.concat([longShortReturns[marketCode] for marketCode in self.marketCodes if "KQ" in marketCode], axis=0)

        momentumData = pd.DataFrame({"KSMMT": kospiReturn, "KQMMT": kosdaqReturn})

        return momentumData


if __name__ == "__main__":
    mmtStrategy = MomentumStrategy()
    mmtStrategy.mmtData.to_csv(path_or_buf="../Files/mmtData.csv")
