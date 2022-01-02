import json
import pandas as pd


def deserialize_json(filePath):
    with open(filePath, "r") as jsonFile:
        sampledData = json.load(jsonFile)

        for paramsData in sampledData.values():
            paramsData["InitialData"] = pd.DataFrame(paramsData["InitialData"])
            paramsData["InitialData"].index = pd.to_datetime(paramsData["InitialData"].index)
            paramsData["SimulatedData"] = pd.Series(paramsData["SimulatedData"])
            paramsData["SimulatedData"].index = pd.to_datetime(paramsData["SimulatedData"].index)

    return sampledData
