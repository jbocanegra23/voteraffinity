import typing
import pandas as pd
import re


def numLastElectionsVoted(df: pd.DataFrame, prevElectNum: int, 
                      election_type: str, partisan: str)->pd.DataFrame:
    """
    !! Updated to Scale !!
    This function takes in a dataframe and calculates the number of past specified election types
    that a voter voted in. It includes off year and even year elections. 

    inputs:
    ================
        df: pd.DataFrame
            Voter table. Needs the Last Year Voted column already.

        prevElectNum: int
            The number of past election to sum up (past 2, past 6 etc)

        election_type: str
            either general or primary

        partisan: str
            specify either Republican or Democrat.
            Assumes that Republican == 2 & Democrat == 3

    """
    if election_type.upper()=='GENERAL':
        pattern = "^GENERAL.*-11/.*$"
    else:
        pattern = "^PRIMARY.*-05/.*$|^PRIMARY.*-03/.*$"

    ## Collect all election history columns
    electionColumns = list(filter(re.compile(pattern).match, list(df.columns)))

    ## Create df_small with only ID, Last Vote Year and Election Columns
    df_small = df[~df['LAST_YEAR_VOTED'].isnull()][['SOS_VOTERID', 'LAST_YEAR_VOTED']+electionColumns]
    years = list(df_small.LAST_YEAR_VOTED.unique())

    if election_type.upper() == 'GENERAL':
        newColumn = 'PAST_'+str(prevElectNum)+'_'+election_type.upper()+'_ELECTIONS'
    else:
        newColumn = 'PAST_'+str(prevElectNum)+'_'+partisan.upper()+'_PRI_ELECTIONS'

    finalDF = pd.DataFrame()

    for year in years:
        # Get the columns
        yearsIncludeMax = int(year-1)
        yearsIncludeMin = int(year-prevElectNum)
        columnsIncl = []

        for j in range(int(yearsIncludeMin),int(yearsIncludeMax)+1,1):
            pattern = ".*"+str(j)+"$"
            column = list(filter(re.compile(pattern).match, list(df_small.columns)))
            for i in range(len(column)):
                columnsIncl.append(column[i])

        df_new = df_small[df_small['LAST_YEAR_VOTED']==year][['SOS_VOTERID']+columnsIncl].set_index('SOS_VOTERID')

        if election_type.upper()=='GENERAL':
            num=1
        elif partisan.upper()== 'REPUBLICAN':
            num=2
        elif partisan.upper()== 'DEMOCRAT':
            num=3

        for col in columnsIncl:
            df_new[col]=df_new[col].apply(lambda x: 1 if x==num else 0)

        df_new[newColumn]=df_new.sum(axis=1)
        finalDF = finalDF.append(df_new[[newColumn]].reset_index())

    df_final = df.merge(finalDF, how='left', on='SOS_VOTERID')

    return df_final


def prevElectionPrecResult(data: pd.DataFrame, election_type: str)->pd.DataFrame:
    """
    Changed.
    This function finds the mid-term and presidential precinct result based on the 
    last year voted. These are hard-coded for ease. Future iterations will need 
    to generalize.

        df: pd.DataFrame

        election_type: Presidential / Midterm

    """
    years = list(data.LAST_YEAR_VOTED.unique())
    df = pd.DataFrame()
    if election_type.upper()=='MIDTERM':
        for electionYear in years:
            if electionYear==2024:
                targetYear=2022
            elif electionYear==2022:
                targetYear=2018
            elif electionYear==2020:
                targetYear=2018
            elif electionYear==2018:
                targetYear=2014
            elif electionYear==2016:
                targetYear=2014

            repColumnPattern = "Republican_"+str(targetYear)
            turColumnPattern = "Turnout_"+str(targetYear)

            repColumn = list(filter(re.compile(repColumnPattern).match, list(data.columns)))[0]
            turColumn = list(filter(re.compile(turColumnPattern).match, list(data.columns)))[0]

            prevTurnCol = 'PREV_MIDT_ELECT_TURNOUT'
            prevRepCol  = 'PREV_MIDT_ELECT_REP_PERC'

            data_small = data[data['LAST_YEAR_VOTED']==electionYear]

            data_small[prevRepCol]=data_small[repColumn]
            data_small[prevTurnCol]=data_small[turColumn]

            df = df.append(data_small[['SOS_VOTERID', prevRepCol, prevTurnCol]])

    elif election_type.upper()=='PRESIDENTIAL':
        for electionYear in years:
            if electionYear==2024:
                targetYear=2020
            elif electionYear==2022:
                targetYear=2020
            elif electionYear==2020:
                targetYear=2016
            elif electionYear==2018:
                targetYear=2016
            elif electionYear==2016:
                targetYear=2012

            repColumnPattern = "Republican_"+str(targetYear)
            turColumnPattern = "Turnout_"+str(targetYear)

            repColumn = list(filter(re.compile(repColumnPattern).match, list(data.columns)))[0]
            turColumn = list(filter(re.compile(turColumnPattern).match, list(data.columns)))[0]

            prevTurnCol = 'PREV_PRES_ELECT_TURNOUT'
            prevRepCol  = 'PREV_PRES_ELECT_REP_PERC'

            data_small = data[data['LAST_YEAR_VOTED']==electionYear]

            data_small[prevRepCol]=data_small[repColumn]
            data_small[prevTurnCol]=data_small[turColumn]

            df = df.append(data_small[['SOS_VOTERID', prevRepCol, prevTurnCol]])

    return df

def rep_perc(df):
    if df['PAST_6_REPUBLICAN_PRI_ELECTIONS']==0 and df['PAST_6_DEMOCRAT_PRI_ELECTIONS']==0:
        return -1
    else:
        return       df['PAST_6_REPUBLICAN_PRI_ELECTIONS']/(df['PAST_6_REPUBLICAN_PRI_ELECTIONS']+df['PAST_6_DEMOCRAT_PRI_ELECTIONS'])


def dem_perc(df):
    if df['PAST_6_REPUBLICAN_PRI_ELECTIONS']==0 and df['PAST_6_DEMOCRAT_PRI_ELECTIONS']==0:
        return -1
    else:
        return df['PAST_6_DEMOCRAT_PRI_ELECTIONS']/(df['PAST_6_REPUBLICAN_PRI_ELECTIONS']+df['PAST_6_DEMOCRAT_PRI_ELECTIONS'])