import sys
import pandas as pd
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess
from pykalman import KalmanFilter 
import matplotlib.pyplot as plt

file = sys.argv[1]

cpu_data = pd.read_csv(file, sep=',')

plt.figure(figsize=(12, 4))

#Loess method of smoothing
timestamp = cpu_data['timestamp'].apply(np.datetime64)
cpu_data['timestamp'] = pd.to_datetime(cpu_data['timestamp'], format='%Y-%m-%d %H:%M:%S')

loess_smoothed = lowess(cpu_data['temperature'], timestamp,  frac=0.04)

#Kalman method of smoothing

kalman_data = cpu_data[['temperature', 'cpu_percent', 'sys_load_1', 'fan_rpm']]
initial_state = kalman_data.iloc[0]
observation_covariance = np.diag([0.5,0.5,0.5,0.5]) ** 2 #how much do you trust the measurements
transition_covariance = np.diag([0.035, 0.035, 0.035, 0.035]) ** 2 #how far is this prediction from the truth
transition = [[0.96,0.5,0.2,-0.001], [0.1,0.4,2.3,0], [0,0,0.96,0], [0,0,0,1]] # TODO: shouldn't (all) be zero

kf = KalmanFilter(initial_state_mean = initial_state, observation_covariance = observation_covariance,
                  transition_covariance = transition_covariance, transition_matrices = transition)
kalman_smoothed, _ = kf.smooth(kalman_data)

#Plotting
plt.plot(cpu_data['timestamp'], cpu_data['temperature'], 'b.', alpha=0.5)
plt.plot(cpu_data['timestamp'], loess_smoothed[:, 1], 'r-')
plt.plot(cpu_data['timestamp'], kalman_smoothed[:, 0], 'g-')
plt.legend(['Data Points', 'LOESS Smoothed Line', 'KALMAN Smoothed Line'])
plt.title('CPU temperature')
plt.xlabel('Time')
plt.ylabel('Temperature(C)')
plt.savefig('cpu.svg') # for final submission

