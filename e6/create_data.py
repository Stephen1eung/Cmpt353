import time
import pandas as pd
import numpy as np
from implementations import all_implementations

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 12:24:45 2022

@author: steph
"""
#dataframe with each sort method
data = pd.DataFrame(columns=['qs1', 'qs2', 'qs3', 'qs4', 'qs5', 'merge1', 'partition_sort'], index = np.arange(50))

start_time = time.time()

#random array from -10000 to 10000
for x in range(50):
    random_array = np.random.randint(-10000, 10000, size = 10000)
    for sort in all_implementations:
        st = time.time()
        res = sort(random_array)
        en = time.time()
        data.iloc[x][sort.__name__] = en - st

        
data.to_csv('data.csv', index=False)

#testing for speed
#print(data)
#print("%s seconds" % (time.time() - start_time))