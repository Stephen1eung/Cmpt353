import sys
import pandas as pd
import numpy as np
from xml.dom.minidom import parseString
from pykalman import KalmanFilter 

def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.7f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.7f' % (pt['lon']))
        trkseg.appendChild(trkpt)
    
    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)
    
    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)
    
    with open(output_filename, 'w') as fh:
        doc.writexml(fh, indent=' ')

def get_data(filename):
    input_gpx = open(filename).read()
    gpx = parseString(input_gpx)
    trkpt = gpx.getElementsByTagName("trkpt")
    lat = []
    lon = []
    for data in trkpt:
        lat.append(float(data.getAttribute('lat')))
        lon.append(float(data.getAttribute('lon')))

    elements = gpx.getElementsByTagName('time')
    points = pd.DataFrame(list(map(element_to_data, elements)), columns=['datetime'])
    points['lat'] = lat
    points['lon'] = lon
    points['datetime'] = pd.to_datetime(points['datetime'], utc=True)
    return points

def element_to_data(element):
    time = element.childNodes[0].data
    return time

def distance(points):
    #https://www.geeksforgeeks.org/python-iterating-with-python-lambda/
    data = points.copy()
    data['shifted_lat'] = data['lat'].shift(periods = 1)
    data['shifted_lon'] = data['lon'].shift(periods = 1)
    data['distance'] = data.apply(lambda x: haversine(x['lat'], x['lon'], x['shifted_lat'], x['shifted_lon']), axis = 1)
    return data['distance'].sum()

def haversine(lat1, lon1, lat2, lon2):
    #https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206
    dlat = np.deg2rad(lat2-lat1)
    dlon = np.deg2rad(lon2-lon1)
    a = np.sin(dlat/2.0) * np.sin(dlat/2.0) + np.cos(np.deg2rad(lat1)) * np.cos(np.deg2rad(lat2)) * np.sin(dlon/2.0) * np.sin(dlon/2.0)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    km = 6371 * c
    meters = km * 1000
    return meters

def smooth(points):
    initial_state_mean = points.iloc[0]
    observation_covariance = np.diag([0.5, 0.5, 0, 0]) ** 2 #how much do you trust the measurements
    transition_covariance = np.diag([0.35, 0.35, 0, 0]) ** 2 #how far is this prediction from the truth
    transition = [[1,0,(6*(10**-7)),(29*(10**-7))], [0,1,(-43*(10**-7)),(12*(10**-7))], [0,0,1,0], [0,0,0,1]] # TODO: shouldn't (all) be zero
    kf = KalmanFilter(initial_state_mean = initial_state_mean, observation_covariance = observation_covariance,
                      transition_covariance = transition_covariance, transition_matrices = transition)
    kalman_smoothed, _ = kf.smooth(points)
    data = pd.DataFrame(kalman_smoothed)
    data = data.rename(columns={0: "lat", 1: "lon"})
    return data
    
def main():
    points = get_data(sys.argv[1])
    input_csv = sys.argv[2]
    
    points = points.set_index('datetime')
    sensor_data = pd.read_csv(input_csv, parse_dates=['datetime']).set_index('datetime')
    points['Bx'] = sensor_data['Bx']
    points['By'] = sensor_data['By']

    print(points)
    dist = distance(points)
    print(f'Unfiltered distance: {dist:.2f}')

    smoothed_points = smooth(points)
    smoothed_dist = distance(smoothed_points)
    print(f'Filtered distance: {smoothed_dist:.2f}')

    output_gpx(smoothed_points, 'out.gpx')

if __name__ == '__main__':
    main()
