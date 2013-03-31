#coding: utf-8
'''
This module contains all unittests for the utils module.

Created on Jan 5, 2012
@author: cbanack
'''

from unittest import TestCase
from unittest.loader import TestLoader
from utils import natural_compare

#==============================================================================
def load_tests(loader, tests, pattern):
   ''' Returns all of the testcases in this module as a testsuite '''
   return TestLoader().loadTestsFromTestCase(TestUtils)

#==============================================================================
class TestUtils(TestCase):

   # --------------------------------------------------------------------------
   def test_natural_compare(self):
      ''' Checks to see if the BookData's series_s property works. '''
      
      unsorted = ["10", "1", "23", "5", "1.2", "11", "1.01", "55" ]
      expected = ["1", "1.01", "1.2", "5", "10", "11", "23", "55" ]
      self.assertEquals(expected, sorted(unsorted,natural_compare))
      
      unsorted = ["10a", "1b", "2", "1c", "1a", "1" ]
      expected = ["1", "1a", "1b", "1c", "2", "10a" ]
      self.assertEquals(expected, sorted(unsorted,natural_compare))
      
      unsorted = ["a1", "a10", "a1.1", "aa2", "aa2.3" ]
      expected = ["a1", "a1.1", "a10", "aa2", "aa2.3" ]
      self.assertEquals(expected, sorted(unsorted,natural_compare))
      
      unsorted = ["-5", "-6", "-0.1", "-0.2", "-.11", ".3", "0.31" ]
      expected = ["-6", "-5", "-0.2", "-.11", "-0.1", ".3", "0.31" ]
      self.assertEquals(expected, sorted(unsorted,natural_compare))
      
      unsorted = ["⅞","⅝","⅜","⅛","⅚","⅙","⅘","⅗","⅖","⅕","⅔","⅓","¾","½","¼"]
      expected = ["⅛","⅙","⅕","¼","⅓","⅜","⅖","½","⅗","⅝","⅔","¾","⅘","⅚","⅞"]
      self.assertEquals(expected, sorted(unsorted,natural_compare))
      
      unsorted = [".4", "0.6", "½", "6", "5", "5½", "5 ¾", " 5 ¼ "]
      expected = [".4", "½", "0.6", "5", " 5 ¼ ", "5½", "5 ¾", "6"]
      self.assertEquals(expected, sorted(unsorted,natural_compare))
      
      unsorted = ["-.4", "-0.6", "-½", "-6", "-5", "-5½", "-5 ¾", "- 5 ¼ "]
      expected = ["-6", "-5 ¾", "-5½", "- 5 ¼ ", "-5", "-0.6", "-½", "-.4"]
      self.assertEquals(expected, sorted(unsorted,natural_compare))
      
            
