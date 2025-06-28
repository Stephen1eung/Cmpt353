# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 03:23:40 2022

@author: steph
"""

import os
import pathlib
import sys
import numpy as np
import pandas as pd
from datetime import datetime as dt
from xml.dom.minidom import getDOMImplementation, parseString

def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation, parse
    xmlns = 'http://www.topografix.com/GPX/1/0'
    
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.10f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.10f' % (pt['lon']))
        time = doc.createElement('time')
        time.appendChild(doc.createTextNode(pt['datetime'].strftime("%Y-%m-%dT%H:%M:%SZ")))
        trkpt.appendChild(time)
        trkseg.appendChild(trkpt)

    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)

    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)

    doc.documentElement.setAttribute('xmlns', xmlns)

    with open(output_filename, 'w') as fh:
        fh.write(doc.toprettyxml(indent='  '))


def get_data(input_gpx):
    # TODO: you may use your code from exercise 3 here.
    gps_doc = parseString(open(input_gpx).read())
    gps_elements = gps_doc.getElementsByTagName('trkpt')
    data = pd.DataFrame(list(map(element_to_data, gps_elements)),
                     columns=['datetime', 'lat', 'lon'])
    data['datetime'] = pd.to_datetime(data['datetime'], utc=True)
    return data

def element_to_data(elem):
    latitude = float(elem.getAttribute('lat'))
    longitude = float(elem.getAttribute('lon'))
    datetime = elem.getElementsByTagName('time')[0].firstChild.nodeValue 
    return datetime, latitude, longitude
    
def main():
    input_directory = pathlib.Path(sys.argv[1])
    output_directory = pathlib.Path(sys.argv[2])
    
    accl = pd.read_json(input_directory / 'accl.ndjson.gz', lines=True, convert_dates=['timestamp'])[['timestamp', 'x']]
    gps = get_data(input_directory / 'gopro.gpx')
    phone = pd.read_csv(input_directory / 'phone.csv.gz')[['time', 'gFx', 'Bx', 'By']]
    # TODO: create "combined" as described in the exercise

    #locate best offset by iterating and finding max dot product
    max_correlation = -1000
    for offset in np.linspace(-5.0, 5.0, 101):
        phone['time'] = phone['time'] + offset
        
        first_time_phone = accl['timestamp'].min()
        phone['timestamp'] = first_time_phone + pd.to_timedelta(phone['time'], unit='sec')
        
        gps['datetime'] = gps['datetime'].round('4s')
        gps_mean = gps.groupby('datetime').mean()
        
        accl['timestamp'] = accl['timestamp'].round('4s')
        accl_mean = accl.groupby('timestamp').mean()    
        
        phone['timestamp'] = phone['timestamp'].round('4s')
        phone_mean = phone.groupby('timestamp').mean()
        
        combined = pd.concat([accl_mean, gps_mean, phone_mean], axis=1)
        combined = combined.dropna()
        
        dot_product = combined['x'] @ combined['gFx']
        
        phone['time'] = phone['time'] - offset
        
        if(max_correlation < dot_product):
            max_correlation = dot_product
            best_offset = offset

    #once best_offset found, use to combine dataset
    phone['time'] = phone['time'] + best_offset
    
    first_time_phone = accl['timestamp'].min()
    phone['timestamp'] = first_time_phone + pd.to_timedelta(phone['time'], unit='sec')
    
    gps['datetime'] = gps['datetime'].round('4s')
    gps_mean = gps.groupby('datetime').mean()
    
    accl['timestamp'] = accl['timestamp'].round('4s')
    accl_mean = accl.groupby('timestamp').mean()    
    
    phone['timestamp'] = phone['timestamp'].round('4s')
    phone_mean = phone.groupby('timestamp').mean()
    
    combined = pd.concat([accl_mean, gps_mean, phone_mean], axis=1)
    combined = combined.dropna().reset_index().rename(columns={"index": "datetime"})
    
    print(f'Best time offset: {best_offset:.1f}')
    os.makedirs(output_directory, exist_ok=True)
    output_gpx(combined[['datetime', 'lat', 'lon']], output_directory / 'walk.gpx')
    combined[['datetime', 'Bx', 'By']].to_csv(output_directory / 'walk.csv', index=False)
        
main()
