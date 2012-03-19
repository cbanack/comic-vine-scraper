'''
This module contoins the Configuration object.

@author: Cory Banack
'''

import clr
from resources import Resources
from utils import persist_map, load_map, persist_string, load_string
import re
import utils

clr.AddReference('System')
from System.IO import File

#==============================================================================
class Configuration(object):
   '''
   This class contains the configuration details for the scraper, including
   methods for reading and writing those details to the filesystem.
   '''
   
   # map names for basic boolean settings (checkboxes)   
   __UPDATE_SERIES = 'updateSeries'
   __UPDATE_NUMBER = 'updateNumber'
   __UPDATE_MONTH = 'updateMonth'
   __UPDATE_TITLE = 'updateTitle'
   __UPDATE_STORYARC = 'updateStoryArc'
   __UPDATE_ALT_SERIES = 'updateAltSeries'
   __UPDATE_WRITER = 'updateWriter'
   __UPDATE_PENCILLER = 'updatePenciller'
   __UPDATE_INKER = 'updateInker'
   __UPDATE_COVER_ARTIST = 'updateCoverArtist'
   __UPDATE_COLORIST = 'updateColorist'
   __UPDATE_LETTERER = 'updateLetterer'
   __UPDATE_EDITOR = 'updateEditor'
   __UPDATE_SUMMARY = 'updateSummary'
   __UPDATE_YEAR = 'updateYear'
   __UPDATE_IMPRINT = 'updateImprint'
   __UPDATE_PUBLISHER = 'updatePublisher'
   __UPDATE_VOLUME = 'updateVolume'
   __UPDATE_CHARACTERS = 'updateCharacters'
   __UPDATE_TEAMS = 'updateTeams'
   __UPDATE_LOCATIONS = 'updateLocations'
   __UPDATE_WEBPAGE = 'updateWebpage'
   __UPDATE_RATING = 'updateRating'
   __OVERWRITE_EXISTING = 'overwriteExisting'
   __IGNORE_BLANKS = 'ignoreBlanks'
   __CONVERT_IMPRINTS = 'convertImprints'
   __SPECIFY_SERIES = 'specifySeriesName'
   __SHOW_COVERS = 'showCovers'
   __DOWNLOAD_THUMBS = 'downloadThumbs'
   __PRESERVE_THUMBS = 'preserveThumbs'
   __SCRAPE_IN_GROUPS = 'scrapeInGroups'
   __FAST_RESCRAPE = 'fastRescrape'
   __RESCRAPE_NOTES = 'updateNotes'
   __RESCRAPE_TAGS = 'updateTags'
   __WELCOME_DIALOG = 'welcomeDialog'
   __SUMMARY_DIALOG = 'summaryDialog'
   
   # default values for advanced settings
   __DEFAULT_FILTERED_PUBLISHERS = set()
   __DEFAULT_FILTER_BEFORE_YEAR = 0
   __DEFAULT_FILTER_AFTER_YEAR = 9999999
   __DEFAULT_NEVER_FILTER_THRESHOLD = 9999999
   __DEFAULT_ALT_SEARCH_REGEX = "" 
  
  
   #=========================================================================== 
   def __init__(self):
      ''' Initializes a new Configuration object with default settings '''
      
      self.ow_existing_b = True # scraper should overwrite existing metadata?
      self.ignore_blanks_b = False  # ...unless the new metada is blank?
      self.convert_imprints_b = True # convert imprints to parent publishers
      self.specify_series_b = False # user specify series search terms
      self.show_covers_b = True # show cover images when possible
      self.download_thumbs_b = True # download thumbnails for fileless comics
      self.preserve_thumbs_b = True # ...except when they already have thumbs
      self.scrape_in_groups_b = True # group comics by series when scraping
      self.fast_rescrape_b = True # use previous scrape choice when available
      self.rescrape_notes_b = True # store prev scrape choice in notes field
      self.rescrape_tags_b = True # store prev scrape choice in tags field
      self.welcome_dialog_b = True # show the welcome dialog before scraping
      self.summary_dialog_b = True # show summary dialog after scrape finishes

      self.update_series_b = True # scrape comic's series metadata
      self.update_number_b = True # scrape comic's issue number metadata
      self.update_month_b = True # scrape comic's publication month metadata
      self.update_year_b = True # scrape comic's publication year metadata
      self.update_title_b = True # scrape comic's issue title metadata
      self.update_storyarc_b = True # scrape comic's issue storyarc metadata
      self.update_alt_series_b = True # scrape comic's alternate series metadata
      self.update_writer_b = True # scrape comic's writer metadata
      self.update_penciller_b = True # scrape comic's penciller metadata
      self.update_inker_b = True # scrape comic's inker metadata
      self.update_cover_artist_b = True # scrape comic's cover artist metadata
      self.update_colorist_b = True # scrape comic's colorist metadata
      self.update_letterer_b = True # scrape comic's letterer metadata
      self.update_editor_b = True # scrape comic's editor metadata
      self.update_summary_b = True # scrape comic's summary metadata
      self.update_publisher_b = True # scrape comic's publisher metadata
      self.update_imprint_b = True # scrape comic's imprint metadata
      self.update_volume_b = True # scrape comic's volume (year) metadata
      self.update_characters_b = True # scrape comic's characters metadata
      self.update_teams_b = True # scrape comic's teams metadata
      self.update_locations_b = True # scrape comic's location metadata
      self.update_webpage_b = True # scrape comic's webpage metadata
      self.update_rating_b = True # scrape comic's community rating metadata
      
            
      # this is a general purpose map for saving ad-hoc data in a highly 
      # flexible, unstructured fashion.  this data only lasts as long as this
      # Configuration object is around, and it DOES NOT get saved or reloaded.
      self.session_data_map = {}
      
      # the contents of the advanced settings file (and the values parsed out
      # of it.)  this advanced settings string value gets persisted and reloaded
      # when we save and load a Configuration object, but the parsed values are
      # tied to the string, and only change when it does.
      self.__advanced_settings_s = None
      self.__filtered_publishers_sl = None # filter publishers out of searches
      self.__filter_before_year_n = None # filter series started before year
      self.__filter_after_year_n = None # filter series started after year
      self.__never_filter_threshold_n = None # min issues before we don't filter
      self.__alt_search_regex_s = None # alternate filename parsing regex
      self.__set_advanced_settings_s("")
      
      return self
   
   
   
   #===========================================================================   
   def __set_advanced_settings_s(self, advanced_settings_s = None):
      ''' 
      Changes the current advanced settings string, then reparses it to obtain
      new values for all of the advanced settings.
      '''
      
      self.__advanced_settings_s = "" if advanced_settings_s is None \
         else advanced_settings_s.strip()
      
      # 1. reset to defaults
      c = Configuration
      self.__filtered_publishers_sl = c.__DEFAULT_FILTERED_PUBLISHERS
      self.__filter_before_year_n = c.__DEFAULT_FILTER_BEFORE_YEAR
      self.__filter_after_year_n = c.__DEFAULT_FILTER_AFTER_YEAR
      self.__never_filter_threshold_n = c.__DEFAULT_NEVER_FILTER_THRESHOLD
      self.__alt_search_regex_s = c.__DEFAULT_ALT_SEARCH_REGEX
      
      # 2. scan through the string looking at each line for advanced settings
      lines_s = [ x.strip() for x in self.__advanced_settings_s.split("\n") \
                 if x.strip() ]
      pattern_s = r"^(?i){0}\s*=\s*['\"]?(.+?)['\"]?$"
      for line_s in lines_s:
         # 2a. parse the "IGNORE_PUBLISHER=XXXX" line
         match = re.match(pattern_s.format("IGNORE_PUBLISHER"), line_s) 
         if match: 
            self.__filtered_publishers_sl.add(match.group(1).lower().strip())
            
         # 2b. parse the "IGNORE_BEFORE_YEAR=XXXX" line
         match = re.match(pattern_s.format("IGNORE_BEFORE_YEAR"), line_s)
         if match and utils.is_number(match.group(1)):
            self.__filter_before_year_n = int(float(match.group(1)))
            
         # 2c. parse the "IGNORE_AFTER_YEAR=XXXX" line
         match = re.match(pattern_s.format("IGNORE_AFTER_YEAR"), line_s)
         if match and utils.is_number(match.group(1)):
            self.__filter_after_year_n = int(float(match.group(1)))
            
         # 2d. parse the "NEVER_IGNORE_THRESHOLD=XXXX" line
         match = re.match(pattern_s.format("NEVER_IGNORE_THRESHOLD"), line_s)
         if match and utils.is_number(match.group(1)):
            self.__never_filter_threshold_n = int(float(match.group(1)))
            
         # 2e. parse the "ALT_SEARCH_REGEX=XXXX" line
         match = re.match(pattern_s.format("ALT_SEARCH_REGEX"), line_s)
         if match:
            try:
               re.compile(match.group(1))
               self.__alt_search_regex_s = match.group(1)
            except:
               pass # nope, looks like it's not a parsable regex
      
      
   
   advanced_settings_s = property( lambda self : self.__advanced_settings_s, 
      __set_advanced_settings_s, __set_advanced_settings_s,
      "The advanced settings string for this Configuration. Not None." )
   
   filtered_publishers_sl = property( 
      lambda self : list(self.__filtered_publishers_sl), None, None,
      "List of publisher names to filter out of series searches. Not None.")
   
   filtered_before_year_n = property( 
      lambda self : self.__filter_before_year_n, None, None,
      "Filter out searched series first published before this year. Not None.")
   
   filtered_after_year_n = property( 
      lambda self : self.__filter_after_year_n, None, None,
      "Filter out searched series first published after this year. Not None.")
   
   never_filter_threshold_n = property( 
      lambda self : self.__never_filter_threshold_n, None, None,
      "Never filter series that have this many issues, or more. Not None.")
   
   alt_search_regex_s = property( 
      lambda self : self.__alt_search_regex_s, None, None,
      "Alternate regex for parsing issue/series/etc from filename. Not None.")
      
   
   #===========================================================================
   def load_defaults(self):
      ''' 
      Loads any settings that are saved in the user's settings files (if there 
      are any) and stores them in this Configuration object.
      '''

      # load the loaded dict out of the serialized file
      loaded = {}
      if File.Exists(Resources.SETTINGS_FILE):
         loaded = load_map(Resources.SETTINGS_FILE)
         
      # any settings that the serialized dict happens to contain, u
      if Configuration.__UPDATE_SERIES in loaded:
         self.update_series_b = loaded[Configuration.__UPDATE_SERIES]
      
      if Configuration.__UPDATE_NUMBER in loaded:
         self.update_number_b = loaded[Configuration.__UPDATE_NUMBER]
         
      if Configuration.__UPDATE_MONTH in loaded:
         self.update_month_b = loaded[Configuration.__UPDATE_MONTH]
         
      if Configuration.__UPDATE_TITLE in loaded:
         self.update_title_b = loaded[Configuration.__UPDATE_TITLE]
         
      if Configuration.__UPDATE_STORYARC in loaded:
         self.update_storyarc_b = loaded[Configuration.__UPDATE_STORYARC]
         
      if Configuration.__UPDATE_ALT_SERIES in loaded:
         self.update_alt_series_b = loaded[Configuration.__UPDATE_ALT_SERIES]
         
      if Configuration.__UPDATE_WRITER in loaded:
         self.update_writer_b = loaded[Configuration.__UPDATE_WRITER]

      if Configuration.__UPDATE_PENCILLER in loaded:
         self.update_penciller_b = loaded[Configuration.__UPDATE_PENCILLER]
         
      if Configuration.__UPDATE_INKER in loaded:
         self.update_inker_b = loaded[Configuration.__UPDATE_INKER]

      if Configuration.__UPDATE_COVER_ARTIST in loaded:
         self.update_cover_artist_b = loaded[Configuration.__UPDATE_COVER_ARTIST]

      if Configuration.__UPDATE_COLORIST in loaded:
         self.update_colorist_b = loaded[Configuration.__UPDATE_COLORIST]

      if Configuration.__UPDATE_LETTERER in loaded:
         self.update_letterer_b = loaded[Configuration.__UPDATE_LETTERER]

      if Configuration.__UPDATE_EDITOR in loaded:
         self.update_editor_b = loaded[Configuration.__UPDATE_EDITOR]
         
      if Configuration.__UPDATE_SUMMARY in loaded:
         self.update_summary_b = loaded[Configuration.__UPDATE_SUMMARY]
         
      if Configuration.__UPDATE_YEAR in loaded:
         self.update_year_b = loaded[Configuration.__UPDATE_YEAR]

      if Configuration.__UPDATE_IMPRINT in loaded:
         self.update_imprint_b = loaded[Configuration.__UPDATE_IMPRINT]

      if Configuration.__UPDATE_PUBLISHER in loaded:
         self.update_publisher_b = loaded[Configuration.__UPDATE_PUBLISHER]
         
      if Configuration.__UPDATE_VOLUME in loaded:
         self.update_volume_b = loaded[Configuration.__UPDATE_VOLUME]

      if Configuration.__UPDATE_CHARACTERS in loaded:
         self.update_characters_b = loaded[Configuration.__UPDATE_CHARACTERS]

      if Configuration.__UPDATE_TEAMS in loaded:
         self.update_teams_b = loaded[Configuration.__UPDATE_TEAMS]
      
      if Configuration.__UPDATE_LOCATIONS in loaded:
         self.update_locations_b = loaded[Configuration.__UPDATE_LOCATIONS]
         
      if Configuration.__UPDATE_WEBPAGE in loaded:
         self.update_webpage_b = loaded[Configuration.__UPDATE_WEBPAGE]
         
      if Configuration.__UPDATE_RATING in loaded:
         self.update_rating_b = loaded[Configuration.__UPDATE_RATING]

      if Configuration.__OVERWRITE_EXISTING in loaded:
         self.ow_existing_b = loaded[Configuration.__OVERWRITE_EXISTING]

      if Configuration.__IGNORE_BLANKS in loaded:
         self.ignore_blanks_b = loaded[Configuration.__IGNORE_BLANKS]

      if Configuration.__CONVERT_IMPRINTS in loaded:
         self.convert_imprints_b = loaded[Configuration.__CONVERT_IMPRINTS]

      if Configuration.__SPECIFY_SERIES in loaded:
         self.specify_series_b = loaded[Configuration.__SPECIFY_SERIES]

      if Configuration.__SHOW_COVERS in loaded:
         self.show_covers_b = loaded[Configuration.__SHOW_COVERS]
         
      if Configuration.__DOWNLOAD_THUMBS in loaded:
         self.download_thumbs_b=loaded[Configuration.__DOWNLOAD_THUMBS]
         
      if Configuration.__PRESERVE_THUMBS in loaded:
         self.preserve_thumbs_b=loaded[Configuration.__PRESERVE_THUMBS]
         
      if Configuration.__FAST_RESCRAPE in loaded:
         self.fast_rescrape_b=loaded[Configuration.__FAST_RESCRAPE]
         
      if Configuration.__SCRAPE_IN_GROUPS in loaded:
         self.scrape_in_groups_b=loaded[Configuration.__SCRAPE_IN_GROUPS]

      if Configuration.__RESCRAPE_NOTES in loaded:
         self.rescrape_notes_b = loaded[Configuration.__RESCRAPE_NOTES]
         
      if Configuration.__RESCRAPE_TAGS in loaded:
         self.rescrape_tags_b = loaded[Configuration.__RESCRAPE_TAGS]
         
      if Configuration.__WELCOME_DIALOG in loaded:
         self.welcome_dialog_b = loaded[Configuration.__WELCOME_DIALOG]
         
      if Configuration.__SUMMARY_DIALOG in loaded:
         self.summary_dialog_b = loaded[Configuration.__SUMMARY_DIALOG]
      
      # grab the contents of the advanced settings file, too   
      if File.Exists(Resources.ADVANCED_FILE): 
         self.advanced_settings_s = load_string(Resources.ADVANCED_FILE)
         
         
   #===========================================================================
   def save_defaults(self):
      ''' 
      Saves the settings in this Configuration object to the user's settings 
      files, replacing the current contents of those files (if there are any).
      '''
      
      defaults = {}
      defaults[Configuration.__UPDATE_SERIES] = self.update_series_b
      defaults[Configuration.__UPDATE_NUMBER] = self.update_number_b
      defaults[Configuration.__UPDATE_MONTH] = self.update_month_b
      defaults[Configuration.__UPDATE_TITLE] = self.update_title_b
      defaults[Configuration.__UPDATE_STORYARC] = self.update_storyarc_b
      defaults[Configuration.__UPDATE_ALT_SERIES] = self.update_alt_series_b
      defaults[Configuration.__UPDATE_WRITER] = self.update_writer_b
      defaults[Configuration.__UPDATE_PENCILLER] = self.update_penciller_b
      defaults[Configuration.__UPDATE_INKER] = self.update_inker_b
      defaults[Configuration.__UPDATE_COVER_ARTIST] = self.update_cover_artist_b
      defaults[Configuration.__UPDATE_COLORIST] = self.update_colorist_b
      defaults[Configuration.__UPDATE_LETTERER] = self.update_letterer_b
      defaults[Configuration.__UPDATE_EDITOR] = self.update_editor_b
      defaults[Configuration.__UPDATE_SUMMARY] = self.update_summary_b
      defaults[Configuration.__UPDATE_YEAR] = self.update_year_b
      defaults[Configuration.__UPDATE_IMPRINT] = self.update_imprint_b
      defaults[Configuration.__UPDATE_PUBLISHER] = self.update_publisher_b
      defaults[Configuration.__UPDATE_VOLUME] = self.update_volume_b
      defaults[Configuration.__UPDATE_CHARACTERS] = self.update_characters_b
      defaults[Configuration.__UPDATE_TEAMS] = self.update_teams_b
      defaults[Configuration.__UPDATE_LOCATIONS] = self.update_locations_b
      defaults[Configuration.__UPDATE_WEBPAGE] = self.update_webpage_b
      defaults[Configuration.__UPDATE_RATING] = self.update_rating_b
      
      defaults[Configuration.__OVERWRITE_EXISTING] = self.ow_existing_b
      defaults[Configuration.__CONVERT_IMPRINTS] = self.convert_imprints_b
      defaults[Configuration.__SPECIFY_SERIES] = self.specify_series_b
      defaults[Configuration.__IGNORE_BLANKS] = self.ignore_blanks_b
      defaults[Configuration.__SHOW_COVERS] = self.show_covers_b
      defaults[Configuration.__DOWNLOAD_THUMBS] = self.download_thumbs_b
      defaults[Configuration.__PRESERVE_THUMBS] = self.preserve_thumbs_b
      defaults[Configuration.__SCRAPE_IN_GROUPS] = self.scrape_in_groups_b
      defaults[Configuration.__FAST_RESCRAPE] = self.fast_rescrape_b
      defaults[Configuration.__RESCRAPE_NOTES] = self.rescrape_notes_b
      defaults[Configuration.__RESCRAPE_TAGS] = self.rescrape_tags_b
      defaults[Configuration.__WELCOME_DIALOG] = self.welcome_dialog_b
      defaults[Configuration.__SUMMARY_DIALOG] = self.summary_dialog_b
   
      persist_map(defaults, Resources.SETTINGS_FILE)
      persist_string(self.advanced_settings_s, Resources.ADVANCED_FILE)
   
   
   #===========================================================================
   def __ne__(self, other):
      ''' Implements "negative equality" for standard python objects. '''
      
      return not self.__eq__(other)

   
   #===========================================================================
   def __eq__(self, other):
      ''' Implements "equality" for standard python objects. '''
      
      return \
      self.ow_existing_b == other.ow_existing_b and \
      self.ignore_blanks_b == other.ignore_blanks_b and \
      self.convert_imprints_b == other.convert_imprints_b and \
      self.specify_series_b == other.specify_series_b and \
      self.show_covers_b == other.show_covers_b and \
      self.download_thumbs_b == other.download_thumbs_b and \
      self.preserve_thumbs_b == other.preserve_thumbs_b and \
      self.scrape_in_groups_b == other.scrape_in_groups_b and \
      self.fast_rescrape_b == other.fast_rescrape_b and \
      self.rescrape_notes_b == other.rescrape_notes_b and \
      self.rescrape_tags_b == other.rescrape_tags_b and \
      self.welcome_dialog_b == other.welcome_dialog_b and \
      self.summary_dialog_b == other.summary_dialog_b and \
                                                        \
      self.update_series_b == other.update_series_b and \
      self.update_number_b == other.update_number_b and \
      self.update_month_b == other.update_month_b and \
      self.update_title_b == other.update_title_b and \
      self.update_storyarc_b == other.update_storyarc_b and \
      self.update_alt_series_b == other.update_alt_series_b and \
      self.update_writer_b == other.update_writer_b and \
      self.update_penciller_b == other.update_penciller_b and \
      self.update_inker_b == other.update_inker_b and \
      self.update_cover_artist_b == other.update_cover_artist_b and \
      self.update_colorist_b == other.update_colorist_b and \
      self.update_letterer_b == other.update_letterer_b and \
      self.update_editor_b == other.update_editor_b and \
      self.update_summary_b == other.update_summary_b and \
      self.update_imprint_b == other.update_imprint_b and \
      self.update_year_b == other.update_year_b and \
      self.update_publisher_b == other.update_publisher_b and \
      self.update_volume_b == other.update_volume_b and \
      self.update_characters_b == other.update_characters_b and \
      self.update_teams_b == other.update_teams_b and \
      self.update_locations_b == other.update_locations_b and \
      self.update_webpage_b == other.update_webpage_b and \
      self.update_rating_b == other.update_rating_b
   
   
   #===========================================================================
   def __str__(self):
      ''' Implements "to string" functionality for standard python objects. '''
      
      def x(x):
         return 'X' if x else ' '
             
      # display details about regular settings (which are all booleans)
      retval = \
      "--------------------------------------------------------------------\n"+\
      "[{0}] Series".format(x(self.update_series_b)).ljust(20) +\
      "[{0}] Number".format(x(self.update_number_b)).ljust(20) +\
      "[{0}] Month".format(x(self.update_month_b)).ljust(20) +\
      "\n" + \
      "[{0}] Title".format(x(self.update_title_b)).ljust(20) +\
      "[{0}] StoryArc".format(x(self.update_storyarc_b)).ljust(20) +\
      "[{0}] Alt Series".format(x(self.update_alt_series_b)).ljust(20) +\
      "\n" + \
      "[{0}] Writer".format(x(self.update_writer_b)).ljust(20) +\
      "[{0}] Penciller".format(x(self.update_penciller_b)).ljust(20) +\
      "[{0}] Inker".format(x(self.update_inker_b)).ljust(20) +\
      "\n" + \
      "[{0}] Cover Art".format(x(self.update_cover_artist_b)).ljust(20) +\
      "[{0}] Colorist".format(x(self.update_colorist_b)).ljust(20) +\
      "[{0}] Letterer".format(x(self.update_letterer_b)).ljust(20) +\
      "\n" + \
      "[{0}] Editor".format(x(self.update_editor_b)).ljust(20) +\
      "[{0}] Summary".format(x(self.update_summary_b)).ljust(20) +\
      "[{0}] Imprint".format(x(self.update_imprint_b)).ljust(20) +\
      "\n" + \
      "[{0}] Year".format(x(self.update_year_b)).ljust(20) +\
      "[{0}] Publisher".format(x(self.update_publisher_b)).ljust(20) +\
      "[{0}] Volume".format(x(self.update_volume_b)).ljust(20) +\
      "\n" + \
      "[{0}] Characters".format(x(self.update_characters_b)).ljust(20) +\
      "[{0}] Teams".format(x(self.update_teams_b)).ljust(20) +\
      "[{0}] Locations".format(x(self.update_locations_b)).ljust(20) +\
      "\n" + \
      "[{0}] Webpage".format(x(self.update_webpage_b)).ljust(20) +\
      "[{0}] Rating".format(x(self.update_rating_b)).ljust(20) +\
      "\n" +\
      "-------------------------------------------------------------------\n"+\
      "[{0}] Overwrite Existing".format(x(self.ow_existing_b)).ljust(30)+\
      "[{0}] Ignore Blanks".format(x(self.ignore_blanks_b)).ljust(30) +\
      "\n" + \
      "[{0}] Convert Imprints".format(x(self.convert_imprints_b)).ljust(30) +\
      "[{0}] Specify Series".format(x(self.specify_series_b)).ljust(30)+\
      "\n" + \
      "[{0}] Download Thumbs".format(x(self.download_thumbs_b)).ljust(30) +\
      "[{0}] Preserve Thumbs".format(x(self.preserve_thumbs_b)).ljust(30)+\
      "\n" + \
      "[{0}] Scrape in Groups".format(x(self.scrape_in_groups_b)).ljust(30)+\
      "[{0}] Rescraping: Notes".format(x(self.rescrape_notes_b)).ljust(30)+\
      "\n" + \
      "[{0}] Fast Rescrape".format(x(self.fast_rescrape_b)).ljust(30)+\
      "[{0}] Rescraping: Tags".format(x(self.rescrape_tags_b)).ljust(30) +\
      "\n" + \
      "[{0}] Welcome Dialog".format(x(self.welcome_dialog_b)).ljust(30)+\
      "[{0}] Summary Dialog".format(x(self.summary_dialog_b)).ljust(30)+\
      "\n" + \
      "[{0}] Show Covers".format(x(self.show_covers_b)).ljust(30)+\
      "\n" + \
      "-------------------------------------------------------------------"

      # display details about any advanced settings that may be in effect      
      lines_sl = []
      c = Configuration
      if self.filtered_publishers_sl != c.__DEFAULT_FILTERED_PUBLISHERS:
         for publisher_s in self.filtered_publishers_sl:
            lines_sl.append("Ignore all series published by '{0}'\n"\
               .format(publisher_s))
      if self.filtered_before_year_n != c.__DEFAULT_FILTER_BEFORE_YEAR:
         lines_sl.append("Ignore all series that start before {0}.\n"\
             .format(self.filtered_before_year_n))
      if self.filtered_after_year_n != c.__DEFAULT_FILTER_AFTER_YEAR:
         lines_sl.append("Ignore all series that start after {0}.\n"\
            .format(self.filtered_after_year_n))
      if self.never_filter_threshold_n != c.__DEFAULT_NEVER_FILTER_THRESHOLD:
         lines_sl.append("Don't ignore series that have {0} or more issues.\n"\
            .format(self.never_filter_threshold_n))
      if self.alt_search_regex_s != c.__DEFAULT_ALT_SEARCH_REGEX:
         lines_sl.append("Alternate Filename Search Regex:\n   {0}\n"\
            .format(self.alt_search_regex_s))
               
      advanced_lines_s = "".join(lines_sl)
      if advanced_lines_s:
         retval += "\n" + advanced_lines_s + \
         "-------------------------------------------------------------------"
   
      return retval   