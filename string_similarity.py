import numpy as np

def string_to_ngram(ngram: int, string: str):
    """
    ngram = number of characters (for bigram (2), for trigram (3))
    string = long string to split into ngrams
    """
    
    set_1 = []
    
    strings = list(set(string.split(' ')))
    
    strings_split = [x.upper() for x in strings if len(x)>=ngram]
    
    for string in strings_split:
        for i in range(len(string)-1):
            if len(string[i:i+ngram]) >= ngram:
                set_1.append(string[i:i+ngram])
    
    return(set(set_1))

def jaccard(ngram: int, string1: str, string2: str):
    
    if string1 == string2:
        return(1.0)
    
    stringA_ngrams = string_to_ngram(ngram, string1)
    stringB_ngrams = string_to_ngram(ngram, string2)
    
    intersect = len(stringA_ngrams.intersection(stringB_ngrams))
    union     = len(stringA_ngrams.union(stringB_ngrams))
    
    jaccard_score = intersect / union
    
    return(jaccard_score)