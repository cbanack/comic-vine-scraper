'''
This module contains all of the unit tests for this project, amalgamated into 
a single test suite.

Created on Oct 26, 2011
@author: cbanack
'''
import unittest
from test_fnameparser import TestFnameParser
from test_utils import TestUtils

#==============================================================================
class Test(unittest.TestSuite):
   ''' A testsuite containing all unit tests for this project. '''
   
   def __init__(self):
      testcases = [TestFnameParser, TestUtils ]
      unittest.TestSuite.__init__( self, [ x.suite() for x in testcases ])