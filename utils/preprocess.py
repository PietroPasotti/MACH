import bs4, nltk
from os.path import isfile

punct = """.,;:'"(){}[]\/!?^*#|-_=&%$         \t\n"""
	
def html_filter(path):
	"""
	If path is a path, opens it, cleans html and returns str.
	If path is a str, cleans html and returns str.
	"""
	
	rawtext = ''
	if isfile(path):
		with open(path,'rb') as f:
								
			soup = bs4.BeautifulSoup(f)
			rawtext += soup.get_text()
	else:
		
		soup = bs4.BeautifulSoup(path)
		rawtext += soup.get_text()
	
	# sometimes soupping collapses dots-space structures: from 
	# "... something. Another day...", we get "... something.Another day..."
	# which is bad for tokenizers.
	
	splitted = rawtext.split('.')				# splits at the dots
	dotted = '. '.join(splitted) 				# add back dot ** + space **
	uniform = dotted.replace('  ',' ').strip() 	# clean some extra whitespace
	
	return uniform

def tokenize(path):
	
	rawtext = html_filter(path) # we tear off html straight away
		
	tokens = []
	
	sent_tokenizer = nltk.tokenize.PunktSentenceTokenizer()	
	word_tokenizer = nltk.tokenize.PunktWordTokenizer()
	
	senttokens = sent_tokenizer.tokenize(rawtext)
	
	for sent in senttokens:
		
		twords = word_tokenizer.tokenize(sent)
		# list of words: a sentence
		
		twords = [word for word in twords if word not in punct] # we erase meaningless bits
		
		# manually correct strange dutch construct that trick tokenizers,
		# or other markup constructs that produce weird results:
		
		pos = 0
		for word in twords:
			
			# zo'n --> zo, 'n
			if word == 'zo' and twords[pos+1] == "'n":
				del twords[pos+1]
				twords[pos] = "zo'n"
			
			# vooren --> voor- en	
			elif word[-1] == '-':
				twords[pos] = word[:-1] + twords[pos+1] # we glue back the two words
				del twords[pos+1] # we erase the next one
			
			else:
				pass
			
			pos += 1
		
		tokens.append(twords)
		
	# now tokens should consist of a list of sentences, which are lists of words.
	return tokens

class Structure(object):
	
	def __init__(self,path):
		"""
		Should be initialized on a path to a file; which contains the full
		text to be analysed."""
		
		self.content = self.parse(path)
				
		return None
	
	def parse(self,content):
		
		if not isinstance(content,str):
			raise Exception('path-to-file needed')
		
		tokens = tokenize(content)
		
		struct = {}
		sentpos = 0
		
		for sentence in tokens:
			
			struct_sent = {}
			wordpos = 0
			
			for word in sentence:
				
				struct_word = {'word' : word, 'tags' : set()}
				struct_sent[wordpos] = struct_word
				
				wordpos += 1
			
			struct[sentpos] = struct_sent
			sentpos += 1

		# now a text consisting of two sentences, with 4 words the 
		# first, two the latter, should look like this:
		# 	{0:	
		#		{0:{ 'word':'Today', 'tags': set() } like this...
		#		1:'I',
		#		2:'feel',
		#		3:'good'}
		#	1:	
		#		{0:'Hello',
		#		1:'World'}
		#	}
		
		return struct

	def update_word_tags(self,info):
		"""
		Requires info to be a dictionary from 2-tuples of integers to 
		lists of tags. Each tuple stands for a sentence and a word in
		the sentence; that word's tags get updated by the value.
		"""
		
		for index, tags in info.items():			
			self.content[idnex[0]][index[1]]['tags'].update(tags)

