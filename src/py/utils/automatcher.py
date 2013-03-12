'''
This module contains code that search the database in an attempt to 
automatically find a good match for a given ComicBook object. 

@author: Cory Banack
'''
import clr
from dbmodels import IssueRef, SeriesRef
import db
import dbutils
from matchscore import MatchScore
import log
clr.AddReference('System')

#==============================================================================
def find_series_ref(book, config):
   ''' 
   Performs a number of queries on the database, and attempts to find an 
   IssueRef object that describes the given book.  The user's search and 
   filtering preferences (in 'config') are taken into account.
      
   Returns None if no clear identification could be made. 
   '''
   # coryhigh: START HERE
   issue_num_s = book.issue_num_s
   if issue_num_s:
      pass
   return None;

def __find_best_series(book, config):      
   series_refs = dbutils.filter_series_refs(
         db.query_series_refs(book.series_s),
         config.ignored_publishers_sl, 
         config.ignored_before_year_n,
         config.ignored_after_year_n,
         config.never_ignore_threshold_n)

   series_ref = None   
   if len(series_refs) > 0:
      mscore = MatchScore()
      series_ref = reduce( lambda x,y: 
         x if mscore.compute_n(book, x) >= mscore.compute_n(book,y) else y,
         series_refs)
   return None; 

def __find_best_issue(book, series_ref):
#               if not ref in self.__series_cache:
#               issue_refs = db.query_issue_refs(ref)
#               if issue_refs:
#                  for issue_ref in issue_refs:
#                     if issue_ref.issue_num_s == self.__issue_num_hint_s:
#                        self.__series_cache[ref] = issue_ref
#                        break
#               if not ref in self.__series_cache:
#                  self.__series_cache[ref] = ref      
   return None; 