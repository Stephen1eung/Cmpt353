import sys
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, chi2_contingency

OUTPUT_TEMPLATE = (
    '"Did more/less users use the search feature?" p-value:  {more_users_p:.3g}\n'
    '"Did users search more/less?" p-value:  {more_searches_p:.3g} \n'
    '"Did more/less instructors use the search feature?" p-value:  {more_instr_p:.3g}\n'
    '"Did instructors search more/less?" p-value:  {more_instr_searches_p:.3g}'
)

def main():
    searchdata_file = sys.argv[1]
    data = pd.read_json(searchdata_file, orient='records', lines=True)
    
    #filter new and old search ui
    old = data[(data['uid']%2 == 0)]
    new = data[(data['uid']%2 == 1)]
    
    #filter new and old search counts
    old_count = old[(old['search_count'] != 0)]
    old_count_zero = old[(old['search_count'] == 0)]
    new_count = new[(new['search_count'] != 0)]
    new_count_zero = new[(new['search_count'] == 0)]
    
    #contigency table 
    contigency = [[old_count.shape[0], old_count_zero.shape[0]], [new_count.shape[0], new_count_zero.shape[0]]]
    chi2, p, dof, ex = chi2_contingency(contigency)
    search_p = mannwhitneyu(old['search_count'], new['search_count']).pvalue
    

    #filter new and old instructors
    old_instructor = old[(old['is_instructor'] == True)]
    new_instructor = new[(new['is_instructor'] == True)]
    
    #filter new and old instructor search counts
    old_instructor_count = old_instructor[(old_instructor['search_count'] != 0)]
    old_instructor_count_zero = old_instructor[(old_instructor['search_count'] == 0)]
    new_instructor_count = new_instructor[(new_instructor['search_count'] != 0)]
    new_instructor_count_zero = new_instructor[(new_instructor['search_count'] == 0)]
    
    #instructor contigency table 
    instructor_contigency = [[old_instructor_count.shape[0], old_instructor_count_zero.shape[0]], [new_instructor_count.shape[0], new_instructor_count_zero.shape[0]]]
    
    chi2, instructor_p, dof, ex = chi2_contingency(instructor_contigency)
    instructor_search_p = mannwhitneyu(old_instructor['search_count'], new_instructor['search_count']).pvalue
    
    # Output
    print(OUTPUT_TEMPLATE.format(
        more_users_p = p,
        more_searches_p = search_p,
        more_instr_p = instructor_p,
        more_instr_searches_p = instructor_search_p,
    ))


if __name__ == '__main__':
    main()