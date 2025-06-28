import time
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 15:43:45 2022

@author: steph
"""

data = pd.read_csv("data.csv")

qs1 = data['qs1']
qs2 = data['qs2']
qs3 = data['qs3']
qs4 = data['qs4']
qs5 = data['qs5']
merge1 = data['merge1']
partition_sort = data['partition_sort']

print("Sort:             Mean:") 
print(data.describe().loc['mean'].sort_values())

#ANOVA test
anova = stats.f_oneway(qs1, qs2, qs3, qs4, qs5, merge1, partition_sort)
print("ANOVA pvalue = ", anova.pvalue, '\n')

#Post Hoc Analysis
x_melt = pd.melt(data)
posthoc = pairwise_tukeyhsd(x_melt['value'], x_melt['variable'], alpha=0.05)
print(posthoc)
fig = posthoc.plot_simultaneous()