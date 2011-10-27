'''
This module contains all unittests for the utils module.

Created on Oct 26, 2011
@author: cbanack
'''
from unittest import TestLoader, TestCase

#==============================================================================
def suite():
   ''' Returns all of the testcases in this module as a testsuite '''
   return TestLoader().loadTestsFromTestCase(TestUtils)


#==============================================================================
class TestUtils(TestCase):
   pass
   