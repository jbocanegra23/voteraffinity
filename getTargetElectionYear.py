import pandas as pd
import re

class getTargetElectionYear:
    """
    The purpose of this class is to serve two purposes:
        01. For training a model and testing a model: to get the last year voted give a list of elections years
        02. For model in production: assign the election year to use for further downstream feature engineering
    """
    def __init__(self, data: pd.DataFrame, targetYears: list, electionType: str,
                  training: bool, assignYear: int):
        self.training_ = training
        
        if self.training_:
            self.years_ = targetYears
            self.electionType_ = electionType
            self.data_ = data
            self.assignYear_ = None
            
        else:
            self.years_ = None
            self.electionType_ = None
            self.data_ = data
            self.assignYear_ = assignYear            
            
    def getLastYearVoted(self)->pd.DataFrame:
        
        if self.training_:
            self.data_ = self._getLastYearTraining()
            return self.data_
        
        else:
            
            self.data_['LAST_YEAR_VOTED']=int(self.assignYear_)
            return self.data_

        
    def _getLastYearTraining(self)->pd.DataFrame:        
        
        cols = list(self.data_.columns)  
        electCols = self._getElectCols(cols=cols)
        lastElectionDF = pd.DataFrame()
        df = pd.DataFrame()

        for i in range(len(electCols)):
            df = self.data_[self.data_[electCols[i]]!=0][['SOS_VOTERID', electCols[i]]]
            df['LAST_YEAR_VOTED'] = int(str(electCols[i][-4:]))
            df['LAST_VOTE_DATE'] = int(str(electCols[i][-4:])+str(electCols[i][-10:-8])+str(electCols[i][-7:-5]))
            df.columns = ['SOS_VOTERID', 'LAST_VOTE_DESIGNATION', 'LAST_YEAR_VOTED', 'LAST_VOTE_DATE']
            if len(lastElectionDF) == 0:
                lastElectionDF = df
            else:
                lastElectionDF = pd.concat([lastElectionDF, df])

        lastElectionDF = self._postProcessing(lastElectionData=lastElectionDF)
        data = self.data_.merge(lastElectionDF[['SOS_VOTERID', 'LAST_VOTE_DESIGNATION', 'LAST_YEAR_VOTED']], how='left', on='SOS_VOTERID')

        return data            

    def _getElectCols(self, cols: list)->list:

        electCols = []

        for year in self.years_:
            str_expression = "^"+str(self.electionType_)+".*"+str(year)+"$"
            t = re.compile(str_expression)
            val = list(filter(t.match, cols))
            for v in range(len(val)):
                electCols.append(val[v])

        return electCols
    
    def _postProcessing(self, lastElectionData: pd.DataFrame):
        lastElectionData = lastElectionData.reset_index(drop=True)
        lastElectionData['RN'] = lastElectionData.sort_values('LAST_VOTE_DATE', ascending=False)\
                                        .groupby(['SOS_VOTERID'])\
                                        .cumcount()+1
        lastElectionData = lastElectionData[lastElectionData['RN']==1]
        
        return lastElectionData
    
    