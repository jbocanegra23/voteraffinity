
census_cols = ['Management, business, science, and arts occupations',	
            'Service occupations',
            'Sales and office occupations',	
            'Natural resources, construction, and maintenance occupations',	
            'Production, transportation, and material moving occupations',
            'Agriculture, forestry, fishing and hunting, and mining',
            'Construction',
            'Manufacturing',	
            'Wholesale trade',
            'Retail trade',
            'Transportation and warehousing, and utilities',
            'Information',
            'Finance and insurance, and real estate and rental and leasing',
            'Professional, scientific, and management, and administrative and waste management services',	
            'Educational services, and health care and social assistance',	
            'Arts, entertainment, and recreation, and accommodation and food services',	
            'Other services, except public administration',	
            'Public administration',
            'Married', 'Divorced Seperated',
            'Less Than $50k','Between $50k-$75k','Over $75k',
            'In labor force','In Poverty','Bachelors Degree',
            'Lives in Owner Occupied','Native-Born',
            'Self-employed in own not incorporated business workers']

## Model Features for testing
modFeats = ['SOS_VOTERID', 'Target',
            
            ## Election Features
            'PREV_PRES_ELECT_TURNOUT', 'PREV_PRES_ELECT_REP_PERC', 'PREV_MIDT_ELECT_TURNOUT', 'PREV_MIDT_ELECT_REP_PERC',
            'PAST_6_GENERAL_ELECTIONS', 'PAST_6_REPUBLICAN_PRI_ELECTIONS', 'PAST_6_DEMOCRAT_PRI_ELECTIONS',
            'AGE_AT_LAST_ELECTION',
            
            ## Demographics / zip code compilations
            'Female', 'pctwhite', 'pctblack', 'pcthispanic'#, 'cluster'
           ]
