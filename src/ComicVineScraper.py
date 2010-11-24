###############################################################################
#
# ComicVineScraper.py
#
#   This is the 'entry point' into the Comic Vine Scraper add-on for 
#   ComicRack.  This script requires the latest version of ComicRack in order 
#   to run.
#   
#
#   Credits:    - written and maintained by Cory Banack
#               - based on the ComicVineInfo script started by wadegiles 
#                   and perezmu (from the ComicRack) forum
#               - xml2py.py and ipypulldom.py modules (c) DevHawk.net
#               - ComicVine API (c) whiskeymedia.com (http://api.comicvine.com)
#
#   This software is licensed under the Apache 2.0 software license.
#   http://www.apache.org/licenses/LICENSE-2.0.html
#             
###############################################################################
# coryhigh: FIX THE ABOVE COMMENT!!
import clr
import log
import re
from scrapeengine import ScrapeEngine
from utils import sstr

clr.AddReference('System')
from System.Threading import ThreadExceptionEventHandler

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import Application, MessageBox, \
    MessageBoxButtons, MessageBoxIcon

if False:
   # this gets rid of a stubborn compiler warning
   ComicRack = None


# ============================================================================      
# Don't change this comment; it's needed to integrate into ComicRack!
#
#@Name   Comic Vine Scraper...
#@Image  comicvinescraper.png
#@Key    comic-vine-scraper-cbanack
#@Hook   Books, Editor
# ============================================================================      
def ComicVineScraper(books):
   try:
      # fire up the debug logging system
      log.install(ComicRack.MainWindow)
      
      # install a handler to catch uncaught Winforms exceptions
      def exception_handler(sender, event):
         log.handle_error(event.Exception)
      Application.ThreadException \
         += ThreadExceptionEventHandler(exception_handler)

      # uncomment this to create a pickled load file for my pydev launcher
      #with open("k:/sample.pickled", "w") as f:
         #cPickle.dump(books, f);
         
      # see if we're in a valid environment
      if __validate_environment() and books:
         # create a Scraping Engine and use it to scrape the given books.
         engine = ScrapeEngine(ComicRack)
         engine.scrape(books)
         
   finally:
      
      # make sure the Winform exception handler is removed
      Application.ThreadException -=\
         ThreadExceptionEventHandler(exception_handler)
      # shut down the logging system
      log.uninstall()
      
      
      
# ============================================================================      
def __validate_environment():
   '''
   Checks to see if the current environment is valid to run this script in.
   If it is not, an error message is displayed to explain the problem.
   
   Returns True if the current environment is valid, False if it is not.
   '''
   
   # the minimum versions required for a valid environment
   REQUIRED_MAJOR=0
   REQUIRED_MINOR=9
   REQUIRED_BUILD=129
   
   valid_environment = True
   try:
      version = re.split(r'\.', ComicRack.App.ProductVersion) 
      def hash( major, minor, build ):
         return float(sstr(major * 5000 + minor) + "." + sstr(build))
      
      valid_environment = \
         hash(int(version[0]),int(version[1]), int(version[2])) >= \
            hash(REQUIRED_MAJOR, REQUIRED_MINOR, REQUIRED_BUILD)
         
      if not valid_environment:
         log.debug("WARNING: script requires ComicRack ", REQUIRED_MAJOR, '.',
            REQUIRED_MINOR, '.', REQUIRED_BUILD, ' or higher.  Exiting...')
         MessageBox.Show( ComicRack.MainWindow,
            'This script reqires a newer version of ComicRack in order to\n' +
            'run properly.  Please download and install the latest version\n' +
            'from the ComicRack website, and then try again.', 
            'ComicRack Update Required',
             MessageBoxButtons.OK, MessageBoxIcon.Warning)
         
   except:
      log.debug_exc("WARNING: couldn't validate comicrack version")
      valid_environment = True
      
   return valid_environment



