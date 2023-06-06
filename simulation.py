import os
import pandas as pd
from configparser import ConfigParser
import re
import pickle
pd.set_option('display.max_columns', None)
import warnings
import numpy as np
warnings.filterwarnings("ignore")

from sklearn.ensemble import RandomForestClassifier

from voteraffinity.createBaseDataset import createBaseDatasets
from voteraffinity.getTargetElectionYear import getTargetElectionYear
from voteraffinity.electionFeatureTransformer import featureTransformerBeta
from voteraffinity.featureTransform import (rep_perc, dem_perc)
from voteraffinity.utils import modFeats

def simulation(config_file: str,
               all_data: pd.DataFrame): 
    
    config = ConfigParser()
    config.read(config_file)
    
    directory  = config['models']['directory']
    r_affinity = config['models']['r_affinity']
    d_affinity = config['models']['d_affinity']
    year       = config['inputs']['election_year']

    rAffinityMod = pickle.load(open(os.path.join(directory,r_affinity), "rb"))
    dAffinityMod = pickle.load(open(os.path.join(directory,d_affinity), "rb"))
    
    print('Setting Target Election Year')
    prodElectionYears = getTargetElectionYear(data=all_data,targetYears=[], electionType='PRIMARY', training=False, assignYear=year)
    prodData = prodElectionYears.getLastYearVoted()
    prodData = prodData[~prodData['LAST_YEAR_VOTED'].isnull()]
    print(prodData.LAST_YEAR_VOTED.value_counts())
    print(" ")

    print('Starting Feature Transformer')
    feature_transformer = featureTransformerBeta(numPrevGenElections=6,
                                                 numPrevPriElections=6)

    print('Feature Engineering:')
    prodData = feature_transformer.transform(data=prodData)
    prodData['Rep_Vote_Perc'] = prodData.apply(rep_perc, axis=1)
    prodData['Dem_Vote_Perc'] = prodData.apply(dem_perc, axis=1)
    
    modFeats.remove('Target')
    
    print('Running the Republican Affinity Model')
    ## Run the Republican Model
    prodDataModR     = prodData[modFeats+['Rep_Vote_Perc']].set_index('SOS_VOTERID')
    y_pred_probaR    = rAffinityMod.predict_proba(prodDataModR)
    all_data['R Affinity'] = np.array(pd.DataFrame(y_pred_probaR)[[1]])

    print('Running the Democrat Affinity Model')
    ## Run the Democrat Model
    prodDataModD     = prodData[modFeats+['Dem_Vote_Perc']].set_index('SOS_VOTERID')
    y_pred_probaD    = dAffinityMod.predict_proba(prodDataModD)
    all_data['D Affinity'] = np.array(pd.DataFrame(y_pred_probaD)[[1]])

    print('Combining the scores')
    all_data['Affinity Score'] = all_data['R Affinity']-all_data['D Affinity']

    print('Done!')
    return all_data[['SOS_VOTERID', 'R Affinity', 'D Affinity', 'Affinity Score']]