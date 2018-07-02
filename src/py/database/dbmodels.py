'''
This module defines the 'model' classes for the database described in db.py.
That is, it defines classes to hold the data retrieved by the database's query
methods.

@author: Cory Banack
'''

import re
from utils import sstr
import utils

#==============================================================================
class IssueRef(object):
   '''
   This class contains minimal reference details about a single issue of a 
   comic book in an unspecified series and database.  It instantiates into a 
   lightweight, immutable object, suitable for storing and sorting in large
   numbers in collections.
   '''
   
   #===========================================================================
   def __init__(self, issue_num_s, issue_key, title_s, thumb_url_s):
      ''' 
      Initializes a newly created IssueRef, checking the given parameters to
      make sure they are legal, and then storing them as read-only properties.
         
      issue_key --> a database specific object (i.e. the 'memento' design 
         pattern) that can be used by the database at a later date to 
         unambiguously identify this comic book issue. This cannot be None, 
         and it should have a useful __str__ method.  It should also be unique
         for each comic book issue.
      
      issue_num_s --> a string describing this comic's issue number (which may 
         not be a number at all, it can be '' or '1A' or 'A', etc. It cannot
         be None.)
         
      title_s --> a string describing the title of this comic book issue.
         if no title is available, pass in "" here.
         
      thumb_url_s --> the (http) url of an appropriate thumbnail image for this
         comic book issue (usually the cover.)  if no image is available, 
         pass in None here.
      '''

      if not issue_key or len(sstr(issue_key).strip()) == 0 \
            or issue_num_s is None:
         raise Exception()
      
      self.__issue_key = issue_key
      self.__issue_num_s = sstr(issue_num_s).strip()
      self.__title_s = title_s if utils.is_string(title_s) else ""
      
      # make sure thumb_url_s is either valid, or none (but not '').
      self.__thumb_url_s =None if not thumb_url_s else sstr(thumb_url_s).strip()
      if self.__thumb_url_s == '':
         self.__thumb_url_s = None 
      
      # used only for comparisons
      self._cmpkey_s = sstr(self.issue_key)
      
      
   #===========================================================================
   # the 'number' of this IssueRef's issue, as a string. not None. maybe empty.
   issue_num_s = property( lambda self : self.__issue_num_s )
   
   # the db key (i.e. a memento object) of this IssueRef's issue. not None.
   issue_key = property( lambda self : self.__issue_key )
   
   # the title of this IssueRef's issue. not None, may be empty.
   title_s = property( lambda self : self.__title_s )
   
   # the url of this series's thumbnail, as a string. may be None.
   thumb_url_s = property( lambda self : self.__thumb_url_s )
      
      
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
   in an unspecified database.  It instantiates into a lightweight, immutable 
   object, suitable for storing and sorting in large numbers in collections.
   '''
   
   #===========================================================================
   def __init__(self, series_key, series_name_s, volume_year_n, publisher_s,
         issue_count_n, thumb_url_s):
      ''' 
      Initializes a newly created SeriesRef, checking the given parameters to
      make sure they are legal, and then storing them as read-only properties.
      
      series_key --> a database specific object (i.e. the 'memento' design 
         pattern) that can be used by the database at a later date to 
         unambiguously identify this comic book series. This cannot be None, 
         and it should have a useful  __str__ method.  It should also be 
         unique for each series.
           
      series_name_s --> the name of this comic book series.  If this is None 
         (not recommended), the series_key will be converted to a string and 
         used as the name instead.
         
      volume_year_n --> the first year that this comic book series was published.
         if the volume year is unknown, pass in '-1' here.  this value can
         also be a string, if so it will be automatically parsed.
         
      publisher_s --> the name of the publisher/imprint of this comic book
         series.  if the publisher is unknown, pass in '' here.
         
      issue_count_n --> the number of issues in this comic book series.  
         this value can also be a string, if so it will be automatically parsed.
         
      thumb_url_s --> the (http) url of an appropriate thumbnail image for this
         comic book series (usually the cover of the first issue.)  if no image
         is available, pass in None here.
         
      '''

      # series_key != None, and must not convert to and empty/whitespace string.
      if not series_key or len(sstr(series_key).strip()) == 0:
         raise Exception()
      self.__series_key = series_key
      
      # use series_key as the series name if a meaningful one isn't provided
      self.__series_name_s = '' if not series_name_s \
         else series_name_s.strip().replace(r'&amp;', '&')
      if self.__series_name_s == '':
         self.__series_name_s = "Series " + sstr(self.__series_key)
         
      # make sure publisher_s is a string
      self.__publisher_s = '' if not publisher_s else sstr(publisher_s).strip()
      
      # make sure thumb_url_s is either valid, or none (but not '').
      self.__thumb_url_s =None if not thumb_url_s else sstr(thumb_url_s).strip()
      if self.__thumb_url_s == '':
         self.__thumb_url_s = None 
      
      # volume_year_n can be a string, as per method comment
      try:
         self.__volume_year_n = max(-1, int(volume_year_n))
      except:
         self.__volume_year_n = -1;
      
      # issue_count_n can be a string, as per method comment
      try:
         self.__issue_count_n = max(0, int(issue_count_n))
      except:
         self.__issue_count_n = 0;
      
      # used only for comparisons
      self._cmpkey_s = sstr(self.series_key)
   
      
   #===========================================================================
   # the db key (i.e. a memento object) of this series. not None.
   series_key = property( lambda self : self.__series_key )
   
   # the 'name' of this series, as a string. not None.
   series_name_s = property( lambda self : self.__series_name_s )
   
   # the publisher/imprint of this series, as a string. not None, maybe ''.
   publisher_s = property( lambda self : self.__publisher_s )
   
   # the url of this series's thumbnail, as a string. may be None.
   thumb_url_s = property( lambda self : self.__thumb_url_s )
   
   # the first publication year of this series. an int >= -1; -1 means unknown.
   volume_year_n = property( lambda self : self.__volume_year_n )
   
   # the number of issues in this series. an int >= 0.
   issue_count_n = property( lambda self : self.__issue_count_n )

      
   #===========================================================================
   def __str__(self):
      ''' Implements "to string" functionality for standard python objects. '''
      return sstr(self.series_name_s) + " (" + sstr(self.series_key) + ")"
   
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
class Issue(object):
   '''
   This class contains all the data that can be obtained about a single comic 
   book.  A database query will normally create an instance of this object, and 
   then populate its properties with as much data as possible.  All fields start
   out with valid default values.
   
   Properties in this object should always be accessed directly, i.e.:
          self.summary_s = "this is a summary" 
          log.debug(self.webpage_s)
   '''
   
   #===========================================================================
   def __init__(self, ref):
      ''' 
      Initializes a new Issue object.   The given parameter must be an IssueRef
      object that references the same comic book (in the database) that this
      Issue object will be based on.  Both objects share an issue_key.
      '''
      
      # these all call the property setters defined below...
      
      self.issue_key = ref.issue_key
      self.series_key = ''
      
      self.issue_num_s = ''
      self.title_s = ''
      self.series_name_s = ''
      self.publisher_s = ''
      self.imprint_s = ''
      self.summary_s = ''
      self.webpage_s = '' 
      
      self.pub_day_n = -1
      self.pub_month_n = -1
      self.pub_year_n = -1
      self.rel_day_n = -1
      self.rel_month_n = -1
      self.rel_year_n = -1
      
      self.volume_year_n = -1
      self.rating_n = 0.0
      
      self.crossovers_sl = []
      self.characters_sl = []
      self.teams_sl = []
      self.locations_sl = []
      self.writers_sl = []
      self.pencillers_sl = []
      self.inkers_sl = []
      self.cover_artists_sl = []
      self.editors_sl = []
      self.colorists_sl = []
      self.letterers_sl = []
      self.image_urls_sl = []
      

   # the external, unique db key of this Issue, as a string 
   def __set_issue_key(self, issue_key):
      ''' called when you assign a value to 'self.issue_key' '''
      self.__issue_key = '' if not issue_key else sstr(issue_key).strip();
      self._cmpkey_s = self.__issue_key  # used only for comparisons
   issue_key = property( lambda self : self.__issue_key, __set_issue_key )
   
   # the external, unique db key of this Issue's series, as a string 
   def __set_series_key(self, series_key):
      ''' called when you assign a value to 'self.series_key' '''   
      self.__series_key = '' if not series_key else sstr(series_key).strip();
   series_key = property( lambda self : self.__series_key, __set_series_key )

   # the 'number' of this Issue, as a string. not None. maybe '' or non-numeric.
   def __set_issue_num_s(self, issue_num_s):
      ''' called when you assign a value to 'self.issue_num_s' '''   
      self.__issue_num_s = '' if issue_num_s == None else sstr(issue_num_s)
   issue_num_s = property( lambda self : self.__issue_num_s, __set_issue_num_s )   


   # the title of this Issue, as a string. not None. maybe empty.
   def __set_title_s(self, title_s):
      ''' called when you assign a value to 'self.title_s' '''   
      self.__title_s = '' if title_s == None else sstr(title_s)
   title_s = property( lambda self : self.__title_s, __set_title_s )
   
      
   # the series name of this Issue, as a string. not None. maybe empty.
   def __set_series_name_s(self, series_name_s):
      ''' called when you assign a value to 'self.series_name_s' '''   
      self.__series_name_s= '' if series_name_s == None else sstr(series_name_s)
   series_name_s = property( 
      lambda self : self.__series_name_s, __set_series_name_s )

      
   # the publisher for this Issue, as a string. not None. maybe empty.
   def __set_publisher_s(self, publisher_s):
      ''' called when you assign a value to 'self.publisher_s' '''   
      self.__publisher_s = '' if publisher_s == None else sstr(publisher_s)
   publisher_s = property( lambda self : self.__publisher_s, __set_publisher_s )

      
   # the imprint for this Issue, as a string. not None. maybe empty.
   def __set_imprint_s(self, imprint_s):
      ''' called when you assign a value to 'self.imprint_s' '''   
      self.__imprint_s = '' if imprint_s == None else sstr(imprint_s)
   imprint_s = property( lambda self : self.__imprint_s, __set_imprint_s )   

      
   # the summary/description for this Issue, as a string. not None. maybe empty.
   def __set_summary_s(self, summary_s):
      ''' called when you assign a value to 'self.summary_s' '''   
      self.__summary_s = '' if summary_s == None else sstr(summary_s)
   summary_s = property( lambda self : self.__summary_s, __set_summary_s )
   
   
   # the webpage url for this Issue, as a string. not None. maybe empty.
   def __set_webpage_s(self, webpage_s):
      ''' called when you assign a value to 'self.webpage_s' '''   
      self.__webpage_s = '' if webpage_s == None else sstr(webpage_s)
   webpage_s = property( lambda self : self.__webpage_s, __set_webpage_s )
      
      
   # the publication day for this Issue, as an int. not None. 
   # will always be <= 31 and >= 1, or else -1 for unknown.
   def __set_pub_day_n(self, pub_day_n):
      ''' called when you assign a value to 'self.pub_day_n' '''
      try:
         self.__pub_day_n = int(pub_day_n)
         self.__pub_day_n = self.__pub_day_n \
            if (1 <= self.__pub_day_n <= 31) else -1
      except:
         self.__pub_day_n = -1
   pub_day_n = property( lambda self : self.__pub_day_n, __set_pub_day_n )
   
   # the publication month for this Issue, as an int. not None. 
   # will always be <= 12 and >= 1, or else -1 for unknown.
   def __set_pub_month_n(self, pub_month_n):
      ''' called when you assign a value to 'self.pub_month_n' '''
      try:
         self.__pub_month_n = int(pub_month_n)
         self.__pub_month_n = self.__pub_month_n \
            if (1 <= self.__pub_month_n <= 12) else -1
      except:
         self.__pub_month_n = -1
   pub_month_n = property( lambda self : self.__pub_month_n, __set_pub_month_n )
   
      
   # the publication year for this Issue, as an int. not None. 
   # will always be >= 0 or else -1 for unknown.
   def __set_pub_year_n(self, pub_year_n):
      ''' called when you assign a value to 'self.pub_year_n' '''
      try:
         self.__pub_year_n = int(pub_year_n)
         self.__pub_year_n = self.__pub_year_n if self.__pub_year_n >= 0 else -1
      except:
         self.__pub_year_n = -1
   pub_year_n = property( lambda self : self.__pub_year_n, __set_pub_year_n )   
   
   
   # the release (in store) day for this Issue, as an int. not None. 
   # will always be <= 31 and >= 1, or else -1 for unknown.
   def __set_rel_day_n(self, rel_day_n):
      ''' called when you assign a value to 'self.rel_day_n' '''
      try:
         self.__rel_day_n = int(rel_day_n)
         self.__rel_day_n = self.__rel_day_n \
            if (1 <= self.__rel_day_n <= 31) else -1
      except:
         self.__rel_day_n = -1
   rel_day_n = property( lambda self : self.__rel_day_n, __set_rel_day_n )
   
   # the release (in store) month for this Issue, as an int. not None. 
   # will always be <= 12 and >= 1, or else -1 for unknown.
   def __set_rel_month_n(self, rel_month_n):
      ''' called when you assign a value to 'self.rel_month_n' '''
      try:
         self.__rel_month_n = int(rel_month_n)
         self.__rel_month_n = self.__rel_month_n \
            if (1 <= self.__rel_month_n <= 12) else -1
      except:
         self.__rel_month_n = -1
   rel_month_n = property( lambda self : self.__rel_month_n, __set_rel_month_n )
   
      
   # the release (in store) year for this Issue, as an int. not None. 
   # will always be >= 0 or else -1 for unknown.
   def __set_rel_year_n(self, rel_year_n):
      ''' called when you assign a value to 'self.rel_year_n' '''
      try:
         self.__rel_year_n = int(rel_year_n)
         self.__rel_year_n = self.__rel_year_n if self.__rel_year_n >= 0 else -1
      except:
         self.__rel_year_n = -1
   rel_year_n = property( lambda self : self.__rel_year_n, __set_rel_year_n )  
   
   
   # the FIRST publication year for this Issue, as an int. not None. 
   # will always be >= 0 or else -1 for unknown.
   def __set_volume_year_n(self, volume_year_n):
      ''' called when you assign a value to 'self.volume_year_n' '''
      try:
         self.__volume_year_n = int(volume_year_n)
         self.__volume_year_n = self.__volume_year_n \
            if self.__volume_year_n >= 0 else -1
      except:
         self.__volume_year_n = -1
   volume_year_n = property(
      lambda self: self.__volume_year_n, __set_volume_year_n)
   
   
   # the (quality) rating for this Issue, as an float. not None. 
   # will always be >= 0.0 and <= 5.0.
   def __set_rating_n(self, rating_n):
      ''' called when you assign a value to 'self.rating_n' '''
      try:
         self.__rating_n = float(rating_n)
         self.__rating_n = self.__rating_n \
            if (0.0 <= self.__rating_n <= 5.0) else 0.0 
      except:
         self.__rating_n = 0.0
   rating_n = property(lambda self: self.__rating_n, __set_rating_n)
   
   
   # the crossover titles for this Issue, as a [] of strings. not None.
   # maybe empty. the strings in the [] will not be None or '', either.
   def __set_crossovers_sl(self, crossovers_sl):
      ''' called when you assign a value to 'self.crossovers_sl' '''
      try:
         self.__crossovers_sl = \
            [sstr(x) for x in crossovers_sl if x and len(sstr(x).strip())>0]
      except:
         self.__crossovers_sl = []
   crossovers_sl = property(lambda self: self.__crossovers_sl,
      __set_crossovers_sl)
   
   
   # the characters in this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_characters_sl(self, characters_sl):
      ''' called when you assign a value to 'self.characters_sl' '''
      try:
         self.__characters_sl =  [ re.sub(r',|;', '', sstr(x))
            for x in characters_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__characters_sl = []
   characters_sl =\
      property(lambda self: self.__characters_sl, __set_characters_sl)
   
   
   # the teams in this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_teams_sl(self, teams_sl):
      ''' called when you assign a value to 'self.teams_sl' '''
      try:
         self.__teams_sl =  [ re.sub(r',|;', '', sstr(x)) 
            for x in teams_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__teams_sl = []
   teams_sl = property(lambda self: self.__teams_sl, __set_teams_sl)
   
   
   # the locations in this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_locations_sl(self, locations_sl):
      ''' called when you assign a value to 'self.locations_sl' '''
      try:
         self.__locations_sl =  [ re.sub(r',|;', '', sstr(x)) 
            for x in locations_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__locations_sl = []
   locations_sl = property(lambda self: self.__locations_sl, __set_locations_sl)
   
   
   # the writers for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_writers_sl(self, writers_sl):
      ''' called when you assign a value to 'self.writers_sl' '''
      try:
         self.__writers_sl =  [ re.sub(r',|;', '', sstr(x))
             for x in writers_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__writers_sl = []
   writers_sl = property(lambda self: self.__writers_sl, __set_writers_sl)
   
   
   # the pencillers for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_pencillers_sl(self, pencillers_sl):
      ''' called when you assign a value to 'self.pencillers_sl' '''
      try:
         self.__pencillers_sl =  [ re.sub(r',|;', '', sstr(x)) 
            for x in pencillers_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__pencillers_sl = []
   pencillers_sl = \
      property(lambda self: self.__pencillers_sl, __set_pencillers_sl)
   
   
   # the inkers for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_inkers_sl(self, inkers_sl):
      ''' called when you assign a value to 'self.inkers_sl' '''
      try:
         self.__inkers_sl =  [ re.sub(r',|;', '', sstr(x)) 
            for x in inkers_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__inkers_sl = []
   inkers_sl = property(lambda self: self.__inkers_sl, __set_inkers_sl)
   
   
   # the cover artists for this Issue, as a [] of strings. not None.
   # maybe empty. the strings in the [] will not be None or '', either.
   def __set_cover_artists_sl(self, cover_artists_sl):
      ''' called when you assign a value to 'self.cover_artists_sl' '''
      try:
         self.__cover_artists_sl =  [ re.sub(r',|;', '', sstr(x)) 
            for x in cover_artists_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__cover_artists_sl = []
   cover_artists_sl = property(lambda self: self.__cover_artists_sl, 
      __set_cover_artists_sl)
   
   
   # the editors for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_editors_sl(self, editors_sl):
      ''' called when you assign a value to 'self.editors_sl' '''
      try:
         self.__editors_sl =  [ re.sub(r',|;', '', sstr(x)) 
            for x in editors_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__editors_sl = []
   editors_sl = property(lambda self: self.__editors_sl, __set_editors_sl)
   
   
   # the colorists for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_colorists_sl(self, colorists_sl):
      ''' called when you assign a value to 'self.colorists_sl' '''
      try:
         self.__colorists_sl =  [ re.sub(r',|;', '', sstr(x)) 
            for x in colorists_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__colorists_sl = []
   colorists_sl = property(lambda self: self.__colorists_sl, __set_colorists_sl)
   
   
   # the letterers for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_letterers_sl(self, letterers_sl):
      ''' called when you assign a value to 'self.letterers_sl' '''
      try:
         self.__letterers_sl = [ re.sub(r',|;', '', sstr(x)) 
            for x in letterers_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__letterers_sl = []
   letterers_sl = property(lambda self: self.__letterers_sl, __set_letterers_sl)
   
   
   # the known cover image urls for this Issue, as a [] of strings. not None. 
   # maybe empty.  the strings in the [] will not be None or '', either.
   def __set_image_urls_sl(self, image_urls_sl):
      ''' called when you assign a value to 'self.image_urls_sl' '''
      try:
         self.__image_urls_sl =\
            [ sstr(x) for x in image_urls_sl if x and len(sstr(x).strip())>0 ]
      except:
         self.__image_urls_sl = []
   image_urls_sl = \
      property(lambda self: self.__image_urls_sl, __set_image_urls_sl)
   
      
         
   #===========================================================================
   def __str__(self):
      ''' Implements "to string" functionality for standard python objects. '''
      return "Issue Object (" + sstr(self.issue_key) + ")"
   
         
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
   
