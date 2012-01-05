'''
This module contains the Book class, which is an "abstract class" that defines
the data attributes and read/write functionality and any kind of comic book 
must have.  Various subclasses will implement the specific details.

@author: Cory Banack
'''
import re
import log
from time import strftime
from utils import sstr
import db
import utils
from dbmodels import IssueRef
import fnameparser

# coryhigh: start here
# so BookData will be the superclass of PluginBookData and CRBookData.
# CRBookData is for the ComicRack metadata format. (maybe more to come.)
# CRBookData will have 3 subclasses, CBZBookData, CB7BookData, and CBRBookData
# ComicBook merely has to contain and use a subclass of BookData.

# coryhigh: use this
#   clr   clr.AddReference("Ionic.Zip.dll") # a 3rd party dll
#   from Ionic.Zip import ZipFile #@UnresolvedImport
#   from System.IO import Directory, File
#   def delegate2(): # coryhigh: delete
#      zip = r"K:\xmlstuff\comic.cbz";
#      xml = r"ComicInfo.xml" 
#      
#      # grab the default (i.e. english) zip file, unzip it, and grab the
#      # xml file from inside.  parse that to obtain default i18n strings.
#      with ZipFile.Read(zip) as zipfile:
#         zipfile.AddEntry("cory.txt", "this is some sample text")
#         zipfile.Save(zip+".zip")

#==============================================================================
class BookData(object):
   '''
   This class defines the attributes that persistable book objects must have. 
   '''
   
   #===========================================================================   
   def __init__(self):
      self.__series_s = ""
      self.__issue_num_s = "blank"
      self.__volume_year_n = -1 # -1 is a blank value
      self.__year_n =  -1 # -1 is a blank value
      self.__month_n = -1 # -1 is a blank value
      self.__format_s = ""
      self.__title_s =""
      self.__alt_series_sl = [] 
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
      self.__filename_s = ""
      self.__webpage_s = ""
      self.__rating_n = 0.0 # 0.0 to 5.0
      self.__page_count_n = 0
      
      self.__saved_properties = BookData.__all_properties();
      self.dont_save("page_count_n")
      self.dont_save("filename_s")
      
      
   #===========================================================================   
   def dont_save(self, property):
      if property in self.__saved_properties:
         self.__saved_properties.remove(property)
      elif not property in BookData.__dict__:
         raise Exception("unrecognized property: " + property)
      
      
   def saved_properties(self):
      return set(self.__saved_properties)
   
   @classmethod
   def blank(cls, property):
      if not hasattr(cls, "__BLANKMAP"):
         book = BookData() 
         cls.__BLANKMAP = {x : getattr(book, x) for x in cls.__all_properties()}  
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
         if title_s is None else title_s.strip();
      
   title_s = property( lambda self : self.__title_s, 
      __set_title_s, __set_title_s,
      "Title of this book (issue specific).  Not None, may be empty.")
      
      
   #===========================================================================   
   def __set_alt_series_sl(self, alt_series_sl = None ):
      self.__alt_series_sl = \
         BookData.blank("alt_series_sl") if alt_series_sl == None else \
         [x.strip() for x in alt_series_sl if x != None and len(x.strip()) > 0] 
      
   alt_series_sl = property( lambda self : list(self.__alt_series_sl),
      __set_alt_series_sl, __set_alt_series_sl,
      "A [] of alternate series names ('arcs') for this book.  May be empty." )
       
       
   #===========================================================================   
   def __set_summary_s(self, summary_s = None):
      self.__summary_s = BookData.blank("summary_s") \
         if summary_s is None else summary_s.strip();
      
   summary_s = property( lambda self : self.__summary_s,
      __set_summary_s, __set_summary_s,
      "Plot summary of this book.  Not None, may be empty.")
   

   #===========================================================================   
   def __set_year_n(self, year_n = None):
      self.__year_n = int(year_n) if year_n >= 0 else BookData.blank("year_n")
      
   year_n = property( lambda self : self.__year_n, __set_year_n, __set_year_n, 
      "Publication year of this book, as an int >= -1, where -1 is unknown" )
      
      
   #===========================================================================   
   def __set_month_n(self, month_n = None):
      remap={ 1:1, 26:1, 2:2, 19:2, 3:3, 13:3, 27:3, 4:4, 20:4, 5:5, 28:5, \
              6:6, 14:6, 21:6, 7:7, 29:7, 8:8, 22:8, 9:9, 15:9, 30:9, 10:10,\
              23:10, 11:11, 31:11, 12:12, 16:12, 24:12, 25:12, 18:-1, 17:-1 }
      month_n = None if month_n is None else int(month_n)
      if month_n in remap:
         month_n = remap[month_n]
      self.__month_n = month_n if month_n <= 12 \
         and month_n >= 1 else BookData.blank("month_n")
      
   month_n = property( lambda self : self.__month_n, 
      __set_month_n, __set_month_n, 
      ''' Publication month of this book, as an int from 1 to 12. -1 is unknown.
          Values from  13 to 31 are also allowed, but will be recoded as: 
              13 = Spring (3)     23 = Sep/Oct (10)   
              14 = Summer (6)     24 = Nov/Dec (12)
              15 = Fall (9)       25 = Holiday (12)
              16 = Winter (12)    26 = Dec/Jan (1)
              17 = Annual (-1)    27 = Feb/Mar (3)
              18 = None (-1)      28 = Apr/May (5)
              19 = Jan/Feb (2)    29 = Jun/Jul (7)
              20 = Mar/Apr (4)    30 = Aug/Sep (9)
              21 = May/Jun (6)    31 = Oct/Nov (11)
              22 = Jul/Aug (8)                         ''')

   
   #===========================================================================   
   def __set_volume_year_n(self, volume_year_n = None):
      self.__volume_year_n = int(volume_year_n) \
         if volume_year_n >= 0 else BookData.blank("volume_year_n")
      
   volume_year_n = property( lambda self : self.__volume_year_n, 
      __set_volume_year_n, __set_volume_year_n, 
      "Volume (start year) of this book as an int >= -1, where -1 is unknown.")



   #===========================================================================   
   def __set_format_s(self, format_s = None):
      self.__format_s = BookData.blank("format_s") if format_s is None \
         else format_s.strip();
         
   format_s = property( lambda self : self.__format_s, 
      __set_format_s, __set_format_s, 
      "The format of this book (giant, annual, etc.)  Not None, may be empty.")

   
   #===========================================================================   
   def __set_imprint_s(self, imprint_s = None):
      self.__imprint_s = BookData.blank("imprint_s") \
         if imprint_s is None else imprint_s.strip();
      
   imprint_s = property( lambda self : self.__imprint_s, 
      __set_imprint_s, __set_imprint_s,
      "The imprint of this book's publisher.  Not None, may be empty.")

   
   #===========================================================================   
   def __set_publisher_s(self, publisher_s = None):
      self.__publisher_s = BookData.blank("publisher_s") \
         if publisher_s is None else publisher_s.strip();
      
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
         if webpage_s is None else webpage_s.strip();   

   webpage_s = property( lambda self : self.__webpage_s, 
      __set_webpage_s, __set_webpage_s, 
      "The webpage associated with this book.  Not None, may be empty.")

      
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
         if notes_s is None else notes_s.strip();
      
   notes_s = property( lambda self : self.__notes_s, 
      __set_notes_s, __set_notes_s, 
      "The user notes associated with this book.  Not None, may be empty.")


   #===========================================================================   
   def __set_rating_n(self, rating_n = None):
      self.__rating_n = float(rating_n) \
         if rating_n <= 5.0 and rating_n >= 0.0 else BookData.blank("rating_n");

   rating_n = property( lambda self : self.__rating_n, 
      __set_rating_n, __set_rating_n, 
      "The community rating for this book, i.e. a value between 0.0 and 5.0." )


   #===========================================================================   
   def __set_filename_s(self, filename_s = None ):
      self.__filename_s = BookData.blank("filename_s") \
         if filename_s is None else filename_s.strip();

   filename_s = property( lambda self : self.__filename_s, __set_filename_s, 
      __set_filename_s, 'The underlying filename for this book,' +
      ' or "" if it is a fileless book.  Will never be None.')
   
   
   #===========================================================================   
   def __set_page_count_n(self, page_count_n = None):
      self.__page_count_n = int(page_count_n) \
         if page_count_n >= 0 else BookData.blank("page_count_n")
      
   page_count_n = property( lambda self : self.__page_count_n,
      __set_page_count_n, __set_page_count_n, 
      "The number of pages in this book, an integer >= 0." )
   
   
   #===========================================================================   
   @classmethod
   def __all_properties(cls):
      return [ x for x in cls.__dict__ if 
         x[0] != '_' and isinstance(cls.__dict__[x], property) ]
      
      
if __name__ == '__main__':  
   book = BookData()
   book.month_n = 5
   print book.month_n
   book.month_n = None
   print book.month_n
   book.month_n = 12
   print book.month_n
   del book.month_n
   print book.month_n
