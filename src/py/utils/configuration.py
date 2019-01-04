'''
This module contoins the Configuration object.

@author: Cory Banack
'''

import re
import clr
from resources import Resources
from utils import persist_map, load_map, persist_string, load_string
import utils

clr.AddReference('System')
from System.IO import File

#==============================================================================
class Configuration(object):
   '''
   This class contains the configuration details for the scraper, including
   methods for reading and writing those details to the filesystem.
   '''
   
   # map names for basic settings (checkboxes, etc)
   __API_KEY = 'apiKey'   
   __UPDATE_SERIES = 'updateSeries'
   __UPDATE_NUMBER = 'updateNumber'
   __UPDATE_RELEASED = 'updateReleased'
   __UPDATE_PUBLISHED = 'updatePublished'
   __UPDATE_TITLE = 'updateTitle'
   __UPDATE_CROSSOVERS = 'updateCrossovers'
   __UPDATE_WRITER = 'updateWriter'
   __UPDATE_PENCILLER = 'updatePenciller'
   __UPDATE_INKER = 'updateInker'
   __UPDATE_COVER_ARTIST = 'updateCoverArtist'
   __UPDATE_COLORIST = 'updateColorist'
   __UPDATE_LETTERER = 'updateLetterer'
   __UPDATE_EDITOR = 'updateEditor'
   __UPDATE_SUMMARY = 'updateSummary'
   __UPDATE_IMPRINT = 'updateImprint'
   __UPDATE_PUBLISHER = 'updatePublisher'
   __UPDATE_VOLUME = 'updateVolume'
   __UPDATE_CHARACTERS = 'updateCharacters'
   __UPDATE_TEAMS = 'updateTeams'
   __UPDATE_LOCATIONS = 'updateLocations'
   __UPDATE_WEBPAGE = 'updateWebpage'
   __OVERWRITE_EXISTING = 'overwriteExisting'
   __IGNORE_BLANKS = 'ignoreBlanks'
   __CONVERT_IMPRINTS = 'convertImprints'
   __AUTOCHOOSE_SERIES = 'autochooseSeries'
   __CONFIRM_ISSUE = 'confirmIssue'
   __DOWNLOAD_THUMBS = 'downloadThumbs'
   __PRESERVE_THUMBS = 'preserveThumbs'
   __FAST_RESCRAPE = 'fastRescrape'
   __RESCRAPE_NOTES = 'updateNotes'
   __RESCRAPE_TAGS = 'updateTags'
   __SUMMARY_DIALOG = 'summaryDialog'
   
   # default values for advanced settings
   __DEFAULT_IGNORED_BEFORE_YEAR = 0
   __DEFAULT_IGNORED_AFTER_YEAR = 9999999
   __DEFAULT_NEVER_IGNORE_THRESHOLD = 9999999
   __DEFAULT_UPDATE_RATING = False
   __DEFAULT_SHOW_COVERS = True
   __DEFAULT_WELCOME_DIALOG = True 
   __DEFAULT_ALT_SEARCH_REGEX = "" 
   __DEFAULT_IGNORE_FOLDERS = False
   __DEFAULT_FORCE_SERIES_ART = False
   __DEFAULT_NOTE_SCRAPE_DATE = False
   __DEFAULT_SCRAPE_DELAY = 1
   __DEFAULT_MAX_SEARCH_RESULTS = 100

  
   #=========================================================================== 
   def __init__(self):
      ''' Initializes a new Configuration object with default settings '''
      self.api_key_s = "" # the api key to use when contacting comicvine
      self.ow_existing_b = True # scraper should overwrite existing metadata?
      self.ignore_blanks_b = False  # ...unless the new metada is blank?
      self.convert_imprints_b = True # convert imprints to parent publishers
      self.autochoose_series_b = False # auto pick series by matching covers
      self.confirm_issue_b = False # confirm each issue choice before scraper
      self.download_thumbs_b = True # download thumbnails for fileless comics
      self.preserve_thumbs_b = True # ...except when they already have thumbs
      self.scrape_in_groups_b = True # group comics by series when scraping
      self.fast_rescrape_b = True # use previous scrape choice when available
      self.rescrape_notes_b = True # store prev scrape choice in notes field
      self.rescrape_tags_b = False # store prev scrape choice in tags field
      self.summary_dialog_b = True # show summary dialog after scrape finishes

      self.update_series_b = True # scrape comic's series metadata
      self.update_number_b = True # scrape comic's issue number metadata
      self.update_published_b = True # scrape comic's published year metadata
      self.update_released_b = True # scrape comic's released year metadata
      self.update_title_b = True # scrape comic's issue title metadata
      self.update_crossovers_b = True # scrape comic's crossovers metadata
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
            
      # this is a general purpose map for saving ad-hoc data in a highly 
      # flexible, unstructured fashion.  this data only lasts as long as this
      # Configuration object is around, and it DOES NOT get saved or reloaded.
      self.session_data_map = {}
      
      # the contents of the advanced settings file (and the values parsed out
      # of it.)  this advanced settings string value gets persisted and reloaded
      # when we save and load a Configuration object, but the parsed values are
      # tied to the string, and only change when it does.
      self.__advanced_settings_s = None
      
      self.__ignored_publishers_sl = None # ignore publishers out of searches
      self.__ignored_searchterms_sl = None # ignore terms when searching
      self.__publisher_aliases_sm = None # map of publisher names to new names
      self.__user_imprints_sm = None # map of publisher names to imprints
      self.__ignored_before_year_n = None # filter series started before year
      self.__ignored_after_year_n = None # filter series started after year
      self.__never_ignore_threshold_n = None # min issues before we don't filter
      self.__update_rating_b = None # whether to scrape the "rating" metadata
      self.__show_covers_b = None # whether to display issue covers by default
      self.__welcome_dialog_b = None # whether to display the welcome dialog
      self.__alt_search_regex_s = None # alternate filename parsing regex
      self.__ignore_folders_b = None # use folders w/ grouping issue into series
      self.__force_series_art_b = None # series dialog always shows series art?
      self.__note_scrape_date_b = None # put date when scraping the Notes field?
      self.__scrape_delay_n = None # num of seconds to wait between each scrape
      self.__max_search_results_n = None # max # of series to return on search
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
      self.__ignored_publishers_sl = set()
      self.__ignored_searchterms_sl = set()
      self.__publisher_aliases_sm = dict()
      self.__user_imprints_sm = dict()
      self.__ignored_before_year_n = c.__DEFAULT_IGNORED_BEFORE_YEAR
      self.__ignored_after_year_n = c.__DEFAULT_IGNORED_AFTER_YEAR
      self.__never_ignore_threshold_n = c.__DEFAULT_NEVER_IGNORE_THRESHOLD
      self.__update_rating_b = c.__DEFAULT_UPDATE_RATING
      self.__show_covers_b = c.__DEFAULT_SHOW_COVERS
      self.__welcome_dialog_b = c.__DEFAULT_WELCOME_DIALOG
      self.__alt_search_regex_s = c.__DEFAULT_ALT_SEARCH_REGEX
      self.__ignore_folders_b = c.__DEFAULT_IGNORE_FOLDERS
      self.__force_series_art_b = c.__DEFAULT_FORCE_SERIES_ART
      self.__note_scrape_date_b = c.__DEFAULT_NOTE_SCRAPE_DATE
      self.__scrape_delay_n = c.__DEFAULT_SCRAPE_DELAY
      self.__max_search_results_n = c.__DEFAULT_MAX_SEARCH_RESULTS

      
      # 2. scan through the string looking at each line for advanced settings
      lines_s = [ x.strip() for x in self.__advanced_settings_s.split("\n") \
                 if x.strip() ]
      pattern_s = r"^(?i){0}\s*=\s*['\"]?(.+?)['\"]?$"
      for line_s in lines_s:
         # 2a. parse the "IGNORE_PUBLISHER=XXXX" line
         match = re.match(pattern_s.format("IGNORE_PUBLISHER"), line_s) 
         if match: 
            self.__ignored_publishers_sl.add(match.group(1).lower().strip())
            
         # 2b. parse the "IGNORE_SEARCHTERM=XXXX" line
         match = re.match(pattern_s.format("IGNORE_SEARCHTERM"), line_s) 
         if match:
            term = match.group(1).lower().strip()
            if term and term.isalnum(): # only alphanumeric terms allowed!
               self.__ignored_searchterms_sl.add(term)
            
         # 2c. parse the "IGNORE_BEFORE_YEAR=XXXX" line
         match = re.match(pattern_s.format("IGNORE_BEFORE_YEAR"), line_s)
         if match and utils.is_number(match.group(1)):
            self.__ignored_before_year_n = int(float(match.group(1)))
            
         # 2d. parse the "IGNORE_AFTER_YEAR=XXXX" line
         match = re.match(pattern_s.format("IGNORE_AFTER_YEAR"), line_s)
         if match and utils.is_number(match.group(1)):
            self.__ignored_after_year_n = int(float(match.group(1)))
            
         # 2e. parse the "NEVER_IGNORE_THRESHOLD=XXXX" line
         match = re.match(pattern_s.format("NEVER_IGNORE_THRESHOLD"), line_s)
         if match and utils.is_number(match.group(1)):
            self.__never_ignore_threshold_n = int(float(match.group(1)))
            
         # 2f. parse the "SCRAPE_RATING=XXXX" line
         match = re.match(pattern_s.format("SCRAPE_RATING"), line_s)
         if match:
            self.__update_rating_b = match.group(1).strip().lower()=="true"
            
         # 2g. parse the "SHOW_COVERS=XXXX" line
         match = re.match(pattern_s.format("SHOW_COVERS"), line_s)
         if match:
            self.__show_covers_b = match.group(1).strip().lower()=="true"
            
         # 2h. parse the "WELCOME_DIALOG=XXXX" line
         match = re.match(pattern_s.format("WELCOME_DIALOG"), line_s)
         if match:
            self.__welcome_dialog_b = match.group(1).strip().lower()=="true"
            
         # 2i. parse the "ALT_SEARCH_REGEX=XXXX" line
         match = re.match(pattern_s.format("ALT_SEARCH_REGEX"), line_s)
         if match:
            try:
               re.compile(match.group(1))
               self.__alt_search_regex_s = match.group(1)
            except:
               pass # nope, looks like it's not a parsable regex
         
         # 2j. parse the "IGNORE_FOLDERS=XXXX" line
         match = re.match(pattern_s.format("IGNORE_FOLDERS"), line_s)
         if match:
            self.__ignore_folders_b = match.group(1).strip().lower()=="true"
            
         # 2k. parse the "FORCE_SERIES_ART=XXXX" line
         match = re.match(pattern_s.format("FORCE_SERIES_ART"), line_s)
         if match:
            self.__force_series_art_b = match.group(1).strip().lower()=="true"
            
         # 2l. parse the "NOTE_SCRAPE_DATE=XXXX" line
         match = re.match(pattern_s.format("NOTE_SCRAPE_DATE"), line_s)
         if match:
            self.__note_scrape_date_b = match.group(1).strip().lower()=="true"
            
         # 2m. parse the "PUBLISHER_ALIAS=XXXX-->YYYY" line
         match = re.match(pattern_s.format("PUBLISHER_ALIAS"), line_s)
         if match:
            match = re.match(r"^\s*(\S.*?)\s*[-=]+>\s*(\S.*?)$", match.group(1))
            if match:
               pub, alias = match.group(1).strip(" '\"").lower(), \
                  match.group(2).strip(" '\"")
               if pub and alias and len(alias) <= 50: 
                  self.__publisher_aliases_sm[pub] = alias
                  
         # 2n. parse the "IMPRINT=IIII-->PPPP" line
         match = re.match(pattern_s.format("IMPRINT"), line_s)
         if match:
            match = re.match(r"^\s*(\S.*?)\s*[-=]+>\s*(\S.*?)$", match.group(1))
            if match:
               imprint_s = match.group(1).lower().strip(" '\"")
               publisher_s = match.group(2).strip(" '\"")
               if publisher_s and imprint_s and \
                     len(publisher_s) <= 50 and len(imprint_s) <= 50:  
                  self.__user_imprints_sm[imprint_s] = publisher_s
         
         # 2o. parse the "SCRAPE_DELAY=XXXX" line
         match = re.match(pattern_s.format("SCRAPE_DELAY"), line_s)
         if match and utils.is_number(match.group(1)):
            self.__scrape_delay_n = \
               min(3600, max(2, int(float(match.group(1)))))

         # 2p. parse the "MAX_SEARCH_RESULTS=XXXX" line
         match = re.match(pattern_s.format("MAX_SEARCH_RESULTS"), line_s)
         if match and utils.is_number(match.group(1)):
            self.__max_search_results_n = \
               min(5000, max( 10, int(float(match.group(1))) ) )

   advanced_settings_s = property( lambda self : self.__advanced_settings_s, 
      __set_advanced_settings_s, __set_advanced_settings_s,
      "The advanced settings string for this Configuration. Not None." )
   
   ignored_publishers_sl = property( 
      lambda self : list(self.__ignored_publishers_sl), None, None,
      "List of publisher names to filter out of series searches. Not None.")
   
   ignored_searchterms_sl = property( 
      lambda self : list(self.__ignored_searchterms_sl), None, None,
      "List of search terms to filter out of series searches. Not None.")
   
   publisher_aliases_sm = property( 
      lambda self : dict(self.__publisher_aliases_sm), None, None,
      "Dict mapping publisher names (lower case) to user's aliases. Not None.")
   
   user_imprints_sm = property( 
      lambda self : dict(self.__user_imprints_sm), None, None,
      "Dict mapping user's imprint names (lower case) to publishers. Not None.")
   
   ignored_before_year_n = property( 
      lambda self : self.__ignored_before_year_n, None, None,
      "Filter out searched series first published before this year. Not None.")
   
   ignored_after_year_n = property( 
      lambda self : self.__ignored_after_year_n, None, None,
      "Filter out searched series first published after this year. Not None.")
   
   never_ignore_threshold_n = property( 
      lambda self : self.__never_ignore_threshold_n, None, None,
      "Never filter series that have this many issues, or more. Not None.")
   
   update_rating_b = property( 
      lambda self : self.__update_rating_b, None, None,
      "Attempt to scrape (very slow) rating metadata for each issue. Not None.")
   
   show_covers_b = property( 
      lambda self : self.__show_covers_b, None, None,
      "Whether or not to show issue covers by default.  Not None.")
   
   welcome_dialog_b = property( 
      lambda self : self.__welcome_dialog_b, None, None,
      "Whether or not to show the Welcome Dialog when scraping. Not None.")
   
   alt_search_regex_s = property( 
      lambda self : self.__alt_search_regex_s, None, None,
      "Alternate regex for parsing issue/series/etc from filename. Not None.")
   
   ignore_folders_b = property( 
      lambda self : self.__ignore_folders_b, None, None,
      "Whether to consider folders when grouping issues into series. Not None.")
   
   force_series_art_b = property( 
      lambda self : self.__force_series_art_b, None, None,
      "Whether or not to force the series dialog to always display series art.")
   
   note_scrape_date_b = property( 
      lambda self : self.__note_scrape_date_b, None, None,
      "Whether or not to include the date when scraping Notes.  Not None.")
   
   scrape_delay_n = property( 
      lambda self : self.__scrape_delay_n, None, None,
      "How long to wait (in seconds) between each scrape.  Not None.")

   max_search_results_n = property( 
      lambda self : self.__max_search_results_n, None, None,
      "Maximum # of series search results to return for a query. Not None.")
   
   
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
         
      # any settings that the serialized dict happens to contain
      if Configuration.__API_KEY in loaded:
         self.api_key_s = loaded[Configuration.__API_KEY]
         
      if Configuration.__UPDATE_SERIES in loaded:
         self.update_series_b = loaded[Configuration.__UPDATE_SERIES]
      
      if Configuration.__UPDATE_NUMBER in loaded:
         self.update_number_b = loaded[Configuration.__UPDATE_NUMBER]
         
      if Configuration.__UPDATE_PUBLISHED in loaded:
         self.update_published_b = loaded[Configuration.__UPDATE_PUBLISHED]
         
      if Configuration.__UPDATE_RELEASED in loaded:
         self.update_released_b = loaded[Configuration.__UPDATE_RELEASED]
         
      if Configuration.__UPDATE_TITLE in loaded:
         self.update_title_b = loaded[Configuration.__UPDATE_TITLE]
         
      if Configuration.__UPDATE_CROSSOVERS in loaded:
         self.update_crossovers_b = loaded[Configuration.__UPDATE_CROSSOVERS]
         
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
         
      if Configuration.__OVERWRITE_EXISTING in loaded:
         self.ow_existing_b = loaded[Configuration.__OVERWRITE_EXISTING]

      if Configuration.__IGNORE_BLANKS in loaded:
         self.ignore_blanks_b = loaded[Configuration.__IGNORE_BLANKS]

      if Configuration.__CONVERT_IMPRINTS in loaded:
         self.convert_imprints_b = loaded[Configuration.__CONVERT_IMPRINTS]

      if Configuration.__AUTOCHOOSE_SERIES in loaded:
         self.autochoose_series_b = loaded[Configuration.__AUTOCHOOSE_SERIES]
         
      if Configuration.__CONFIRM_ISSUE in loaded:
         self.confirm_issue_b = loaded[Configuration.__CONFIRM_ISSUE]

      if Configuration.__DOWNLOAD_THUMBS in loaded:
         self.download_thumbs_b=loaded[Configuration.__DOWNLOAD_THUMBS]
         
      if Configuration.__PRESERVE_THUMBS in loaded:
         self.preserve_thumbs_b=loaded[Configuration.__PRESERVE_THUMBS]
         
      if Configuration.__FAST_RESCRAPE in loaded:
         self.fast_rescrape_b=loaded[Configuration.__FAST_RESCRAPE]
         
      if Configuration.__RESCRAPE_NOTES in loaded:
         self.rescrape_notes_b = loaded[Configuration.__RESCRAPE_NOTES]
         
      if Configuration.__RESCRAPE_TAGS in loaded:
         self.rescrape_tags_b = loaded[Configuration.__RESCRAPE_TAGS]
         
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
      defaults[Configuration.__API_KEY] = self.api_key_s
      defaults[Configuration.__UPDATE_SERIES] = self.update_series_b
      defaults[Configuration.__UPDATE_NUMBER] = self.update_number_b
      defaults[Configuration.__UPDATE_RELEASED] = self.update_released_b
      defaults[Configuration.__UPDATE_PUBLISHED] = self.update_published_b
      defaults[Configuration.__UPDATE_TITLE] = self.update_title_b
      defaults[Configuration.__UPDATE_CROSSOVERS] = self.update_crossovers_b
      defaults[Configuration.__UPDATE_WRITER] = self.update_writer_b
      defaults[Configuration.__UPDATE_PENCILLER] = self.update_penciller_b
      defaults[Configuration.__UPDATE_INKER] = self.update_inker_b
      defaults[Configuration.__UPDATE_COVER_ARTIST] = self.update_cover_artist_b
      defaults[Configuration.__UPDATE_COLORIST] = self.update_colorist_b
      defaults[Configuration.__UPDATE_LETTERER] = self.update_letterer_b
      defaults[Configuration.__UPDATE_EDITOR] = self.update_editor_b
      defaults[Configuration.__UPDATE_SUMMARY] = self.update_summary_b
      defaults[Configuration.__UPDATE_IMPRINT] = self.update_imprint_b
      defaults[Configuration.__UPDATE_PUBLISHER] = self.update_publisher_b
      defaults[Configuration.__UPDATE_VOLUME] = self.update_volume_b
      defaults[Configuration.__UPDATE_CHARACTERS] = self.update_characters_b
      defaults[Configuration.__UPDATE_TEAMS] = self.update_teams_b
      defaults[Configuration.__UPDATE_LOCATIONS] = self.update_locations_b
      defaults[Configuration.__UPDATE_WEBPAGE] = self.update_webpage_b
      
      defaults[Configuration.__OVERWRITE_EXISTING] = self.ow_existing_b
      defaults[Configuration.__CONVERT_IMPRINTS] = self.convert_imprints_b
      defaults[Configuration.__AUTOCHOOSE_SERIES] = self.autochoose_series_b
      defaults[Configuration.__CONFIRM_ISSUE] = self.confirm_issue_b
      defaults[Configuration.__IGNORE_BLANKS] = self.ignore_blanks_b
      defaults[Configuration.__DOWNLOAD_THUMBS] = self.download_thumbs_b
      defaults[Configuration.__PRESERVE_THUMBS] = self.preserve_thumbs_b
      defaults[Configuration.__FAST_RESCRAPE] = self.fast_rescrape_b
      defaults[Configuration.__RESCRAPE_NOTES] = self.rescrape_notes_b
      defaults[Configuration.__RESCRAPE_TAGS] = self.rescrape_tags_b
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
      self.autochoose_series_b == other.autochoose_series_b and \
      self.confirm_issue_b == other.confirm_issue_b and \
      self.download_thumbs_b == other.download_thumbs_b and \
      self.preserve_thumbs_b == other.preserve_thumbs_b and \
      self.fast_rescrape_b == other.fast_rescrape_b and \
      self.rescrape_notes_b == other.rescrape_notes_b and \
      self.rescrape_tags_b == other.rescrape_tags_b and \
      self.summary_dialog_b == other.summary_dialog_b and \
                                                        \
      self.api_key_s == other.api_key_s and \
      self.update_series_b == other.update_series_b and \
      self.update_number_b == other.update_number_b and \
      self.update_published_b == other.update_published_b and \
      self.update_released_b == other.update_released_b and \
      self.update_title_b == other.update_title_b and \
      self.update_crossovers_b == other.update_crossovers_b and \
      self.update_writer_b == other.update_writer_b and \
      self.update_penciller_b == other.update_penciller_b and \
      self.update_inker_b == other.update_inker_b and \
      self.update_cover_artist_b == other.update_cover_artist_b and \
      self.update_colorist_b == other.update_colorist_b and \
      self.update_letterer_b == other.update_letterer_b and \
      self.update_editor_b == other.update_editor_b and \
      self.update_summary_b == other.update_summary_b and \
      self.update_imprint_b == other.update_imprint_b and \
      self.update_publisher_b == other.update_publisher_b and \
      self.update_volume_b == other.update_volume_b and \
      self.update_characters_b == other.update_characters_b and \
      self.update_teams_b == other.update_teams_b and \
      self.update_locations_b == other.update_locations_b and \
      self.update_webpage_b == other.update_webpage_b and \
      self.advanced_settings_s == other.advanced_settings_s
   
   
   #===========================================================================
   def __str__(self):
      ''' Implements "to string" functionality for standard python objects. '''
      
      def x(x):
         return 'X' if x else ' '
             
      # display details about regular settings (which are all booleans)
      retval = \
      "--------------------------------------------------------------------\n"+\
      "[{0}] Series".format(x(self.update_series_b)).ljust(20) +\
      "[{0}] Volume".format(x(self.update_volume_b)).ljust(20) +\
      "[{0}] Number".format(x(self.update_number_b)).ljust(20) +\
      "\n" + \
      "[{0}] Title".format(x(self.update_title_b)).ljust(20) +\
      "[{0}] Published".format(x(self.update_published_b)).ljust(20) +\
      "[{0}] Released".format(x(self.update_released_b)).ljust(20) +\
      "\n" + \
      "[{0}] Crossovers".format(x(self.update_crossovers_b)).ljust(20) +\
      "[{0}] Publisher".format(x(self.update_publisher_b)).ljust(20) +\
      "[{0}] Imprint".format(x(self.update_imprint_b)).ljust(20) +\
      "\n" + \
      "[{0}] Writer".format(x(self.update_writer_b)).ljust(20) +\
      "[{0}] Penciller".format(x(self.update_penciller_b)).ljust(20) +\
      "[{0}] Inker".format(x(self.update_inker_b)).ljust(20) +\
      "\n" + \
      "[{0}] Colorist".format(x(self.update_colorist_b)).ljust(20) +\
      "[{0}] Letterer".format(x(self.update_letterer_b)).ljust(20) +\
      "[{0}] Cover Art".format(x(self.update_cover_artist_b)).ljust(20) +\
      "\n" + \
      "[{0}] Editor".format(x(self.update_editor_b)).ljust(20) +\
      "[{0}] Summary".format(x(self.update_summary_b)).ljust(20) +\
      "[{0}] Characters".format(x(self.update_characters_b)).ljust(20) +\
      "\n" + \
      "[{0}] Teams".format(x(self.update_teams_b)).ljust(20) +\
      "[{0}] Locations".format(x(self.update_locations_b)).ljust(20) +\
      "[{0}] Webpage".format(x(self.update_webpage_b)).ljust(20) +\
      "\n" +\
      "-------------------------------------------------------------------\n"+\
      "[{0}] Overwrite Existing".format(x(self.ow_existing_b)).ljust(30)+\
      "[{0}] Ignore Blanks".format(x(self.ignore_blanks_b)).ljust(30) +\
      "\n" + \
      "[{0}] Convert Imprints".format(x(self.convert_imprints_b)).ljust(30) +\
      "[{0}] Autochoose Series".format(x(self.autochoose_series_b)).ljust(30)+\
      "\n" + \
      "[{0}] Download Thumbs".format(x(self.download_thumbs_b)).ljust(30) +\
      "[{0}] Preserve Thumbs".format(x(self.preserve_thumbs_b)).ljust(30)+\
      "\n" + \
      "[{0}] Confirm Issues".format(x(self.confirm_issue_b)).ljust(30)+\
      "[{0}] Rescraping: Notes".format(x(self.rescrape_notes_b)).ljust(30)+\
      "\n" + \
      "[{0}] Fast Rescrape".format(x(self.fast_rescrape_b)).ljust(30)+\
      "[{0}] Rescraping: Tags".format(x(self.rescrape_tags_b)).ljust(30) +\
      "\n" + \
      "[{0}] Summary Dialog".format(x(self.summary_dialog_b)).ljust(30)+\
      "\n" + \
      "-------------------------------------------------------------------"

      # display details about any advanced settings that may be in effect      
      lines_sl = []
      c = Configuration
      
      if self.ignored_before_year_n != c.__DEFAULT_IGNORED_BEFORE_YEAR:
         lines_sl.append("Ignore all series that start before {0}.\n"\
             .format(self.ignored_before_year_n))
      
      if self.ignored_after_year_n != c.__DEFAULT_IGNORED_AFTER_YEAR:
         lines_sl.append("Ignore all series that start after {0}.\n"\
            .format(self.ignored_after_year_n))
      
      if self.never_ignore_threshold_n != c.__DEFAULT_NEVER_IGNORE_THRESHOLD:
         lines_sl.append("Don't ignore series that have {0} or more issues.\n"\
            .format(self.never_ignore_threshold_n))
      
      if self.update_rating_b != c.__DEFAULT_UPDATE_RATING:
         lines_sl.append("Scrape Community Rating into each issue (slow).\n")
         
      if self.show_covers_b != c.__DEFAULT_SHOW_COVERS:
         lines_sl.append("Hide series and issue covers while scraping.\n")
         
      if self.welcome_dialog_b != c.__DEFAULT_WELCOME_DIALOG:
         lines_sl.append("Do not show the initial 'Welcome Dialog'.\n")
      
      if self.alt_search_regex_s != c.__DEFAULT_ALT_SEARCH_REGEX:
         lines_sl.append("Alternate Filename Search Regex:\n   {0}\n"\
            .format(self.alt_search_regex_s))
               
      if self.ignore_folders_b != c.__DEFAULT_IGNORE_FOLDERS:
         lines_sl.append("Ignore folders when grouping issues into series.\n")
         
      if self.force_series_art_b != c.__DEFAULT_FORCE_SERIES_ART:
         lines_sl.append("Always display Series Art in the Series dialog.\n")
         
      if self.note_scrape_date_b != c.__DEFAULT_NOTE_SCRAPE_DATE:
         lines_sl.append("Include scrape date when scraping to Notes.\n")
         
      if self.scrape_delay_n != c.__DEFAULT_SCRAPE_DELAY:
         lines_sl.append("Using scrape delay of {0} seconds.\n"\
            .format(self.scrape_delay_n))

      if self.max_search_results_n != c.__DEFAULT_MAX_SEARCH_RESULTS:
         lines_sl.append("Series search will return first {0} results.\n"\
            .format(self.max_search_results_n))
       
      for publisher_s in self.ignored_publishers_sl:
         lines_sl.append("Ignore all series published by '{0}'\n"\
            .format(publisher_s))
         
      for searchterm_s in self.ignored_searchterms_sl:
         lines_sl.append("Ignore search term '{0}'\n".format(searchterm_s))
         
      for imprint_s in self.user_imprints_sm.keys():
         lines_sl.append("Treat '{0}' as an imprint of '{1}'\n"\
            .format(imprint_s, self.user_imprints_sm[imprint_s]))
          
      for publisher_s in self.publisher_aliases_sm.keys():
         lines_sl.append("Replace publisher '{0}' with '{1}'\n"\
            .format(publisher_s, self.publisher_aliases_sm[publisher_s])) 
      

            
      advanced_lines_s = "".join(lines_sl) 
      if advanced_lines_s:
         retval += "\n" + advanced_lines_s + \
         "-------------------------------------------------------------------"
   
      return retval
  