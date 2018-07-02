'''
This module contains all unittests for the fnameparser module.

Created on Oct 26, 2011
@author: cbanack
'''
import re
from unittest import TestCase, TestSuite
import clr
from fnameparser import extract
import utils

clr.AddReference('System')
from System.IO import File, StreamReader
from System.Text import Encoding

#==============================================================================
def load_tests(loader, tests, pattern): #pylint: disable=W0613
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
                  data = re.findall(r'"(.*?)"', line)
               else:
                  data = re.findall(r"'(.*?)'", line)
               if len(data) == 3:
                  data.append("")
               if len(data) != 4:
                  raise Exception("badly formatted test data");
               retval.append( data ) 
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
      super(TestFnameParser, self).__init__()
      self.__testdata = testdata
            
   # --------------------------------------------------------------------------
   def runTest(self):
      ''' Checks to see if the filename for this test parses correctly. '''
      
      expected_series = self.__testdata[1] 
      expected_issue_num = self.__testdata[2]
      expected_year = self.__testdata[3]
      filename = self.__testdata[0]
      try:
         actual_series, actual_issue_num, actual_year = extract(filename)
      except Exception as e:
         # pylint: disable=W1503
         self.assertFalse(True, "Unexpected error parsing: "
             + filename + "\n" + utils.sstr(e) )
         
      error = 'error parsing filename "' + filename + '"\n   -->' +\
         'got series "' + actual_series + '", issue "' + actual_issue_num +\
         '" and year "' + actual_year + '"'
      self.assertEqual(expected_series, actual_series, error) 
      self.assertEqual(expected_issue_num, actual_issue_num, error) 
      self.assertEqual(expected_year, actual_year, error) 
      
