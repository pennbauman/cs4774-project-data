#!/bin/python3
# Get Monthly Wind Capacity Data
#   https://windexchange.energy.gov/maps-data/321
#
#   Penn Bauman (pcb8gb@virginia.edu)
#     CS 4774 - Spring 2021
import sys
import os.path
import pandas as pd
import urllib.request
import zipfile

XLSX_99_17 = 'wind_capacity_1999-2017.xls'
XLSX_20_21 = 'wind_capacity_2020-2021.xlsx'
STATES = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}
OUTPUT_FILE = "capacity_data.csv"

ZIP_URL = "https://www.eia.gov/electricity/data/eia860/archive/xls/"
ZIP_FILE = "eia860{year}.zip"


try:
    os.remove(OUTPUT_FILE)
except:
    pass
with open(OUTPUT_FILE, 'w') as csv_out:
    csv_out.write("Year,State,Wind,Solar\n")

os.makedirs("tmp", exist_ok=True)
for y in range(1, 20):
    y += 2000
    f = ZIP_FILE.format(year = y)
    if not os.path.isfile("tmp/" + f):
        print("Downloading '%s'" % f)
        try:
            if (y == 2019):
                urllib.request.urlretrieve(ZIP_URL.replace("archive/", "") + f, "tmp/" + f)
            else:
                urllib.request.urlretrieve(ZIP_URL + f, "tmp/" + f)
        except:
            print('Download failed')
            sys.exit(1)

        print("Unzipping '%s'" % f)
        with zipfile.ZipFile("tmp/" + f, 'r') as zip_ref:
            zip_ref.extractall("tmp/" + f[0:-4])

def parse_state_caps(raw_data):
    data = {}
    # Scan for used columans
    i = 0
    state_i = -1
    sum_cap_i = -1
    for h in raw_data.columns.values:
        if h == "State":
            state_i = i
        if "Summer Capacity" in h:
            sum_cap_i = i
        i += 1
    # Check needed columns were found
    if (state_i == -1 or sum_cap_i == -1):
        if (state_i == -1):
            print("Column not found 'State'")
        if (sum_cap_i == -1):
            print("Column not found 'Summer Capacity*'")
        sys.exit(1)
    # Read rows for data
    for j, line in raw_data.iterrows():
        if line[state_i] in data:
            data[line[state_i]] += line[sum_cap_i]
        else:
            data[line[state_i]] = line[sum_cap_i]
    return data


def get_Type_Y(f):
    print(f, "+")
    raw_wind = pd.read_excel(f, header=1, engine="openpyxl")
    solar_f = f[0:16] + "_3_Solar_" + f[24:]
    print(solar_f, ".", end='', flush=True)
    raw_solar = pd.read_excel(f, header=1, engine="openpyxl")

    wind_data = parse_state_caps(raw_wind)
    solar_data = parse_state_caps(raw_solar)
    print(".", end='', flush=True)

    # Merge data
    data = {}
    for state, wind in wind_data.items():
        if state in solar_data.keys():
            solar = solar_data.pop(state)
        else:
            solar = 0
        data[state] = (wind, solar)
    for state in solar_data.keys():
        solar = solar_data[state]
        wind = 0
        data[state] = (wind, solar)

    print(".")
    # Output to CSV
    y = f[10:14]
    for state, x in data.items():
        with open(OUTPUT_FILE, 'a') as csv_out:
            csv_out.write("%s,%s,%s,%s\n" % (y, state, x[0], x[1]))


def write_any(raw, y):
    print(".", end='', flush=True)
    # Read rows for data
    solar_abbrev = ["PVC", "PV", "PC", "SUN"]
    wind_data = {}
    solar_data = {}
    unknown_types = set()
    for j, line in raw.iterrows():
        if line[2] == "WTG" or line[2] == "WND":
            if line[0] in wind_data:
                wind_data[line[0]] += line[1]
            else:
                wind_data[line[0]] = line[1]
        elif line[2] in solar_abbrev:
            if line[0] in solar_data:
                solar_data[line[0]] += line[1]
            else:
                solar_data[line[0]] = line[1]
        else:
            unknown_types.add(line[2])
    # Merge data
    data = {}
    for state, wind in wind_data.items():
        if state in solar_data.keys():
            solar = solar_data.pop(state)
        else:
            solar = 0
        data[state] = (wind, solar)
    for state in solar_data.keys():
        solar = solar_data[state]
        wind = 0
        data[state] = (wind, solar)
    print(".")
    # Output to CSV
    for state, data in data.items():
        with open(OUTPUT_FILE, 'a') as csv_out:
            csv_out.write("%s,%s,%s,%s\n" % (y, state, data[0], data[1]))

def get_GeneratorY(f):
    print(f, ".", end='', flush=True)
    #if f[12:0]
    raw = pd.read_excel(f, header=1, engine="openpyxl")
    solar_data = {}
    # Scan for used columans
    for h in raw.columns.values:
        if h == "State":
            raw.rename(columns = {h : "STATE"}, inplace=True)
        if "Summer Capacity" in h:
            raw.rename(columns = {h : "SUMMER_CAPABILITY"}, inplace=True)
        if h == "Energy Source 1":
            raw.rename(columns = {h : "ENERGY_SOURCE_1"}, inplace=True)
    # Check needed columns were found
    if "STATE" not in raw.columns.values:
        print("Column not found 'STATE'")
        sys.exit(1)
    if "SUMMER_CAPABILITY" not in raw.columns.values:
        print("Column not found 'SUMMER_CAPABILITY'")
        sys.exit(1)
    if "ENERGY_SOURCE_1" not in raw.columns.values:
        print("Column not found 'ENERGY_SOURCE_1'")
        sys.exit(1)
    # Output data
    y = f[10:14]
    write_any(raw[["STATE", "SUMMER_CAPABILITY", "ENERGY_SOURCE_1"]], y)

def get_old(f):
    print(f, ".", end='', flush=True)
    raw = pd.read_excel(f, header=0)
    wind_data = {}
    solar_data = {}
    # Scan for used columans
    for h in raw.columns.values:
        if "SUMMCAP" in h:
            raw.rename(columns = {h : "SUMMER_CAPABILITY"}, inplace=True)
        if "SUMMER_CAPACITY" in h:
            raw.rename(columns = {h : "SUMMER_CAPABILITY"}, inplace=True)
    # Check needed columns were found
    if "STATE" not in raw.columns.values:
        print("Column not found 'STATE'")
        sys.exit(1)
    if "SUMMER_CAPABILITY" not in raw.columns.values:
        print("Column not found 'SUMMER_CAPABILITY'")
        sys.exit(1)
    if "ENERGY_SOURCE_1" not in raw.columns.values:
        print("Column not found 'ENERGY_SOURCE_1'")
        sys.exit(1)
    # Output data
    y = f[10:14]
    write_any(raw[["STATE", "SUMMER_CAPABILITY", "ENERGY_SOURCE_1"]], y)



for d in os.listdir("tmp"):
    if os.path.isdir("tmp/" + d):
        d = "tmp/" + d
        found = False
        for f in os.listdir(d):
            if "3_2_Wind_Y" == f[0:10]:
                get_Type_Y(d + "/" + f)
                found = True
            if ("GeneratorY" == f[0:10] and ".xlsx" == f[-5:]):
                get_GeneratorY(d + "/" + f)
                found = True
            elif "GenY" == f[0:4] or "Generator" == f[0:9]:
                get_old(d + "/" + f)
                found = True
            if "GENY" == f[0:4]:
                print(d + "/" + f)
                print("Not Implemented")
                found = True
        if not found:
            print("failed:", d)
