import os
import pandas as pd
from configparser import ConfigParser
from voteraffinity.raceGenderFeature import (genderFeature, raceFeature)
from voteraffinity.electionResultsReader import electionResultsReader
from voteraffinity.voterFileWrangling import electionHistoryEncoding
from voteraffinity.voterFileWrangling import populationShare
from voteraffinity.utils import census_cols
import numpy as np
from sklearn.impute import KNNImputer

def createBaseDatasets(config_file='config.ini', 
                     party='Republican', 
                     election_years = [2012, 2014, 2016, 2018, 2020, 2022],
                     threshold=0.5)->pd.DataFrame:
    """
    This inputs a config file and outputs a ready for analysis dataset with all
    of the relevant data and features.
    
    config_file = 'config.ini'
    party = 'Republican'
    election_years = [2012, 2014, 2016, 2018, 2020]
    threshold = 0.5
    """
    print("Initializing")
    ## Initiate ConfigParser
    config = ConfigParser()
    config.read(config_file)

    ## Parse out fields and where everything is
    data_folder  = config['data']['directory']
    voter_file   = config['data']['voter_file']
    employment   = config['data']['employment']
    demographics = config['data']['demographics']
    race         = config['data']['race']
    zipArea      = config['data']['zipArea']
    LKP_CO_NM_NO = config['data']['LKP_CO_NM_NO']
    surnameRace  = config['data']['surnameRace']
    name_gender  = config['data']['name_gender']
    zipClusters  = config['data']['zipClusters']
    
    ## Load datasets
    print("Loading & Importing Datasets")
    voters       = pd.read_csv(os.path.join(data_folder, voter_file))
    name_gender  = pd.read_csv(os.path.join(data_folder, name_gender))
    surname_race = pd.read_csv(os.path.join(data_folder, surnameRace))
    employment   = pd.read_csv(os.path.join(data_folder, employment))
    demographics = pd.read_csv(os.path.join(data_folder, demographics))
    racial_data  = pd.read_csv(os.path.join(data_folder, race))
    zipcd_sqmi   = pd.read_csv(os.path.join(data_folder, zipArea))
    lkp_co_nm_no = pd.read_csv(os.path.join(data_folder, LKP_CO_NM_NO))
    zipClusters  = pd.read_csv(os.path.join(data_folder, zipClusters))

    ## Load Previous Election Results
    electionResults = electionResultsReader(years = election_years,
                                            folder_path = data_folder,
                                            party = party,
                                            joinCols = ['County Name', 'Precinct Code'])

    ## Create M/F Gender Column
    print("Calculating Gender & Race")
    print("Gender Matching Progress:")
    name_gender['Name'] = name_gender['Name'].str.upper()
    voters_gender = genderFeature(df = voters,
                                  name_gender = name_gender,
                                  Name_Column = 'FIRST_NAME',
                                  threshold = threshold,
                                  fill_NA = 'U')

    ## Create the Race Probabilities based on Last Name Similarity
    print("Race Matching Progress:")
    voters_race = raceFeature(df=voters, 
                              surname_race=surname_race, 
                              Name_Column = 'LAST_NAME', 
                              threshold=threshold, 
                              fill_NA = 0)

    ## Join all of the census data together
    print("Merging Census datasets, cleaning and Imputing Missing Values")
    census_data = racial_data.merge(employment, how='left', left_on='ZIP Code', right_on = 'Zip Code')\
                             .merge(demographics, how='left', left_on='ZIP Code', right_on='Zip Code')\
                             .merge(zipcd_sqmi, how='left', left_on='ZIP Code', right_on='ZIP Code')\
                             .drop(['Zip Code_y', 'Zip Code_x'], axis=1)

    census_data['Land Area (Sq. Miles)'] = census_data['Land Area (Sq. Miles)'].replace(to_replace=0, value=0.5)

    nan = np.nan
    imputer = KNNImputer(n_neighbors=5, weights="uniform")
    census_data_imp = imputer.fit_transform(census_data)
    census_data = pd.DataFrame(data=census_data_imp, 
                              columns = census_data.columns)

    ## Format the voter file for matching
    print("Merging all datasets together")
    voters = voters.merge(lkp_co_nm_no, how='left', left_on = 'COUNTY_NUMBER', right_on = 'COUNTY_NO')
    voters['PRECINCT_CODE_2'] = voters_race['PRECINCT_CODE'].str.replace(r'[0-9]', '', regex=True)

    all_data = voters.merge(voters_gender[['SOS_VOTERID', 'Gender']], 
                                 how = 'left', 
                                 on = 'SOS_VOTERID') \
        .merge(voters_race[['SOS_VOTERID', 'pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pcthispanic']],
                                how = 'left',
                                on = 'SOS_VOTERID') \
        .merge(census_data, 
                                how = 'left',
                                left_on = 'RESIDENTIAL_ZIP',
                                right_on = 'ZIP Code') \
        .merge(electionResults, 
                                how = 'left',
                                left_on = ['PRECINCT_CODE_2', 'COUNTY_NAME'],
                                right_on = ['Precinct Code', 'County Name']) \
        .merge(zipClusters, 
                                how='left', 
                                left_on='RESIDENTIAL_ZIP', 
                                right_on='ZIP Code')

    ## Encode election history from 
    print("Final Data Wrangling and Cleaning")
    all_data = electionHistoryEncoding(all_data, mapping=[0,1,2,3], default=4)

    ## Standardize Population Share for the 
    all_data = populationShare(column_lists = census_cols,
                               data = all_data, 
                               DenominatorColumn = 'Total Population')
    
    ## More imputation for missing precinct result values (due to new/old precincts)
    ## Method: Impute the median for each zip code
    columns_to_impute = list(electionResults.columns)
    columns_to_impute.remove('County Name')
    columns_to_impute.remove('Precinct Code')
    columns_to_impute.remove('Precinct Name Final')

    for col in columns_to_impute:
        all_data[col]=all_data.groupby('RESIDENTIAL_ZIP')[col].transform(lambda x: x.fillna(x.median()))
    
    ## Generate a couple additional columns of data
    all_data['BIRTH_YR'] = all_data['DATE_OF_BIRTH'].apply(lambda x: int(x[0:4]))
    all_data['POP_DENSITY'] = all_data['Total Population']/all_data['Land Area (Sq. Miles)']
    print("Done!")
    return all_data
    
    
    
