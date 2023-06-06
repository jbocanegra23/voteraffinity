import typing
import pandas as pd
import numpy as np
import re
from progressbar import ProgressBar 

def electionHistoryEncoding(df: pd.DataFrame, mapping: list, default: int)->pd.DataFrame:
    """
    mapping
        mapping[0] = Did not vote
        mapping[1] = Voted / Voted Non-Partisan
        mapping[2] = Republican
        mapping[3] = Democrat 
    """
    electionHistoryCols = list(filter(re.compile("^GENERAL|^SPECIAL|^PRIMARY").match, list(df.columns)))
        
    for column in electionHistoryCols:
        df[column] = df[column].fillna(0)
        conditions = [df[column]==0, df[column]=='X', df[column]=='R', df[column]=='D']
        df[column] = np.select(conditions, mapping, default=default)
        
    return df

def populationShare(column_lists: list,
                    data: pd.DataFrame,
                    DenominatorColumn: str)->pd.DataFrame:

    df = data    
    for i in range(len(column_lists)):
        ## Get share
        column_name = column_lists[i]+" Perc"
        df[column_name] = df[column_lists[i]]/df[DenominatorColumn]
        
        ## If share is greater than 100% than cap at 100%
        df[column_name] = df[column_name].apply(lambda x: 1 if x>1 else x)
        
    return df