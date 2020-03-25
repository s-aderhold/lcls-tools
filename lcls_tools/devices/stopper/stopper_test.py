import sys
import unittest
import inspect
import stopper_constants as sc
from stopper import Stopper, get_stoppers

STOPPER = {
    'ctrl': 'SIOC:SYS0:MP01:DISABLE_ctrl',
    'open': 'test Allowed',
    'closed': 'test Disabled',
    'status': 'status'
}

STOPPERS = [
    'AOM',
    'MPS'
]

class StopperTest(unittest.TestCase):

    ####### Constants #######

    def test_stopper2_dict(self):  # These are LCLS2 stopper conventions
        test_stopper = sc.stopper2_dict('test', 'ctrl', 'status')
        self.assertEqual(test_stopper, STOPPER)

    def test_get_stoppers(self):
        self.assertEqual(get_stoppers(), STOPPERS)

    ###### Object ##########

    def test_properties(self):
        s = Stopper()
        self.assertEqual(isinstance(type(s).state, property), True)
        self.assertEqual(isinstance(type(s).states, property), True)
        self.assertEqual(isinstance(type(s).stopper, property), True)

    def test_methods(self):
        s = Stopper()
        self.assertEqual(inspect.ismethod(s.open), True)
        self.assertEqual(inspect.ismethod(p._opened), True)
        self.assertEqual(inspect.ismethod(p.close), True)
        self.assertEqual(inspect.ismethod(p._closed), True)

if __name__ == '__main__':
    unittest.main()
