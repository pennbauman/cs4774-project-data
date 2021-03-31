#!/bin/python3
# Get Monthly Electric Generation Data
#   https://www.eia.gov/electricity/data/state/
#
#   Penn Bauman (pcb8gb@virginia.edu)
#     CS 4774 - Spring 2021
import os.path
import pandas as pd
import urllib.request

XLSX = 'generation_monthly.xlsx'
XLSX_SHEET_HEADERS = [
    0, 0, 0, 0, 0,
    4, 4, 4, 4, 4, 4, 4, 4, 4
]
CSV_COLUMNS = ["Year", "Month", "State", "MWh"]


solar_set = pd.DataFrame(columns=CSV_COLUMNS)
wind_set = pd.DataFrame(columns=CSV_COLUMNS)

solar_i = 0
wind_i = 0

if not os.path.isfile(XLSX):
    print("Downloading '%s'" % XLSX)
    respose = urllib.request.urlretrieve('https://www.eia.gov/electricity/data/state/generation_monthly.xlsx', XLSX)
    try:
        f = open(XLSX, "r")
        f.close()
    except:
        raise ValueError('http get fail')

i = 0
for start in XLSX_SHEET_HEADERS:
    print("Processing Sheet %d" % i)
    raw = pd.read_excel(XLSX, i, header=start, engine="openpyxl")
    raw = raw[raw["STATE"] != "US-TOTAL"]
    data = raw.loc[raw["TYPE OF PRODUCER"] == "Total Electric Power Industry"]
    solar = data.loc[data["ENERGY SOURCE"] == "Solar Thermal and Photovoltaic"]
    wind = data.loc[data["ENERGY SOURCE"] == "Wind"]

    gen_col = None
    for label in data.columns.values:
        if (label.find("GENERATION") != -1):
            gen_col = label
    if not gen_col:
        raise ValueError("GENERATION column not found")

    for j, row in solar.iterrows():
        solar_set.loc[solar_i] = [row["YEAR"], row["MONTH"], row["STATE"], row[gen_col]]
        solar_i += 1

    for j, row in wind.iterrows():
        wind_set.loc[wind_i] = [row["YEAR"], row["MONTH"], row["STATE"], row[gen_col]]
        wind_i += 1

    #print(i)
    #print(wind)
    #print(solar)
    i += 1

solar_set.to_csv("solar_data.csv", index=False)
wind_set.to_csv("wind_data.csv", index=False)
