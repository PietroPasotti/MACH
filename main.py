
import mach.functions as functions
import mach.utils as utils
import mach.pipeline as pipe

pipeline = pipe.pipeline
del pipe

_OUT = {}

def run(path_to_file,kwargs = {},test = 0):
	
	global _OUT

	structure = utils.preprocess.tokenize(path_to_file) # groundworks.
	
	for step in pipeline:
		function = getattr(functions,step) 		# reads off the pipeline
												# the next function to be
												# called.
												
		output = function(structure,kwargs)		# collects output of a func
		
		structure = addinfo(structure,output) 	# updates the final output 
												# with the partial output 
												# just collected

	_OUT = structure # we store the output in a global
	
	return structure # and return it
	
def addinfo(out,pout):
	"""out is a list of sentences, which are list of [word,info_dict] 
	lists. addinfo will update the info_dict part."""
	
	merged_out = []
	for sent,psent in out,pout:
		merged_sent = []
		
		for uword,puword in sent,psent:
			word,infodict = uword
			pword,pinfodict = puword
			
			infodict.update(pinfodict)
			merged_sent.append([word,infodict])
			
		merged_out.append(merged_sent)
	
	return merged_out		
			
