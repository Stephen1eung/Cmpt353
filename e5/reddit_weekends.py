 # -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import datetime as dt
from scipy import stats
import matplotlib.pyplot as plt
import sys

OUTPUT_TEMPLATE = (
    "Initial T-test p-value: {initial_ttest_p:.3g}\n"
    "Original data normality p-values: {initial_weekday_normality_p:.3g} {initial_weekend_normality_p:.3g}\n"
    "Original data equal-variance p-value: {initial_levene_p:.3g}\n"
    "Transformed data normality p-values: {transformed_weekday_normality_p:.3g} {transformed_weekend_normality_p:.3g}\n"
    "Transformed data equal-variance p-value: {transformed_levene_p:.3g}\n"
    "Weekly data normality p-values: {weekly_weekday_normality_p:.3g} {weekly_weekend_normality_p:.3g}\n"
    "Weekly data equal-variance p-value: {weekly_levene_p:.3g}\n"
    "Weekly T-test p-value: {weekly_ttest_p:.3g}\n"
    "Mann-Whitney U-test p-value: {utest_p:.3g}"
)


def main():
    
    counts = pd.read_json(sys.argv[1], lines=True)
    
    #filtering 2012 and 2013 and subreddit r/canada
    #altered from https://stackoverflow.com/questions/22898824/filtering-pandas-dataframes-on-dates
    counts = counts.set_index('date')
    counts = counts.loc['2012-01-01':'2013-12-31']
    counts = counts.loc[counts['subreddit'] == 'canada']
    counts = counts.reset_index()
    
    #Weekend/Weekday filtering
    #altered from https://splunktool.com/find-if-date-is-weekend-or-weekday-in-pandas-dataframe
    weekend = counts[(counts['date'].dt.weekday >= 5)]
    weekday = counts[(counts['date'].dt.weekday < 5)]
    
    #T-test
    weekday_normality_p = stats.normaltest(weekday['comment_count']).pvalue
    weekend_normality_p = stats.normaltest(weekend['comment_count']).pvalue
    ttest_p = stats.ttest_ind(weekend['comment_count'],weekday['comment_count']).pvalue
    levene_p = stats.levene(weekend['comment_count'], weekday['comment_count']).pvalue

    #Histograph of transformed data
    plt.hist(weekday['comment_count'])
    plt.hist(weekend['comment_count'])
    
    #sqrt() comes closest to normal distribution
    #transformed_weekday = np.log(weekday['comment_count'])
    #transformed_weekend = np.log(weekend['comment_count'])
    #transformed_weekday = np.exp(weekday['comment_count'])
    #transformed_weekend = np.exp(weekend['comment_count'])
    transformed_weekday = np.sqrt(weekday['comment_count'])
    transformed_weekend = np.sqrt(weekend['comment_count'])
    #transformed_weekday = weekday['comment_count']**2
    #transformed_weekend = weekend['comment_count']**2
    
    transformed_weekday_normality_p = stats.normaltest(transformed_weekday).pvalue
    transformed_weekend_normality_p = stats.normaltest(transformed_weekend).pvalue
    transformed_levene_p = stats.levene(transformed_weekend,transformed_weekday).pvalue
    
    #U-test
    utest_p = stats.mannwhitneyu(weekend['comment_count'], weekday['comment_count'], alternative='two-sided').pvalue
    
    #Central Limit Theorem
    weekend_iso = weekend['date'].dt.isocalendar()
    weekend_iso = weekend_iso[['year','week']]
    weekday_iso = weekday['date'].dt.isocalendar()
    weekday_iso = weekday_iso[['year','week']]
    
    weekday = pd.concat([weekday,weekday_iso], axis=1)
    weekend = pd.concat([weekend,weekend_iso], axis=1)
    
    weekend = weekend.groupby(by=['year','week']).aggregate('mean').reset_index()
    weekday = weekday.groupby(by=['year','week']).aggregate('mean').reset_index()
    
    weekly_weekday_normality_p = stats.normaltest(weekday['comment_count']).pvalue
    weekly_weekend_normality_p = stats.normaltest(weekend['comment_count']).pvalue
    weekly_ttest_p = stats.ttest_ind(weekend['comment_count'], weekday['comment_count']).pvalue
    weekly_levene_p = stats.levene(weekend['comment_count'], weekday['comment_count']).pvalue  

    print(OUTPUT_TEMPLATE.format(
        initial_ttest_p = ttest_p,
        initial_weekday_normality_p = weekday_normality_p,
        initial_weekend_normality_p = weekend_normality_p,
        initial_levene_p = levene_p,
        transformed_weekday_normality_p = transformed_weekday_normality_p,
        transformed_weekend_normality_p = transformed_weekend_normality_p,
        transformed_levene_p = transformed_levene_p,
        weekly_weekday_normality_p = weekly_weekday_normality_p,
        weekly_weekend_normality_p = weekly_weekend_normality_p,
        weekly_levene_p = weekly_levene_p,
        weekly_ttest_p = weekly_ttest_p,
        utest_p = utest_p,
    ))
    


if __name__ == '__main__':
    main()