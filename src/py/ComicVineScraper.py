''' ===========================================================================

This module is the entry point into the 'Comic Vine Scraper' add-on for 
ComicRack.  It conforms to ComicRack add-on specifications, outlined at:

     http://comicrack.cyolito.com/faqs/28-comicrack-scripts


License: 
    
   The Comic Vine Scraper add-on is licensed under the Apache 2.0 software 
   license, available at: http://www.apache.org/licenses/LICENSE-2.0.html

       
Credits:

   The add-on is written and maintained by Cory Banack.  It is based on the
   the ComicVineInfo script started by wadegiles and perezmu (from the 
   ComicRack forums).  It also makes use of the following:
       - the ComicVine API - http://www.comicvine.gamespot.com/api
       - xml2py.py and ipypulldom.py - http://devhawk.net/
       - the DotNetZip library - http://dotnetzip.codeplex.com/
       - MessageBoxManager - http://www.codeproject.com/

=========================================================================== '''
import re
import clr
import log
import i18n
from scrapeengine import ScrapeEngine
from configform import ConfigForm
from utils import sstr
from resources import Resources
import db

clr.AddReference('System')
from System.Threading import ThreadExceptionEventHandler

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import Application, MessageBox, \
    MessageBoxButtons, MessageBoxIcon

if False and True:
   # this gets rid of a stubborn compiler warning
   ComicRack = None


# ============================================================================      
# The is a plugin hook to attach this method to ComicRack.  Don't change!
#@Key    comic-vine-scraper
#@Hook   ConfigScript
# ============================================================================      
def cvs_config():
   # create and launch a delegate that runs the configuration dialog
   def delegate():
      with ConfigForm(ComicRack.MainWindow) as config_form:
         config_form.show_form() # blocks
   __launch(delegate)


# ============================================================================      
# The is a plugin hook to attach this method to ComicRack.  Don't change!
#@Image        comicvinescraper.png
#@Key          comic-vine-scraper
#@Hook         Books, Editor
# ============================================================================      
def cvs_scrape(books):
   # create a launch a delegate that scrapes the given books
   def delegate():
      if books:
      # uncomment this to create a pickled load file for my pydev launcher
#         with open("k:/sample.pickled", "w") as f:
#            cPickle.dump(books, f);
         engine = ScrapeEngine(ComicRack)
         engine.scrape(books)
   __launch(delegate)



# =============================================================================
def __launch(delegate):
   ''' 
   Runs the given (no-argument) delegate method in a 'safe' script environment.
   This environment will take care of all error handling, logging/debug stream,
   and other standard initialization behaviour before delegate() is called, and
   it will take care of cleaning everything up afterwards.
   ''' 
   try:
      # initialize the application resources (import directories, etc)
      Resources.initialize()
      
      # fire up the debug logging system
      log.install(ComicRack.MainWindow)
      
      # install a handler to catch uncaught Winforms exceptions
      def exception_handler(sender, event):
         del sender #unused
         log.handle_error(event.Exception)
      Application.ThreadException \
         += ThreadExceptionEventHandler(exception_handler)
         
      # fire up the localization/internationalization system
      i18n.install(ComicRack)
      
      # see if we're in a valid environment
      if __validate_environment():
         delegate()
   
   except Exception, ex:
      log.handle_error(ex)
         
   finally:
      
      # shut down our database connection
      db.shutdown()
      
      # shut down the localization/internationalization system
      i18n.uninstall()
      
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
   REQUIRED_BUILD=165
   
   valid_environment = True
   try:
      version = re.split(r'\.', ComicRack.App.ProductVersion) 
      def vhash( major, minor, build ):
         return float(sstr(major * 5000 + minor) + "." + sstr(build)) 
      
      valid_environment = \
         vhash(int(version[0]), int(version[1]), int(version[2])) >= \
            vhash(REQUIRED_MAJOR, REQUIRED_MINOR, REQUIRED_BUILD)
         
      if not valid_environment:
         log.debug("WARNING: script requires ComicRack ", REQUIRED_MAJOR, '.',
            REQUIRED_MINOR, '.', REQUIRED_BUILD, ' or higher.  Exiting...')
         MessageBox.Show( ComicRack.MainWindow, i18n.get("ComicRackOODText"),
            i18n.get("ComicRackOODTitle"), MessageBoxButtons.OK, 
            MessageBoxIcon.Warning)
         
   except Exception:
      log.debug_exc("WARNING: couldn't validate comicrack version")
      valid_environment = True
      
   return valid_environment



