'''
This module contains all unittests for the fnameparser module.

Created on Oct 26, 2011
@author: cbanack
'''
from unittest import TestLoader, TestCase
from fnameparser import extract

#==============================================================================
def suite():
   ''' Returns all of the testcases in this module as a testsuite '''
   return TestLoader().loadTestsFromTestCase(TestFnameParser)


#==============================================================================
class TestFnameParser(TestCase):

   def testParseBasic1(self):
      self.assertEqual(['2000AD', '1740'], 
         extract("2000AD 1740 (29-06-11) (John Williams-DCP)"), "test1" )