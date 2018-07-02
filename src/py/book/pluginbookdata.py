'''
This module contains the PluginBookData class, which is an implementation of
BookData that reads and writes directly to the ComicRack database via 
ComicRack's plugin api.

@author: Cory Banack
'''
import re
from System import DateTime
from bookdata import BookData
import utils
from utils import sstr
import clr
import db
import log

clr.AddReference('System')

#==============================================================================
class PluginBookData(BookData):
   ''' A BookData object customized for working with ComicRack directly. '''
   
   __ISSUE_KEY = "comicvine_issue"
   __SERIES_KEY = "comicvine_volume"
   
   #===========================================================================   
   def __init__(self, crbook, scraper):
      '''
      Construct a new PluginBookData.
      'crbook' is one of the ComicBook objects that ComicRack directly 
          passes to it's plugin scripts. 
      'comicrack' is a reference to the ComicRack App object. 
      '''
      super(PluginBookData, self).__init__();
      if not "ComicBook" in utils.sstr(type(crbook)): 
         raise Exception("invalid backing ComicBook")
      
      # a quick function to make splitting ComicRack comicbook fields easier 
      def split(s):
         return s.split(",") if s else [] 
      
      # load our own copy of all data from the ComicRack database
      self.series_s = crbook.Series    # don't use shadows!  we'll parse these 3
      self.issue_num_s = crbook.Number # values from the comic's filename our
      self.pub_year_n =  crbook.Year   # self if they are not present!
      self.pub_month_n = crbook.Month
      self.pub_day_n = crbook.Day
      self.rel_year_n = crbook.ReleasedTime.Year
      self.rel_month_n = crbook.ReleasedTime.Month
      self.rel_day_n = crbook.ReleasedTime.Day
      self.volume_year_n = crbook.ShadowVolume
      self.format_s = crbook.ShadowFormat
      self.title_s = crbook.Title
      self.crossovers_sl = split(crbook.AlternateSeries)
      self.summary_s = crbook.Summary
      self.publisher_s = crbook.Publisher
      self.imprint_s = crbook.Imprint
      self.characters_sl = split(crbook.Characters)
      self.teams_sl = split(crbook.Teams)
      self.locations_sl = split(crbook.Locations)
      self.writers_sl = split(crbook.Writer)
      self.pencillers_sl = split(crbook.Penciller)
      self.inkers_sl = split(crbook.Inker)
      self.colorists_sl = split(crbook.Colorist)
      self.letterers_sl = split(crbook.Letterer)
      self.cover_artists_sl = split(crbook.CoverArtist)
      self.editors_sl = split(crbook.Editor)
      self.tags_sl = split(crbook.Tags) 
      self.notes_s = crbook.Notes
      self.path_s = crbook.FilePath 
      self.webpage_s = crbook.Web
      self.rating_n = crbook.CommunityRating
      self.page_count_n = crbook.PageCount
      self.issue_key_s = crbook.GetCustomValue(PluginBookData.__ISSUE_KEY)
      self.series_key_s = crbook.GetCustomValue(PluginBookData.__SERIES_KEY)
      self.__crbook = crbook;
      self.__scraper = scraper;
                                    
   #==========================================================================
   def create_image_of_page(self, page_index):
      ''' Overridden to implement the superclass method of the same name. '''
      
      fileless = not self.path_s
      page_image = None
      if fileless:
         page_image = None
      else:
         try:
            page_image = self.__scraper.comicrack.App.GetComicPage(
               self.__crbook, page_index)
         except Exception:
            # we can't rely on self.page_count_n, thanks to bug 235.
            # (page count is zero after "clear data", so use try-catch instead.
            page_image = None
            
         if page_image:
            page_image = utils.strip_back_cover(page_image)
      return page_image                              

      
   #===========================================================================
   def update(self):
      '''
      Overridden to implement abstract method defined in superclass. Writes all 
      eligible properties in this object out to their counterparts in ComicRack 
      (i.e. back into the ComicBook object that was passed into __init__.) 
      '''
      ok_to_update = self.updated_properties()
      
      
      # removes commas from the the given string  
      def cleanup(s):
         s = re.sub(r",(\s+)", r"\1", s) if s else ""
         return re.sub(r",", r" ", s)
      
      
      if "series_s" in ok_to_update:
         self.__crbook.Series = self.series_s
         ok_to_update.remove("series_s")

      if "issue_num_s" in ok_to_update:
         self.__crbook.Number = self.issue_num_s
         ok_to_update.remove("issue_num_s")
      
      if "volume_year_n" in ok_to_update:
         self.__crbook.Volume = self.volume_year_n
         ok_to_update.remove("volume_year_n")
         
      if "format_s" in ok_to_update:
         self.__crbook.Format = self.format_s
         ok_to_update.remove("format_s")
         
      if "title_s" in ok_to_update:
         self.__crbook.Title = self.title_s
         ok_to_update.remove("title_s")
         
      if "crossovers_sl" in ok_to_update:
         self.__crbook.AlternateSeries = \
            ', '.join([cleanup(x) for x in self.crossovers_sl])
         ok_to_update.remove("crossovers_sl")
         
      if "summary_s" in ok_to_update:
         self.__crbook.Summary = self.summary_s
         ok_to_update.remove("summary_s")
         
      if "publisher_s" in ok_to_update:
         self.__crbook.Publisher = self.publisher_s
         ok_to_update.remove("publisher_s")
         
      if "imprint_s" in ok_to_update:
         self.__crbook.Imprint = self.imprint_s
         ok_to_update.remove("imprint_s")
         
      if "characters_sl" in ok_to_update:
         self.__crbook.Characters = \
            ', '.join([cleanup(x) for x in self.characters_sl])
         ok_to_update.remove("characters_sl")
            
      if "teams_sl" in ok_to_update:
         self.__crbook.Teams = \
            ', '.join([cleanup(x) for x in self.teams_sl])
         ok_to_update.remove("teams_sl")
            
      if "locations_sl" in ok_to_update:
         self.__crbook.Locations = \
            ', '.join([cleanup(x) for x in self.locations_sl])
         ok_to_update.remove("locations_sl")
            
      if "writers_sl" in ok_to_update:
         self.__crbook.Writer = \
            ', '.join([cleanup(x) for x in self.writers_sl])
         ok_to_update.remove("writers_sl")
            
      if "pencillers_sl" in ok_to_update:
         self.__crbook.Penciller = \
            ', '.join([cleanup(x) for x in self.pencillers_sl])
         ok_to_update.remove("pencillers_sl")
            
      if "inkers_sl" in ok_to_update:
         self.__crbook.Inker = \
            ', '.join([cleanup(x) for x in self.inkers_sl])
         ok_to_update.remove("inkers_sl")
         
      if "colorists_sl" in ok_to_update:
         self.__crbook.Colorist = \
            ', '.join([cleanup(x) for x in self.colorists_sl])
         ok_to_update.remove("colorists_sl")
         
      if "letterers_sl" in ok_to_update:
         self.__crbook.Letterer = \
            ', '.join([cleanup(x) for x in self.letterers_sl])
         ok_to_update.remove("letterers_sl")
            
      if "cover_artists_sl" in ok_to_update:
         self.__crbook.CoverArtist = \
            ', '.join([cleanup(x) for x in self.cover_artists_sl])
         ok_to_update.remove("cover_artists_sl")
            
      if "editors_sl" in ok_to_update:
         self.__crbook.Editor = \
            ', '.join([cleanup(x) for x in self.editors_sl])
         ok_to_update.remove("editors_sl")
         
      if "tags_sl" in ok_to_update:
         self.__crbook.Tags = \
            ', '.join([cleanup(x) for x in self.tags_sl])
         ok_to_update.remove("tags_sl")
            
      if "notes_s" in ok_to_update:
         self.__crbook.Notes = self.notes_s
         ok_to_update.remove("notes_s")
         
      if "webpage_s" in ok_to_update:
         self.__crbook.Web = self.webpage_s
         ok_to_update.remove("webpage_s")
         
      if "rating_n" in ok_to_update:
         self.__crbook.CommunityRating = self.rating_n
         ok_to_update.remove("rating_n")
         
      if "issue_key_s" in ok_to_update:
         self.__crbook.SetCustomValue(
            PluginBookData.__ISSUE_KEY, sstr(self.issue_key_s))
         ok_to_update.remove("issue_key_s")
         
      if "series_key_s" in ok_to_update:
         self.__crbook.SetCustomValue(
            PluginBookData.__SERIES_KEY, sstr(self.series_key_s))
         ok_to_update.remove("series_key_s")
         
         
      # dates are a little special.  any element in the data could be blank
      # (missing), and we only update the released date if NONE of the 
      # elements are missing.  the published date, however, can have a missing
      # day, or a missing day and month, and we'll still update the rest
      if "rel_year_n" in ok_to_update and \
         "rel_month_n" in ok_to_update and \
         "rel_day_n" in ok_to_update:
         if self.rel_year_n != BookData.blank("rel_year_n") and \
            self.rel_month_n != BookData.blank("rel_month_n") and \
            self.rel_day_n != BookData.blank("rel_day_n"):
            date = DateTime(self.rel_year_n, self.rel_month_n, self.rel_day_n)
            self.__crbook.ReleasedTime = date
         ok_to_update.remove("rel_year_n")
         ok_to_update.remove("rel_month_n")
         ok_to_update.remove("rel_day_n")
         
        
      if "pub_year_n" in ok_to_update:
         if self.pub_year_n != BookData.blank("pub_year_n"):
            self.__crbook.Year = self.pub_year_n
         ok_to_update.remove("pub_year_n")
         
      if "pub_month_n" in ok_to_update:
         if self.pub_year_n != BookData.blank("pub_year_n") and \
            self.pub_month_n != BookData.blank("pub_month_n"):
            self.__crbook.Month = self.pub_month_n
         ok_to_update.remove("pub_month_n")
         
      if "pub_day_n" in ok_to_update:
         if self.pub_year_n != BookData.blank("pub_year_n") and \
            self.pub_month_n != BookData.blank("pub_month_n") and \
            self.pub_day_n != BookData.blank("pub_day_n"):
            self.__crbook.Day = self.pub_day_n
         ok_to_update.remove("pub_day_n")
      
   
      # we only download and install a thumbnail for fileless CR books, and
      # even then, only if the user's prefs indicate that they want us to      
      if "cover_url_s" in ok_to_update:
         already_has_thumb = self.__crbook.CustomThumbnailKey
         book_is_fileless = not self.path_s
         config = self.__scraper.config
   
         if not self.cover_url_s or not book_is_fileless or \
               not config.download_thumbs_b or \
               (already_has_thumb and config.preserve_thumbs_b): 
            pass
         else:
            image = db.query_image(self.cover_url_s)
            if not image:
               log.debug("ERROR: can't download thumbnail: ", self.cover_url_s)
            else:
               cr = self.__scraper.comicrack.App
               success = cr.SetCustomBookThumbnail(self.__crbook, image)
               if not success:
                  log.debug("ERROR: can't set thumbnail: ", self.cover_url_s)
         ok_to_update.remove("cover_url_s")

         
      # a nice safety check to make sure we didn't miss anything
      if len(ok_to_update) > 0:
         for s in ok_to_update:
            log.debug(self.__class__.__name__ + " can't update property: " + s)
         raise Exception()
      
