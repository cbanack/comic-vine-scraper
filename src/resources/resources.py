#corylow: comment and cleanup this file

###############################################################################
# Created on Feb 7, 2010
# @author: cbanack
################################################################################
import clr;
clr.AddReference('System.Drawing')
from System.Drawing import Image

# corylow: make this into a static class rather than module variables
# corylow: when possible, swith to us os.path.dirname() here
_SCRIPT_DIRECTORY =  __file__[:-len('resources.py')] 
LOCAL_CACHE_DIRECTORY = _SCRIPT_DIRECTORY + 'localCache/'
SETTINGS_FILE = _SCRIPT_DIRECTORY + 'settings.dat'
GEOMETRY_FILE = _SCRIPT_DIRECTORY + 'geometry.dat'

# do NOT change the following lines.  they are modified by the build process!
SCRIPT_VERSION = "!DEV!"
if SCRIPT_VERSION.startswith("!"):
   SCRIPT_VERSION = "0.0.0"

def createComicVineLogo():
   dir = __file__[:-(len(__name__) + len('.py'))]
   return Image.FromFile( dir + 'comicvinelogo.png')

def getComicName(eComic, include_volume=False, include_issue=False ):
   comic_name = 'unknown comic'
   if eComic.ShadowSeries != '' and eComic.ShadowSeries is not None:
      comic_name = eComic.ShadowSeries
      if include_volume and eComic.ShadowVolume >= 0:
         comic_name += ' (V' + str(eComic.ShadowVolume) +')'
      if include_issue and eComic.ShadowNumber >= 0:
            comic_name += ", #" + eComic.ShadowNumber 

   return comic_name