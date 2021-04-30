#!/bin/python
# Get All Data
#   Penn Bauman (pcb8gb@virginia.edu)
#     CS 4774 - Spring 2021
import os
import pandas as pd


# NOAA Weather
if not os.path.isfile("./noaa-cag/weather_data.csv"):
    os.chdir("noaa-cag")
    os.system("./get_weather.py")
    os.chdir("..")
weather_data = pd.read_csv("./noaa-cag/weather_data.csv")
data = weather_data

# EIA Electric
if not os.path.isfile("./eia-electricity/solar_data.csv"):
    os.chdir("eia-electricity")
    os.system("./get_electric.py")
    os.chdir("..")
solar_data = pd.read_csv("./eia-electricity/solar_data.csv")
solar_data.rename(columns = {'MWh':'Solar_MWh'}, inplace = True)
wind_data = pd.read_csv("./eia-electricity/wind_data.csv")
wind_data.rename(columns = {'MWh':'Wind_MWh'}, inplace = True)
data = data.combine_first(solar_data)
data = data.combine_first(wind_data)

# EIA Capacity
if not os.path.isfile("./eia-capacity/capacity_data.csv"):
    os.chdir("eia-capacity")
    os.system("./get_capacity.py")
    os.chdir("..")
cap_data = pd.read_csv("./eia-capacity/capacity_data.csv")
cap_data.rename(columns = {'Wind':'Wind_Capacity'}, inplace = True)
cap_data.rename(columns = {'Solar':'Solar_Capacity'}, inplace = True)
data = data.combine_first(cap_data)


data["Wind_MWh"].fillna(0, inplace=True)
data["Solar_MWh"].fillna(0, inplace=True)
data["Wind_Capacity"].fillna(0, inplace=True)
data["Solar_Capacity"].fillna(0, inplace=True)
#print(data.info())

# Print to CSV
data = data[["State", "Year", "Month", "Solar_MWh", "Wind_MWh", "Temp", "Precip", "Wind_Capacity", "Solar_Capacity"]]
data.to_csv("data.csv", index=False)
