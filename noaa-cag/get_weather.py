#!/bin/python3
# Get Monthly Weather by State from NOAA
#   https://www.ncdc.noaa.gov/cag/statewide/time-series
#
#   Penn Bauman (pcb8gb@virginia.edu)
#     CS 4774 - Spring 2021
import os
import urllib.request

START_YEAR = 2000
END_YEAR = 2020


states = {
    "AL": 1,  "AZ": 2,  "AR": 3,  "CA": 4,  "CO": 5,  "CT": 6,  "DE": 7,  "FL": 8,
    "GA": 9,  "ID": 10, "IL": 11, "IN": 12, "IA": 13, "KS": 14, "KY": 15, "LA": 16,
    "ME": 17, "MD": 18, "MA": 19, "MI": 20, "MN": 21, "MS": 22, "MO": 23, "MT": 24,
    "NE": 25, "NV": 26, "NH": 27, "NJ": 28, "NM": 29, "NY": 30, "NC": 31, "ND": 32,
    "OH": 33, "OK": 34, "OR": 35, "PA": 36, "RI": 37, "SC": 38, "SD": 39, "TN": 40,
    "TX": 41, "UT": 42, "VT": 43, "VA": 44, "WA": 45, "WV": 46, "WI": 47, "WY": 48,
    #"HI": 49,
    "AK": 50,
}
kind = {
    "temp_avg": "tavg",
    "precip": "pcp",
}

def name(state, month, kind):
    fmt = "{ST}-{kind}-1-{month}-{start}-{end}.csv"
    return fmt.format(ST = state, kind = kind, month = month,
            start = START_YEAR, end = END_YEAR)

def url(state, month, kind):
    return "https://www.ncdc.noaa.gov/cag/statewide/time-series/" + name(state, month, kind)

def get_data(state, month, kind):
    n = name(state, month, kind)
    try:
        raw = open("tmp/" + n, "r")
    except:
        u = url(state, month, kind)
        urllib.request.urlretrieve(u, "tmp/" + n)
        try:
            raw = open("tmp/" + n, "r")
        except:
            raise ValueError('http get fail')

    raw.readline()
    raw.readline()
    raw.readline()
    raw.readline()
    raw.readline()

    data = {}
    while True:
        line = raw.readline()
        if not line:
            break
        try:
            arr = line.split(",")
            #.decode('ascii')
            data[int(arr[0][0:4])] = float(arr[1])
        except:
            print(arr)
    #for k, v in data.items():
        #print(k + ": " + str(v))
    return data

os.remove("weather_data.csv")
os.makedirs("tmp", exist_ok=True)
try:
    out = open("weather_data.csv", "a")
except:
    out = open("weather_data.csv", "x")

out.write("Year,Month,State,Temp,Precip\n");

for s in states:
    print("[%s]" % s)
    for m in range(1, 13):
        temp = get_data(states[s], m, "tavg")
        precip = get_data(states[s], m, "pcp")
        for y in range(2000, 2021):
            out.write("{y},{m},{s},{t},{p}\n".format(
                    y = y, m = m, s = s,
                    t = temp[y],
                    p = precip[y],
                ))
out.close()
