

"""In order to make a more accurate guess about the semantic role of a word,
we may want to start from the syntax."""

import subprocess as _subprocess
import shlex as _shlex
import re

_dupira_cd = '/home/pietro/Perceptum/code/mach/mach/DUPIRA/agfl/' # we have to run the command in the agfl directory, otherwise dupira won't be found
_dupira_prompt_cmd = _shlex.split("agfl-run dupira -t -P1")

def nicify(dupira_sent):
	"""
	A dupira_sent looks like "{[N:economie <DET de ] <SUBJ[V:krimpen ]} 
	[[N:Q:0 ] |[N:procent <QUANT 1]]". Ugly. So we transform it into a
	nested block of pretty tuples.
	"""
	
	particles = re.compile("(?P<syntcateg>(?:[A-Z]:)+)(?P<word>\w*)")
	modifiers = re.compile("(?P<modifier>[<][A-Z]+)[ ]?(?P<word>[a-z]+)")
		
		# the first one returns 
		#	[('N:', 'recessie'),
		#	 ('N:', 'economie'),
		#	 ('N:', 'Duitse'),
		#	 ('A:', 'in'),
		#	 ('X:', 'niet'),
		#	 ('X:', 'net'),
		
		# the second one returns
		#	[('<DET', 'de'),
		#	('<PREP', 'met'),
		#	('<PREP', 'voor'),
		#	('<PREP', 'met'),
		#	('<PREP', 'in'),
		
	output = {}
	
	translation = {	'N:': 'noun',
					'V:': 'verb',
					'Q:': 'quantity',
					'A:': 'attribute',
					'X:': 'x_type', # dafuq is X?
					'<DET': 'determiner',
					'<QUANT': 'quantifier',
					'<SUBJ': 'subject',
					'<MOD': 'modifier',
					'<TEMP': 'temporal',
					'<PREP': 'preposition',
					'<AUX': 'auxiliary',
					'<PRED': 'predicate',
					'P:': 'preposition',
					'>OBJ': 'object'}
	
	matches = [[piece for piece in match if piece] for match in particles.findall(dupira_sent)]
	matches += [[piece for piece in match if piece] for match in modifiers.findall(dupira_sent)]
	for categ, content in matches:
		
		if categ in translation:
			categ = translation[categ]
		else:
			categ = 'categ_unknown=' + categ
		
		if content in output and categ not in output[content]:
			output[content] += [categ] 
		else:
			output[content] = [categ]
	
	return output
	
def dupira_parse(sentence):
	"""
	Asks DUPIRA the parsetree of a sentence, and returns it 
	"""
	
	if not isinstance(sentence,bytes):
		sentence = bytes(sentence,encoding = 'utf-8')
	
	pipe = _subprocess.PIPE
	p = _subprocess.Popen(_dupira_prompt_cmd , cwd = _dupira_cd, stdin = pipe,
							stdout = pipe , stderr = pipe, bufsize = 1)
	out = p.communicate(sentence) # simulates me entering the sentence to DUPIRA's interactive prompt
	
	if not p.returncode == 0:
		raise Exception('popen did not terminate well; retcode = {}, stderr = "{}"'.format(p.returncode, p.stderr.read()))
	
	parsed = out[0].decode().strip() # decode it to string and remove trailing blanks/newlines.
	
	return {'raw' : parsed,
			'nice' : nicify(parsed)} # we want it nicer.
	
def dupira_parse_batch(sentences):
	
	out = []
	for sentence in sentences:
		out.append(dupira_parse(sentence))
		
	return out
		
		
