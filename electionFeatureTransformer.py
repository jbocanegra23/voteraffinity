import typing
import pandas as pd
import re
from voteraffinity.featureTransform import (numLastElectionsVoted,prevElectionPrecResult, rep_perc)


class featureTransformerBeta:
    def __init__(self, numPrevGenElections: int, numPrevPriElections: int):
        self.numPrevGenElections_ = numPrevGenElections
        self.numPrevPriElections_ = numPrevPriElections
        
    def transform(self, data: pd.DataFrame):
        ## Age at Last Election
        data['AGE_AT_LAST_ELECTION'] = data['LAST_YEAR_VOTED']-data['BIRTH_YR']
        
        ## Female Indicator
        data['Female'] = data['Gender'].apply(lambda x: 1 if x=='F' else 0)
        data = data.loc[:, data.columns != 'Gender']
        
        ## Number of General Elections Voted in at the target year(s)
        print("# of General Elections voted in past 6")
        data = numLastElectionsVoted(df=data,
                                   prevElectNum=self.numPrevGenElections_,
                                   election_type = 'General', 
                                   partisan = None)

        ## Number of Primary Elections Voted in at the target year(s)
        print("# of Republican Primaries voted in past 6")
        data = numLastElectionsVoted(df=data,
                                   prevElectNum=self.numPrevPriElections_,
                                   election_type = 'Primary', 
                                   partisan = 'Republican')

        print("# of Democrat Primaries voted in past 6")
        data = numLastElectionsVoted(df=data,
                                   prevElectNum=self.numPrevPriElections_,
                                   election_type = 'Primary', 
                                   partisan = 'Democrat')

        ## Previous Presidential / MidTerm Election Results
        print("Previous Presidential Result")
        presOutput = prevElectionPrecResult(data=data, election_type='PRESIDENTIAL')

        print("Previous Midterm Result")
        midtOutput = prevElectionPrecResult(data=data, election_type='Midterm')

        ## Merge all data together and 
        print("Merging Final Dataset")
        output_df = data.merge(presOutput, how='left', on='SOS_VOTERID')\
                             .merge(midtOutput, how='left', on='SOS_VOTERID')
        
        print("Complete!")
        
        return output_df

