import requests 
from collections import Counter
import subprocess as _subprocess
import shlex as _shlex
import atexit as _atexit

server_process = None # will store the subprocess.Popen instance that runs the server
clv = None # will store the Clavin class instance to interface with the server

# directory with the clavin.jar executables
_clavin_cd = '/home/pietro/Perceptum/code/mach/mach/clavin/CLAVIN-rest/'
_command = _shlex.split('java -Xmx2048m -jar clavin-rest.jar server clavin-rest.yml')

class Clavin:
    """CLAVIN (Cartographic Location And Vicinity INdexer)
        Copyright (C) 2012-2013 Berico Technologies
        http://clavin.bericotechnologies.com"""

    def __init__(self, server = "http://localhost:9090/api/v0/geotag"):
        
        self.server = server
        
        global clv
        if clv:
            raise BaseException('Clavin instance already running! Use that instead.')
        else:
            clv = self
            
        return
        
    def resolve(self, document):
        headers = {'content-type': 'text/plain'}
        r = requests.post(self.server, data=document, headers=headers)
        try:
            results = r.json()
        except Exception as e:
            global output
            output = r # at least we won't lose it all
            print('Json went astray. Request saved in global "output".')
            raise e
            
        self.dict_format = results
        self.result = Result(results)
        return self.result

    def __unicode__(self):
        return "Python-Clavin at {}".format(self.server)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def whichClavin(self):
        return self.result.version
    
    def matches(self,string):
        """
        Quick check: returns True if there is some resolved entity in string,
        False otherwise.
        """
        
        if self.resolve(string).locations:
            return True
        else:
            return False
    
class Location:
    """A class to store the data fields returned from the server for resolved locations"""

    def __init__(self,record):
        
        for key,value in record.items():
            setattr(self, key, value)
        
        return
        
    def __unicode__(self):
        return u"{}\t{}\tadmin 1 code: {}\tpop: {}\tCLAVIN-id: {}".format(self.name, self.matchedName, self.admin1Code, self.population, self.geonameID)

    def __str__(self):
        return unicode(self).encode('utf-8')

class Result:
    """A class to store the CLAVIN version and list of resolved Location objects"""

    def __init__(self,res):
        try:
            #self.version = res['version'] # no 'version' is specified in the result!!
            self.locations = [Location(record) for record in res['resolvedLocations']]
        except Exception as e:
            print('Dafuq. Storing result in global "result".')
            global result
            result = res
            raise e
            
    def __unicode__(self):
        u_str = "Clavin version {}\n".format(self.version)
        for loc in self.locations:
            u_str+=(unicode(loc)+"\n")
        return u_str

    def __str__(self):
        return unicode(self).encode('utf-8')

    def whichCountries(self):
        countries = [location.countryName for location in self.locations]
        howmany = Counter(countries)
        return howmany  

    def locationsByCountry(self):
        loc_by_country = {}
        for country in set([location.countryName for location in self.locations]):
            loc_by_country[country] = list(set([location.name for location in self.locations if location.matchedName == country])) 
        return loc_by_country

def start_server():
    """
    Sets up the Clavin server, and returns an handle to the popen subprocess.
    """
    
    pipe = _subprocess.PIPE
    print('\nSetting up server... Wait 5 seconds.')
    p = _subprocess.Popen(_command, cwd = _clavin_cd, stdin = pipe,
                            stdout = pipe , stderr = pipe, bufsize = 1)
    
    from time import sleep
    sleep(5) # the server takes some time to start up... we avoid premature requests by waiting here instead.
    
    global server_process
    server_process = p
    return

@_atexit.register # makes sure that the server is cleanly killed at exit
def kill_server():
    """
    Kills the Clavin-rest server.
    """
    global server_process
    
    server_process.kill()
    server_process = None
    
    print('\nKilling Clavin-rest server process...\n')
    return

def ask(text):
    """
    Resolves a piece of text.
    """
    
    global server_process, clv
    
    if not server_process:
        start_server()
    
    if not clv:     
        clv = Clavin()
        
    return clv.resolve(text)    

def get_geotags(text):
    
    result = ask(text)
    
    output = {}
    
    for loc in result.locations:
        pos = loc.location['position'] # where the match starts
        match = loc.location['text']   # matched text
        geoname = loc.geoname['geonameID'] # geoname of the locality
        
        output[match] = (pos,geoname)
        
    return output
        
def tag_structure(structure):
    """
    The toplevel function of this module.
    Takes a Structure instance, gets the raw text, tags all it can tag,
    updates the structure, returns.
    """
    
    geotags = get_geotags(structure.raw())
    
    for name, data in geotags.items():
        
        lenname = len(name)
        match_pos, geo_id = data # unpack the data
    
        positions = structure.locate(name)
        
        tags = set( ['responsible=clavin',
					'type=location', # type of entity
                    'geotag={}'.format(geo_id) ]) # ID of the entity
        
        matches = { pos:tags for pos in positions } # each position is mapped to the set of tags we determined.
        
        structure.update(matches) # stable update of the structure.
        
    return
        
    
    
    







