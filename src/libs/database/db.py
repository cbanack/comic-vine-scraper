'''
This module contains is the gateway to the "database" that the script uses to 
obtain information about comic books.   The exact nature of this database is 
intentionally vague; the rest of this script/app can be understood using only 
the contract described by each of the functions in this module.  

The underlying implementation of this class is probably an internet query on 
some remote data source, so it may be quite slow.

Created on May 6, 2010
@author: cbanack
'''
import cvdb
import utils

# a cache for storing the results of series reference searches
# maps 'search terms string' -> 'list of SeriesRefs objects'
__series_ref_cache = {}

# =============================================================================
def query_series_refs(search_terms_s, callback_function=lambda x,y : False):
   '''
   This method takes a some search terms (space separated words) and uses them
   to query the database for comic book series that match those words.   
   
   Each matching series is encoded as a SeriesRef object; this method returns 
   a set of them.  The set may be empty if no series match the search, or
   if the search is cancelled (see below).
   
   You can pass in an optional callback function, which may be called 
   periodically while the search is accumulating results.  This function takes 
   two arguments:
        an integer: how many matches have been found so far
        an integer: how many times the callback is expected to be called
        
   The function must also return a boolean indicating whether or not to cancel
   the search.   If this returned value is true, of course, the query will stop
   immediately and return an empty list of results.
   
   Note that if the backing database implementation (or the search itself) is 
   fast enough, it may choose NOT to call the callback function at all.
   '''
   
   # this method would normally be a simple call to the CVDB method..but we've
   # got a cache here, just to handle the common cases where the same search 
   # gets called repeatedly. 
   global __series_ref_cache
   if search_terms_s in __series_ref_cache:
      return list(__series_ref_cache[search_terms_s])
   else:
      series_refs = cvdb._query_series_refs(search_terms_s, callback_function)
      if len(__series_ref_cache ) > 10:
         __series_ref_cache = {} # keep the cache from ever getting too big
      __series_ref_cache[search_terms_s] = list(series_refs)
      return series_refs



# =============================================================================
def query_issue_refs(series_ref, callback_function=lambda x,y : False):
   '''
   This method takes a SeriesRef object (not None) and uses it to 
   query the database for all comic book issues in that series.   
   
   Each issue is encoded as a IssueRef object; this method returns 
   an set of them.  The set may be empty if the series has no 
   issues, or if the query is cancelled (see below).
   
   You can pass in an optional callback function, which may be called 
   periodically while the IssueRefs are accumulating.  This function takes 
   one float argument: the percentage (between 0.0 and 1.0) of the available
   IssueRefs that have been read in so far.
        
   The function must also return a boolean indicating whether or not to cancel
   the query.   If this returned value is true, of course, the query will stop
   immediately and return an empty set of results.
   
   Note that if the backing database implementation is fast enough, (or the 
   series doesn't have very many issues), the callback function may
   NEVER be called.
   '''
   return cvdb._query_issue_refs(series_ref, callback_function)  


# =============================================================================
def query_issue(issue_ref):
   '''
   This method takes an IssueRef object (not None) and uses it to query the
   database for all of the details about that issue, which are returned 
   in a new Issue object. 
   '''
   return cvdb._query_issue(issue_ref)


# =============================================================================
def query_image(ref):
   '''
   This method takes either an IssueRef object, a SeriesRef object, or a direct
   URL string, and queries the database for a single associated cover image.   
   If no image can be found, if an error occurs, or if the given ref is None, 
   this method will return None.
   
   Note that the returned Image object (if there is one) is a .NET Image object,
   which must be explicitly Disposed() when you are done with it, in order
   to prevent memory leaks.
   '''
   return utils.strip_back_cover( cvdb._query_image(ref) )