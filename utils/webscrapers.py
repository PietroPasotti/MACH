
import requests

filters = {'person': "(all (name:{0} or alias:{0}) type:/people/person)",
            'location': "(all name: {0} type:/location)" }
            
def freebase_matcher(query,parameters = {},entity_type = None):
    """
    Query the freebase database
    """
    
    keyfile = open('/home/pietro/Perceptum/code/mach/mach/freebase_api_key.txt','r')
    api_key = keyfile.read()                # get api key
    keyfile.close()
    
    if entity_type:
        f = filters.get(entity_type)        # if available, fetches a filter preset
        filtered_query = f.format({query})  # we stick in the filter the original query
    else:
        filtered_query = query
    
    url = 'https://www.googleapis.com/freebase/v1/search'
    parameters.update({
            'key' : api_key,
            'query': filtered_query
            })
    
    request = requests.get(url,params = parameters)     # actual request
    
    return request
    
def freebase_dutch_top(query):
    """
    Retrieves the best result (top likelyhood) of a query to the dutch
    freebase ontology.
    """
    
    outcome = freebase_matcher(query,{'lang':'nl'}).json()['result']
    if outcome:
        return outcome [0]
    else:
        return 

def freebase_eng_top(query):
    """
    Retrieves the best result (top likelyhood) of a query to the english
    freebase ontology.
    """
    
    outcome = freebase_matcher(query,{'lang':'en'}).json()['result']
    if outcome:
        return outcome [0]
    else:
        return  

def multiquery_dutch(text):
    """
    Takes a text, calls freebase_dutch_top on each word in it.
    """
    
    out = []
    
    for sentence in text:
        sent = []
        for word in sentence:
            
            outcome = freebase_dutch_top(word)
            
            if outcome:
                sent.append((word, outcome))
            
        out.append(sent)
        
    return out
        
def tag_structure(structure,lang = 'dutch',vb = False):
    """
    The toplevel function of this module. Works with dutch freebase.
    Takes a Structure instance, gets the raw text, tags all it can tag,
    updates the structure, returns.
    """
    
    if lang == 'dutch':
        funct = freebase_dutch_top
    else:
        funct = freebase_eng_top
    
    matches_full = {}
    
    for position, word in structure.walk_entities(enc='utf-8'):
            
            if vb:
                print('Grabbed word {}, at {}...'.format(word,position))
            
            outcome = funct(word)
            
            if not outcome:
                print('  [no result]  ',end = '')
                continue
            
            if vb:
                print('\t'+str(outcome))
                        
            tags = set( ['responsible=freebase', # who got the match
                        'freebase_id={}'.format(outcome.get('id')),
                         'freebase_id={}'.format(outcome.get('mid'))
                         ]) # ID of the entity
            
            matches = { position:tags } # position is mapped to the set of tags we determined.
            matches_full.update(matches)
    if vb:
        print('\n\tMATCHES:   ')
        for match,text in matches_full.items():
            print(match,'\t\t',text)
             
    structure.update(matches_full) # stable update of the structure.
        
    return
    
    
    
    
    
    
    
    
