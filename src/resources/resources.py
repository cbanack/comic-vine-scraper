'''
This module contains the Resources class.
'''

import clr, sys;
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
   def initialize(cls, external_profile):
      '''
      Initialize the Resources class.  This method MUST be called exactly once
      before you try to make use of this class in any other way.  The 
      'external_profile' argument determines whether we should save/load
      Resources (True means in Windows designated ApplicationData folder, False
      means alongside the script itself.)
      '''
      # this code runs before we have our proper error handling installed, so 
      # wrap it in a try-except block so at least we have SOME error handling
      try:
         cls.__initialize(external_profile)
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
   def createArrowIcon(cls, left=True):
      '''
      Obtains a brand new Image object (don't forget to Dispose() it!) that 
      displays either a left or right pointing arrow.
      '''
      dir = __file__[:-(len(__name__) + len('.py'))]
      return Image.FromFile( dir + 'leftarrow.png') if left \
         else Image.FromFile( dir + 'rightarrow.png') 
   
  
   
   #==============================================================================
   @classmethod
   def __initialize(cls, external_profile):
      ''' Implements the publicly accessible method of the same name. '''
      # get the basic locations that the other locations build on      
      script_dir = Directory.GetParent(__file__).FullName
      profile_dir = Environment.GetFolderPath(
         Environment.SpecialFolder.ApplicationData) + \
         r"\Comic Vine Scraper"
      if not File.Exists(profile_dir):
         Directory.CreateDirectory(profile_dir)
      
      if external_profile:
         # set the standard locations for when we are running in standalone
         # mode (including when running directly out of the IDE) 
         cls.SETTINGS_FILE = profile_dir + r'\settings.dat'
         cls.ADVANCED_FILE = profile_dir + r'\advanced.dat'
         cls.GEOMETRY_FILE = profile_dir + r'\geometry.dat'
         cls.SERIES_FILE = profile_dir + r'\series.dat'
         cls.I18N_DEFAULTS_FILE = script_dir + r"\en.zip"
         
         # do a special trick to make standalone mode run from within the IDE,
         # where certain files like 'en.zip' are in different locations
         ide_i18n_file = Directory.GetParent( 
            Directory.GetParent( script_dir).FullName ).FullName + \
            r'\src\resources\languages\en.zip'
         if not File.Exists(cls.I18N_DEFAULTS_FILE) \
               and File.Exists( ide_i18n_file ):
            cls.I18N_DEFAULTS_FILE = ide_i18n_file
             
      else:
         # set the standard locations for when we are running in plugin mode
         cls.SETTINGS_FILE = script_dir + r'\settings.dat'
         cls.ADVANCED_FILE = script_dir + r'\advanced.dat'
         cls.GEOMETRY_FILE = script_dir + r'\geometry.dat'
         cls.SERIES_FILE = script_dir + r'\series.dat'
         cls.I18N_DEFAULTS_FILE = script_dir + r'\en.zip'
         
      # coryhigh: START HERE 2: is the cache even needed anymore?
      # also, investigate making EVERYTHING run in "external_profile" mode.
      # (copy old prefs over cleanly, etc.)
      
      # the cache directory is the same regardless of which mode we're running
      cls.LOCAL_CACHE_DIRECTORY = profile_dir + r'\localCache'
      
      # see if there is a old cache available for us to import
      cls.__import_legacy_cache()
   
   #==============================================================================
   @classmethod
   def __import_legacy_cache(cls):
      '''
      This method looks to see if there is a) a cache available in the old
      location, and b) no cache available in the new location.  If so, it 
      moves the entire cache from the old location to the new one.
      '''
      roaming_dir = Environment.GetFolderPath(
         Environment.SpecialFolder.ApplicationData)
      legacy_dir = roaming_dir + \
         "\cYo\ComicRack\Scripts\Comic Vine Scraper\localCache"
      target_dir = cls.LOCAL_CACHE_DIRECTORY
      if Directory.Exists(legacy_dir) and not Directory.Exists(target_dir):
         Directory.Move(legacy_dir, target_dir)
