from PriceUnlimitedSimulator.utils import *
from PriceUnlimitedSimulator.visualFunc import *

import pandas as pd

if __name__ == "__main__":
    priceData = deserialize_json("./Result/2022-01-02_GibbsSample.json")
    factorData = pd.read_csv("./Files/calhart.csv", index_col="Date")
