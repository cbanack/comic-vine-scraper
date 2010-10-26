# corylow: comment and cleanup this file

import clr, re

import resources 
import log
from utils import sstr
from configuration import Configuration
from comicform import ComicForm
from seriesform import SeriesForm, SeriesFormResult
from issueform import IssueForm, IssueFormResult
from progressbarform import ProgressBarForm
from searchform import SearchForm, SearchFormResult
import utils
import db
import bookutils
from welcomeform import WelcomeForm

clr.AddReference('System')
from System import Array
from System.Collections import IComparer

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import Application, MessageBox, \
    MessageBoxButtons, MessageBoxIcon
    
    
# =============================================================================
class ScrapeEngine(object):
   '''
   This class contains the main program loop for the Comic Vine Scraper
   script.   Once initialized, you pass a collection of books to the 
   ScrapeEngine via the 'scrape' method.
   
   Those books will be processed one at a time, with windows and dialogs
   popping up to interact with the user as needed (including a single 
   ComicForm window, which is present the during the entire scrape to show
   the user which Comic Book is currently being scraped.)
   '''

   # ==========================================================================
   def __init__(self, comicrack):
      '''
      Initializes this ScrapeEngine so it is ready to scrape.  It takes the 
      ComicRack application object as it's only parameter.
      '''
      
      # the Configuration details for this ScrapeEngine.  initialized at the 
      # start of the 'scrape' method; possibly again during the scrape   
      self.config = Configuration()
      
      # the ComicRack application object, i.e. the instance of ComicRack that
      # is running this script.  its API changes (infrequently) with CR version.
      self.comicrack = comicrack
      
      # a list of methods that will each be fired whenever the 'scrape' 
      # operation begins processing/scraping a new book. these methods should
      # look like:   'start_scrape(book, num_remaining)'
      # where 'book' is the new book being scraped and 'num_remaining' is the 
      # number of books left to scrape, including the one currently starting
      self.start_scrape_listeners = []

      # a list of no-argument methods that will each be fired when (and if) 
      # the scrape operation gets cancelled.
      self.cancel_listeners = []
      
      # this variable can be set by calling the 'cancel' method.  when it is 
      # set to true, it indicates that the entire script should be cancelled as 
      # soon as possible.  slow, major loops in the code should check this value
      # at frequent intervals.
      self.__cancelled_b = False


   # ==========================================================================
   def scrape(self, books):
      '''
      This is the entry-point to the ScraperEngine's main processing loop.
      
      A typical invocation of the scraper script will create a new ScraperEngine 
      object and then call this method on it ONCE, passing it a list of all the
      ComicBook objects that need to be scraped.   
      
      This method will then begin a conversation with the user, displaying
      various dialogs and asking the user for confirmation of each books 
      identity based on specific details that it has obtained from a remote
      database.
        
      Then for each confirmed book, the engine will copy ('scrape') the obtained
      details into the ComicBook itself, which ultimately causes ComicRack to 
      write those details out to the ComicBook's backing file.
      '''
      
      try:
         # a litte bit of logging to help make our debug logs more useful
         log.debug()
         log.debug("-"*80)
         log.debug("CV Scraper Version:  ", resources.SCRIPT_VERSION)
         log.debug("Comic Rack Version:  ", self.comicrack.App.ProductVersion)
         log.debug("Cache Directory:     ", resources.LOCAL_CACHE_DIRECTORY)
         log.debug("Settings File:       ", resources.SETTINGS_FILE)
         log.debug("-"*80)
         log.debug()

         # do the main part of the script
         if books:
            scrape_vs_skipped = self.__scrape(books)
            log.debug("SCRAPED ", scrape_vs_skipped[0], " BOOKS")
            log.debug("SKIPPED ", scrape_vs_skipped[1], " BOOKS")

         if self.__cancelled_b:
            print 'Scrape was cancelled by the user'
            MessageBox.Show(self.comicrack.MainWindow,
               'This scrape was cancelled.', 'Scrape cancelled.',
               MessageBoxButtons.OK, MessageBoxIcon.Information)
         else:
            print 'Scrape completed normally'
            MessageBox.Show(self.comicrack.MainWindow, 
               'This scrape is complete', 'Scrape Complete', 
               MessageBoxButtons.OK, MessageBoxIcon.Information)

      except Exception, ex:
         log.handle_error(ex)



   # ==========================================================================
   def cancel(self):
      '''
      This method cancels the ScrapeEngine's current (and future) scrape
      operations, causes the main processing loop to exit on the next iteration;
      all ComicBooks that haven't been scraped will be skipped.
      
      This method is thread safe.
      '''
      
      if not self.__cancelled_b:
         def delegate(): 
            if not self.__cancelled_b:
               self.__cancelled_b = True;
               for cancel_listener in self.cancel_listeners:
                  cancel_listener()
      utils.invoke(self.comicrack.MainWindow, delegate, True)



   # ==========================================================================
   def __scrape(self, books):
      '''
      The private implementation of the public 'scrape' method.
      
      This method returns a list containing two integers.  The first integer 
      is the number of books that were scraped, the second is the number that 
      were skipped over. 
      '''
      
      # how many books were scraped [0], and how many skipped over by user [1].
      scrape_vs_skip = [0,0];
      
      # 1. sort ComicBook so that all comics that are from the same series are
      #    grouped together.  we'll loop through them in this order
      Array.Sort(books, self._BookComparer())

      # 2. show the welcome form. in addition to being a friendly summary of 
      #    what's about to happen, it loads (and allows the user to tweak)
      #    the Configuration that we'll use for the remainder of this operation.
      with WelcomeForm(self.comicrack.MainWindow, books) as welcome_form:
         self.config = welcome_form.show_form()
         if self.config:
            # 2a. print the entire configuration to the debug stream
            log.debug(self.config)
            log.debug() 
         else:
            # 2b. a null config means the user cancelled the scrape
            self.__cancelled_b = True
            return scrape_vs_skip

      # 3. display the ComicForm dialog.  it is a special dialog that stays 
      #    around for the entire time that the this scrape operation is running.
      comic_form = ComicForm.show_threadsafe(self)
      try:
         
         # caches the scraped data we've accumulated as the loop progresses
         scrape_map = {}
         
         # 4. start the main ComicBook processing loop
         for i in range( len(books) ):
            if self.__cancelled_b: break
            book = books[i]

            # 4a. notify 'start_scrape_listeners' that we're scraping a new book
            log.debug("======> scraping next eComic book: '", book.FileName,"'")
            for start_scrape in self.start_scrape_listeners:
               start_scrape(book, len(books) - i)

            # 4b. ...keep trying to scrape that book until either it is scraped,
            #     the user chooses to skip it, or the user cancels altogether.
            manual_search = self.config.specify_series_b
            bookstatus = self._BookStatus.UNSCRAPED
            while bookstatus == self._BookStatus.UNSCRAPED \
                  and not self.__cancelled_b:
               
               bookstatus = self.__scrape_book( comic_form, book, 
                  manual_search, scrape_map)
               if self.__cancelled_b: 
                  scrape_vs_skip[1] += len(books)-i; # loop will end
               else:
                  if bookstatus == self._BookStatus.UNSCRAPED:
                     # this return code means 'no series could be found using 
                     # the current (automatic or manual) search terms'.  when  
                     # that happens, for the user to chose the search terms.
                     manual_search = True
                  elif bookstatus == self._BookStatus.SCRAPED:
                     scrape_vs_skip[0] += 1;
                  elif bookstatus == self._BookStatus.SKIPPED:
                     scrape_vs_skip[1] += 1;
            log.debug()
            log.debug()
            
      finally:
         if comic_form: comic_form.close_threadsafe()
         
      return scrape_vs_skip


   # ==========================================================================
   def __scrape_book(self, comic_form, book, manual_search, scrape_map):

      # WARNING:  THE CODE IN THIS METHOD IS EXTREMELY SUBTLE.
      # Be sure you understand EVERYTHING that's going on and why before you
      # try to change anything in here.  You've been warned!
      
      Application.DoEvents()
      if self.__cancelled_b: return self._BookStatus.SKIPPED

      issue_ref = bookutils.extract_issue_ref(book)

      # exit point 1: if the cv issue ID is the string "skip", that means this
      # issue should never be scraped, so skip it automatically
      if issue_ref == 'skip': 
         log.debug("found SKIP tag, so skipping the scrape for this book.")
         return self._BookStatus.SKIPPED

      # exit point 2: if the cv issue ID can be parsed directly out of the book
      if issue_ref and self.config.fast_rescrape_b:
         log.debug("found CVDB tag in book, " + 
            "scraping details directly: " + sstr(issue_ref));
         try:
            issue = db.query_issue(issue_ref)
            bookutils.save_issue_to_book(issue, book, self)
            return self._BookStatus.SCRAPED
         except:
            log.debug_exc("Error scraping details directly:")
            log.debug("Ignoring CVDB tag and falling back to normal search...")
            issue_ref = None # fall through to the next section

      # exit point 3: figure out if we're in a series that has already been
      # chosen by the user.  if not, get the search term for finding that series
      log.debug("no CVDB tag found in book, beginning search...")
      key = self._ScrapedSeries.build_mapkey(book)
      search_string = None
      series_refs = None
      if key in scrape_map and not self.config.scrape_in_groups_b:
         # removing this key forces the scraper to treat this comic series
         # as though this was the first time we'd seen it
         del scrape_map[key] 
      if key not in scrape_map: 
         # build a new series info for this key, and add it to the map
         search_string = book.ShadowSeries.strip()
         if manual_search or not search_string:
            search_string = self.__get_search_string(
               comic_form, book, search_string)
            if search_string == SearchFormResult.CANCEL:
               self.__cancelled_b = True
               return self._BookStatus.SKIPPED
            elif search_string == SearchFormResult.SKIP:
               return self._BookStatus.SKIPPED
         series_refs = self.__get_series_refs(search_string)
         if self.__cancelled_b: return self._BookStatus.SKIPPED
         if not series_refs:
            MessageBox.Show(self.comicrack.MainWindow,
               "Couldn't find any comic books that match the search terms:\n\n"\
               "     '" + search_string + "'\n\n"\
               "Be sure that these search terms are spelled correctly!\n\n"\
               "Searches should include part (or all) of a comic book's "\
               "title,\nbut NOT its issue number, publisher, publication "\
               "date, etc.",
               "Search Failed", MessageBoxButtons.OK, MessageBoxIcon.Warning)
            return self._BookStatus.UNSCRAPED



      # exit point 4: search comic vine for the series that match the search
      # term, and then force the user to pick one of them.  put that series
      # into the map so the user doesn't have to pick it again for any other
      # books that appear to be in the same series.
      while True:
         force_issue_dialog_b = False 
         if key not in scrape_map: 
            if not series_refs or not search_string:
               return self._BookStatus.UNSCRAPED # rare but possible, bug 77
            result = self.__choose_series_ref(
               comic_form, book, search_string, series_refs)
            
            if SeriesFormResult.CANCEL == result.get_name() or self.__cancelled_b:
               self.__cancelled_b = True
               return self._BookStatus.SKIPPED # user says 'cancel'
            elif SeriesFormResult.SKIP == result.get_name():
               return self._BookStatus.SKIPPED # user says 'skip this book'
            elif SeriesFormResult.SEARCH == result.get_name(): 
               return self._BookStatus.UNSCRAPED # user says 'search again'
            elif SeriesFormResult.SHOW == result.get_name() or \
                 SeriesFormResult.OK == result.get_name(): # user says 'ok'
               scraped_series = self._ScrapedSeries()
               scraped_series.series_ref = result.get_ref()
               force_issue_dialog_b = SeriesFormResult.SHOW == result.get_name()
               scrape_map[key] = scraped_series
         scraped_series = scrape_map[key]


         # exit point 5: get a list of issues for the chosen series, and then
         # chose one (automatically if possible, manually if needed or forced).
         # scrape its details and placed int the current book.
         log.debug("searching for the right issue in '", 
            scraped_series.series_ref, "'")
         
         if not scraped_series.issue_refs:
            scraped_series.issue_refs = self.__get_issue_refs(
               scraped_series.series_ref)
            if self.__cancelled_b: return self._BookStatus.SKIPPED

         result = self.__choose_issue_ref(comic_form, book.ShadowNumber,
            scraped_series.issue_refs, book, 
            scraped_series.series_ref.series_name_s, force_issue_dialog_b)
         if result.get_name() == IssueFormResult.CANCEL or self.__cancelled_b:
            self.__cancelled_b = True
            return self._BookStatus.SKIPPED
         elif result.get_name() == IssueFormResult.SKIP:
            if force_issue_dialog_b:
               # the user clicked 'show issues', then 'skip', so we have to
               # ignore his previous series selection.
               del scrape_map[key]
            return self._BookStatus.SKIPPED
         elif result.get_name() == IssueFormResult.BACK:
            # ignore users previous series selection
            del scrape_map[key]
         else:
            log.debug("querying comicvine for issue details...")
            issue = db.query_issue( result.get_ref() )
            bookutils.save_issue_to_book(issue, book, self)
            return self._BookStatus.SCRAPED

      raise Exception("should never get here")


   def __get_search_string(self, comic_form, book, initial_search_string):
      log.debug('asking user for series search term...');

      with SearchForm(self, initial_search_string) as search_form:
         new_terms = search_form.show_form() # blocks

      if new_terms == SearchFormResult.CANCEL:
         log.debug("...and the user clicked 'cancel'")
      elif new_terms == SearchFormResult.SKIP:
         log.debug("...and the user clicked 'skip'")
      else:
         log.debug("...the user provided: '", new_terms, "'")
      return new_terms


   def __get_series_refs(self, search_terms_s):
      ''' can return a empty list if search found nothing!'''
      with ProgressBarForm(self.comicrack.MainWindow, self, 1) as progbar:
         # this function gets called each time an issue ref is obtained
         def callback(num_matches_n, expected_callbacks_n):
            if not self.__cancelled_b:
               if not progbar.Visible:
                  progbar.prog.Maximum = expected_callbacks_n
                  progbar.show_form()
               if progbar.Visible and not self.__cancelled_b:
                  progbar.prog.PerformStep()
                  progbar.Text = \
                     'Searching Comic Vine (' + sstr(num_matches_n) + ' matches)'
            Application.DoEvents()
            return self.__cancelled_b
         
         search_terms_s = self.__cleanup_search_terms(search_terms_s, False)
         log.debug("searching for all series that match: '", search_terms_s, "'")
         series_refs = db.query_series_refs(search_terms_s, callback)
         if len(series_refs) == 0:
            altsearch_s = self.__cleanup_search_terms(search_terms_s, True);
            if altsearch_s != search_terms_s:
               log.debug("no results. trying alternate search: '", altsearch_s, "'")
               series_refs = db.query_series_refs(altsearch_s, callback)
         
      
      if len(series_refs) == 0:
         log.debug("no database results found for this search.  try again...")
      else:
         log.debug("database provided {0} results for the search"\
            .format(len(series_refs)))
      return series_refs
   

   def __choose_series_ref(self, comic_form, book, search_string, series_refs):
      result = SeriesFormResult(SeriesFormResult.SEARCH) # default
      if series_refs:
         log.debug('displaying the series selection dialog...')
         with  SeriesForm(self, book, series_refs, search_string) as sform:
            result = sform.show_form()
         log.debug('   ...chose to ', result.get_debug_string())
      return result


   def __get_issue_refs(self, series_ref):
      
      # a note about the returned pairs:  (issue_id, issue_num), where issue_num
      # can be '' in rare cases.  both are strings.
      log.debug("querying comicvine for all available issues...")
      with ProgressBarForm(self.comicrack.MainWindow, self, 1) as progform:
         
         # this function gets called each time an issue ref is obtained
         def callback(complete_ratio_n):
            complete_ratio_n = max(0.0, min(1.0, complete_ratio_n))
            if complete_ratio_n < 1.0 and not progform.Visible\
                  and not self.__cancelled_b:
               progform.prog.Maximum = 100
               progform.prog.Value = complete_ratio_n * 100
               progform.show_form()
            if progform.Visible and not self.__cancelled_b:
               progform.prog.Value = complete_ratio_n * 100
               progform.Text = 'Loading Series Details (' + \
                  sstr((int)(complete_ratio_n * 100)) + "% complete)"
            Application.DoEvents()
            return self.__cancelled_b
         return db.query_issue_refs(series_ref, callback)


   def __choose_issue_ref(self, comic_form, issue_num_s, issue_refs, \
         book, series_name_s, force_b):

      issue_num_s = '' if not issue_num_s else issue_num_s.strip()
      log.debug("trying to find issue ID for issue number: ", issue_num_s)

      result = None

      # try to find the issue ID in the issue_refs
      if issue_num_s:
         # grab all the "unsafe" issue numbers 
         # (the duplicates, which are rare but possible).
         counts = {}
         for ref in issue_refs:
            counts[ref.issue_num_s] = counts.get(ref.issue_num_s, 0) + 1
         if issue_num_s in counts and counts[issue_num_s] > 1:
            issue_refs = [ref for ref in issue_refs \
                  if ref.issue_num_s == issue_num_s]
         else:
            for ref in issue_refs:
               # strip leading zeroes (see issue 81)
               if ref.issue_num_s.lstrip('0') == issue_num_s.lstrip('0'):
                  result = IssueFormResult(IssueFormResult.OK, ref) # found it!
                  break

      # if we don't know the issue number, and there is only one issue in the
      # series, then it is very likely that comic vine simply has no issue
      # number for that book (this happens a lot).  the user has already seen
      # the cover for this issue in the series dialog and chosen it, so no 
      # point in making them choose it again...just use the one choice we have
      if len(issue_refs) == 1 and not issue_num_s and not force_b:
         result = IssueFormResult(IssueFormResult.OK, list(issue_refs)[0])

      if len(issue_refs) == 0:
         MessageBox.Show(self.comicrack.MainWindow,
         "You selected '" + series_name_s + "'.\n\n"
         "This series cannot be displayed because it does not \n"
         "contain any issues in the Comic Vine database.\n\n"
         "You can add missing issues at: http://comicvine.com/",
         "Series has No Issues", MessageBoxButtons.OK, MessageBoxIcon.Warning)
         result = IssueFormResult(IssueFormResult.BACK)
         log.debug("no issues in this series; forcing user to go back...")
      elif force_b or not result:
         forcing_s = ' (forced)' if force_b else ''
         hint = result.get_ref() if result else None
         log.debug("displaying the issue selection dialog", forcing_s, "...")
         with IssueForm(self, book, hint, issue_refs, 
               series_name_s) as issue_form:
            result = issue_form.show_form()
            result = result if result else IssueFormResult(IssueFormResult.BACK)
         log.debug('   ...chose to ', result.get_debug_string())

      return result


   def __cleanup_search_terms(self, search_terms_s, alt_b):
      # All of the symbols below cause inconsistency in title searches
      # alt_b means use the alternate search terms

      search_terms_s = search_terms_s.lower()
      search_terms_s = search_terms_s.replace('.', '')
      search_terms_s = search_terms_s.replace('_', ' ')
      search_terms_s = search_terms_s.replace('-', ' ')
      search_terms_s = re.sub(r'\b(vs\.?|versus|and|or|the|an|of|a|is)\b',
         '', search_terms_s)
      search_terms_s = re.sub(r'giantsize', r'giant size', search_terms_s)
      search_terms_s = re.sub(r'giant[- ]*sized', r'giant size', search_terms_s)
      search_terms_s = re.sub(r'kingsize', r'king size', search_terms_s)
      search_terms_s = re.sub(r'king[- ]*sized', r'king size', search_terms_s)
      search_terms_s = re.sub(r"directors", r"director's", search_terms_s)
      search_terms_s = re.sub(r"\bvolume\b", r"\bvol\b", search_terms_s)
      search_terms_s = re.sub(r"\bvol\.\b", r"\bvol\b", search_terms_s)

      # of the alternate search terms is requested, try to expand single number
      # words, and if that fails, try to contract them.
      orig_search_terms_s = search_terms_s
      if alt_b:
         search_terms_s = utils.convert_number_words(search_terms_s, True)
      if alt_b and search_terms_s == orig_search_terms_s:
         search_terms_s = utils.convert_number_words(search_terms_s, False)
         
      # strip out punctuation
      word = re.compile(r'[\w]{1,}')
      search_terms_s = ' '.join(word.findall(search_terms_s))
      
      return search_terms_s


   # ==========================================================================
   class _ScrapedSeries(object):
      '''
      An object that contains all the scraped information for a particular 
      ComicBook series--that is, the SeriesRef for the particular series, 
      and all of the IssueRefs that are associated with that series.
      '''
      def __init__(self):
         self.series_ref = None  
         self.issue_refs = None
 
      @classmethod
      def build_mapkey(cls, book):
         '''
         Constructs a "mapkey" for the given ComicBook.   The idea is that any 
         books that appear to be from the same series should have the same 
         mapkeys.  
         
         We can map these keys to _ScrapeSeries objects, and use the resulting
         map  as a cache to avoid rescraping for the same _ScrapedSeries
         object over and over again.
         '''
          
         sname = '' if not book.ShadowSeries else book.ShadowSeries
         if sname and book.ShadowFormat:
            sname += sstr(book.ShadowFormat)
         sname = re.sub('\W+', '', sname).lower()

         svolume = ''
         if sname:
            if book.ShadowVolume and book.ShadowVolume > 0:
               svolume = "[v" + sstr(book.ShadowVolume) + "]"
         else:
            # if we can't find a name at all (very weird), fall back to the
            # ComicRack ID, which should be unique and thus ensure that this 
            # comic doesn't get lumped in to the same series choice as any 
            # other unnamed comics! 
            sname = sstr(book.Id)
         return sname + svolume


   # ==========================================================================
   class _BookStatus(object):
      '''
      Constants used to represent the various states that a book can be in 
      while the scraper is running or finished.
      '''
      
      UNSCRAPED = "unscraped"   # hasn't been scraped yet
      SCRAPED = "scraped"   # successfully scraped
      SKIPPED = "skipped"   # user chose to skip this book


   # ==========================================================================
   class _BookComparer(IComparer):
      '''
      This class is used to sort ComicBook objects.  It is designed to sort
      them in order of increasing mapkeys, and where the mapkeys are the same,
      in order of increasing issue number. 
      '''

      def Compare(self, book1, book2):
         try:
            key1 = ScrapeEngine._ScrapedSeries.build_mapkey(book1)
            key2 = ScrapeEngine._ScrapedSeries.build_mapkey(book2)
            result = key1.CompareTo(key2)
            if result == 0:
               num1 = '' if not book1.ShadowNumber else sstr(book1.ShadowNumber)
               num2 = '' if not book2.ShadowNumber else sstr(book2.ShadowNumber)
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
         except Exception, ex:
            log.debug_exc("exception in BookComparer:")
            raise(ex)

