#corylow: comment and cleanup this file

###############################################################################
# Created on Feb 7, 2010
# @author: Cory Banack
################################################################################
import clr;
clr.AddReference('System.Drawing')
from System.Drawing import Image

# do NOT change the following lines.  they are modified by the build process!
SCRIPT_VERSION = "!DEV!"


class Resources(object):
   
   __SCRIPT_DIRECTORY =  __file__[:-len('resources.py')] 
   LOCAL_CACHE_DIRECTORY = __SCRIPT_DIRECTORY + 'localCache/'
   SETTINGS_FILE = __SCRIPT_DIRECTORY + 'settings.dat'
   GEOMETRY_FILE = __SCRIPT_DIRECTORY + 'geometry.dat'
   I18N_DEFAULTS_FILE = __SCRIPT_DIRECTORY + 'en.zip'
   I18N_XML_ENTRY = 'Script.ComicVineScraper.xml'
   
   # do NOT change the following lines.  they are modified by the build process!
   SCRIPT_VERSION = "!DEV!"
   if SCRIPT_VERSION.startswith("!"):
      SCRIPT_VERSION = "0.0.0"
   SCRIPT_FULLNAME = 'Comic Vine Scraper - v' + SCRIPT_VERSION
   
   @classmethod
   def enable_ide_mode(cls, project_dir):
      cls.__SCRIPT_DIRECTORY = project_dir + r"\\profile\\"
      cls.LOCAL_CACHE_DIRECTORY = cls.__SCRIPT_DIRECTORY + r'localCache\\'
      cls.SETTINGS_FILE = cls.__SCRIPT_DIRECTORY + r'settings.dat'
      cls.GEOMETRY_FILE = cls.__SCRIPT_DIRECTORY + r'geometry.dat'
      cls.I18N_DEFAULTS_FILE = project_dir + \
         r'\src\resources\languages\en.zip'
         
   @classmethod
   def createComicVineLogo(cls):
      dir = __file__[:-(len(__name__) + len('.py'))]
      return Image.FromFile( dir + 'comicvinelogo.png')