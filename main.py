
import mach.functions as functions
import mach.utils as utils
import mach.pipeline as pipe

pipeline = pipe.pipeline
del pipe

_OUT = {}

def run(path_to_file,kwargs = {},test = 0):
	
	global _OUT
	
	if not isinstance( path_to_file, utils.preprocess.Structure):
		structure = utils.preprocess.Structure(path_to_file) # groundworks.
	else:
		structure = path_to_file
	
	for step in pipeline:
		function = getattr(functions,step) 		# reads off the pipeline
												# the next function to be
												# called.
												
		output = function(structure)		# collects output of a func
		# the function is expected to stably update the structure at once

	_OUT = structure # we store the output in a global
	
	return structure # and return it
			
