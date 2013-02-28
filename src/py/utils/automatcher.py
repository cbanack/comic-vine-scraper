'''
This module contains code that search the database in an attempt to 
automatically find a good match for a given ComicBook object. 

@author: Cory Banack
'''
import clr
from dbmodels import IssueRef
clr.AddReference('System')

#==============================================================================
def find_image_ref(book):
   ''' 
   Performs a number of queries on the database, and attempts to find an 
   IssueRef object that describes the given book.  Returns None if no 
   clear identification could be made. 
   '''
   return None; 
