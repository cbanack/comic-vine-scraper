'''
This module defines the 'model' classes for the database described in db.py.
That is, it defines classes to hold the data retrieved by the database's query
methods.

@author: Cory Banack
'''
# coryhigh: externalize
#corylow: comment and cleanup this file

from utils import sstr

#==============================================================================
class IssueRef(object):
   '''
   This class contains minimal reference details about a single issue of a 
   comic book in an unspecified series and database.  It is a lightweight, 
   immutable object, suitable for storing and sorting in large collections.
   '''
   
   #===========================================================================
   def __init__(self, issue_num_s, issue_key):
      ''' 
      Initializes a newly created IssueRef, checking the given parameters to
      make sure they are legal, and then storing them as read-only properties.
      
      issue_num_s --> a string describing the comics issue number (which may 
         not be a number at all, it can be '' or '1A' or 'A', etc. It cannot
         be None.
         
      issue_key --> a database specific object (i.e. the 'memento' design 
         pattern) that can be used by the database at a later date to 
         unambiguously identify the comic book that this IssueRef represents.
         This cannot be None, and it should have a useful __str__ method. 
      '''

      if issue_key is None or issue_num_s is None:
         raise Exception()
      
      self.__issue_key = issue_key
      self.__issue_num_s = issue_num_s.strip()
      
      # used only for comparisons
      self._cmpkey_s = sstr(self.issue_key)
      
      
   #===========================================================================
   # the 'number' of this IssueRef's issue, as a string. not None. maybe empty.
   issue_num_s = property( lambda self : self.__issue_num_s )
   
   # the db key (i.e. a memento object) of this IssueRef's issue. not None.
   issue_key = property( lambda self : self.__issue_key )
      
      
   #===========================================================================
   def __str__(self):
      ''' Implements "to string" functionality for standard python objects. '''
      return "Issue #" + sstr(self.issue_num_s) \
         + " (" + sstr(self.issue_key) + ")"
         
         
   #===========================================================================
   def __cmp__(self, other):
      ''' Implements comparisons for standard python objects. '''
      if not hasattr(other, "_cmpkey_s"):
         return -1
      
      if self._cmpkey_s < other._cmpkey_s:
         return -1
      else:
         return 1 if self._cmpkey_s > other._cmpkey_s else 0
      
      
   #===========================================================================
   def __hash__(self):
      ''' Implements the hash function for standard python objects. '''
      return self._cmpkey_s.__hash__() 





      
#==============================================================================
class SeriesRef(object):
   '''
   This class contains minimal reference details about a series of comic books 
   in an unspecified database.  It is a lightweight, immutable object, 
   suitable for storing and sorting in large collections.
   '''
   
   #===========================================================================
   def __init__(self, series_key, series_name_s, start_year_s, publisher_s,
         issue_count_s, thumb_url_s):
      ''' coryhigh: START HERE '''
      # series name will become series key if empty
      # series key must be something ('not issue_key' == False)
      # start_year can be '', or digits
      # publisher can be '' 
      # issue_count_n will be an integer
      # thumb_url_s can be None, or a thumbnail url address
      if not series_key:
         raise Exception()
      self.series_key = series_key
      self.series_name_s = ("Series " + sstr(series_key)) if not series_name_s\
         else series_name_s.strip().replace(r'&amp;', '&')
      self.start_year_s = '' if not start_year_s or not start_year_s.isdigit() \
         else start_year_s.strip()
      self.publisher_s = '' if not publisher_s else publisher_s.strip()
      self.issue_count_n=0 if not issue_count_s or not issue_count_s.isdigit() \
         else int(issue_count_s)
      self.thumb_url_s = None if not thumb_url_s else thumb_url_s.strip()
      
      # used only for comparisons
      self._cmpkey_s = sstr(self.series_key)
      
   #===========================================================================
   def __str__(self):
      return sstr(self.series_name_s) + " (" + sstr(self.series_key) + ")"
   
   #===========================================================================
   def __cmp__(self, other):
      if not hasattr(other, "_cmpkey_s"):
         return -1
      
      if self._cmpkey_s < other._cmpkey_s:
         return -1
      else:
         return 1 if self._cmpkey_s > other._cmpkey_s else 0
      
   #===========================================================================
   def __hash__(self):
      return self._cmpkey_s.__hash__()



       
   
#==============================================================================
class Issue(object):
   
   #===========================================================================
   def __init__(self):
      self.issue_key = ''
      self.issue_num_s = ''
      self.title_s = ''
      self.series_name_s = ''
      self.publisher_s = ''
      self.imprint_s = ''
      self.alt_series_name_s = ''
      self.summary_s = ''
      self.month_s = ''
      self.year_s = ''
      self.start_year_s = ''
      self.characters_s = ''
      self.teams_s = ''
      self.locations_s = ''
      self.writer_s = ''
      self.penciller_s = ''
      self.inker_s = ''
      self.cover_artist_s = ''
      self.editor_s = ''
      self.colorist_s = '' 
      self.letterer_s = ''
      self.webpage_s = '' 
      self.rating_n = 0 # MUST be a float
      self.image_urls = []
      
      # coryhigh: improve classes here?
      # (i.e. explicitly subclassing "object")
#   def get_title_s(self):
#      return self.__title_s
#   
#   def set_title_s(self, value):
#      self.__title_s = "bob";
#      
#   def del_title_s(self):
#      del self.__title_s
#      
#   title_s = property(get_title_s, set_title_s, del_title_s, "bah")
#
      
   #===========================================================================
   def __str__(self):
      return "Issue #" + sstr(self.issue_num_s) \
         + " (" + sstr(self.issue_key) + ")"
         
   # coryhigh: hash? __cmp__? 
   
