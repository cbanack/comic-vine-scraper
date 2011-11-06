'''
This module contains all unittests for the fnameparser module.

Created on Oct 26, 2011
@author: cbanack
'''
import clr
import re
from unittest import TestCase, TestSuite
from fnameparser import extract

clr.AddReference('System')
from System.IO import File, StreamReader
from System.Text import Encoding

#==============================================================================
def load_tests(loader, tests, pattern):
   ''' Returns all of the testcases in this module as a testsuite '''
   file = __file__[:-(len(__name__) + len('.py'))] + r"\test_fnameparser.data"
   return TestSuite( [ TestFnameParser(x) for x in __load_testdata(file) ] )

#==============================================================================
def __load_testdata(file):
   """
   Reads the testdata out of a file.  Testdata consists of exactly three 
   strings on each line, each one enclosed in quotation marks (" or ').  
   The first is the filename to be parsed, the second is the series name
   that should be parsed out of it, and the third is the issue number string
   that should be parsed out of it.
   
   Blank lines and lines that begin with # are ignored.
   """
   retval = []
   if File.Exists(file): 
      with StreamReader(file, Encoding.UTF8, False) as sr:
         line = sr.ReadLine()
         while line is not None:
            line = line.strip()
            if len(line) > 0 and not line.startswith("#"):
               if line.startswith('"'):
                  data = re.findall(r'".*?"', line)
               else:
                  data = re.findall(r"'.*?'", line)
               if len(data) != 3:
                  raise Exception("badly formatted test data");
               retval.append( [x.strip('"\'') for x in data] ) 
            line = sr.ReadLine()
   return retval
     
      
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
      
