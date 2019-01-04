'''
This module is home to the ScrapeEngine class.
@author: Cory Banack
'''
import clr

import log
import utils
from utils import sstr, natural_key
from resources import Resources 
from configuration import Configuration
from comicform import ComicForm
from seriesform import SeriesForm, SeriesFormResult
from issueform import IssueForm, IssueFormResult
from progressbarform import ProgressBarForm
from searchform import SearchForm
import db
from welcomeform import WelcomeForm
from finishform import FinishForm
import i18n
from matchscore import MatchScore
from comicbook import ComicBook
import automatcher
import dbutils
from configform import ConfigForm

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import Application, MessageBox, \
    MessageBoxButtons, MessageBoxIcon

clr.AddReference('System')
from System.IO import Path
from System import GC, DateTime
from System.Threading import Thread, ThreadStart
    
# =============================================================================
class ScrapeEngine(object):
   '''
   This class contains the main processing loop for the Comic Vine Scraper
   script.   Once initialized, you pass a collection of books to the 
   ScrapeEngine via the 'scrape' method.
   
   Those books will be processed one at a time, with windows and dialogs
   popping up to interact with the user as needed (including a single 
   ComicForm window, which is present the during the entire scrape, always
   showing the user the current status of the ScrapeEngine.)
   '''

   # ==========================================================================
   def __init__(self, comicrack):
      '''
      Initializes this ScrapeEngine.  It takes the ComicRack Application 
      object as it's only parameter.
      '''
      
      # the Configuration details for this ScrapeEngine.  used everywhere.  
      self.config = Configuration()
      
      # the ComicRack application object, i.e. the instance of ComicRack that
      # is running this script.  used everywhere.
      self.comicrack = comicrack
      
      # a list of methods that will each be fired whenever the 'scrape' 
      # operation begins processing/scraping a new book. these methods should
      # look like:   
      #             start_scrape(book, num_remaining)
      #
      # where 'book' is the new book being scraped and 'num_remaining' is the 
      # number of books left to scrape, including the one currently starting
      self.start_scrape_listeners = []

      # a list of no-argument methods that will each be fired once 
      # when (and if) the scrape operation gets cancelled.
      self.cancel_listeners = []
      
      # this variable can be set by calling the 'cancel' method.  when it is 
      # set to True, it indicates that the entire script should be cancelled as 
      # soon as possible.
      self.__cancelled_b = False
      
      # a list of two values, the first value tells how many books this 
      # scrape engine has scraped, the second tells how many it has skipped.
      # it becomes valid as soon as the main processing loop starts running.
      self.__status = [0,0]
      
      # an object that we use to keep (and add to) a persistent list of which 
      # series' the user has chosen while scraping.  it can then be used to
      # help present better sorted choices to the user in the future.
      self.__matchscore = MatchScore()



   # ==========================================================================
   def cancel(self):
      '''
      This method cancels the ScrapeEngine's current scrape operation, 
      and causes the main processing loop to exit on the next iteration;
      all ComicBooks that haven't yet been scraped will be skipped.
      '''
      
      if not self.__cancelled_b:
         # do this on calling thread, even if its not the mainwindow UI
         # thread, cause that thread could be blocked by SCRAPE_DELAY
         self.__cancelled_b = True 
         def delegate(): 
            for cancel_listener in self.cancel_listeners:
               cancel_listener()
         utils.invoke(self.comicrack.MainWindow, delegate, False)



   # ==========================================================================
   def scrape(self, books):
      '''
      This is the entry-point to the ScraperEngine's main processing loop.
      
      A typical invocation of the scraper script will create a new ScraperEngine 
      object and then call this method on it ONCE, passing it a list of all the
      ComicBook objects that need to be scraped.
      '''
      
      try:
         # a litte bit of logging to help make our debug logs more useful
         log.debug()
         log.debug("-"*80)
         log.debug("CV Scraper Version:  ", Resources.SCRIPT_VERSION)
         log.debug("Running As:          ", "ComicRack Plugin (CR version " +
            self.comicrack.App.ProductVersion + ")")
         log.debug("Cache Directory:     ", Resources.LOCAL_CACHE_DIRECTORY)
         log.debug("Settings File:       ", Resources.SETTINGS_FILE)
         log.debug("-"*80)
         log.debug()

         # do the main part of the script
         if books:
            # uncomment this to try out scraping a single, specific issue
            #books[0].Series = "The Living Corpse"
            #books[0].Number = ".5"
            #books = books[0:1]
            
            # this populates the "status" variable, and the "config" variable
            self.__scrape(books) 
            
         log.debug("Scraper terminated normally (scraped {0}, skipped {1})."\
            .format(self.__status[0], self.__status[1]))
            
      except Exception, ex:
         log.handle_error(ex)
         
      finally:
         if self.config.summary_dialog_b:
            try:
               # show the user a dialog describing what was scraped
               with FinishForm(self, self.__status) as finish_form:
                  finish_form.show_form()
            except Exception, ex:
               log.handle_error(ex)



   # ==========================================================================
   def __scrape(self, books):
      '''
      The private implementation of the 'scrape' method.
      '''
      
      # initialize the status member variable, and then keep it up-to-date 
      # from now on (so that it can be used to report the status of this 
      # scrape, even if an error occurs.)
      self.__status = [0, len(books)]
      
      # 1. load the currently saved configuration settings from disk
      self.config = Configuration()
      self.config.load_defaults()
      
      if not self.config.api_key_s:
         log.debug("API key not available.  Showing config dialog.")
         with ConfigForm(self.comicrack.MainWindow) as config_form:
            config_form.show_form() # blocks
         self.config.load_defaults()
         if not self.config.api_key_s:
            log.debug("API key still not available.  Aborting.")
            return
         
      
      # 2. show the welcome form. in addition to being a friendly summary of 
      #    what's about to happen, it allows the user to tweak the 
      #    Configuration settings.
      if self.config.welcome_dialog_b:
         with WelcomeForm(self, books) as welcome_form:
            self.__cancelled_b = not welcome_form.show_form()
         self.config = Configuration()
         self.config.load_defaults()
         if self.__cancelled_b:
            log.debug("Cancelled!")
            return

      # 3. print the entire configuration to the debug stream
      log.debug(self.config)
      log.debug()
      
      # 4. fire up our database connection
      db.initialize(**{'cv_apikey':self.config.api_key_s,
                       'cv_maxresults':self.config.max_search_results_n}) 
      
      # 5. sort the ComicBooks in the order that we're gonna loop them in
      #    (sort AFTER config is loaded cause config affects the sort!)
      books = [ ComicBook(book, self) for book in books ]
      books = self.__sort_books(books) 

      # 6. display the ComicForm dialog.  it is a special dialog that stays 
      #    around for the entire time that the this scrape operation is running.
      comic_form = ComicForm.show_threadsafe(self)
      
      try:
         # this caches the scraped data we've accumulated as we loop
         scrape_cache = {}
         
         # 7. start the "Main Processing Loop". 
         #    notice the list of books can get longer while we're looping,
         #    if we choose to delay processing a book until the end.
         i = 0
         orig_length = len(books)
         while i < len(books):
            if self.__cancelled_b: break
            book = books[i]
            
            # 7a. wait for the scrape delay to pass after scraping each book.  
            #     don't do this for books that have been delayed or for the 
            #     first book that the user scrapes.
            delayed_b = i >= orig_length # book was delayed until the end
            if i != 0 and not delayed_b:
               self.__wait_until_ready()
               if self.__cancelled_b: break  # user cancelled while we waited
               

            # 7b. notify 'start_scrape_listeners' that we're scraping a new book
            
            log.debug("======> scraping next comic book: '",
               'FILELESS ("' + book.series_s +" #"+ book.issue_num_s+ ''")"
               if book.path_s == "" else Path.GetFileName(book.path_s),"'")
            num_remaining = len(books) - i
            for start_scrape in self.start_scrape_listeners:
               start_scrape(book, num_remaining)

            # 7c. ...keep trying to scrape that book until either it is scraped,
            #     the user chooses to skip it, or the user cancels altogether.
            manual_search_b = False
            fast_rescrape_b = self.config.fast_rescrape_b and not delayed_b
            autoscrape_b = self.config.autochoose_series_b and \
                not self.config.confirm_issue_b and not delayed_b
            bookstatus = BookStatus("DELAYED") \
               if delayed_b else BookStatus("UNSCRAPED")
               
            while not self.__cancelled_b:
               
               bookstatus = self.__scrape_book(book, scrape_cache,
                 manual_search_b, fast_rescrape_b, autoscrape_b, bookstatus)
               
               if bookstatus.equals("UNSCRAPED"):
                  # this return code means 'no series could be found using 
                  # the current (automatic or manual) search terms'.  when  
                  # that happens, force the user to choose the search terms.
                  manual_search_b = True
                  continue
               elif bookstatus.equals("SCRAPED"):
                  # book was scraped normally, all is good, update status
                  self.__status[0] += 1
                  self.__status[1] -= 1
                  break
               elif bookstatus.equals("SKIPPED"):
                  # book was skipped, status is already correct for that book
                  break
               elif bookstatus.equals("DELAYED"):
                  # put this book into the end of the list, where we can try
                  # rescraping  after we've handled the ones that we can do
                  # automatically.  ignore it if it's already been delayed.
                  if not delayed_b: 
                     books.append(book)
                  break
            
            # keep memory usage from getting out of control!
            GC.Collect()
            GC.WaitForPendingFinalizers()
            
            log.debug()
            log.debug()
            i = i + 1
            
      finally:
         self.comicrack.MainWindow.Activate() # fixes issue 159
         if comic_form: comic_form.close_threadsafe()
         


   # ==========================================================================
   def __scrape_book(self, book, scrape_cache, 
         manual_search_b, fast_rescrape_b, autoscrape_b, prev_status=None):
      '''
      This method is the heart of the Main Processing Loop. It scrapes a single
      ComicBook object by first figuring out which issue entry in the database 
      matches that book, and then copying those details into the ComicBook 
      object's metadata fields.  
      
      The 10000 foot view of the loop steps:
      
       1.  Attempt to scrape automatically.  If we succeed, we're done.
       2.  Otherwise, obtain search terms for the given 'book'
            - if 'manual_search_b' then ask the user to provide the search terms
            - else guess the terms based on the book's name
       3.  Search database for all comic series that match those search terms.
       4.  Ask the user which of the series that we found is the correct one
       5a. If the user picks a series:
            - we guess which issue in that series matches our ComicBook, OR
            - we ask the user to specify the correct issue (if we can't guess)
       5b. Else the use might decide to skip scraping this book.
       5c. Else the user might decide to start over with new search terms
       5d. Else the user might choose to specify the correct issue manually
       5e. Else the user might cancel the entire operation
             
       Throughout this process, the 'scrape_cache' (a map, empty at first) is
       used to speed things up.  It caches details from previous calls to this 
       method, so if this method is called repeatedly, the same scrape_cache 
       must be passed in each time.
       
       AUTOMATIC SCRAPING
       
       Iff 'fast_rescrape_b' is set to true, this method will attempt to find 
       and use any database key that was written to the book during a previous
       scrape.  Else iff 'autoscrape_b' is true, this method attempts a search
       algorithm on the database, again to obtain the key.  Iff either attempt
       succeeds, the key allows us to instantly identify a comic, thus skipping
       everything after step 1.  If no key is available, just fall back to
       the user-interactive method of identifying the comic (step 2+).
       
       RETURN VALUES
       
       When this method is called repeatedly on the same book, a 'prev_status'
       should be passed in, giving this method access to the BookStatus object 
       that it returned the last time it was called for that book. 
              
       BookStatus("UNSCRAPED"): if the book wasn't be scraped, either because
          the search terms yielded no results, or the user opted to specify
          new search terms
          
       BookStatus("SKIPPED"): if this one book was skipped over by the user, or  
          of the user cancelled the entire current scrape operation (check the
          status if the ScrapeEngine).
          
       BookStatus("SCRAPED"): if the book was scraped successfully, and now 
          contains updated metadata.
          
       BookStatus("DELAYED"): if we attempted to automatically scrape the book,
          but failed.  the book has not been scraped successfully.
          
       
      '''

      # WARNING:  THE CODE IN THIS METHOD IS EXTREMELY SUBTLE.
      # Be sure you understand EVERYTHING that's going on and why before you
      # try to change anything in here.  You've been warned!
      
      Application.DoEvents()
      if self.__cancelled_b: return BookStatus("SKIPPED")
      if prev_status == None: prev_status = BookStatus("UNSCRAPED")
         
      # 1. METHOD EXIT: if this book has been tagged to skip, do so.
      if book.skip_b: 
         log.debug("found SKIP tag, so skipping the scrape for this book.")
         return BookStatus("SKIPPED")

      
      # 2. if this book is being 'rescraped', sometimes it already knows the 
      #    correct IssueRef from a previous scrape. METHOD EXIT: if that 
      #    rescrape IssueRef is available, we use it immediately and exit.
      #    if an error occurs, retry a manual scrape later on.
      issue_ref = book.issue_ref
      if issue_ref and fast_rescrape_b:
         log.debug("rescraping details in book identified its issue as: '",
            sstr(issue_ref), "'")
         try:
            issue = db.query_issue(issue_ref, self.config.update_rating_b)
            book.update(issue)
            return BookStatus("SCRAPED")
         except:
            log.debug_exc("Error rescraping details:")
            log.debug("we'll retry scraping this book again at the end.")
            return BookStatus("DELAYED")

   
      # 3. what follows is an attempt to get the unique series key for this book
      #    into the scrape cache. this effectively tells us which series the 
      #    book belongs to, and also allows us to automatically use the same
      #    series for other books that have the same unique series key.
      key = book.unique_series_s
      
      # 3a. see if the book already knows the correct series keys based on a 
      #     previous scrape.  that's pretty unlikely since we didn't find the
      #     IssueRef from a previous scrape, but in certain special cases, it
      #     can happen (mostly compatibility with other scripts)
      if key not in scrape_cache and not manual_search_b:
         if book.series_ref and fast_rescrape_b:
            log.debug("rescraping details in book identified its series as: '",
               book.series_ref, "'")
            scraped_series = ScrapedSeries( book.series_ref )
            scrape_cache[key] = scraped_series
   
      # 3b. see if this book has an special file in it's folder that tells us
      #     what series the book belongs to.  if so, add that map that book
      #     to that series in the scrape_cache.
      if key not in scrape_cache and not manual_search_b:
         magic_series_ref = db.check_magic_file(book.path_s)
         if magic_series_ref:        
            log.debug("a 'magic' file identified this book's series as: '",
              magic_series_ref, "'")
            scraped_series = ScrapedSeries( magic_series_ref )
            scrape_cache[key] = scraped_series
         
      # 3c. or maybe the user requested that we try the auto-scrape algorithm on 
      #     all new (unscraped) books?  if so, now's the time to give it a try.  
      #     if we find the series for this book, add it to the scrape cache.
      if key not in scrape_cache and autoscrape_b:
         if self.config.confirm_issue_b:
            raise Exception("can't confirm issues while autoscraping")
         log.debug("trying to match this book automatically...")
         auto_series_ref = automatcher.find_series_ref(book, self.config) 
         if auto_series_ref:
            log.debug("...found a suitable match:  ", auto_series_ref)
            scraped_series = ScrapedSeries( auto_series_ref )
            scrape_cache[key] = scraped_series
         else:
            log.debug("...couldn't find a match. leave it until the end.")
            return BookStatus("DELAYED")

      # 3d. if the series still hasn't been added to the scrape cache, the next
      #     step is to search the online database for the book's series name.
      #     the user may have to modify the auto-generated search terms. the
      #     goal is to get some potential SeriesRefs to show the user. 
      #     METHOD EXIT: if the user cancels or skips from the search dialog.          
      search_terms_s = None
      series_refs = None
      if key not in scrape_cache: 
         # get search terms for the book that we're scraping
         search_terms_s = book.series_s
         if manual_search_b or not search_terms_s:
            # show dialog asking the user for the right search terms
            log.debug('asking user for series search terms...')
            with SearchForm(self, search_terms_s, 
                  prev_status.get_failed_search_terms_s() ) as search_form:
               search_form_result = search_form.show_form() # blocks
            log.debug( "...and the user chose to " 
               + search_form_result.get_debug_string() )
            
            if search_form_result.equals("SEARCH"):
               search_terms_s = search_form_result.get_search_terms_s()
            elif search_form_result.equals("CANCEL"):
               self.__cancelled_b = True
               return BookStatus("SKIPPED")
            elif search_form_result.equals("SKIP"):
               return BookStatus("SKIPPED")
            elif search_form_result.equals("PERMSKIP"):
               book.skip_forever()
               return BookStatus("SKIPPED")
         # query the database for series_refs that match the search terms
         series_refs = self.__query_series_refs(search_terms_s)
         if self.__cancelled_b: 
            return BookStatus("SKIPPED")
         if not series_refs:
            # include failed search terms here, so search dialog mentions them
            return BookStatus("UNSCRAPED", search_terms_s)


      # 3d. now that we have a set of SeriesRefs that match this book, 
      #     show the user the Series dialog so he/she can choose the right one.
      #     put the chosen series into the series cache.  METHOD EXIT: while 
      #     viewing the series dialog, the user might skip, request to 
      #     re-search, or cancel the entire scrape operation.
      while True:
         force_issue_dialog_b = self.config.confirm_issue_b 
         if key not in scrape_cache: 
            if not series_refs or not search_terms_s:
               return BookStatus("UNSCRAPED") # rare but possible, bug 77
            series_form_result =\
               self.__choose_series_ref(book, search_terms_s, series_refs)
            
            if series_form_result.equals("CANCEL") or self.__cancelled_b:
               self.__cancelled_b = True
               return BookStatus("SKIPPED") # user says 'cancel'
            elif series_form_result.equals("SKIP"):
               return BookStatus("SKIPPED") # user says 'skip this book'
            elif series_form_result.equals("PERMSKIP"):
               book.skip_forever()
               return BookStatus("SKIPPED") # user says 'skip book always'
            elif series_form_result.equals("SEARCH"): 
               return BookStatus("UNSCRAPED") # user says 'search again'
            elif series_form_result.equals("SHOW") or \
                 series_form_result.equals("OK"): # user says 'ok'
               scraped_series = ScrapedSeries( series_form_result.get_ref() )
               # user has chosen a series, so ignore config.confirm_issue_b
               # and only force the issue dialog if she clicked 'show' 
               force_issue_dialog_b = series_form_result.equals("SHOW")
               scrape_cache[key] = scraped_series
               

         # 4. at this point, the 'correct' series for the book is now in the
         #    series cache.  now we try to pick the matching issue in that 
         #    series. do so automatically if possible, or show the user the
         #    issue dialog if necessary (or requesting in config).  METHOD EXIT:
         #    if the user sees the  issue dialog, she may skip, cancel the 
         #    whole scrape operation, go back to the series dialog, or 
         #    actually scrape an issue.
         scraped_series = scrape_cache[key]


         # 5. now that we know the right series for this book, try to find
         #    the right issue, either automatically, or by showing the user 
         #    the "issues dialog".  METHOD EXIT: if we're scraping automatically
         #    we MUST be able to find the issue num automatically too, or else
         #    we delay the book til later.  if we're manual, we may still be 
         #    able to find the issue automatically, but if not we show the user
         #    the query dialog, and she may skip, cancel the whole scrape, go 
         #    back to the series dialog, or actually choose an issue.
         log.debug("searching for the right issue in '",
                   scraped_series.series_ref, "'")

         issue_ref = None         
         if autoscrape_b:
            # 5a. autoscrape means we MUST find the issue automatically...
            series_ref = scraped_series.series_ref
            if book.issue_num_s == "":
               if series_ref.issue_count_n <=1:
                  refs = self.__query_issue_refs(series_ref)
                  if len(refs) == 1: issue_ref = list(refs)[0]
            else:
               issue_ref = db.query_issue_ref( series_ref, book.issue_num_s )
               
            if issue_ref == None:
               log.debug("couldn't find issue number.  leaving until the end.")
               del scrape_cache[key] # this was probably the wrong series, too
               return BookStatus("DELAYED")
            else: 
               log.debug("   ...identified issue number ", book.issue_num_s )
               
         else:            
            # 5b. ...otherwise, try to find the issue interactively         
            issue_form_result = self.__choose_issue_ref( book, 
               scraped_series.series_ref, scraped_series.issue_refs, 
               force_issue_dialog_b)
            
            if issue_form_result.equals("CANCEL") or self.__cancelled_b:
               self.__cancelled_b = True
               return BookStatus("SKIPPED")
            elif issue_form_result.equals("SKIP") or \
                  issue_form_result.equals("PERMSKIP"):
               if force_issue_dialog_b and not self.config.confirm_issue_b:
                  # the user clicked 'show issues', then 'skip', so we have to
                  # ignore his previous series selection.
                  del scrape_cache[key]
               if issue_form_result.equals("PERMSKIP"):
                  book.skip_forever()
               return BookStatus("SKIPPED")
            elif issue_form_result.equals("BACK"):
               # ignore user's previous series selection
               del scrape_cache[key]
            else:
               issue_ref = issue_form_result.get_ref() # not None!
         
         if issue_ref != None:      
            # we've found the right issue!  copy it's data into the book.
            log.debug("querying comicvine for issue details...")
            issue = db.query_issue( issue_ref, self.config.update_rating_b )
            book.update(issue)
            
            # record the users choice.  this allows the SeriesForm to give this
            # choice a higher priority (sort order) in the future
            self.__matchscore.record_choice(scraped_series.series_ref)
            
            return BookStatus("SCRAPED")

      raise Exception("should never get here")


   # ==========================================================================
   def __sort_books(self, books):
      '''
      Examines the given list of ComicBook objects, and returns a new list
      that contains the same comics, but sorted in order of increasing series
      name, and where the series names are the same, in order of increasing 
      issue number.  Comics for which an IssueRef can be instantly generated
      (comics that have been scraped before) will automatically be sorted to
      the beginning of the list.
      '''
      
      # this is the comparator we'll use for sorting this list
      def __compare_books(book1, book2):
         result = book1.unique_series_s.CompareTo(book2.unique_series_s)
         if result == 0:
            num1 = '' if not book1.issue_num_s else book1.issue_num_s
            num2 = '' if not book2.issue_num_s else book2.issue_num_s
            def pad(num):
               try:
                  f = float(num.lower().strip('abcdefgh'))
                  if f < 10: return "000" + num
                  elif f < 100: return "00" + num
                  elif f < 1000: return "0" + num
                  else: return num
               except:
                  return num
            result = pad(num1).CompareTo(pad(num2))
         return result

      # divide the books up into the ones that will scrape quickly ('cause they
      # are rescrapes) and ones that have never been scraped before.  sort each
      # group separately, and append the sorted lists together so the fast ones 
      # will come first.   (the idea is to save the user interaction until
      # the end of the scrape operation.  see issue 161.)
      slow_scrape_books = []
      fast_scrape_books = []
      if self.config.fast_rescrape_b:
         for book in books:
            if book.skip_b or book.issue_ref:
               fast_scrape_books.append(book)
            else:
               slow_scrape_books.append(book)
      else:
         slow_scrape_books = list(books)
      
      slow_scrape_books.sort(cmp=__compare_books)     
      fast_scrape_books.sort(cmp=__compare_books)     
      
      return fast_scrape_books+slow_scrape_books



   # ==========================================================================   
   def __choose_series_ref(self, book, search_terms_s, series_refs):
      '''
      This method displays the SeriesForm, a dialog that shows all of the
      SeriesRefs from a database query and asks the user to choose one.
      
      'book' -> the book that we are currently scraping
      'search_terms_s' -> the search terms we used to find the SeriesRefs
      'series_refs' -> a set of SeriesRefs; the results of the search
      
      This method returns a SeriesFormResult object (from the SeriesForm). 
      '''
      
      
      result = SeriesFormResult("SEARCH") # default
      if series_refs:
         log.debug('displaying the series selection dialog...')
         with  SeriesForm(self, book, series_refs, search_terms_s) as sform:
            result = sform.show_form() 
         log.debug('   ...user chose to ', result.get_debug_string())
      return result



   # ==========================================================================   
   def __choose_issue_ref(self, book, series_ref, issue_refs, force_b):
      '''
      This method chooses the IssueRef that matches the given book from among 
      the given set of IssueRefs.  It may do this automatically if it can, or 
      it may display the IssueForm, a dialog that displays the IssueRefs and 
      asks the user to choose one.
      
      'book' -> the book that we are currently scraping
      'series_ref_s' -> the SeriesRef for the given set of issue refs
      'issue_refs' -> a set of IssueRefs; if empty, it MAY be filled with
          the issue refs for the given series ref, if non-empty, this is the
          list of IssueRefs we'll be choosing from.
      'force_b' -> whether we should force the IssueForm to be shown, or 
                   only show it when we have no choice.
      
      This method returns a IssueFormResult object (from the IssueForm). 
      '''

      result = None  # the return value; must start out null
      
      series_name_s = series_ref.series_name_s
      issue_num_s = '' if not book.issue_num_s else book.issue_num_s
      if issue_refs == None: raise "issue_refs must be a set we can populate"

      # 1. are our issue refs empty? if so, and we're not forced to display
      #    the IssueForm, then try the shortcut way to find the right issue ref.
      #    if that fails, get all the issue refs for this series (so we can
      #    search for the issue the long way.)  
      if len(issue_refs) == 0 and issue_num_s and not force_b:
         issue_ref = db.query_issue_ref(series_ref, book.issue_num_s)
         if issue_ref:
            result = IssueFormResult("OK", issue_ref) # found it!
            log.debug("   ...identified issue number ", issue_num_s )
            
      # 2. if we don't have our issue_refs yet, and we're going to be 
      #    displaying the issue dialog, then get the issue_refs
      if len(issue_refs) == 0 and (not result or force_b):
         for ref in self.__query_issue_refs(series_ref):
            issue_refs.add(ref) # do NOT make a new set here!
         if self.__cancelled_b: 
            result = IssueFormResult("CANCEL")
         elif len(issue_refs) == 0:
            MessageBox.Show(self.comicrack.MainWindow,
            i18n.get("NoIssuesAvailableText").format(series_name_s),
            i18n.get("NoIssuesAvailableTitle"), MessageBoxButtons.OK, 
               MessageBoxIcon.Warning)
            result = IssueFormResult("BACK")
            log.debug("   ...no issues in this series; user must go back")

      # 3. try to find the issue number directly in the given issue_refs.  
      if not result and len(issue_refs) > 0 and issue_num_s:
         counts = {}
         for ref in issue_refs:
            counts[ref.issue_num_s] = counts.get(ref.issue_num_s, 0) + 1
         if issue_num_s in counts and counts[issue_num_s] > 1:
            # the same issue number appears more than once! user must pick.
            log.debug("   ...found more than one issue number ", issue_num_s, )
         else:
            for ref in issue_refs:
               # use natural keys for issue comparison
               if natural_key(ref.issue_num_s) == natural_key(issue_num_s):
                  result = IssueFormResult("OK", ref) # found it!
                  log.debug("   ...identified issue number ", issue_num_s, )
                  break

      # 4. if we don't know the issue number, and there is only one issue in 
      # the series, then it is very likely that the database simply has no issue
      # *number* for the book (this happens a lot).  the user has already seen
      # the cover for this issue in the series dialog and chosen it, so no 
      # point in making them choose it again...just use the one choice we have
      if not result and not issue_num_s and len(issue_refs)==1:
         result = IssueFormResult("OK", list(issue_refs)[0])

      # 5. if we are forced to, or we have no result yet, display IssueForm
      if not result or force_b:
         if len(issue_refs) == 0:
            result = IssueFormResult("BACK") # shouldn't happen
         else:
            if not force_b:
               log.debug("   ...could not identify issue number automatically")
            hint = result.get_ref() if result else None
            log.debug("displaying the issue selection dialog...")
            with IssueForm(self, hint, issue_refs, series_ref) as issue_form:
               result = issue_form.show_form()
               result = result if result else IssueFormResult("BACK")
            log.debug('   ...user chose to ', result.get_debug_string())

      return result # will not be None now



   # ==========================================================================   
   def __query_series_refs(self, search_terms_s):
      '''
      This method queries the online database for a set of SeriesRef objects
      that match the given (non-empty) search terms.   It will return a set 
      of SeriesRefs, which may be empty if no matches could be found.
      '''
      if not search_terms_s:
         raise Exception("cannot query for empty search terms")
      
      # 1. query the database for series
      with ProgressBarForm(self.comicrack.MainWindow, self) as progbar:
         # this function gets called each time an series_ref is obtained
         def callback(num_matches_n, expected_callbacks_n):
            if not self.__cancelled_b:
               if not progbar.Visible:
                  progbar.pb.Maximum = expected_callbacks_n
                  progbar.show_form()
               if progbar.Visible and not self.__cancelled_b:
                  progbar.pb.PerformStep()
                  progbar.Text = \
                     i18n.get("SearchProgbarText").format(sstr(num_matches_n))
            Application.DoEvents()
            return self.__cancelled_b
         log.debug("searching for series that match '", search_terms_s, "'...")
         
         series_refs = db.query_series_refs( search_terms_s,
            self.config.ignored_searchterms_sl, callback )
         
      # 2. filter out any series that the user has specified
      filtered_refs = dbutils.filter_series_refs(series_refs,
         self.config.ignored_publishers_sl, 
         self.config.ignored_before_year_n,
         self.config.ignored_after_year_n,
         self.config.never_ignore_threshold_n)
      
      # 3. some userful debug output
      filtered_n = len(series_refs) - len(filtered_refs) 
      if filtered_n > 0:
         log.debug("...filtered out ", filtered_n, " (of ", 
            len(series_refs), ") results.")
      if len(filtered_refs) == 0:
         log.debug("...no results found for this search")
      else:
         log.debug("...found {0} results".format(len(filtered_refs)))
      return filtered_refs



   # ==========================================================================   
   def __query_issue_refs(self, series_ref):
      '''
      This method queries the online database for a set of IssueRef objects
      that match the given SeriesRef.   The returned set may be empty if no 
      matches were found.
      '''
      
      log.debug("finding all issues for '", series_ref, "'...")
      with ProgressBarForm(self.comicrack.MainWindow, self) as progform:
         def callback(complete_ratio_n):
            complete_ratio_n = max(0.0, min(1.0, complete_ratio_n))
            if complete_ratio_n < 1.0 and not progform.Visible\
                  and not self.__cancelled_b:
               progform.pb.Maximum = 100
               progform.pb.Value = complete_ratio_n * 100
               progform.show_form()
            if progform.Visible and not self.__cancelled_b:
               progform.pb.Value = complete_ratio_n * 100
               progform.Text = i18n.get("IssuesProgbarText")\
                  .format(sstr((int)(complete_ratio_n * 100)))
            Application.DoEvents()
            return self.__cancelled_b
         issue_refs = db.query_issue_refs(series_ref, callback)
         log.debug("   ...found ", len(issue_refs), " issues at comicvine.gamespot.com")
         return issue_refs


   # =============================================================================
   def __wait_until_ready(self):
      '''
      Waits until a fixed amount of time has passed since this function was 
      last called.  Returns immediately if that much time has already passed.
      '''
      done_time_ms = (DateTime.Now-DateTime(1970,1,1)).TotalMilliseconds \
         + self.config.scrape_delay_n*1000
      now_ms = (DateTime.Now-DateTime(1970,1,1)).TotalMilliseconds
      
      while now_ms < done_time_ms and not self.__cancelled_b: 
         t = Thread(ThreadStart(lambda x=0: Thread.CurrentThread.Sleep(500)))
         t.Start()
         t.Join()         
         now_ms = (DateTime.Now-DateTime(1970,1,1)).TotalMilliseconds         
         

# ==========================================================================
class ScrapedSeries(object):
   '''
   An object that contains all the scraped information for a particular 
   ComicBook series--that is, the SeriesRef for the particular series, 
   and all of the IssueRefs that are associated with that series.
   '''
   def __init__(self, series_ref = None):
      self.series_ref = series_ref  
      self.issue_refs = set()
 

# ==========================================================================
class BookStatus(object):
   '''
   A status object used to represent the various states that a book can be in 
   while the scraper is running or finished.
   '''
    
   #===========================================================================         
   def __init__(self, id, failed_search_terms_s=""):
      ''' 
      Creates a new BookStatus object with the given ID.
      
      id -> the status ID.  Must be one of "SCRAPED" (book was successfully 
            scraped), "SKIPPED" (user chose to skip this book), "UNSCRAPED" 
            (hasn't been scraped yet) or "DELAYED" (hasn't been scraped, try
            again later).
      failed_search_terms_s -> (optional) the series search terms that couldn't 
            be found, if there are any.  This only makes sense in certain cases
            where the id is "UNSCRAPED". 
      '''  
            
      if id != "SCRAPED" and id != "SKIPPED" and \
            id != "UNSCRAPED" and id != "DELAYED":
         raise Exception()
      
      self.__id = id
      self.__failed_search_terms_s = failed_search_terms_s \
          if id=="UNSCRAPED" and utils.is_string(failed_search_terms_s) else ""
      
   #===========================================================================         
   def __str__(self):
      return self.__id
      
   #===========================================================================         
   def equals(self, id):
      ''' 
      Returns True iff this BookStatus has the given ID (i.e. one of "SCRAPED",
      "UNSCRAPED", "SKIPPED", or "DELAYED").
      '''
      return self.__id == id

  
   #===========================================================================         
   def get_failed_search_terms_s(self):
      '''
      Get the series search terms that could not be found in the comic database,
      leading to this BookStatus's "UNSCRAPED" status.   This value will be "" 
      there are no failed search terms, OR if our status is not "UNSCRAPED".
      '''
      return self.__failed_search_terms_s
