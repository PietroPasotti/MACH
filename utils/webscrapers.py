
import requests

filters = {'person': "(all (name:{0} or alias:{0}) type:/people/person)",
			'location': "(all name: {0} type:/location)" }
			
def freebase_matcher(query,parameters = {},entity_type = None):
	
	keyfile = open('/home/pietro/Perceptum/code/mach/mach/freebase_api_key.txt','r')
	api_key = keyfile.read()
	keyfile.close()
	
	if entity_type in filters:
		f = filters.get(entity_type)
		filtered_query = f.format({query}) # we stick in the filter the original query
	else:
		filtered_query = query
	
	url = 'https://www.googleapis.com/freebase/v1/search'
	parameters.update({
			'key' : api_key,
			'query': filtered_query
			})
	
	request = requests.get(url,params = parameters)
	
	return request
	
def get_dutch_best_result(query):
	
	return freebase_matcher(query,{'lang':'nl'}).json()['result'][0]
