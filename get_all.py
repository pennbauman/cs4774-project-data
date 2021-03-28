#!/bin/python
import os
import pandas as pd

# Get all source CSVs
for f in os.listdir("."):
    if os.path.isdir(f) and (f[0] != "."):
        os.chdir(f)
        for sh in os.listdir("."):
            if (sh[:4] == "get_") and (sh[-3:] == ".py"):
                print(sh)
                os.system("./" + sh)
        os.chdir("..")

# NOAA Weather
weather_data = pd.read_csv("./noaa-cag/weather_data.csv")
data = weather_data

# EIA Electric
solar_data = pd.read_csv("./eia-electricity/solar_data.csv")
solar_data.rename(columns = {'MWh':'Solar MWh'}, inplace = True)
wind_data = pd.read_csv("./eia-electricity/wind_data.csv")
wind_data.rename(columns = {'MWh':'Wind MWh'}, inplace = True)
data = data.combine_first(solar_data)
data = data.combine_first(wind_data)

# Print to CSV
data.to_csv("data.csv", columns=[
        "State", "Year", "Month", "Solar MWh", "Wind MWh", "Temp", "Precip"
    ], index=False)
