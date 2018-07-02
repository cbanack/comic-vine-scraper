'''
This module contains the Book class, which is an "abstract class" that defines
the data attributes and read/write functionality that any kind of comic book 
must have.  Various subclasses will implement the specific details.

@author: Cory Banack
'''
from utils import sstr

#==============================================================================
class BookData(object):
   '''
   This abstract class defines the attributes and behaviours for all kinds of
   persistable book objects. 
   '''
   
   #===========================================================================   
   def __init__(self):
      self.__series_s = ""
      self.__issue_num_s = ""
      self.__volume_year_n = -1 # -1 is a blank value
      self.__published_s = ""
      self.__released_s = ""
      self.__pub_year_n =  -1 # -1 is a blank value
      self.__pub_month_n = -1 # -1 is a blank value
      self.__pub_day_n = -1 # -1 is a blank value
      self.__rel_year_n =  -1 # -1 is a blank value
      self.__rel_month_n = -1 # -1 is a blank value
      self.__rel_day_n = -1 # -1 is a blank value
      self.__format_s = ""
      self.__title_s =""
      self.__crossovers_sl = [] 
      self.__summary_s = ""
      self.__publisher_s = ""
      self.__imprint_s = ""
      self.__characters_sl = []
      self.__teams_sl = []
      self.__locations_sl = []
      self.__writers_sl = []
      self.__pencillers_sl = []
      self.__inkers_sl = []
      self.__colorists_sl = []
      self.__letterers_sl = []
      self.__cover_artists_sl = []
      self.__editors_sl = []
      self.__tags_sl = [] 
      self.__notes_s = ""
      self.__path_s = ""
      self.__webpage_s = ""
      self.__cover_url_s = ""
      self.__rating_n = 0.0 # 0.0 to 5.0
      self.__page_count_n = 0
      self.__issue_key_s = ""
      self.__series_key_s = ""
      
      self.__updated_properties = BookData.all_properties()
      self.dont_update("page_count_n")
      self.dont_update("path_s")
      
      
   #===========================================================================
   def update(self):
      '''
      This method (which is meant to be implemented by subclasses) will write
      some of the properties in this BookData object back out to whatever source
      they were originally read in from, thus updating the original source of
      this book (and likely doing file or network IO.)
      
      The updated_properties() method defines which properties of this class 
      should be written out by implementing subclasses; ALL other properties
      should be ignored.
      '''  
      pass

      

   #===========================================================================   
   def updated_properties(self):
      ''' 
      Returns a set containing all of the properties ("series_s", etc) that will
      be updated when this BookData is "updated".   By default, it contains
      everything except read-only attributes like path_s and page_count_n.
      ''' 
      return set(self.__updated_properties) 
   
   
   #===========================================================================   
   def dont_update(self, property):
      '''
      Use this member to REMOVE the given property from the set of properties
      that are updated when this BookData is "updated".
      '''
      if property in self.__updated_properties:
         self.__updated_properties.remove(property)
      elif not property in BookData.__dict__:
         raise Exception("unrecognized property: " + property)
   
   
   #==========================================================================
   def create_image_of_page(self, page_index):
      ''' 
      Retrieves an COPY of a single page (a .NET "Image" object) for this 
      BookData.  Returns None if the requested page could not be obtained.
      
      page_index --> the index of the page to retrieve; a value on the range
                  [0, n-1], where n is self.page_count_n.
      '''
      del page_index # unused
      return None
     
      
   #===========================================================================   
   @classmethod
   def all_properties(cls):
      '''
      Returns a new list containing string names for ALL the properties in
      any instance of this class (regardless of whether they will be saved out
      when this BookData is "updated".) 
      '''
      return [ x for x in cls.__dict__ if 
         x[0] != '_' and isinstance(cls.__dict__[x], property) ]
      
   
   #===========================================================================   
   @classmethod
   def blank(cls, property):
      '''
      Returns the blank value for the given property in this bookdata.  This 
      value should be interpreted as "I don't know" or "undefined".  All new 
      BookData objects start with these properties by default, so volume_year_n
      is blank("volume_year_n"), series_s is blank("series_s"), etc.
      
      Values return by this method will never be None.
      '''   
      if not hasattr(cls, "__BLANKMAP"):
         book = BookData() 
         cls.__BLANKMAP = {x : getattr(book, x) for x in cls.all_properties()}
         for prop in cls.__BLANKMAP.values():
            if prop == None: raise Exception("None not allowed")
              
      return cls.__BLANKMAP[property]
    
    
   #===========================================================================   
   def __set_series_s(self, series_s = None):
      self.__series_s = BookData.blank("series_s") \
         if series_s is None else series_s.strip()
   
   series_s = property( lambda self : self.__series_s, 
      __set_series_s, __set_series_s,
      "Series name of this book.  Not None, may be empty." )
      
   
   #===========================================================================   
   def __set_issue_num_s(self, issue_num_s = None):
      self.__issue_num_s = BookData.blank("issue_num_s") \
         if issue_num_s is None else issue_num_s.strip()
      
   issue_num_s = property( lambda self : self.__issue_num_s, 
      __set_issue_num_s, __set_issue_num_s, 
      "Issue number (string) of this book. Not None, may be empty." )
   
   
   #===========================================================================   
   def __set_title_s(self, title_s = None):
      self.__title_s = BookData.blank("title_s") \
         if title_s is None else title_s.strip()
      
   title_s = property( lambda self : self.__title_s, 
      __set_title_s, __set_title_s,
      "Title of this book (issue specific).  Not None, may be empty.")
   
   
   #===========================================================================   
   def __set_crossovers_sl(self, crossovers_sl = None ):
      self.__crossovers_sl = \
         BookData.blank("crossovers_sl") if crossovers_sl == None else \
         [x.strip() for x in crossovers_sl if x != None and len(x.strip()) > 0] 
      
   crossovers_sl = property( lambda self : list(self.__crossovers_sl),
      __set_crossovers_sl, __set_crossovers_sl,
      "A [] of crossover names ('alt storylines') for this book. May be empty.")
       
       
   #===========================================================================   
   def __set_summary_s(self, summary_s = None):
      self.__summary_s = BookData.blank("summary_s") \
         if summary_s is None else summary_s.strip()
      
   summary_s = property( lambda self : self.__summary_s,
      __set_summary_s, __set_summary_s,
      "Plot summary of this book.  Not None, may be empty.")
   
   #===========================================================================   
   def __set_pub_year_n(self, pub_year_n = None):
      pub_year_n = -1 if pub_year_n is None else int(pub_year_n)
      self.__pub_year_n = pub_year_n if 0 < pub_year_n < 9999 \
         else BookData.blank("pub_year_n")
      
   pub_year_n = property( lambda self : self.__pub_year_n, 
      __set_pub_year_n, __set_pub_year_n, 
      "Publication year of this book, as an int >= -1, where -1 is unknown" )
      
      
   #===========================================================================   
   def __set_pub_month_n(self, pub_month_n = None):
      pub_month_n = -1 if pub_month_n is None else int(pub_month_n)
      self.__pub_month_n = pub_month_n \
         if 1 <= pub_month_n <= 12 else BookData.blank("pub_month_n")
      
   pub_month_n = property( lambda self : self.__pub_month_n,
      __set_pub_month_n, __set_pub_month_n, 
      "Publication month of this book, as an int from 1 to 12. -1 is unknown.")
   
   
   #===========================================================================   
   def __set_pub_day_n(self, pub_day_n = None):
      pub_day_n = -1 if pub_day_n is None else int(pub_day_n)
      self.__pub_day_n = pub_day_n \
         if pub_day_n >= 0 else BookData.blank("pub_day_n")
      
   pub_day_n = property( lambda self : self.__pub_day_n, 
      __set_pub_day_n, __set_pub_day_n,  
      "Publication day of this book, an int from 1 to 31, where -1 is unknown" )
   
   #===========================================================================   
   def __set_rel_year_n(self, rel_year_n = None):
      rel_year_n = -1 if rel_year_n is None else int(rel_year_n)
      self.__rel_year_n = rel_year_n if 0 < rel_year_n < 9999 \
         else BookData.blank("rel_year_n")
      
   rel_year_n = property( lambda self : self.__rel_year_n, 
      __set_rel_year_n, __set_rel_year_n, 
      "Release year of this book, as an int >= -1, where -1 is unknown")
      
      
   #===========================================================================   
   def __set_rel_month_n(self, rel_month_n = None):
      rel_month_n = -1 if rel_month_n is None else int(rel_month_n)
      self.__rel_month_n = rel_month_n \
         if 1 <= rel_month_n <= 12 else BookData.blank("rel_month_n")
      
   rel_month_n = property( lambda self : self.__rel_month_n,
      __set_rel_month_n, __set_rel_month_n, 
      "Release month of this book, as an int from 1 to 12. -1 is unknown.")
   
   
   #===========================================================================   
   def __set_rel_day_n(self, rel_day_n = None):
      rel_day_n = -1 if rel_day_n is None else int(rel_day_n)
      self.__rel_day_n = rel_day_n \
         if rel_day_n >= 0 else BookData.blank("rel_day_n")
      
   rel_day_n = property( lambda self : self.__rel_day_n, 
      __set_rel_day_n, __set_rel_day_n,  
      "Release day of this book, an int from 1 to 31, where -1 is unknown" )

   
   #===========================================================================   
   def __set_volume_year_n(self, volume_year_n = None):
      volume_year_n = -1 if volume_year_n is None else int(volume_year_n)
      self.__volume_year_n = volume_year_n \
         if volume_year_n >= 0 else BookData.blank("volume_year_n")
      
   volume_year_n = property( lambda self : self.__volume_year_n, 
      __set_volume_year_n, __set_volume_year_n, 
      "Volume (start year) of this book as an int >= -1, where -1 is unknown.")



   #===========================================================================   
   def __set_format_s(self, format_s = None):
      self.__format_s = BookData.blank("format_s") if format_s is None \
         else format_s.strip()
         
   format_s = property( lambda self : self.__format_s, 
      __set_format_s, __set_format_s, 
      "The format of this book (giant, annual, etc.)  Not None, may be empty.")

   
   #===========================================================================   
   def __set_imprint_s(self, imprint_s = None):
      self.__imprint_s = BookData.blank("imprint_s") \
         if imprint_s is None else imprint_s.strip()
      
   imprint_s = property( lambda self : self.__imprint_s, 
      __set_imprint_s, __set_imprint_s,
      "The imprint of this book's publisher.  Not None, may be empty.")

   
   #===========================================================================   
   def __set_publisher_s(self, publisher_s = None):
      self.__publisher_s = BookData.blank("publisher_s") \
         if publisher_s is None else publisher_s.strip()
      
   publisher_s = property( lambda self : self.__publisher_s, 
      __set_publisher_s, __set_publisher_s,
      "The publisher of this book.  Not None, may be empty.")
      
   
   #===========================================================================   
   def __set_characters_sl(self, characters_sl = None ):
      self.__characters_sl = \
         BookData.blank("characters_sl") if characters_sl == None else \
         [x.strip() for x in characters_sl if x != None and len(x.strip()) > 0] 
      
   characters_sl = property( lambda self : list(self.__characters_sl),
      __set_characters_sl, __set_characters_sl,
      "A [] of characters appearing in this book.  May be empty." )
   
   
   #===========================================================================   
   def __set_teams_sl(self, teams_sl = None ):
      self.__teams_sl = \
         BookData.blank("teams_sl") if teams_sl == None else \
         [x.strip() for x in teams_sl if x != None and len(x.strip()) > 0] 
      
   teams_sl = property( lambda self : list(self.__teams_sl),
      __set_teams_sl, __set_teams_sl,
      "A [] of teams appearing in this book.  May be empty." )
     
      
   #===========================================================================   
   def __set_locations_sl(self, locations_sl = None ):
      self.__locations_sl = \
         BookData.blank("locations_sl") if locations_sl == None else \
         [x.strip() for x in locations_sl if x != None and len(x.strip()) > 0] 
      
   locations_sl = property( lambda self : list(self.__locations_sl),
      __set_locations_sl, __set_locations_sl,
      "A [] of locations appearing in this book.  May be empty." )
     
 
   #===========================================================================   
   def __set_writers_sl(self, writers_sl = None ):
      self.__writers_sl = \
         BookData.blank("writers_sl") if writers_sl == None else \
         [x.strip() for x in writers_sl if x != None and len(x.strip()) > 0] 
      
   writers_sl = property( lambda self : list(self.__writers_sl),
      __set_writers_sl, __set_writers_sl,
      "A [] of writers who worked on this book.  May be empty." )

      
   #===========================================================================   
   def __set_pencillers_sl(self, pencillers_sl = None):
      self.__pencillers_sl = BookData.blank("pencillers_sl") \
         if pencillers_sl == None else [ x.strip() for x in pencillers_sl 
            if x != None and len(x.strip()) > 0 ]
      
   pencillers_sl = property( lambda self : list(self.__pencillers_sl), 
      __set_pencillers_sl, __set_pencillers_sl,
      "A [] of pencillers who worked on this book.  May be empty." )

     
   #===========================================================================   
   def __set_inkers_sl(self, inkers_sl = None):
      self.__inkers_sl = BookData.blank("inkers_sl") if inkers_sl == None else \
         [ x.strip() for x in inkers_sl if x != None and len(x.strip()) > 0 ]
      
   inkers_sl = property( lambda self : list(self.__inkers_sl), 
      __set_inkers_sl, __set_inkers_sl, 
      "A [] of inkers who worked on this book.  May be empty.")
      
      
   #===========================================================================   
   def __set_colorists_sl(self, colorists_sl = None):
      self.__colorists_sl = BookData.blank("colorists_sl") \
         if colorists_sl == None else [ x.strip() for x in colorists_sl 
            if x != None and len(x.strip()) > 0 ]
      
   colorists_sl = property( lambda self : list(self.__colorists_sl), 
      __set_colorists_sl, __set_colorists_sl,
      "A [] of colorists who worked on this book.  May be empty." )
      
      
   #===========================================================================   
   def __set_letterers_sl(self, letterers_sl = None):
      self.__letterers_sl = BookData.blank("letterers_sl") \
         if letterers_sl == None else [ x.strip() for x in letterers_sl 
            if x != None and len(x.strip()) > 0 ]
      
   letterers_sl = property( lambda self : list(self.__letterers_sl), 
      __set_letterers_sl, __set_letterers_sl,
      "A [] of letterers who worked on this book.  May be empty." )

      
   #===========================================================================   
   def __set_cover_artists_sl(self, cover_artists_sl = None):
      self.__cover_artists_sl = BookData.blank("cover_artists_sl") \
         if cover_artists_sl == None else [ x.strip() for x in cover_artists_sl 
            if x != None and len(x.strip()) > 0 ]
      
   cover_artists_sl = property( lambda self : list(self.__cover_artists_sl), 
      __set_cover_artists_sl, __set_cover_artists_sl,
      "A [] of cover artists who worked on this book.  May be empty." )

      
   #===========================================================================   
   def __set_editors_sl(self, editors_sl = None):
      self.__editors_sl = BookData.blank("editors_sl") \
         if editors_sl == None else [ x.strip() for x in editors_sl 
            if x != None and len(x.strip()) > 0 ]

   editors_sl = property( lambda self : list(self.__editors_sl),
      __set_editors_sl, __set_editors_sl,
      "A [] of editors who worked on this book.  May be empty." )

      
   #===========================================================================   
   def __set_webpage_s(self, webpage_s = None): 
      self.__webpage_s = BookData.blank("webpage_s") \
         if webpage_s is None else webpage_s.strip()   

   webpage_s = property( lambda self : self.__webpage_s, 
      __set_webpage_s, __set_webpage_s, 
      "The webpage associated with this book.  Not None, may be empty.")
   
   #===========================================================================   
   def __set_cover_url_s(self, cover_url_s = None): 
      self.__cover_url_s = BookData.blank("cover_url_s") \
         if cover_url_s is None else cover_url_s.strip()  

   cover_url_s = property( lambda self : self.__cover_url_s, 
      __set_cover_url_s, __set_cover_url_s, 
      "The url to a cover art image for this book.  Not None, may be empty.")

      
   #===========================================================================   
   def __set_tags_sl(self, tags_sl = None):
      self.__tags_sl = BookData.blank("tags_sl") if tags_sl == None else \
         [ x.strip() for x in tags_sl if x != None and len(x.strip()) > 0 ]
      
   tags_sl = property( lambda self : list(self.__tags_sl), 
      __set_tags_sl, __set_tags_sl,
      "A [] of tags associated with this book.  May be empty." )

   
   #===========================================================================   
   def __set_notes_s(self, notes_s = None):
      self.__notes_s = BookData.blank("notes_s") \
         if notes_s is None else notes_s.strip()
      
   notes_s = property( lambda self : self.__notes_s, 
      __set_notes_s, __set_notes_s, 
      "The user notes associated with this book.  Not None, may be empty.")


   #===========================================================================   
   def __set_rating_n(self, rating_n = None):
      rating_n = -1 if rating_n is None else float(rating_n)
      self.__rating_n = rating_n \
         if rating_n <= 5.0 and rating_n >= 0.0 else BookData.blank("rating_n")

   rating_n = property( lambda self : self.__rating_n, 
      __set_rating_n, __set_rating_n, 
      "The community rating for this book, i.e. a value between 0.0 and 5.0." )


   #===========================================================================   
   def __set_path_s(self, path_s = None ):
      self.__path_s = BookData.blank("path_s") \
         if path_s is None else path_s.strip()

   path_s = property( lambda self : self.__path_s, __set_path_s, 
      __set_path_s, 'The underlying path (incl. extension) for this book,' +
      ' or "" if it is a fileless book.  Will never be None.')
   
   
   #===========================================================================   
   def __set_page_count_n(self, page_count_n = None):
      page_count_n = -1 if page_count_n is None else int(page_count_n)
      self.__page_count_n = page_count_n \
         if page_count_n >= 0 else BookData.blank("page_count_n")
   page_count_n = property( lambda self : self.__page_count_n,
      __set_page_count_n, __set_page_count_n, 
      "The number of pages in this book, an integer >= 0." )

   
   #===========================================================================
   def __set_issue_key_s(self, issue_key_s = None):
      self.__issue_key_s = BookData.blank("issue_key_s") \
         if issue_key_s is None else sstr(issue_key_s).strip()
   
   issue_key_s = property( lambda self : self.__issue_key_s, 
      __set_issue_key_s, __set_issue_key_s,
      "The db Issue Key object for this book.  Not None, may be empty.")   
   
   
   #===========================================================================
   def __set_series_key_s(self, series_key_s = None):
      self.__series_key_s = BookData.blank("series_key_s") \
         if series_key_s is None else sstr(series_key_s).strip()
   
   series_key_s = property( lambda self : self.__series_key_s, 
      __set_series_key_s, __set_series_key_s,
      "The db Series Key object for this book.  Not None, may be empty.")   
      
