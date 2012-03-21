'''
This module is home to the ScrapeEngine class.
@author: Cory Banack
'''
import clr

import log
from utils import sstr
from resources import Resources 
from configuration import Configuration
from comicform import ComicForm
from seriesform import SeriesForm, SeriesFormResult
from issueform import IssueForm, IssueFormResult
from progressbarform import ProgressBarForm
from searchform import SearchForm
import utils
import db
from welcomeform import WelcomeForm
from finishform import FinishForm
import i18n
from matchscore import MatchScore
from comicbook import ComicBook

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import Application, MessageBox, \
    MessageBoxButtons, MessageBoxIcon

clr.AddReference('System')
from System.IO import Path
    
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
      
      This method is thread safe.
      '''
      
      if not self.__cancelled_b:
         def delegate(): 
            if not self.__cancelled_b:
               self.__cancelled_b = True;
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
         log.debug("Running As:          ", "Standalone Application" if 
            Resources.STANDALONE_MODE else "ComicRack Plugin (CR version " +
            self.comicrack.App.ProductVersion + ")")
         log.debug("Cache Directory:     ", Resources.LOCAL_CACHE_DIRECTORY)
         log.debug("Settings File:       ", Resources.SETTINGS_FILE)
         log.debug("-"*80)
         log.debug()

         # do the main part of the script
         if books:
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
      
      This method returns a list containing two integers.  The first integer 
      is the number of books that were scraped, the second is the number that 
      were skipped over. 
      '''
      
      # initialize the status member variable, and then keep it up-to-date 
      # from now on (so that it can be used to report the status of this 
      # scrape, even if an error occurs.)
      self.__status = [0, len(books)];
      # 1. load the currently saved configuration settings from disk
      self.config = Configuration()
      self.config.load_defaults()
      
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
            return # user cancelled the scrape

      # 3. print the entire configuration to the debug stream
      log.debug(self.config)
      log.debug()
      
      # 4. sort the ComicBooks in the order that we're gonna loop them in
      #    (sort AFTER config is loaded cause config affects the sort!)
      books = [ ComicBook(book, self) for book in books ]
      books = self.__sort_books(books) 

      # 5. display the ComicForm dialog.  it is a special dialog that stays 
      #    around for the entire time that the this scrape operation is running.
      comic_form = ComicForm.show_threadsafe(self)
      
      try:
         # this caches the scraped data we've accumulated as we loop
         scrape_cache = {}
         
         # 6. start the "Main Processing Loop". 
         #    notice the list of books can get longer while we're looping,
         #    if we choose to delay processing a book until the end.
         i = 0;
         orig_length = len(books)
         while i < len(books):
            if self.__cancelled_b: break
            book = books[i]

            # 6a. notify 'start_scrape_listeners' that we're scraping a new book
            
            log.debug("======> scraping next comic book: '",
               'FILELESS ("' + book.series_s +" #"+ book.issue_num_s+ ''")"
               if book.path_s == "" else Path.GetFileName(book.path_s),"'")
            num_remaining = len(books) - i
            for start_scrape in self.start_scrape_listeners:
               start_scrape(book, num_remaining)

            # 6b. ...keep trying to scrape that book until either it is scraped,
            #     the user chooses to skip it, or the user cancels altogether.
            manual_search_b = self.config.specify_series_b
            fast_rescrape_b = self.config.fast_rescrape_b and i < orig_length
            bookstatus = BookStatus("UNSCRAPED")
            
            while bookstatus.equals("UNSCRAPED") and not self.__cancelled_b:
               bookstatus = self.__scrape_book(book, scrape_cache,
                 manual_search_b, fast_rescrape_b, bookstatus)
               
               if bookstatus.equals("UNSCRAPED"):
                  # this return code means 'no series could be found using 
                  # the current (automatic or manual) search terms'.  when  
                  # that happens, force the user to chose the search terms.
                  manual_search_b = True
               elif bookstatus.equals("SCRAPED"):
                  # book was scraped normally, all is good, update status
                  self.__status[0] += 1;
                  self.__status[1] -= 1;
               elif bookstatus.equals("SKIPPED"):
                  # book was skipped, status is already correct for that book
                  pass;
               elif bookstatus.equals("DELAYED"):
                  # put this book into the end of the list, where we can try
                  # rescraping (with fast_rescrape_b set to false this time)
                  # after we've handled the ones that we can do automatically.
                  books.append(book)
            log.debug()
            log.debug()
            i = i + 1
            
      finally:
         self.comicrack.MainWindow.Activate() # fixes issue 159
         if comic_form: comic_form.close_threadsafe()



   # ==========================================================================
   def __scrape_book(self, book, scrape_cache, 
         manual_search_b, fast_rescrape_b, prev_status=None):
      '''
      This method is the heart of the Main Processing Loop. It scrapes a single
      ComicBook object by first figuring out which issue entry in the database 
      matches that book, and then copying those details into the ComicBook 
      object's metadata fields.  
      
      The steps involved are:
      
       1.  Come up with search terms for the given 'book'
            - if 'manual_search_b' then guess the terms based on the book's name
            - else ask the user to provide search terms
       2.  Search database for all comic series that match those search terms.
       3.  Ask the user which of the resulting series is the correct one
       4a. If the user picks a series:
            - we guess which issue in that series matches our ComicBook, OR
            - we ask the user to specify the correct issue (if we can't guess)
       4b. Else the use might decide to skip scraping this book.
       4c. Else the user might decide to start over with new search terms
       4d. Else the user might choose to specify the correct issue manually
       4e. Else the user might cancel the entire operation
             
       Throughout this process, the 'scrape_cache' (a map, empty at first) is
       used to speed things up.  It caches details from previous calls to this 
       method, so if this method is called repeatedly, the same scrape_cache 
       should be passed in each time.
       
       Iff 'fast_rescrape_b' is set to true, this method will attempt to find 
       and use any database key that was written to the book during a previous
       scrape.  This key allows us to instantly identify a comic, thus skipping
       the steps described above.  If no key is available, just fall back to
       the user-interactive method of identifying the comic.
       
       When this method is called repeatedly on the same book, a 'prev_status'
       should be passed in, giving this method access to the BookStatus object 
       that it returned the last time it was called (for the current book). 
       
       RETURN VALUES
       
       BookStatus("UNSCRAPED"): if the book wasn't be scraped, either because
          the search terms yielded no results, or the user opted to specify
          new search terms
          
       BookStatus("SKIPPED"): if this one book was skipped over by the user, or  
          of the user cancelled the entire current scrape operation (check the
          status if the ScrapeEngine).
          
       BookStatus("SCRAPED"): if the book was scraped successfully, and now 
          contains updated metadata.
          
       BookStatus("DELAYED"): if we attempted to do a fast_rescrape on the book,
          but failed because the database key was invalid.  the book has not
          been scraped successfully.
          
       
      '''

      # WARNING:  THE CODE IN THIS METHOD IS EXTREMELY SUBTLE.
      # Be sure you understand EVERYTHING that's going on and why before you
      # try to change anything in here.  You've been warned!
      
      Application.DoEvents()
      if self.__cancelled_b: return BookStatus("SKIPPED")
      if prev_status == None: prev_status = BookStatus("UNSCRAPED")

      # 1. if this book is being 'rescraped', sometimes it already knows the 
      #    correct issue_ref from a previous scrape. METHOD EXIT: if that 
      #    rescrape issue_ref is available, we use it immediately and exit. and 
      #    if the issue_ref is the string "skip", we skip this book.
      if book.skip_b: 
         log.debug("found SKIP tag, so skipping the scrape for this book.")
         return BookStatus("SKIPPED")

      issue_ref = book.issue_ref
      if issue_ref and fast_rescrape_b:
         log.debug("found rescraping details in book, using: "+sstr(issue_ref));
         try:
            issue = db.query_issue(issue_ref, self.config.update_rating_b)
            book.update(issue)
            return BookStatus("SCRAPED")
         except:
            log.debug_exc("Error rescraping details:")
            log.debug("we'll retry scraping this book again at the end.")
            return BookStatus("DELAYED")


      # 2. search for all the series in the database that match the current
      #    book.  if info for this book's series has already been cached, we 
      #    can skip this step.  METHOD EXIT: if we show the user the 'search' 
      #    dialog, she may use it to skip this book or cancel the whole scrape.
      search_terms_s = None
      series_refs = None
      key = book.unique_series_s
      if key in scrape_cache and not self.config.scrape_in_groups_b:
         # uncaching this key forces the scraper to treat this comic series
         # as though this was the first time we'd seen it
         del scrape_cache[key]
   
      # 3. check to see if this book has an special file in it's folder that
      #    tells us what series the book belongs to.  if so, add the series to 
      #    our scrape_cache, which causes us to skip the "Choose Series" form.      
      magic_series_ref = db.check_magic_file(book.path_s)
      if magic_series_ref:        
         log.debug("a 'magic' file identified this book's series as: '",
              magic_series_ref, "'")
         scraped_series = ScrapedSeries()
         scraped_series.series_ref = magic_series_ref
         scrape_cache[key] = scraped_series
          
      if key not in scrape_cache: 
         # get search terms for the book that we're scraping
         search_terms_s = book.series_s
         if manual_search_b or not search_terms_s:
            # show dialog asking the user for the right search terms
            log.debug('asking user for series search terms...');
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

      # 4. now that we have a set if series_refs that match this book, 
      #    show the user the 'series dialog' so they can pick the right one.  
      #    put the chosen series into the cache so the user won't have to 
      #    pick it again for any future books that are in this book's series.
      #    METHOD EXIT: while viewing the series dialog, the user might skip,
      #    request to re-search, or cancel the entire scrape operation.
      while True:
         force_issue_dialog_b = False 
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
               scraped_series = ScrapedSeries()
               scraped_series.series_ref = series_form_result.get_ref()
               force_issue_dialog_b = series_form_result.equals("SHOW")
               scrape_cache[key] = scraped_series
               
         # one way or another, the chosen series is now in the cache. get it.      
         scraped_series = scrape_cache[key]


         # 5. now that we know the right series for this book, query the 
         #    database for the issues in that series. then try to pick one, 
         #    either  automatically, or by showing the use the "issues dialog".
         #    also, cache the issue data, so we don't have to query again if we 
         #    scrape another book from this series.  METHOD EXIT: if the user 
         #    sees the query dialog, she may skip, cancel the whole scrape, 
         #    go back to the series dialog, or actually an issue.
         log.debug("searching for the right issue in '", 
            scraped_series.series_ref, "'")
         
         # get the issue refs for our chosen series
         if not scraped_series.issue_refs:
            scraped_series.issue_refs = \
               self.__query_issue_refs(scraped_series.series_ref)
            if self.__cancelled_b: 
               return BookStatus("SKIPPED")

         # choose the issue that matches the book we are scraping
         issue_form_result = self.__choose_issue_ref( book, 
            scraped_series.series_ref, scraped_series.issue_refs, 
            force_issue_dialog_b)
         
         if issue_form_result.equals("CANCEL") or self.__cancelled_b:
            self.__cancelled_b = True
            return BookStatus("SKIPPED")
         elif issue_form_result.equals("SKIP") or \
               issue_form_result.equals("PERMSKIP"):
            if force_issue_dialog_b:
               # the user clicked 'show issues', then 'skip', so we have to
               # ignore his previous series selection.
               del scrape_cache[key]
            if issue_form_result.equals("PERMSKIP"):
               book.skip_forever()
            return BookStatus("SKIPPED")
         elif issue_form_result.equals("BACK"):
            # ignore users previous series selection
            del scrape_cache[key]
         else:
            # we've got the right issue!  copy it's data into the book.
            log.debug("querying comicvine for issue details...")
            issue = db.query_issue( issue_form_result.get_ref(), 
               self.config.update_rating_b )
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
      it may display the IssueForm, a dialog that display the IssueRefs and 
      asks the user to choose one.
      
      'book' -> the book that we are currently scraping
      'series_ref_s' -> the SeriesRef for the given set of issue refs
      'issue_refs' -> a set of IssueRefs; the ones we're choosing from
      'force_b' -> whether we should force the IssueForm to be shown, or 
                   only show it when we have no choice.
      
      This method returns a IssueFormResult object (from the IssueForm). 
      '''

      result = None;  # the return value; must start out null
      
      series_name_s = series_ref.series_name_s
      issue_num_s = '' if not book.issue_num_s else book.issue_num_s


      # 1. try to find the issue number directly in the given issue_refs.  
      if issue_num_s:
         counts = {}
         for ref in issue_refs:
            counts[ref.issue_num_s] = counts.get(ref.issue_num_s, 0) + 1
         if issue_num_s in counts and counts[issue_num_s] > 1:
            # the same issue number appears more than once! user must pick.
            log.debug("   ...found more than one issue number ", issue_num_s, )
            issue_refs = \
               [ref for ref in issue_refs if ref.issue_num_s == issue_num_s]
         else:
            for ref in issue_refs:
               # strip leading zeroes (see issue 81)
               if ref.issue_num_s.lstrip('0') == issue_num_s.lstrip('0'):
                  result = IssueFormResult("OK", ref) # found it!
                  log.debug("   ...identified issue number ", issue_num_s, )
                  break

      # 2. if we don't know the issue number, and there is only one issue in 
      # the series, then it is very likely that the database simply has no issue
      # *number* for the book (this happens a lot).  the user has already seen
      # the cover for this issue in the series dialog and chosen it, so no 
      # point in making them choose it again...just use the one choice we have
      if len(issue_refs) == 1 and not issue_num_s and not force_b:
         result = IssueFormResult("OK", list(issue_refs)[0])

      # 3. if there are no issue_refs and that's a problem; tell the user
      if len(issue_refs) == 0:
         MessageBox.Show(self.comicrack.MainWindow,
         i18n.get("NoIssuesAvailableText").format(series_name_s),
         i18n.get("NoIssuesAvailableTitle"), MessageBoxButtons.OK, 
         MessageBoxIcon.Warning)
         result = IssueFormResult("BACK")
         log.debug("   ...no issues in this series; forcing user to go back")
      elif force_b or not result:
         # 4. if we are forced to, or we have no result yet, display IssueForm
         if not force_b:
            log.debug("   ...could not identify issue number automatically")
         hint = result.get_ref() if result else None
         log.debug("displaying the issue selection dialog...")
         with IssueForm(self, hint, issue_refs, series_name_s) as issue_form:
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
         series_refs = db.query_series_refs(search_terms_s, callback)
         
      # 2. filter out any series that the user has specified
      filtered_refs = set() 
      banned_publishers_sl = self.config.ignored_publishers_sl
      threshold_n = self.config.never_ignore_threshold_n
      ignored_before_n = self.config.ignored_before_year_n
      ignored_after_n = self.config.ignored_after_year_n
      for series_ref in series_refs:
         passes_filter = True
         if series_ref.issue_count_n < threshold_n:
            publisher_s = series_ref.publisher_s.lower().strip()
            passes_filter = True if publisher_s not in banned_publishers_sl \
               and series_ref.volume_year_n >= ignored_before_n \
               and series_ref.volume_year_n <= ignored_after_n else False
         if passes_filter:    
            filtered_refs.add(series_ref)
      
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
         # this function gets called each time another issue_ref is obtained
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
         return db.query_issue_refs(series_ref, callback)



# ==========================================================================
class ScrapedSeries(object):
   '''
   An object that contains all the scraped information for a particular 
   ComicBook series--that is, the SeriesRef for the particular series, 
   and all of the IssueRefs that are associated with that series.
   '''
   def __init__(self):
      self.series_ref = None  
      self.issue_refs = None
 

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
         raise Exception();
      
      self.__id = id
      self.__failed_search_terms_s = failed_search_terms_s \
          if id=="UNSCRAPED" and utils.is_string(failed_search_terms_s) else ""
      
      
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