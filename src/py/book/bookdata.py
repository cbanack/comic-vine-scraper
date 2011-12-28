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
   
   def __init__(self):
      self.__series_s = ""
      self.__issue_num_s = ""
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
      self.__uuid_s = ""
      self.__tags_sl = [] 
      self.__notes_s = ""
      self.__filename_s = ""
      self.__webpage_s = ""
      self.__rating_n = 0.0 # 0.0 to 5.0
      self.__page_count_n = 0
      

   #===========================================================================   
   series_s = property( lambda self : self.__series_s, __set_series_s, None,
      "Series name of this book.  Not None, may be empty." )
   def __set_series_s(self, series_s):
      self.__series_s = "" if series_s is None else series_s.strip()
      
   
   #===========================================================================   
   issue_num_s = property( lambda self : self.__issue_num_s, __set_issue_num_s,
      None, "Issue number (string) of this book. Not None, may be empty." )
   def __set_issue_num_s(self, issue_num_s):
      self.__issue_num_s = "" if issue_num_s is None else issue_num_s.strip()
   
   
   #===========================================================================   
   title_s = property( lambda self : self.__title_s, __set_title_s, None,
      "Title of this book (issue specific).  Not None, may be empty.")
   def __set_title_s(self, title_s):
      self.__title_s = "" if title_s is None else title_s.strip();
      
      
   #===========================================================================   
   alt_series_sl = property( lambda self : list(self.__alt_series_sl),
      __set_alt_series_sl, None,
      "A [] of alternate series names ('arcs') for this book.  May be empty." )
   def __set_alt_series_sl(self, alt_series_sl):
      self.__alt_series_sl = [ x.strip() for x in alt_series_sl 
         if x != None and len(x.strip()) > 0 ] # defensive copy!
       
       
   #===========================================================================   
   summary_s = property( lambda self : self.__summary_s, __set_summary_s, None,
      "Plot summary of this book.  Not None, may be empty.")
   def __set_summary_s(self, summary_s):
      self.__summary_s = "" if summary_s is None else summary_s.strip();
   

   #===========================================================================   
   year_n = property( lambda self : self.__year_n, __set_year_n, None, 
      "Publication year of this book, as an int >= -1, where -1 is unknown" )
   def __set_year_n(self, year_n):
      self.__year_n = max(-1, int(year_n))
      
      
   #===========================================================================   
   month_n = property( lambda self : self.__month_n,  __set_month_n, None, 
      '''  Publication month of this book, as an int from 1 to 12. 
      -1 is unknown.  Values from  13 to 31 will be interpreted as: 
        13 - Spring   18 - None      23 - Sep/Oct   28 - Apr/May
        14 - Summer   19 - Jan/Feb   24 - Nov/Dec   29 - Jun/Jul
        15 - Fall     20 - Mar/Apr   25 - Holiday   30 - Aug/Sep
        16 - Winter   21 - May/Jun   26 - Dec/Jan   31 - Oct/Nov
        17 - Annual   22 - Jul/Aug   27 - Feb/Mar ''')  
   def __set_month_n(self, month_n):
      remap={ 1:1, 26:1, 2:2, 19:2, 3:3, 13:3, 27:3, 4:4, 20:4, 5:5, 28:5, \
              6:6, 14:6, 21:6, 7:7, 29:7, 8:8, 22:8, 9:9, 15:9, 30:9, 10:10,\
              23:10, 11:11, 31:11, 12:12, 16:12, 24:12, 25:12 }
      month_n = int(month_n)
      if month_n in remap:
         month_n = remap[month_n]
      self.__month_n = -1 if month_n == -1 else min(12, max(1, month_n))
   
   
   #===========================================================================   
   volume_year_n = property( lambda self :  self.__volume_year_n,
      __set_volume_year_n, None, 
      "Volume (start year) of this book as an int >= -1, where -1 is unknown.")
   def __set_volume_year_n(self, volume_year_n):
      self.__volume_year_n = max(-1, int(volume_year_n))
   
   
   
   # the format of this comic book, as a string, or "" if empty.  Not None.
   format_s = property( lambda self : self.__cr_book.ShadowFormat
      if self.__cr_book.ShadowFormat else "" )
   
   # a comma separated string listing the tags associated with this comic book.   
   # maybe be empty, but will not be None.
   tags_s = property( lambda self : self.__cr_book.Tags 
      if self.__cr_book.Tags else "" )
   
   # the notes string for this comic book.  Mayb be "", but will not be None.
   notes_s = property( lambda self : self.__cr_book.Notes
      if self.__cr_book.Notes else "" )
   
   # the unique id string associated with this comicbook.  no other book will
   # have this id string, and the string will never be None or "".
   uuid_s = property( lambda self : utils.sstr(self.__cr_book.Id) )
   
   # the name of this comic book's backing file, including its file extension.
   # will not be None, will be empty if book is fileless.
   filename_ext_s = property(lambda self : "" if 
      self.__cr_book.FileNameWithExtension is None else 
      self.__cr_book.FileNameWithExtension)
   
   # the unique id string associated with this comic book's series.  all comic
   # books that appear to be from the same series will have the same id string,
   # which will be different for each series. will not be null or None.
   unique_series_s = property( lambda self : self.__unique_series_s() )  
   
   # the number of pages in this comic book.  0 or higher.
   page_count_n = property( lambda self : 0 if 
       not self.__cr_book.PageCount or self.__cr_book.PageCount < 0
       else self.__cr_book.PageCount )

   



      self.__format_s = ""

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
      self.__uuid_s = ""
      self.__tags_sl = [] 
      self.__notes_s = ""
      self.__filename_s = ""
      self.__webpage_s = ""
      self.__rating_n = 0.0 # 0.0 to 5.0
      self.__page_count_n = 0
   
