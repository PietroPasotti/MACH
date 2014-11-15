import nltk, BS4

def tokenize(path):
	
	rawtext = ''
	extrainfo = []

	with open(path,'rb') as f:
		
		soup = BS4.soup(f)
		rawtext += soup.get_text()
		
	tokens = [[[] # word
			] # sentence
				] # text
					
	senttokens = nltk.punkt.tokenize(rawtext)
	
	for sent in senttokens:
		tsent = nltk.punkt.tokenize(sent)

		twords = []
				
		for word in tsent:
			twords.append([word,{}]) # empty dictionary; will contain all the information we can gather about the word, including which idioms it belongs to, which nearby words, together with it, make up a compound or multiword expression or name of person, place & co.

		tokens.append(twords) 
	
	# now tokens should consist of a list of sentences, which are lists of words + attached information.
	
	return tokens
