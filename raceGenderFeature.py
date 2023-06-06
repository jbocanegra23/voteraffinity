import pandas as pd
import py_stringsimjoin as ssj
import py_stringmatching as sm 
import typing

def genderFeature(df: pd.DataFrame, 
                  name_gender: pd.DataFrame,
                  Name_Column: str,
                  threshold: float,
                  fill_NA: str):
    """
    Args:
        df = any dataframe
        
        name_gender = First and Gender Mapping dataset from Census
        
        Name_Column = the column to match on
        
        Threshold = Minimum Threshold for Jaccard Similarity Comparison
        
        fill_NA = the String value for non-matched records
        
        Fixed
    """
    ## Step 1: Get Unique First Names
    unique_first_names = pd.DataFrame(df[Name_Column].unique(), columns = [Name_Column])
    
    ## Step 2: name / gender reference table get the name/gender with highest count
    name_gender['RN'] = name_gender.sort_values(['Name', 'Count'], ascending=[True, False]) \
            .groupby(['Name'])\
            .cumcount()+1
    name_gender = name_gender[name_gender['RN']==1][['Name', 'Gender']]
    
    ## Step 3: Direct Match
    direct_match_results = unique_first_names.merge(name_gender, how='left',
                                                  left_on=Name_Column, 
                                                  right_on='Name')

    unmatched = direct_match_results[direct_match_results['Gender'].isna()][[Name_Column]]
    matched = direct_match_results[~direct_match_results['Gender'].isna()][[Name_Column, 'Gender']]
    
    ## Step 4: Fuzzy Match using bigrams Jaccard Similarity
    
    #### Create a Tokenizer (bigrams)
    qgram = sm.QgramTokenizer(padding=False, qval = 2)
    
    #### Fuzzy Match on Simple Jaccard
    unmatched_fuzzy = ssj.jaccard_join(ltable = unmatched, rtable = name_gender,
                            l_key_attr = Name_Column, r_key_attr = 'Name',
                            l_join_attr = Name_Column, r_join_attr = 'Name',
                            r_out_attrs = ['Gender'],
                            tokenizer = qgram,
                            threshold = threshold,
                            comp_op = '>=')
    
    #### Choose the record with highest Jaccard Score
    newNameColumn = 'l_'+Name_Column
    unmatched_fuzzy['RN'] = unmatched_fuzzy.sort_values([newNameColumn, '_sim_score'], ascending=[True, False]) \
                .groupby(['l_FIRST_NAME'])\
                .cumcount()+1
    unmatched_fuzzy = unmatched_fuzzy[unmatched_fuzzy['RN']==1]
    
    #### Rename Columns
    unmatched_fuzzy = unmatched_fuzzy.rename(columns={newNameColumn: Name_Column, 
                                                 'r_Gender': 'Gender'})
    
    ## Step 5: Concat the two together
    unique_names_gender = pd.concat([matched, unmatched_fuzzy[unmatched_fuzzy['RN']==1][[Name_Column, 'Gender']]])
    
    ## Step 6: Merge back to original DF
    df = df.merge(unique_names_gender, how='left', on=Name_Column)
    
    ## Step 7: Fill Non-Matched with 'U'
    df['Gender'] = df.Gender.fillna(fill_NA)
    
    return df


def raceFeature(df: pd.DataFrame, 
                surname_race: pd.DataFrame,
                Name_Column: str,
                threshold: float,
                fill_NA: int):
    """
    Fixed
    """
    
    uniqueLastName = df[[Name_Column]].drop_duplicates()
    last_name_dmr = uniqueLastName.merge(surname_race, how='left', left_on=Name_Column, right_on='name')
    matched   = last_name_dmr[~last_name_dmr['count'].isna()][[Name_Column, 'pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pcthispanic']]
    unmatched = last_name_dmr[last_name_dmr['count'].isna()][[Name_Column]]

    #### Create a Tokenizer (bigrams)
    qgram = sm.QgramTokenizer(padding=False, qval = 2)

    #### Fuzzy Match on Simple Jaccard
    unmatched_fuzzy = ssj.jaccard_join(ltable = unmatched, rtable = surname_race[~surname_race['name'].isna()],
                            l_key_attr = Name_Column, r_key_attr = 'name',
                            l_join_attr = Name_Column, r_join_attr = 'name',
                            l_out_prefix= '', r_out_prefix='',
                            r_out_attrs = ['pctwhite', 'pctblack', 'pctapi', 'pctaian', 'pcthispanic'],
                            tokenizer = qgram,
                            threshold = threshold,
                            comp_op = '>=')
    unmatched_fuzzy['RN'] = unmatched_fuzzy.sort_values([Name_Column, '_sim_score'], ascending=[True, False]) \
            .groupby([Name_Column])\
            .cumcount()+1
    unmatched_fuzzy = unmatched_fuzzy[unmatched_fuzzy['RN']==1]

    unmatched_fuzzy = unmatched_fuzzy.drop(['_id', '_sim_score', 'RN', 'name'], axis=1)

    race_name_probs = pd.concat([matched, unmatched_fuzzy])

    df = df.merge(race_name_probs, how='left', on=Name_Column)
    
    df['pctwhite']=df['pctwhite'].fillna(fill_NA)
    df['pctblack']=df['pctblack'].fillna(fill_NA)
    df['pctapi']=df['pctapi'].fillna(fill_NA)
    df['pctaian']=df['pctaian'].fillna(fill_NA)
    df['pcthispanic']=df['pcthispanic'].fillna(fill_NA)

    return df