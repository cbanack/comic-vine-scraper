'''
This module contains the Resources class.
'''

import clr, sys;
clr.AddReference('System.Drawing')
from System.Drawing import Image
clr.AddReference('System')
from System import Environment
from System.IO import Directory

#==============================================================================
class Resources(object):
   '''
    This class provides static access to "constants" for all the non-code
    resources that this app uses.  (i.e. pathnames and locations, mostly.)
    ''' 
   
   # a boolean indicating whether we are running in standalone mode (true), or 
   # as a ComicRack plugin (False)
   STANDALONE_MODE = False
   
   # the location of our scraper 'cache' files. 
   LOCAL_CACHE_DIRECTORY = None
   
   # the location of the app's settings file.
   SETTINGS_FILE = None
   
   # the location of the app's geometry settings file.
   GEOMETRY_FILE = None
   
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
   
   #===========================================================================
   @classmethod
   def enable_standalone_mode(cls, project_dir):
      '''
      This method switches the Resources object from "normal" mode (where all
      dirs and paths, etc, are in the user's normal ComicRack profile dir) to
      IDE mode, where these values are pointing to locations inside the IDE's
      project directory.   This is only meant to be run during development.
      '''
      cls.STANDALONE_MODE = True

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
   def __import_legacy_settings(cls):
      roaming_dir = Environment.GetFolderPath(
         Environment.SpecialFolder.ApplicationData)
      legacy_dir = roaming_dir + "\cYo\ComicRack\Scripts\Comic Vine Scraper"
      settings_dir = roaming_dir + "\Comic Vine Scraper"
      print "Legacy: " + legacy_dir
      print "Settings: " + settings_dir
   
   # coryhigh: comment all this
   @classmethod
   def __initialize(cls, standalone):
      cls.STANDALONE_MODE = standalone
      if standalone:
         project_dir = Directory.GetParent( Directory.GetParent(
           Directory.GetParent(__file__).FullName).FullName ).FullName
         script_dir = project_dir + r"\\profile\\"
         cls.LOCAL_CACHE_DIRECTORY = script_dir + r'localCache\\'
         cls.SETTINGS_FILE = script_dir + r'settings.dat'
         cls.GEOMETRY_FILE = script_dir + r'geometry.dat'
         cls.I18N_DEFAULTS_FILE = project_dir + \
            r'\src\resources\languages\en.zip'
      else:
         script_dir = __file__[:-len('resources.py')]
         cls.LOCAL_CACHE_DIRECTORY = script_dir + 'localCache/'
         cls.SETTINGS_FILE = script_dir + 'settings.dat'
         cls.GEOMETRY_FILE = script_dir + 'geometry.dat'
         cls.I18N_DEFAULTS_FILE = script_dir + 'en.zip'
      
   
   @classmethod
   def initialize(cls, standalone):
      # this code runs before we have our proper error handling installed, so 
      # wrap it in a try-except block so at least we have SOME error handling
      try:
         cls.__import_legacy_settings()
         cls.__initialize(standalone)
      except:
         print sys.exc_info()[1]
         sys.exit();