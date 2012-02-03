'''
This module contains all unittests for the storyarcparser module.

Created on Feb 2, 2012
@author: cbanack
'''

from unittest import TestCase
from unittest.loader import TestLoader
from storyarcparser import extract

#==============================================================================
def load_tests(loader, tests, pattern):
   ''' Returns all of the testcases in this module as a testsuite '''
   return TestLoader().loadTestsFromTestCase(TestStoryArcParser)

#==============================================================================
class TestStoryArcParser(TestCase):

   # --------------------------------------------------------------------------
   def test_simple_titles(self):
      ''' Checks the storyarcparser when used with some simple titles.'''
      self.assertEquals("breaker bob", extract("bob rekaerb"))
