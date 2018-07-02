'''
This module contains is the gateway to whatever database(s) this script uses to 
obtain information about comic books.   The exact nature of the database is 
intentionally vague in order for the implementation of this module to stay
modular and completely encapsulated, thus making it easy to interchange/add 
alternate databases.  One way to think of it is that the the behaviour of the
"comic book database" that this module exposes should be understandable entirely  
in terms of the contract described by the public functions in this module.  

While no guarantees about the underlying database implementation are made, you 
should probably expect that the implementation accesses data from a remote 
source, and therefore may be quite slow and occassionally unreliable.

@author: Cory Banack
'''

import re
import cvdb
import utils


# a limited-size cache for storing the results of SeriesRef searches
# maps 'search terms string' -> 'list of SeriesRefs objects'
__series_ref_cache = None

# this cache is used to speed up query_issue_refs.
__issue_refs_cache = None


# =============================================================================
def initialize(**kwargs):
   ''' 
   Initializes this database connection.  Call this method once when the 
   application/script starts up (before using this module for anything else)
   and remember to call "shutdown()" at application shutdown.
   
   Some database implementations may have additional keyword arugments.
   '''
   
   global __series_ref_cache, __issue_refs_cache
   __series_ref_cache = {}
   __issue_refs_cache = {}
   cvdb._initialize(**kwargs)
   
# =============================================================================
def shutdown():
   '''
   Undoes the "initialize()" method, clearing up any permanent resources that 
   this module might be holding onto.  Be sure to call this method before 
   shutting down the application, and don't use this module after shutting down!
   '''
   global __series_ref_cache, __issue_refs_cache
   __series_ref_cache = None
   __issue_refs_cache = None
   cvdb._shutdown()

# =============================================================================
def get_db_name_s():
   ''' 
   Returns the name (a unique string) describing the current backing database 
   implementation.  i.e. "ComicVine" or "AnimeVice", etc.  Will not be empty.
   
   This method does not perform any database reads or writes, i.e. it's fast.
   '''
   return cvdb._get_db_name_s();


# =============================================================================
def create_key_tag_s(issue_key):
   '''
   Creates a "key tag" out of the given issue_key object.  
   
   This method returns the key tag (a string) or None if key tags are not 
   supported by the underlying database implementation.  
   
   This method does not perform any database reads or writes, i.e. it's fast.
   '''
   return cvdb._create_key_tag_s(issue_key) if issue_key else None;


# =============================================================================
def parse_key_tag(text_s):
   '''
   Atempts to parse the given key tag string into the original issue_key object 
   that was passed into create_key_tag.
   
   This function will return the found issue_key, or None if the given string 
   contains no key tag or if the underlying database implementation does not 
   support key tags.  
   
   This method does not perform any database reads or writes, i.e. it's fast.
   '''
   return cvdb._parse_key_tag(text_s) if text_s else None

# =============================================================================
def check_magic_file(path_s):
   ''' 
   Looks at the given directory so see if it contains a 'magic' file that tells
   us what the SeriesRef for this directory is.  The name and format of this 
   magic file are known only to specific db implementations.
   
   If the magic file exists and is formatted correctly, this function converts 
   it into a SeriesRef object and returns it.  Otherwise, it returns None.
   
   The given path_s can be the full path to a directory, or to any file within
   the directory (whether that file exists or not.)
   
   This fuction may need to access the db in order to create a SeriesRef object.
   '''
   return cvdb._check_magic_file(path_s)

# =============================================================================
def query_series_refs( search_terms_s, ignored_search_terms_sl = list(), 
                       callback_function=lambda x,y : False ):
   '''
   This method takes a some search terms (space separated words as a single
   string) and uses them to query the database for comic book series objects 
   that match those words.   
   
   Each matching series is encoded as a SeriesRef object; this method returns 
   a set of them.  The set may be empty if no series matches the search, or
   if the search is cancelled (see below).
   
   You can pass in an optional list of 'ignored' search terms which will be
   removed from the originally provided search terms if present. 
   
   You can also pass in an optional callback function, which MAY be called 
   periodically while the search is accumulating results.  This function takes 
   two arguments:
        an integer: how many matches have been found so far
        an integer: how many times the callback is expected to be called
        
   The function must also return a boolean indicating whether or not to CANCEL
   the search.   If this returned value is ever true, this query will
   stop immediately and return an empty set of results.
   '''
   
   # strip 'ignored' search terms (if any) out of the search terms string
   ig_terms = ignored_search_terms_sl
   if ig_terms: 
      ig_terms = '|'.join([x.strip() for x in ig_terms if x and x.isalnum()])
   if ig_terms: 
      search_terms_s=re.sub(r'(?i)\b(' +ig_terms+ r')\b', '', search_terms_s)
   
   
   # use caching here for when this method gets called repeatedly with the same
   # search term, which happens often if the user is jumping back and forth 
   # between the series and issues dialogs, for example.
   global __series_ref_cache
   if __series_ref_cache == None: 
      raise Exception(__name__ + " module isn't initialized!")
   
   if search_terms_s in __series_ref_cache:
      return list(__series_ref_cache[search_terms_s])
   else:
      series_refs = cvdb._query_series_refs(search_terms_s, callback_function)
      if len(__series_ref_cache ) > 10:
         __series_ref_cache = {} # keep the cache from ever getting too big
      __series_ref_cache[search_terms_s] = list(series_refs)
      return series_refs


# =============================================================================
def query_issue_refs(series_ref, callback_function=lambda x : False):
   '''
   This method takes a SeriesRef object (not None) and uses it to 
   query the database for all comic book issues in that series.   
   
   Each issue is encoded as a IssueRef object; this method returns 
   a set of them.  The set may be empty if the series has no 
   issues, or if the query is cancelled (see below).
   
   You can pass in an optional callback function, which MAY be called 
   periodically while the IssueRefs are accumulating.  This function takes 
   one float argument: the percentage (between 0.0 and 1.0) of the available
   IssueRefs that have been read in so far.
        
   The function must also return a boolean indicating whether or not to cancel
   the query.   If this returned value is true, the query should stop
   immediately and return an empty set of results.
   '''
   
   # use caching here for when this method is called serveral times in a row
   # for the same series ref.  this happens all the time if the user is 
   # scraping a bunch of comics from the same series all at once.
   global __issue_refs_cache
   if __issue_refs_cache == None:
      raise Exception(__name__ + " module isn't initialized!")
   
   issue_refs = set()
   if series_ref in __issue_refs_cache:
      issue_refs = set(__issue_refs_cache[series_ref]) 
   else: 
      __issue_refs_cache = {} # only keep one element in cache (else too big!)
      issue_refs = cvdb._query_issue_refs(series_ref, callback_function)
      __issue_refs_cache[series_ref] = set(issue_refs) 
   return issue_refs


# =============================================================================
def query_issue_ref(series_ref, issue_num_s):
   '''
   This method takes a SeriesRef object (not None) and an issue number string
   representing an issue in that series.  It converts these two objects into
   a new IssueRef object if possible, or it returns None if it is not possible
   (if, for example, the issue number string doesn't match any issue.)
   '''
   return cvdb.query_issue_ref(series_ref, issue_num_s)
   

# =============================================================================
def query_issue(issue_ref, slow_data=False):
   '''
   This method takes an IssueRef object (not None) and uses it to query the
   database for all of the details about that issue, which are returned 
   in a new Issue object.
   
   If slow_data is True, the query MAY take extra time to attempt to retrieve 
   additional OPTIONAL data and add it to the Issue. 
   
   '''
   return cvdb._query_issue(issue_ref, slow_data)


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
   