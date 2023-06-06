import pandas as pd
import re
import os
import typing

def electionResultsReader(
    years: list, 
    folder_path: str,
    party: str,
    joinCols: list
    )->pd.DataFrame:
    """
    
    """
    electionResults = []
    
    ## Read each Precinct Results dataset
    for year in years:
        folder_path = folder_path
        file_name = str(year)+'_Precinct_Results.xlsx'
        path = os.path.join(folder_path, file_name)
        df = pd.read_excel(path)
        ## Add exceptions
        
        # This should be a function
        r = re.compile("Other")
        columns = list(df.columns)
        otherCols = list(filter(r.match, columns))
        df['OtherAll'] = df[otherCols].sum(axis=1)

        if party == 'Republican':
            other_party = 'Democrat'
        else:
            other_party = 'Republican'
        
        party_perc = party+'_'+str(year)
        turnout_col = 'Turnout_'+str(year)
        
        ## Calculate Party Vote Margin this should be a function
        df[party_perc] = df[party]/(df[party]+df[other_party]+df['OtherAll'])
        df[turnout_col] = df['Total Voters'] / df['Registered Voters']
        df = df[['County Name', 'Precinct Name', 'Precinct Code', turnout_col, party_perc]]
        electionResults.append(df)
     
    allResults = electionResultsJoined(dfs = electionResults, 
                                       joinCols=joinCols)
    
    allResults = electionResultsSelect(allResults, joinCols, party)
    
    return allResults

def electionResultsJoined(dfs: pd.DataFrame,
                          joinCols: list
                          )->pd.DataFrame:
    """
    
    """
    allResults = dfs[0]
    
    num_df = len(dfs)
    i = 1
    
    for i in range(1,num_df):
        j=i-1
        if i < num_df:
            allResults = allResults.merge(dfs[i], 
                                         how='outer', 
                                         on = joinCols,
                                         suffixes = [j, i])
        else:
            allResults

    r = re.compile("Precinct Name")
    columns = list(allResults.columns)
    nameCols = list(filter(r.match, columns))

    allResults['Precinct Name Final'] = allResults[nameCols].bfill(axis=1).iloc[:, 0]
    
    return allResults

def electionResultsSelect(df: pd.DataFrame, joinCols: list, party: str)->pd.DataFrame:
    
    columns = list(df.columns)
    t = re.compile('Turnout')
    turnoutCols = list(filter(t.match, columns))
    p = re.compile(party)
    partyCols = list(filter(p.match, columns))
    select_cols = joinCols+['Precinct Name Final']+turnoutCols+partyCols
    
    final_df = df[select_cols]
    
    return final_df