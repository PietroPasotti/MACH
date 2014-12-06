import bs4 as _bs 
import nltk as _nltk
from os.path import isfile as _isfile

_default_toresolve = set(['noun','attribute'])

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
	
	punct = """.,;:'"(){}[]\/!?^*#|-_=&%$         \t\n"""
	
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

def entity(string,struct):
	"""
	Outputs a likelihood ratio (float) that the given string represents
	an entity.
	"""
	
	# 1. NOUNS and "attributes" seem to often be entities. _default_toresolve 
	# 	stores such categories
	
	pos = struct.locate(string)[0]
	nice = struct.trees[pos[0]]['nice']
	
	try:
		categs = nice[string] if string in nice else nice[string.lower()]
	except Exception:
		# some words are just skipped by the parsing engine.
		# so we might not find them at all. Ignore them!
		return 0
	
	value1 = len(set(struct._toresolve).intersection(set(categs)))/ len(_default_toresolve)
	
	# 2. capitalized words, unless they are at the very start of a sentence,
	# are often entities
	
	value2 = 1 if string[0].isupper() and pos[0] != 0 else 0
		
	# 3. boh.
	
	values = (value1, value2)
	final =  sum(values) / len(values)
	return final

def entities(structure):
	"""calls entity on every word in the structure"""
	
	for sent,words in structure.content.items():
		for wordid,wordict in words.items():
			wordict['entity'] = entity(wordict['word'],structure)
	return
	
class Structure(object):
	
	def __init__(self,path):
		"""
		Should be initialized on a path to a file; which contains the full
		text to be analysed."""
		
		global _default_toresolve
		
		self._toresolve = _default_toresolve	# holds whatever we deem useful resolving
		self.content = self.parse(path)			# raw-ish content
		self.trees = self.parse_trees() 		# trees! we like trees!
		entities(self) 							# tries to guess which words denote entities
		return 
	
	def __str__(self):
		
		raw = self.raw()
		return "<Structure('{}'), {} sentences>".format(raw[:15] + '...',len(self.raw_sentences()))
	
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
	
	def raw_sentences(self):
		"""
		Returns the raw, untagged text.
		"""
		
		return [sent + '.' for sent in self.raw().split('.') if sent]
		
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
		Returns [(sent,word),[...]] where string was found in the structure.
		All parts of the string are expected to be found in sequence. 
		"""
		
		words = [word.strip() for word in string.split(' ')]
		first = words[0]
	
		matches = []
	
		sents = [sent.lower().strip('.') for sent in self.raw_sentences()] # .lower!
		matches_sents = [sents.index(sent) for sent in sents if string.lower() in sent] # .lower!
			#	this should return the indexes of the sentences where
			# 	**the full string** was matched.
		
		for idx in matches_sents:
			sent = [word.strip().lower() for word in sents[idx].split(' ')]
			for word in words:
				word = word.lower() # warning: lowercase match!
				if word in sent: 
					matches.append((idx, sent.index(word))) # (index of sentence, index of word)
			
		if not matches:
			# nothing found yet: we have a problem.
			# we could search for individual words, instead of matching 
			# the whole string at the beginning. But that's boring. 
			# Better raise an error.
			
			raise ValueError('String {} not found.'.format(string))
	
		return matches
	
	def to_resolve(self,lst = []):
		"""
		used to determine what to resolve. For example if we know some word
		is a determiner ('that', 'it') or some uninteresting neighbour,
		we probably won't like to waste precious time and resources trying
		to resolve it. 
		"""
		
		if lst:
			self._toresolve.extend(lst)
			
		return self._toresolve
		
		
		
		
			
		
		
