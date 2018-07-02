'''
This module contains the Resources class.
'''

import sys
import clr
clr.AddReference('System.Drawing')
from System.Drawing import Image
clr.AddReference('System')
from System import Environment
from System.IO import Directory, File

#==============================================================================
class Resources(object):
   '''
    This class provides static access to "constants" for all the non-code
    resources that this app uses.  (i.e. pathnames and locations, mostly.)
    ''' 
   
   # the location of our scraper 'cache' files. 
   LOCAL_CACHE_DIRECTORY = None
   
   # the location of the app's settings file.
   SETTINGS_FILE = None
   
   # the location of the app's advanced settings file.
   ADVANCED_FILE = None
   
   # the location of the app's geometry settings file.
   GEOMETRY_FILE = None
   
   # the location of the app's chosen series file.
   SERIES_FILE = None
   
   # the location of the app's localization default strings file
   I18N_DEFAULTS_FILE = None
   
   # the XML file (in each language pack) for our localized strings
   I18N_XML_ENTRY = 'Script.ComicVineScraper.xml'
   
   # the apps version number/string
   SCRIPT_VERSION = "!DEV!"  # do NOT change! build process relies on this!
   if SCRIPT_VERSION.startswith("!"):
      SCRIPT_VERSION = "0.0.0"
   
   # the full name of the app, including version string
   SCRIPT_FULLNAME = 'Comic Vine Scraper - v' + SCRIPT_VERSION

   #==============================================================================
   @classmethod 
   def initialize(cls):
      '''
      Initialize the Resources class.  This method MUST be called exactly once
      before you try to make use of this class in any other way. 
      '''
      # this code runs before we have our proper error handling installed, so 
      # wrap it in a try-except block so at least we have SOME error handling
      try:
         cls.__initialize()
      except:
         print sys.exc_info()[1]
         sys.exit();   

   #===========================================================================         
   @classmethod
   def createComicVineLogo(cls):
      '''
      Obtains a brand new Image object (don't forget to Dispose() it!) that 
      displays the ComicVine logo.
      '''
      dir = __file__[:-(len(__name__) + len('.py'))]
      return Image.FromFile( dir + 'comicvinelogo.png')
   
   #===========================================================================         
   @classmethod
   def createArrowIcon(cls, left=True, full=True):
      '''
      Obtains a brand new Image object (don't forget to Dispose() it!) that 
      displays either a left or right pointing arrow.
      '''
      dir = __file__[:-(len(__name__) + len('.py'))]
      if full:
         return Image.FromFile( dir + 'fullleftarrow.png') if left \
            else Image.FromFile( dir + 'fullrightarrow.png')
      else: 
         return Image.FromFile( dir + 'leftarrow.png') if left \
            else Image.FromFile( dir + 'rightarrow.png') 
   
  
   
   #==============================================================================
   @classmethod
   def __initialize(cls):

      # get the basic locations that the other locations build on      
      script_dir = Directory.GetParent(__file__).FullName
      profile_dir = Environment.GetFolderPath(
         Environment.SpecialFolder.ApplicationData) + \
         r"\Comic Vine Scraper"
      
      # set the standard locations for settings files 
      cls.SETTINGS_FILE = profile_dir + r'\settings.dat'
      cls.ADVANCED_FILE = profile_dir + r'\advanced.dat'
      cls.GEOMETRY_FILE = profile_dir + r'\geometry.dat'
      cls.SERIES_FILE = profile_dir + r'\series.dat'
      cls.LOCAL_CACHE_DIRECTORY = profile_dir + r'\localCache'
      cls.I18N_DEFAULTS_FILE = script_dir + r"\en.zip"
      
      # do a special trick to things run from within the IDE,
      # where certain files like 'en.zip' are in different locations
      ide_i18n_file = Directory.GetParent( 
         Directory.GetParent( script_dir).FullName ).FullName + \
         r'\src\resources\languages\en.zip'
      if not File.Exists(cls.I18N_DEFAULTS_FILE) \
            and File.Exists( ide_i18n_file ):
         cls.I18N_DEFAULTS_FILE = ide_i18n_file

      # import settings from legacy location, if needed.
      # ensure profile directory exists.
      cls.__import_legacy_settings(script_dir, profile_dir)         
      if not File.Exists(profile_dir):
         Directory.CreateDirectory(profile_dir)
         

   #==============================================================================
   @classmethod
   def __import_legacy_settings(cls, legacy_dir, profile_dir):
      '''
      See if there are any legacy settings at the given legacy location, and 
      copy them to the given profile location, if that location doesn't exist.
      '''
      if not File.Exists( cls.SETTINGS_FILE ):
         Directory.CreateDirectory(profile_dir)
         settings_file = legacy_dir + r'\settings.dat'
         advanced_file = legacy_dir + r'\advanced.dat'
         geometry_file = legacy_dir + r'\geometry.dat'
         series_file = legacy_dir + r'\series.dat'
         if File.Exists(settings_file):
            File.Copy(settings_file, cls.SETTINGS_FILE, False )
         if File.Exists(advanced_file):
            File.Copy(advanced_file, cls.ADVANCED_FILE, False )
         if File.Exists(geometry_file):
            File.Copy(geometry_file, cls.GEOMETRY_FILE, False )
         if File.Exists(series_file):
            File.Copy(series_file, cls.SERIES_FILE, False )
