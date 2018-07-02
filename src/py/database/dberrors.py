'''
This module is home to the DatabaseConnectionError class.

@author: Cory Banack
'''

import re
from utils import sstr
   
# =============================================================================
class DatabaseConnectionError(Exception):
   ''' 
   A special Exception that gets thrown anytime there is an error while trying 
   to contact a scraper database.   This is normally because the database is 
   down or unresponsive, the user's network connection is down, or there is 
   something wrong with the user's credentials to access the database.
   '''
   
   # ==========================================================================
   def __init__(self, database_name_s, url_s, underlying, error_code_s="0"):
      ''' 
      database_name_s -> the name of the database that raised this error
      url_s -> the url that caused the problem
      underlying => the underlying io exception object or error string
      error_code => the underlying database error code, or 0 if there isn't one
      '''
      
      super(DatabaseConnectionError,self).__init__(sstr(database_name_s) +
         " database could not be reached\n"\
         "url: " + re.sub(r"api_key=[^&]*", r"api_key=...", url_s) + 
         "\nCAUSE: " + sstr(underlying).replace('\r','') ) # .NET exception
      self.__database_name_s = sstr(database_name_s)
      self.__error_code_s = sstr(error_code_s).strip()
      
   # ==========================================================================   
   def get_db_name_s(self):
      ''' Returns the name of the database that raised this exception. '''
      
      return self.__database_name_s
   
   # ==========================================================================   
   def get_error_code_s(self):
      ''' 
      Returns the underlying database error code associated with this error,
      if there is one.  If there isn't, this value will be "0" 
      '''
      return self.__error_code_s
      