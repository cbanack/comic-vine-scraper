'''
This module contains the PluginBookData class, which is an implementation of
BookData that reads and writes directly to the ComicRack database via 
ComicRack's plugin api.

@author: Cory Banack
'''
from bookdata import BookData
from utils import sstr
import utils
import log
import re
import db

#==============================================================================
class PluginBookData(BookData):
   ''' A BookData object customized for working with ComicRack directly. '''
   
   #===========================================================================   
   def __init__(self, crbook, scraper):
      '''
      Construct a new PluginBookData.
      'crbook' is one of the ComicBook objects that ComicRack directly 
          passes to it's plugin scripts. 
      'comicrack' is a reference to the ComicRack App object. 
      '''
      super(PluginBookData, self).__init__();
      if not ("ComicBook" in utils.sstr(type(crbook))): 
         raise Exception("invalid backing ComicBook")
      
      # load our own copy of all data from the ComicRack database
      self.series_s = crbook.Series    # don't use shadows
      self.issue_num_s = crbook.Number # don't use shadows
      self.volume_year_n = crbook.ShadowVolume
      self.year_n =  crbook.ShadowYear
      self.month_n = crbook.Month
      self.format_s = crbook.ShadowFormat
      self.title_s = crbook.Title
      self.alt_series_sl = crbook.AlternateSeries.split(",")
      self.summary_s = crbook.Summary
      self.publisher_s = crbook.Publisher
      self.imprint_s = crbook.Imprint
      self.characters_sl = crbook.Characters.split(",")
      self.teams_sl = crbook.Teams.split(",")
      self.locations_sl = crbook.Locations.split(",")
      self.writers_sl = crbook.Writer.split(",")
      self.pencillers_sl = crbook.Penciller.split(",")
      self.inkers_sl = crbook.Inker.split(",")
      self.colorists_sl = crbook.Colorist.split(",")
      self.letterers_sl = crbook.Letterer.split(",")
      self.cover_artists_sl = crbook.CoverArtist.split(",")
      self.editors_sl = crbook.Editor.split(",")
      self.tags_sl = crbook.Tags.split(",") 
      self.notes_s = crbook.Notes
      self.filename_s = crbook.FileNameWithExtension
      self.webpage_s = crbook.Web
      self.rating_n = crbook.CommunityRating
      self.page_count_n = crbook.PageCount
      
      self.__crbook = crbook;
      self.__scraper = scraper;
                                    
   #==========================================================================
   def create_image_of_page(self, page_index):
      ''' Overridden to implement the superclass method of the same name. '''
      
      fileless = not self.filename_s
      page_image = None
      if fileless or page_index < 0 or page_index >= self.page_count_n:
         page_image = None
      else:
         page_image = self.__scraper.comicrack.App.GetComicPage(
            self.__crbook, page_index)
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
      
      if "year_n" in ok_to_update:
         self.__crbook.Year = self.year_n
         ok_to_update.remove("year_n")
         
      if "month_n" in ok_to_update:
         self.__crbook.Month = self.month_n
         ok_to_update.remove("month_n")
         
      if "format_s" in ok_to_update:
         self.__crbook.Format = self.format_s
         ok_to_update.remove("format_s")
         
      if "title_s" in ok_to_update:
         self.__crbook.Title = self.title_s
         ok_to_update.remove("title_s")
         
      if "alt_series_sl" in ok_to_update:
         self.__crbook.AlternateSeries = \
            ', '.join([cleanup(x) for x in self.alt_series_sl])
         ok_to_update.remove("alt_series_sl")
         
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
         
      # a nice safety check to make sure we didn't miss anything
      if len(ok_to_update) > 0:
         for s in ok_to_update:
            log.debug(self.__class__.__name__ + " can't update property: " + s)
         raise Exception()
      
     
   #===========================================================================
   def __maybe_download_thumbnail(self, issue):
      # coryhigh: this is never called; we have to pass in an IssueRef?
      # call it when update is called?
      '''
      Iff this PLuginBookData represents a 'fileless' book in the ComicRack
      database, this method downloads and stores a cover image into the database 
      (assuming the scraper's config settings permit.)  Otherwise, this 
      method does nothing.
      
      'issue' -> the Issue for the book that we are updating
      '''
      
      scraper = self.__scraper
      config = scraper.config
      label = "Thumbnail"
      already_has_thumb = self.__crbook.CustomThumbnailKey
      book_is_fileless = not self.filename_s
      
      # don't download the thumbnail if the book has a backing file (cause 
      # that's where the thumbnail will come from!) or if the user has 
      # specified in config that we shouldn't.
      if not book_is_fileless or not config.download_thumbs_b or \
               (already_has_thumb and config.preserve_thumbs_b):
            log.debug("-->  ", label.ljust(15), ": --- skipped ---")
      else:
         # get the url for this issue's cover art.  check to see if the user
         # picked an alternate cover back when they closed the IssueForm, and if
         # not, just grab the url for the default cover art.
         url = None
         alt_cover_key = sstr(issue.issue_key)+"-altcover"
         if alt_cover_key in config.session_data_map:
            url = config.session_data_map[alt_cover_key]
         if not url and len(issue.image_urls):  
            url = issue.image_urls[0]
            
         if not url:
            # there is no image url available for this issue 
            log.debug("-->  ", label.ljust(15),": --- not available! ---")
         else:
            image = db.query_image(url)
            if not image:
               log.debug("ERROR: couldn't download thumbnail: ", url)
            else:
               cr = scraper.comicrack.App
               success = cr.SetCustomBookThumbnail(self.__bookdata, image)
               if success:
                  # it worked!
                  log.debug("--> *", label.ljust(15),": ", url)
               else:
                  log.debug("ERROR: comicrack can't set thumbnail!")
                              