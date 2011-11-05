'''
This module contains all unittests for the fnameparser module.

Created on Oct 26, 2011
@author: cbanack
'''
from unittest import TestCase, TestSuite
from fnameparser import extract

#==============================================================================
def load_tests(loader, tests, pattern):
   ''' Returns all of the testcases in this module as a testsuite '''
   tests = [ 
      ("2000AD 1740 (29-06-11) (John Williams-DCP)", "2000AD", "1740"), 
      ("2000AD 0001 (29-06-11)", "2000AD", "1"), 
   ]
   return TestSuite( [ TestFnameParser(x) for x in tests ] )


#==============================================================================
class TestFnameParser(TestCase):

   # --------------------------------------------------------------------------
   def __init__(self, testdata):
      ''' 
      Constructs a new testcase, based on the given testdata list:
          [ filname, expected series name, expected issue number string ]
      '''
      #TestCase.__init__(self);
      #super(TestFnameParser, self).__init__()
      super(TestFnameParser, self).__init__()
      self.__testdata = testdata
            
   # --------------------------------------------------------------------------
   def runTest(self):
      ''' Checks to see if the filename for this test parses correctly. '''
      
      expectedSeries = self.__testdata[1]
      expectedIssueNum = self.__testdata[2]
      filename = self.__testdata[0]
      error = 'error parsing filename "' + filename + '"'
      
      self.assertEqual(expectedSeries, extract(filename)[0], error) 
      self.assertEqual(expectedIssueNum, extract(filename)[1], error) 
      
