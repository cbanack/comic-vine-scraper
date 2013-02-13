'''
This module is home to the DatabaseConnectionError class.

@author: Cory Banack
'''

from utils import sstr
   
# =============================================================================
class DatabaseConnectionError(Exception):
   ''' 
   A special Exception that gets thrown anytime there is an network error while
   trying to contact a scraper database.   This is normally because the 
   database is down or unresponsive, or the user's network connection is down.
   '''
   
   # ==========================================================================
   def __init__(self, database_name_s, url_s, underlying):
      ''' 
      database_name_s -> the name of the database that raised this error
      url_s -> the url that caused the problem
      underlying => the underlying io exception object or error string
      '''
      
      super(Exception,self).__init__(sstr(database_name_s) +
         " database could not be reached\n"\
         "url: " + url_s + "\nCAUSE: " + 
         sstr(underlying).replace('\r','') ) # .NET exception
      self.__database_name_s = sstr(database_name_s)
      
   # ==========================================================================   
   def db_name_s(self):
      ''' Returns the name of the database that raised this exception. '''
      
      return self.__database_name_s