
"""the pipeline determines the order of execution of the various analysis 
functions, and also determines which functions get called. All of them 
receive the same input, and their outputs are merged along the way."""

pipeline = [
	'clavin_geoparse',
	'freebase_query'#,
	#'multiword_term_finder' 
	]
