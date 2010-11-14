'''
Created on May 6, 2010

@author: cbanack
'''

#corylow: comment and cleanup this file

from utils import sstr
class IssueRef: 
   def __init__(self, issue_num_s, issue_key):
      # issue_num_s can be '' or any other string
      # issue key must be something ('not issue_key' == False)
      if not issue_key or issue_num_s is None:
         raise Exception()
      
      self.issue_key = issue_key
      self.issue_num_s = issue_num_s.strip()
      
      # used only for comparisons
      self._cmpkey_s = sstr(self.issue_key)
      
   def __str__(self):
      return "Issue #" + sstr(self.issue_num_s) \
         + " (" + sstr(self.issue_key) + ")"
         
   def __cmp__(self, other):
      if not hasattr(other, "_cmpkey_s"):
         return -1
      
      if self._cmpkey_s < other._cmpkey_s:
         return -1
      else:
         return 1 if self._cmpkey_s > other._cmpkey_s else 0
      
   def __hash__(self):
      return self._cmpkey_s.__hash__() 

      
class SeriesRef:
   def __init__(self, series_key, series_name_s, start_year_s, publisher_s,
         issue_count_s, thumb_url_s):
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
      
   def __str__(self):
      return sstr(self.series_name_s) + " (" + sstr(self.series_key) + ")"
   
   def __cmp__(self, other):
      if not hasattr(other, "_cmpkey_s"):
         return -1
      
      if self._cmpkey_s < other._cmpkey_s:
         return -1
      else:
         return 1 if self._cmpkey_s > other._cmpkey_s else 0
      
   def __hash__(self):
      return self._cmpkey_s.__hash__()
       
   
class Issue(object):
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
   def __str__(self):
      return "Issue #" + sstr(self.issue_num_s) \
         + " (" + sstr(self.issue_key) + ")" 
   
   
# =============================================================================
class DatabaseConnectionError(Exception):
   ''' 
   A special exception that gets thrown anytime there is an network error while
   trying to contact the scraper database.   This is normally because the 
   database is down or unresponsive, or the user's internet connection is down.
   '''
   
   # ==========================================================================
   def __init__(self, database_name_s, url_s, underlying):
      ''' 
      database_name_s -> the name of the database that raised this error
      url_s -> the url that caused the problem
      underlying => the underlying io exception or error
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