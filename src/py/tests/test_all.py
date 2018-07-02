'''
This module contains all of the unit tests for this project, 
amalgamated into a single test suite.

Created on Oct 26, 2011
@author: cbanack
''' 
import unittest
import sys
import test_fnameparser 
import test_bookdata
import test_utils

#==============================================================================
class AllTests(unittest.TestSuite):
   ''' A testsuite containing all unit tests for this project. '''
   
   #---------------------------------------------------------------------------
   def __init__(self):
      loader = unittest.defaultTestLoader
      unittest.TestSuite.__init__( self,
         # add new test cases and test modules here.
         [
         loader.loadTestsFromModule(test_bookdata),
         loader.loadTestsFromModule(test_fnameparser),
         loader.loadTestsFromModule(test_utils), 
         # corylow: can we make a test_cleanupsearchterms?
         ] 
      )
   
   #---------------------------------------------------------------------------
   def run(self, result):
      # overridden to install our logging framework during unit tests!
      # this may sometimes be needed for debugging failed tests.
   #   log.install(None)
      super(AllTests, self).run(result)
   #   log.uninstall()
      

#==============================================================================
def load_tests():
   ''' Makes sure this module's tests are autodiscovered properly. '''
   return AllTests()
 

#==============================================================================
# # make sure we run properly if called from the command line 
#
if __name__ == "__main__":
   runner = unittest.TextTestRunner( stream=sys.stdout, verbosity=0 )
   unittest.main(module='test_all', defaultTest='AllTests', testRunner=runner)
