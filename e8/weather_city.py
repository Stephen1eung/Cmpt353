# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 20:49:51 2022

@author: steph
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier


def main():
    monthly_label = pd.read_csv(sys.argv[1])
    monthly_unlabel = pd.read_csv(sys.argv[2])
    
    X = monthly_label.loc[:, 'tmax-01':]
    y = monthly_label.loc[:, 'city']
    
    X_unlabel = monthly_unlabel.loc[:,'tmax-01':]
    X_train, X_valid, y_train, y_valid = train_test_split(X, y)
    
    #Gaussian
    #model = make_pipeline(StandardScaler(),GaussianNB())
    
    #K neighbors
    n_neighbors = 25
    model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors))
    
    model.fit(X_train, y_train)

    predictions = model.predict(X_unlabel)
    score = round(model.score(X_valid, y_valid), 3)
    print("score : ", score)

    df = pd.DataFrame({'truth': y_valid, 'prediction': model.predict(X_valid)})

    pd.Series(predictions).to_csv(sys.argv[3], index=False, header=False)

if __name__ == '__main__':
    main()