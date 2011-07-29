'''
This module contains the Resources class.
'''

import clr;
clr.AddReference('System.Drawing')
from System.Drawing import Image

#==============================================================================
class Resources(object):
   '''
    This class provides static access to "constants" for all the non-code
    resources that this app uses.  (i.e. pathnames and locations, mostly.)
    ''' 
   
   # the dir that contains the script files (all of them, including this one)
   __SCRIPT_DIRECTORY =  __file__[:-len('resources.py')]
   
   # the location of our scraper 'cache' files. 
   LOCAL_CACHE_DIRECTORY = __SCRIPT_DIRECTORY + 'localCache/'
   
   # the location of the app's settings file.
   SETTINGS_FILE = __SCRIPT_DIRECTORY + 'settings.dat'
   
   # the location of the app's geometry settings file.
   GEOMETRY_FILE = __SCRIPT_DIRECTORY + 'geometry.dat'
   
   # the location of the app's localization default strings file
   I18N_DEFAULTS_FILE = __SCRIPT_DIRECTORY + 'en.zip'
   
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
   def enable_ide_mode(cls, project_dir):
      '''
      This method switches the Resources object from "normal" mode (where all
      dirs and paths, etc, are in the user's normal ComicRack profile dir) to
      IDE mode, where these values are pointing to locations inside the IDE's
      project directory.   This is only meant to be run during development.
      '''
      cls.__SCRIPT_DIRECTORY = project_dir + r"\\profile\\"
      cls.LOCAL_CACHE_DIRECTORY = cls.__SCRIPT_DIRECTORY + r'localCache\\'
      cls.SETTINGS_FILE = cls.__SCRIPT_DIRECTORY + r'settings.dat'
      cls.GEOMETRY_FILE = cls.__SCRIPT_DIRECTORY + r'geometry.dat'
      cls.I18N_DEFAULTS_FILE = project_dir + \
         r'\src\resources\languages\en.zip'


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
   
   
   