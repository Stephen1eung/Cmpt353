#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


totals = pd.read_csv('totals.csv').set_index(keys=['name'])
counts = pd.read_csv('counts.csv').set_index(keys=['name'])


# In[3]:


sumTotalCity = pd.DataFrame.sum(totals, axis=1)
print("City with lowest total precipitation:")
pd.Series.idxmin(sumTotalCity)


# In[4]:


sumTotalMonth = pd.DataFrame.sum(totals, axis=0)
sumCountObserv = pd.DataFrame.sum(counts, axis=0)
averageMonth = sumTotalMonth / sumCountObserv
print("Average precipitation in each month:")
print(averageMonth)


# In[5]:


sumCountMonth = pd.DataFrame.sum(counts, axis=1)
averageCity = sumTotalCity / sumCountMonth
print("Average precipitation in each city:")
print(averageCity)

