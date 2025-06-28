# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 22:13:14 2022

@author: steph
"""
import pathlib
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def distance(city, stations):
    #altered from #https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206
    lat1 = city['latitude']
    lat2 = stations['latitude']
    
    lon1 = city['longitude']
    lon2 = stations['longitude']
    
    dlat = np.deg2rad(lat2-lat1)
    dlon = np.deg2rad(lon2-lon1)
    
    a = np.sin(dlat/2.0) * np.sin(dlat/2.0) + np.cos(np.deg2rad(lat1)) * np.cos(np.deg2rad(lat2)) * np.sin(dlon/2.0) * np.sin(dlon/2.0)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    km = 6371 * c
    return km


def best_tmax(city, stations):
    stations['distance'] = distance(city, stations)
    min_distance = np.argmin(stations['distance'])
    
    best_avg_tmax = stations.loc[min_distance].avg_tmax
    return best_avg_tmax


stations_file = pathlib.Path(sys.argv[1])
city_file = pathlib.Path(sys.argv[2])
output_file = pathlib.Path(sys.argv[3])

stations = pd.read_json(stations_file, lines=True)
city = pd.read_csv(city_file)

#station filtration
stations['avg_tmax'] = stations['avg_tmax'] / 10

#city filtration
city = city.dropna()
city['area'] = city['area'] / 1000000 # 1000000m^2 = 1km^2 convert m^2 to km^2
city = city[city.area < 10000]
city['density'] = city['population'] / city['area'] 

city['avg_tmax'] = city.apply(best_tmax, stations = stations, axis = 1)

#plotting
plt.scatter(city['avg_tmax'], city['density'])
plt.title('Temperature vs Population Density')
plt.xlabel('Avg Max Temperature (\u00b0C)')
plt.ylabel('Population Density (people/km\u00b2)')

plt.savefig(output_file) 