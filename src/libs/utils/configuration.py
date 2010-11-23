'''
Created on Feb 17, 2010
@author: cbanack
'''
# corylow: comment and cleanup this file

import clr
import resources
from utils import persist_map, load_map

clr.AddReference('System')
from System.IO import File

class Configuration:
      
   __UPDATE_SERIES = 'updateSeries'
   __UPDATE_NUMBER = 'updateNumber'
   __UPDATE_MONTH = 'updateMonth'
   __UPDATE_TITLE = 'updateTitle'
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
   __SUMMARY_DIALOG = 'summaryDialog'
   
   def __init__(self):
      self.ow_existing_b = True
      self.ignore_blanks_b = False
      self.convert_imprints_b = True
      self.specify_series_b = False
      self.show_covers_b = True
      self.download_thumbs_b = True
      self.preserve_thumbs_b = False
      self.scrape_in_groups_b = True
      self.fast_rescrape_b = True
      self.rescrape_notes_b = True
      self.rescrape_tags_b = True
      self.summary_dialog_b = True

      self.update_series_b = True
      self.update_number_b = True
      self.update_month_b = True
      self.update_title_b = True
      self.update_alt_series_b = True
      self.update_writer_b = True
      self.update_penciller_b = True
      self.update_inker_b = True
      self.update_cover_artist_b = True
      self.update_colorist_b = True
      self.update_letterer_b = True
      self.update_editor_b = True
      self.update_summary_b = True
      self.update_imprint_b = True
      self.update_year_b = True
      self.update_publisher_b = True
      self.update_volume_b = True
      self.update_characters_b = True
      self.update_teams_b = True
      self.update_locations_b = True
      self.update_webpage_b = True
      self.update_rating_b = True
      
      # this is a general purpose map that is easily available to every part
      # of the application, and lasts only as long as the current scraping 
      # session.  it is an place for one part of the app to save ad-hoc,
      # session-based data for other parts of the program in a highly 
      # flexible, unstructured fashion.
      self.session_data_map = {}
      
      return self
   
   def load_defaults(self):

      # load the loaded dict out of the serialized file
      loaded = {}
      if File.Exists(resources.SETTINGS_FILE):
         loaded = load_map(resources.SETTINGS_FILE)
         
      # any settings that the serialized dict happens to contain, u
      if Configuration.__UPDATE_SERIES in loaded:
         self.update_series_b = loaded[Configuration.__UPDATE_SERIES]
      
      if Configuration.__UPDATE_NUMBER in loaded:
         self.update_number_b = loaded[Configuration.__UPDATE_NUMBER]
         
      if Configuration.__UPDATE_MONTH in loaded:
         self.update_month_b = loaded[Configuration.__UPDATE_MONTH]
         
      if Configuration.__UPDATE_TITLE in loaded:
         self.update_title_b = loaded[Configuration.__UPDATE_TITLE]
         
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
         
      if Configuration.__SUMMARY_DIALOG in loaded:
         self.summary_dialog_b = loaded[Configuration.__SUMMARY_DIALOG]
         
   
   def save_defaults(self):
      defaults = {}
      defaults[Configuration.__UPDATE_SERIES] = self.update_series_b
      defaults[Configuration.__UPDATE_NUMBER] = self.update_number_b
      defaults[Configuration.__UPDATE_MONTH] = self.update_month_b
      defaults[Configuration.__UPDATE_TITLE] = self.update_title_b
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
      defaults[Configuration.__SUMMARY_DIALOG] = self.summary_dialog_b
   
      persist_map(defaults, resources.SETTINGS_FILE)
   
   def __ne__(self, other):
      return not self.__eq__(other)
   
   def __eq__(self, other):
      
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
      self.summary_dialog_b == other.summary_dialog_b and \
                                                        \
      self.update_series_b == other.update_series_b and \
      self.update_number_b == other.update_number_b and \
      self.update_month_b == other.update_month_b and \
      self.update_title_b == other.update_title_b and \
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
   
   
   def __str__(self):
      
      def x(x):
         return 'X' if x else ' '
             
      return \
      "--------------------------------------------------------------------\n"+\
      "[{0}] Series".format(x(self.update_series_b)).ljust(20) +\
      "[{0}] Number".format(x(self.update_number_b)).ljust(20) +\
      "[{0}] Month".format(x(self.update_month_b)).ljust(20) +\
      "\n" + \
      "[{0}] Title".format(x(self.update_title_b)).ljust(20) +\
      "[{0}] Alt Series".format(x(self.update_alt_series_b)).ljust(20) +\
      "[{0}] Writer".format(x(self.update_writer_b)).ljust(20) +\
      "\n" + \
      "[{0}] Penciller".format(x(self.update_penciller_b)).ljust(20) +\
      "[{0}] Inker".format(x(self.update_inker_b)).ljust(20) +\
      "[{0}] Cover Art".format(x(self.update_cover_artist_b)).ljust(20) +\
      "\n" + \
      "[{0}] Colorist".format(x(self.update_colorist_b)).ljust(20) +\
      "[{0}] Letterer".format(x(self.update_letterer_b)).ljust(20) +\
      "[{0}] Editor".format(x(self.update_editor_b)).ljust(20) +\
      "\n" + \
      "[{0}] Summary".format(x(self.update_summary_b)).ljust(20) +\
      "[{0}] Imprint".format(x(self.update_imprint_b)).ljust(20) +\
      "[{0}] Year".format(x(self.update_year_b)).ljust(20) +\
      "\n" + \
      "[{0}] Publisher".format(x(self.update_publisher_b)).ljust(20) +\
      "[{0}] Volume".format(x(self.update_volume_b)).ljust(20) +\
      "[{0}] Characters".format(x(self.update_characters_b)).ljust(20) +\
      "\n" + \
      "[{0}] Teams".format(x(self.update_teams_b)).ljust(20) +\
      "[{0}] Locations".format(x(self.update_locations_b)).ljust(20) +\
      "[{0}] Webpage".format(x(self.update_webpage_b)).ljust(20) +\
      "\n" + \
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
      "[{0}] Show Covers".format(x(self.show_covers_b)).ljust(30)+\
      "[{0}] Summary Dialog".format(x(self.summary_dialog_b)).ljust(30)+\
      "\n" + \
      "-------------------------------------------------------------------"