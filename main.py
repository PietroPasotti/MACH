
import mach.functions as functions
import mach.utils as utils
import mach.pipeline as pipe

pipeline = pipe.pipeline
del pipe

_OUT = {}

def run(path_to_file,kwargs = {},test = 0):
	
	global _OUT

	structure = utils.preprocess.Structure(path_to_file) # groundworks.
	
	for step in pipeline:
		function = getattr(functions,step) 		# reads off the pipeline
												# the next function to be
												# called.
												
		output = function(structure,kwargs)		# collects output of a func
		
		structure.update(output) 				# updates the final output 
												# with the partial output 
												# just collected

	_OUT = structure # we store the output in a global
	
	return structure # and return it
			
