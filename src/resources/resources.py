#corylow: comment and cleanup this file

###############################################################################
# Created on Feb 7, 2010
# @author: Cory Banack
################################################################################
import clr;
clr.AddReference('System.Drawing')
from System.Drawing import Image

# corylow: make this into a static class rather than module variables
_SCRIPT_DIRECTORY =  __file__[:-len('resources.py')] 
LOCAL_CACHE_DIRECTORY = _SCRIPT_DIRECTORY + 'localCache/'
SETTINGS_FILE = _SCRIPT_DIRECTORY + 'settings.dat'
GEOMETRY_FILE = _SCRIPT_DIRECTORY + 'geometry.dat'
I18N_DEFAULTS_FILE = _SCRIPT_DIRECTORY + 'en.zip'
I18N_XML_ENTRY = 'Script.ComicVineScraper.xml'


# do NOT change the following lines.  they are modified by the build process!
SCRIPT_VERSION = "!DEV!"
if SCRIPT_VERSION.startswith("!"):
   SCRIPT_VERSION = "0.0.0"

def createComicVineLogo():
   dir = __file__[:-(len(__name__) + len('.py'))]
   return Image.FromFile( dir + 'comicvinelogo.png')