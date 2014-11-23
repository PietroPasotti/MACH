

"""In order to make a more accurate guess about the semantic role of a word,
we may want to start from the syntax."""

import subprocess, shlex

_dupira_cd = '/home/pietro/Perceptum/code/mach/mach/DUPIRA/agfl/' # we have to run the command in the agfl directory, otherwise dupira won't be found
_dupira_prompt_cmd = shlex.split("agfl-run dupira -t -P1")

def dupira_parse(sentence):
	"""
	Asks DUPIRA the parsetree of a sentence, and returns it """
	
	if not isinstance(sentence,bytes):
		sentence = bytes(sentence)
	
	pipe = subprocess.PIPE
	p = subprocess.Popen(_dupira_prompt_cmd , cwd = _dupira_cd, stdin = pipe, stdout = pipe , stderr = pipe, bufsize = 1)
	out = p.communicate(sentence)
	
	if not p.returncode == 0:
		raise Exception('popen did not terminate well; retcode = {}, stderr = "{}"'.format(p.returncode, p.stderr.read()))
	
	return out[0].decode().strip() # decode it to string and remove trailing blanks/newlines.
	
def dupira_parse_batch(sentences):
	
	out = []
	for sentence in sentences:
		out.append(dupira_parse(sentence))
		
	return out
		
		
