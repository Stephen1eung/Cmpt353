#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np


# In[2]:


data = np.load('monthdata.npz') #Change Directory
totals = data['totals']
counts = data['counts']


# In[3]:


sumTotalCity = np.sum(totals, axis=1)
print("Row with lowest total precipitation:")
np.argmin(sumTotalCity)


# In[4]:


sumTotalMonth = np.sum(totals, axis=0)
sumCountObserv = np.sum(counts, axis=0)
averageMonth = sumTotalMonth / sumCountObserv
print("Average precipitation in each month:")
print(averageMonth)


# In[5]:


sumCountMonth = np.sum(counts, axis=1)
averageCity = sumTotalCity / sumCountMonth
print("Average precipitation in each city:")
print(averageCity)


# In[6]:


reshape = np.reshape(totals, (4*totals.shape[0],3))
quarterlySum = np.sum(reshape, axis=1)
quarterlyCity = np.reshape(quarterlySum, (totals.shape[0],4))
print("Quarterly precipitation totals: ")
print(quarterlyCity)

