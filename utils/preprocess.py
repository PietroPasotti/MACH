import bs4 as _bs 
import nltk as _nltk
from os.path import isfile as _isfile

punct = """.,;:'"(){}[]\/!?^*#|-_=&%$         \t\n"""
	
def html_filter(path):
	"""
	If path is a path, opens it, cleans html and returns str.
	If path is a str, cleans html and returns str.
	"""
	
	rawtext = ''
	if _isfile(path):
		with open(path,'rb') as f:
								
			soup = _bs.BeautifulSoup(f)
			rawtext += soup.get_text()
	else:
		
		soup = _bs.BeautifulSoup(path)
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
	
	sent_tokenizer = _nltk.tokenize.PunktSentenceTokenizer() 
	word_tokenizer = _nltk.tokenize.PunktWordTokenizer()
	
	senttokens = sent_tokenizer.tokenize(rawtext)
	
	for sent in senttokens:
		
		twords = word_tokenizer.tokenize(sent) # list of words: a sentence
		
		twords = [word.strip(punct) for word in twords if word not in punct] 
		# we erase meaningless bits
		
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
		
		noempty = [word for word in twords if word]
		
		tokens.append(noempty)
		
	# now tokens should consist of a list of sentences, which are lists of words.
	return tokens

class Structure(object):
	
	def __init__(self,path):
		"""
		Should be initialized on a path to a file; which contains the full
		text to be analysed."""
		
		self.content = self.parse(path)
		self.trees = self.parse_trees()		
		return None
	
	def __str__(self):
		
		raw = self.raw()
		return "<Structure({}), at {}>".format(raw[:10] + '...',id(self))
	
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
		#		...
		#	}
		
		return struct
		
	def parse_trees(self):
		"""
		Dupira api.
		"""
		
		raw = self.raw()
		raw_list = [ sent + '.' for sent in raw.split('.') if sent ]
		
		from mach.utils.treeparse import dupira_parse
		
		parsed = { raw_list.index(sent) : dupira_parse(sent) for sent in raw_list }
		
		return parsed
		
	def update(self,info):
		"""
		Requires info to be a dictionary from 2-tuples of integers to 
		sets of tags. Each tuple stands for a sentence and a word in
		the sentence; that word's tags get updated by the value.
		"""
		
		for index, tags in info.items():			
			self.content[index[0]][index[1]]['tags'].update(tags)

	def raw(self):
		"""
		Returns the raw, untagged text.
		"""
		
		fulltext = ''
		
		for sent in self.content.values():
			for word in sent.values():
				if fulltext:
					fulltext += " "
				fulltext += word['word'] # each word is a {'tags': set(), 'word' : str()} object 
			fulltext += '.'
				
		return fulltext.strip()
		
	def raw_textform(self):
		"""
		Returns a hierarchical structure [[[word,word,word] [word...] []]
		"""
		
		t = []
		
		for sent in self.content.values():
			s = []
			for word in sent.values():
				s += [word['word']]
			t += [s]
		
		return t
		
	def locate(self,string):
		"""
		Returns (sent,word1 [,word2*]) where string was found in the structure. 
		"""
		
		words = [word.strip() for word in string.split(' ')]
		firstword = words[0]
		
		def getfirst():
			nonlocal self
			for sentID,sent in self.content.items():
				for wordID,word in sent.items():
					
					if word['word'] == firstword:
						return (sentID,wordID) # coordinates for sentence, word pair.

		firstmatch = getfirst()
		if firstmatch is None:
			raise BaseException('No matches found for "{}".'.format(firstword))
			
		howmany = len(words)
		matches = [firstmatch] + [(firstmatch[0], firstmatch[1] + n) for n in range(1,len(words),1)]
		# this should make sure that, if the match is 4 words long, say United States of America,
		# then if 2,5 is where 'United' was found, then match should be (2,5),(2,6),(2,7),(2,8).
		# 2 stands for the sentence where the match was found, 5 for the word. ASSUMPTION: that no match
		# occurs across two sentences! Could shoot outofrange errors if this goes badly...
		
		return matches
		
		
		
		
