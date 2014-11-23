 
import unittest
from mach.utils import preprocess

example = '/home/pietro/Perceptum/code/mach/mach/utils/twosentences.txt'    
shouldbe = {0:  {
                        0: {'tags': set(), 'word': 'The'},
                        1: {'tags': set(), 'word': 'great'},
                        2: {'tags': set(), 'word': 'gig'},
                        3: {'tags': set(), 'word': 'in'},
                        4: {'tags': set(), 'word': 'the'},
                        5: {'tags': set(), 'word': 'sky.'}
                },
            1:  {
                        0: {'tags': set(), 'word': 'The'},
                        1: {'tags': set(), 'word': 'gods'},
                        2: {'tags': set(), 'word': 'are'},
                        3: {'tags': set(), 'word': 'everywhere.'}
                }
            }

class TestStructure(unittest.TestCase):
    
    def setUp(self):
        self.structure = preprocess.Structure(example)
        
    def test_main_structure(self):
        self.assertEqual( self.structure.content, shouldbe )


if __name__ == '__main__':  
    unittest.main()
