

"""A couple of functions to get what we want from what we have."""

from bs4 import BeautifulSoup
from os.path import isfile, join
from os import listdir

def clean(path):
	"""
	Takes a path to a FILE and returns a tuple (title,body) after cleaning 
	HTML tags.
	"""
	
	text = ''
	with open(path,'rb') as f:
		text += BeautifulSoup(path.read()).get_text()
		
	lines = text.split('\n')
	title = lines[0]
	body = ' '.join(lines[1:])
	
	return (title,body)
	
def clean_batch(mypath):
	"""
	Takes a path to a FOLDER full of .txt files, returns a dictionary
	{id: clean(file.txt)}. Tries to fetch ids from the -8:-4 characters
	of the txt file name.
	"""
	
	files = [ mypath + f for f in listdir(mypath) 
								if isfile(join(mypath,f)) 
									and f[-3:] == 'txt' ]
									
	batch = {}
	
	for art in files:
		content = clean(art)
		batch[content[0]] = content[1]
		
	return batch
	
	
	
