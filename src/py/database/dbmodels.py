'''
This module defines the 'model' classes for the database described in db.py.
That is, it defines classes to hold the data retrieved by the database's query
methods.

@author: Cory Banack
'''

from utils import sstr
import re

#==============================================================================
class IssueRef(object):
   '''
   This class contains minimal reference details about a single issue of a 
   comic book in an unspecified series and database.  It instantiates into a 
   lightweight, immutable object, suitable for storing and sorting in large
   numbers in collections.
   '''
   
   #===========================================================================
   def __init__(self, issue_num_s, issue_key):
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
      '''

      if not issue_key or len(sstr(issue_key).strip()) == 0 \
            or issue_num_s is None:
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
   in an unspecified database.  It instantiates into a lightweight, immutable 
   object, suitable for storing and sorting in large numbers in collections.
   '''
   
   #===========================================================================
   def __init__(self, series_key, series_name_s, start_year_n, publisher_s,
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
         
      start_year_n --> the first year that this comic book series was published.
         if the start year is unknown, pass in '-1' here.  this value can
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
      
      # start_year_n can be a string, as per method comment
      try:
         self.__start_year_n = max(-1, int(start_year_n))
      except:
         self.__start_year_n = -1;
      
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
   start_year_n = property( lambda self : self.__start_year_n )
   
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
   def __init__(self, issue_ref):
      ''' 
      Initializes a new Issue object.   The given parameter must be an IssueRef
      object that references the same comic book (in the database) that this
      Issue object will be based on.  Both objects share an issue_key.
      '''
      
      self.issue_key = issue_ref.issue_key
      
      self.issue_num_s = ''
      self.title_s = ''
      self.series_name_s = ''
      self.publisher_s = ''
      self.imprint_s = ''
      self.summary_s = ''
      self.webpage_s = '' 
      
      self.month_n = -1
      self.year_n = -1
      self.start_year_n = -1
      self.rating_n = 0.0
      
      self.alt_series_names = []
      self.characters = []
      self.teams = []
      self.locations = []
      self.writers = []
      self.pencillers = []
      self.inkers = []
      self.cover_artists = []
      self.editors = []
      self.colorists = []
      self.letterers = []
      self.image_urls = []
      

   # the db key (i.e. a memento object) of this Issue. not None. must be unique
   # for this Issue, and should have a useful __str_ method. 
   def __set_issue_key(self, issue_key):
      ''' called when you assign a value to 'self.issue_key' '''   
      if not issue_key or len(sstr(issue_key).strip()) == 0:
         raise Exception("bad value for issue_key")
      else :
         self.__issue_key = issue_key
         self._cmpkey_s = sstr(self.issue_key) # used only for comparisons
   issue_key = property( lambda self : self.__issue_key, __set_issue_key )


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
      
      
   # the publication month for this Issue, as an int. not None. 
   # will always be <= 12 and >= 1, or else -1 for unknown.
   def __set_month_n(self, month_n):
      ''' called when you assign a value to 'self.month_n' '''
      try:
         self.__month_n = int(month_n)
         self.__month_n = self.__month_n if (1 <= self.__month_n <= 12) else -1
      except:
         self.__month_n = -1
   month_n = property( lambda self : self.__month_n, __set_month_n )
   
      
   # the publication year for this Issue, as an int. not None. 
   # will always be >= 0 or else -1 for unknown.
   def __set_year_n(self, year_n):
      ''' called when you assign a value to 'self.year_n' '''
      try:
         self.__year_n = int(year_n)
         self.__year_n = self.__year_n if self.__year_n >= 0 else -1
      except:
         self.__year_n = -1
   year_n = property( lambda self : self.__year_n, __set_year_n )   
   
   
   # the FIRST publication year for this Issue, as an int. not None. 
   # will always be >= 0 or else -1 for unknown.
   def __set_start_year_n(self, start_year_n):
      ''' called when you assign a value to 'self.start_year_n' '''
      try:
         self.__start_year_n = int(start_year_n)
         self.__start_year_n = self.__start_year_n \
            if self.__start_year_n >= 0 else -1
      except:
         self.__start_year_n = -1
   start_year_n = property(lambda self: self.__start_year_n, __set_start_year_n)
   
   
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
   
   
   # the alternate series names for this Issue, as a [] of strings. not None.
   # maybe empty. the strings in the [] will not be None or '', either.
   def __set_alt_series_names(self, alt_series_names):
      ''' called when you assign a value to 'self.alt_series_names' '''
      try:
         self.__alt_series_names = \
            [sstr(x) for x in alt_series_names if x and len(sstr(x).strip())>0]
      except:
         self.__alt_series_names = []
   alt_series_names = property(lambda self: self.__alt_series_names,
      __set_alt_series_names)
   
   
   # the characters in this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_characters(self, characters):
      ''' called when you assign a value to 'self.characters' '''
      try:
         self.__characters =  [ re.sub(r',|;', '', sstr(x))
            for x in characters if x and len(sstr(x).strip())>0 ]
      except:
         self.__characters = []
   characters = property(lambda self: self.__characters, __set_characters)
   
   
   # the teams in this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_teams(self, teams):
      ''' called when you assign a value to 'self.teams' '''
      try:
         self.__teams =  [ re.sub(r',|;', '', sstr(x)) 
            for x in teams if x and len(sstr(x).strip())>0 ]
      except:
         self.__teams = []
   teams = property(lambda self: self.__teams, __set_teams)
   
   
   # the location in this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_locations(self, locations):
      ''' called when you assign a value to 'self.locations' '''
      try:
         self.__locations =  [ re.sub(r',|;', '', sstr(x)) 
            for x in locations if x and len(sstr(x).strip())>0 ]
      except:
         self.__locations = []
   locations = property(lambda self: self.__locations, __set_locations)
   
   
   # the writers for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_writers(self, writers):
      ''' called when you assign a value to 'self.writers' '''
      try:
         self.__writers =  [ re.sub(r',|;', '', sstr(x))
             for x in writers if x and len(sstr(x).strip())>0 ]
      except:
         self.__writers = []
   writers = property(lambda self: self.__writers, __set_writers)
   
   
   # the pencillers for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_pencillers(self, pencillers):
      ''' called when you assign a value to 'self.pencillers' '''
      try:
         self.__pencillers =  [ re.sub(r',|;', '', sstr(x)) 
            for x in pencillers if x and len(sstr(x).strip())>0 ]
      except:
         self.__pencillers = []
   pencillers = property(lambda self: self.__pencillers, __set_pencillers)
   
   
   # the inkers for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_inkers(self, inkers):
      ''' called when you assign a value to 'self.inkers' '''
      try:
         self.__inkers =  [ re.sub(r',|;', '', sstr(x)) 
            for x in inkers if x and len(sstr(x).strip())>0 ]
      except:
         self.__inkers = []
   inkers = property(lambda self: self.__inkers, __set_inkers)
   
   
   # the cover artists for this Issue, as a [] of strings. not None.
   # maybe empty. the strings in the [] will not be None or '', either.
   def __set_cover_artists(self, cover_artists):
      ''' called when you assign a value to 'self.cover_artists' '''
      cover_artists.append("   ")
      cover_artists.append("")
      try:
         self.__cover_artists =  [ re.sub(r',|;', '', sstr(x)) 
            for x in cover_artists if x and len(sstr(x).strip())>0 ]
      except:
         self.__cover_artists = []
   cover_artists = property(lambda self: self.__cover_artists, 
      __set_cover_artists)
   
   
   # the editors for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_editors(self, editors):
      ''' called when you assign a value to 'self.editors' '''
      try:
         self.__editors =  [ re.sub(r',|;', '', sstr(x)) 
            for x in editors if x and len(sstr(x).strip())>0 ]
      except:
         self.__editors = []
   editors = property(lambda self: self.__editors, __set_editors)
   
   
   # the colorists for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_colorists(self, colorists):
      ''' called when you assign a value to 'self.colorists' '''
      try:
         self.__colorists =  [ re.sub(r',|;', '', sstr(x)) 
            for x in colorists if x and len(sstr(x).strip())>0 ]
      except:
         self.__colorists = []
   colorists = property(lambda self: self.__colorists, __set_colorists)
   
   
   # the letterers for this Issue, as a [] of strings. not None. maybe empty.
   # the strings in the [] will not be None or '', either.
   def __set_letterers(self, letterers):
      ''' called when you assign a value to 'self.letterers' '''
      try:
         self.__letterers = [ re.sub(r',|;', '', sstr(x)) 
            for x in letterers if x and len(sstr(x).strip())>0 ]
      except:
         self.__letterers = []
   letterers = property(lambda self: self.__letterers, __set_letterers)
   
   
   # the known cover image urls for this Issue, as a [] of strings. not None. 
   # maybe empty.  the strings in the [] will not be None or '', either.
   def __set_image_urls(self, image_urls):
      ''' called when you assign a value to 'self.image_urls' '''
      try:
         self.__image_urls =\
            [ sstr(x) for x in image_urls if x and len(sstr(x).strip())>0 ]
      except:
         self.__image_urls = []
   image_urls = property(lambda self: self.__image_urls, __set_image_urls)
   
      
         
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
   
