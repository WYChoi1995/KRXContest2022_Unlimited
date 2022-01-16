import numpy as np
from scipy.stats import wilcoxon, kstest, ttest_1samp


def do_single_stock_vol_test(data, ticker, pValue):
    idiosyncVol = np.array([params[-1] for params in data[ticker]["SimulatedParams"]])
    volLimited = data[ticker]["InitialParams"][-1]

    ksTestResult = kstest(idiosyncVol, "norm")

    if ksTestResult[1] >= pValue:
        ttestResult = ttest_1samp(a=idiosyncVol, popmean=volLimited, nan_policy="omit", alternative="greater")

        return {"Normal": True, "Statistic": ttestResult[0], "PValue": ttestResult[1]}

    else:
        wilcoxonResult = wilcoxon(idiosyncVol - volLimited, zero_method="pratt", alternative="greater")

        return {"Normal": False, "Statistic": wilcoxonResult[0], "PValue": wilcoxonResult[1]}
