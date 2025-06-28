import sys
import pandas as pd
import matplotlib.pyplot as plt

filename1 = sys.argv[1]
filename2 = sys.argv[2]

   
f1 = pd.read_csv(filename1, sep=' ', header=None, index_col=1,
        names=['lang', 'page', 'views', 'bytes'])

f2 = pd.read_csv(filename2, sep=' ', header=None, index_col=1,
        names=['lang', 'page', 'views', 'bytes'])

# Distribution of Views
f1_sorted = f1.sort_values(by=['views'], ascending=False)

plt.figure(figsize=(10, 5)) # change the size to something sensible

plt.subplot(1, 2, 1) # subplots in 1 row, 2 columns, select the first
plt.title('Popularity Distribution')
plt.xlabel('Rank')
plt.ylabel('Views')
plt.plot(f1_sorted['views'].values) # build plot 1

# Hourly Views
f2['page1'] = f1['views']

plt.subplot(1, 2, 2) # ... and then select the second
plt.title('Hourely Correlation')
plt.xlabel('Hour 1 views')
plt.ylabel('Hour 2 views')
plt.xscale('log')
plt.yscale('log')
plt.plot(f2['page1'], f2['views'], 'b.') # build plot 2

plt.savefig('wikipedia.png')
