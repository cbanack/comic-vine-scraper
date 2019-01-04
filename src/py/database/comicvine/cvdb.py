#coding: utf-8
'''
This module contains ComicVine=based implementations of the the functions 
described in the db.py module.  That module can delegate its function calls to
the functions in this module, but other than that, external modules should 
NOT call these functions directly.
  
@author: Cory Banack
'''

import re
import clr
import cvconnection
import log
import utils
from utils import is_string, sstr 
from dbmodels import IssueRef, SeriesRef, Issue
from resources import Resources
import cvimprints

clr.AddReference('System')
from System.Net import WebRequest
from System.IO import Directory, File, Path, StreamReader
from System.Text import Encoding

clr.AddReference('System.Drawing')
from System.Drawing import Image

# this cache is used to speed up __issue_parse_series_details.  it is a 
# memory leak (until the main app shuts down), but it is small and worth it.
__series_details_cache = None

# comicvine has a tendency to return WAY too many search results, so we 
# limit the number returned.  set in _initialize() if user has overridden. 
__max_search_results = 100

# this is the comicvine api key to use when accessing the comicvine api.
# it is set when calling _initialize().
__api_key = ""


# =============================================================================
def _initialize(**kwargs):
   ''' 
   ComicVine implementation of the identically named method in the db.py 
   You must pass in a valid Comic Vine api key as a keyword argument to this
   method, like so:    _initialize(**{'cv_apikey','my-key-here'})
   '''
   global __series_details_cache, __api_key, __max_search_results
   __series_details_cache = {}
   if "cv_apikey" in kwargs: __api_key = kwargs["cv_apikey"] 
   if "cv_maxresults" in kwargs: __max_search_results = kwargs["cv_maxresults"] 
   
   if not __api_key: raise Exception("You must set a ComicVine API key!") 
   
# =============================================================================
def _shutdown():
   ''' ComicVine implementation of the identically named method in the db.py '''
   global __series_details_cache
   __series_details_cache = None
      

# =============================================================================
def _get_db_name_s():
   ''' ComicVine implementation of the identically named method in the db.py '''
   return "ComicVine";


# =============================================================================
def _create_key_tag_s(issue_key):
   ''' ComicVine implementation of the identically named method in the db.py '''
   try:
      return "CVDB" + utils.sstr(int(issue_key))
   except:
      log.debug_exc("Couldn't create key tag out of: " + sstr(issue_key))
      return None


# =============================================================================
def _parse_key_tag(text_s):
   ''' ComicVine implementation of the identically named method in the db.py '''
   
   tag_found = re.search(r'(?i)CVDB(\d{1,})', text_s)
   if not tag_found:
      tag_found = re.search(r'(?i)ComicVine.?\[(\d{1,})', text_s); # old format!
   return int(tag_found.group(1).lower()) if tag_found else None


# =============================================================================
def _check_magic_file(path_s):
   ''' ComicVine implementation of the identically named method in the db.py '''
   series_ref = None
   file_s = None
   try:
      # 1. get the directory to search for a cvinfo file in, or None
      dir_s = path_s if path_s and Directory.Exists(path_s) else \
         Path.GetDirectoryName(path_s) if path_s else None
      dir_s = dir_s if dir_s and Directory.Exists(dir_s) else None
      
      if dir_s:
         # 2. search in that directory for a properly named cvinfo file
         #    note that Windows filenames are not case sensitive.
         for f in [dir_s + "\\" + x for x in ["cvinfo.txt", "cvinfo"]]:
            if File.Exists(f):
               file_s = f 
            
         # 3. if we found a file, read it's contents in, and parse the 
         #    comicvine series id out of it, if possible.
         if file_s:
            with StreamReader(file_s, Encoding.UTF8, False) as sr:
               line = sr.ReadToEnd()
               line = line.strip() if line else line
               series_ref = __url_to_seriesref(line)
   except:
      log.debug_exc("bad cvinfo file: " + sstr(file_s))
      
   if file_s and not series_ref:
      log.debug("ignoring bad cvinfo file: ", sstr(file_s))

   return series_ref # may be None!


# =============================================================================
def _query_series_refs(search_terms_s, callback_function):
   ''' ComicVine implementation of the identically named method in the db.py '''
   
   series_refs = set()
   
   # 1. clean up the search terms (to make them more palatable to comicvine
   # databases) before our first attempt at searching with them
   search_s = __cleanup_search_terms(search_terms_s, False)
   if search_s:
      
      # 2. first see if the search term is actually a comicvine url, from 
      #    which we can decode the correct series that the user wants.
      if not series_refs:
         series_ref = __url_to_seriesref(search_terms_s)
         if series_ref: series_refs.add(series_ref)
      
      # 3. if that didn't work, search comicvine directly
      if not series_refs:
         series_refs = __query_series_refs(search_s, callback_function)
      
      # 4. if that didn't work, cleanup terms more aggressively and try again
      if not series_refs:
         altsearch_s = __cleanup_search_terms(search_s, True);
         if search_terms_s and altsearch_s != search_s:
            series_refs = __query_series_refs(altsearch_s, callback_function)
            
   return series_refs # may be empty if nothing worked


# =============================================================================
def __query_series_refs(search_terms_s, callback_function):
   ''' A private implementation of the public method with the same name. '''

   global __max_search_results

   cancelled_b = [False]
   series_refs = set()
   
   # 1. do the initial query, record how many results in total we're getting
   num_results_n = 0
   if search_terms_s and search_terms_s.strip():
      dom = cvconnection._query_series_ids_dom(__api_key, search_terms_s, 1)
      num_results_n = int(dom.number_of_total_results)
      if not "volume" in dom.results.__dict__:
         num_results_n = 0 # bug 329 
   
   if num_results_n > 0:

      # 2. convert the results of the initial query to SeriesRefs and then add
      #    them to the returned list. notice that the dom could contain single 
      #    volume OR a list of volumes in its 'volume' variable.  
      if not isinstance(dom.results.volume, list):
         if len(series_refs) < __max_search_results:
            series_refs.add( __volume_to_seriesref(dom.results.volume) )
      else:
         for volume in dom.results.volume:
            if len(series_refs) < __max_search_results:
               series_refs.add( __volume_to_seriesref(volume) )

         # 3. if there were more than 100 results, we'll have to do some more 
         #    queries now to get the rest of them
         RESULTS_PAGE_SIZE = 100
         iteration = RESULTS_PAGE_SIZE
         if iteration < num_results_n:
            num_remaining_pages = num_results_n // RESULTS_PAGE_SIZE
            
            # 3a. do a callback for the first results (initial query)...
            cancelled_b[0] = callback_function(
               iteration, num_remaining_pages)

            while iteration < num_results_n and \
                  len(series_refs) < __max_search_results and \
                  not cancelled_b[0]:

               # 4. query for the next batch of results, in a new dom
               dom = cvconnection._query_series_ids_dom(__api_key,
                  search_terms_s, iteration//RESULTS_PAGE_SIZE+1)
               iteration += RESULTS_PAGE_SIZE
               
               # 4a. do a callback for the most recent batch of results
               cancelled_b[0] = callback_function(
                  iteration, num_remaining_pages)

               if "number_of_page_results" not in dom.__dict__ or \
                     int(dom.number_of_page_results) < 1 or \
                        not "volume" in dom.results.__dict__:
                  log.debug("WARNING: got empty results page") # issue 33, 396
               else:
                  # 5. convert the current batch of results into SeriesRefs,
                  #    and then add them to the returned list.  Again, the dom
                  #    could contain a single volume, OR a list.
                  if not isinstance(dom.results.volume, list):
                     if len(series_refs) < __max_search_results:
                        series_refs.add(
                           __volume_to_seriesref(dom.results.volume))
                  else:
                     for volume in dom.results.volume:
                        if len(series_refs) < __max_search_results:
                           series_refs.add( __volume_to_seriesref(volume) )
                        
   # 6. Done.  series_refs now contained whatever SeriesRefs we could find
   if not cancelled_b[0] and len( series_refs ) < num_results_n:
      log.debug("...too many matches, only getting ",
                "the first ", __max_search_results )

   return set() if cancelled_b[0] else series_refs   

   
# ==========================================================================   
def __volume_to_seriesref(volume):
   ''' Converts a cvdb "volume" dom element into a SeriesRef. '''
   publisher = '' if len(volume.publisher.__dict__) <= 1 else \
      volume.publisher.name
   return SeriesRef( int(volume.id), sstr(volume.name), 
      sstr(volume.start_year).rstrip("- "), # see bug 334 
      sstr(publisher), sstr(volume.count_of_issues), __parse_image_url(volume))


# ==========================================================================   
def __url_to_seriesref(url_s):
   ''' 
   Converts a ComicVine URL into a SeriesRef.  The URL has to contain
   a magic number of the form 4050-XXXXXXXX (a series) or 4000-XXXXXXXX
   (an issue.)   If the given URL has a usable magic number, use it to query
   the db and construct a SeriesRef for the series associated with that 
   number.  Returns none if the url couldn't be converted, for any reason. 
   '''
   series_ref = None
   
   # 1. try interpreting the url as a comicvine issue (i.e. 4000-XXXXXXXX)
   if not series_ref:
      url_s = url_s.strip()
      pattern=r"^.*?\b(4000)-(?<num>\d{2,})\b.*$"
         
      match = re.match(pattern, url_s, re.I)
      if match:
         issueid_s = match.group("num")
         try:
            dom = cvconnection._query_issue_details_dom( __api_key, issueid_s)
            num_results_n = int(dom.number_of_total_results)
            if num_results_n == 1:
               # convert url into the series id for this issue
               url_s = "4050-"+dom.results.volume.id
         except:
            pass # happens when the user enters an non-existent key

   # 2. now try interpreting the url as a comicvine series (4050-XXXXXX) 
   if not series_ref:
      url_s = url_s.strip()
      pattern=r"^.*?\b(49|4050)-(?<num>\d{2,})\b.*$"
         
      match = re.match(pattern, url_s, re.I)
      if match:
         seriesid_s = match.group("num")
         try:
            dom = cvconnection._query_series_details_dom(__api_key, seriesid_s)
            num_results_n = int(dom.number_of_total_results)
            if num_results_n == 1:
               series_ref = __volume_to_seriesref(dom.results)
         except:
            pass # happens when the user enters an non-existent key

   return series_ref


# ==========================================================================   
def __cleanup_search_terms(search_terms_s, alt_b):
   '''
   Returns a cleaned up version of the given search terms.  The terms are 
   cleaned by removing, replacing, and massaging certain keywords to make the
   Comic Vine search more likely to return the results that the user really
   wants.
   
   'search_terms_s' -> the search terms to clean up
   'alt_b' -> true to attempt to produce an alternate search string by also
              replacing numerical digits with their corresponding english words
              and vice versa (i.e. "8" <-> "eight")
   '''
   # all of the symbols below cause inconsistency in title searches
   search_terms_s = search_terms_s.lower()
   search_terms_s = re.sub(r" & ", ' and ', search_terms_s)
   search_terms_s = re.sub(r'\b(c2c|ctc|noads+|tbp)\b', '', search_terms_s)
   
   # if the alternate search terms is requested, try to expand single number
   # words, and if that fails, try to contract them.
   orig_search_terms_s = search_terms_s
   if alt_b:
      search_terms_s = utils.convert_number_words(search_terms_s, True)
   if alt_b and search_terms_s == orig_search_terms_s:
      search_terms_s = utils.convert_number_words(search_terms_s, False)
      
   # strip out most remaing punctuation
   word = re.compile(r"[\w':.-]{1,}")
   search_terms_s = ' '.join(word.findall(search_terms_s))
   
   return search_terms_s
  
     
# =============================================================================
def _query_issue_refs(series_ref, callback_function=lambda x : False):
   ''' ComicVine implementation of the identically named method in the db.py '''
   
   # a comicvine series key can be interpreted as an integer
   series_id_n = int(series_ref.series_key)
   cancelled_b = [False]
   issue_refs = set()
   
   # 1. do the initial query, record how many results in total we're getting
   dom = cvconnection._query_issue_ids_dom(__api_key, sstr(series_id_n), 1)
   num_results_n = int(dom.number_of_total_results) if dom else 0
   
   if num_results_n > 0:
    
      # 2. convert the results of the initial query to IssueRefs and then add
      #    them to the returned set. notice that the dom could contain single 
      #    issue OR a list of issues in its 'issue' variable.  
      if not isinstance(dom.results.issue, list):
         issue_refs.add( __issue_to_issueref(dom.results.issue) )
      else:
         for issue in dom.results.issue:
            issue_refs.add( __issue_to_issueref(issue) )

         # 3. if there were more than 100 results, we'll have to do some more 
         #    queries now to get the rest of them
         RESULTS_PAGE_SIZE = 100
         iteration = RESULTS_PAGE_SIZE
         if iteration < num_results_n:

            # 3a. do a callback for the first results (initial query)...
            cancelled_b[0] = callback_function( float(iteration)/num_results_n )

            while iteration < num_results_n and not cancelled_b[0]:
               # 4. query for the next batch of results, in a new dom
               dom = cvconnection._query_issue_ids_dom(__api_key, 
                  sstr(series_id_n), iteration//RESULTS_PAGE_SIZE+1)
               iteration += RESULTS_PAGE_SIZE
               
               # 4a. do a callback for the most recent batch of results
               cancelled_b[0] =callback_function(float(iteration)/num_results_n)

               if int(dom.number_of_page_results) < 1:
                  log.debug("WARNING: got empty results page")
               else:
                  # 5. convert the current batch of results into IssueRefs,
                  #    and then add them to the returned list.  Again, the dom
                  #    could contain a single issue, OR a list.
                  if not isinstance(dom.results.issue, list):
                     issue_refs.add(__issue_to_issueref(dom.results.issue))
                  else:
                     for issue in dom.results.issue:
                        issue_refs.add( __issue_to_issueref(issue) )
                        
   # 6. Done.  issue_refs now contained whatever IssueRefs we could find
   return set() if cancelled_b[0] else issue_refs



# ==========================================================================   
def __issue_to_issueref(issue):
   ''' Converts a cvdb "issue" dom element into an IssueRef. '''
   issue_num_s = issue.issue_number
   issue_num_s = issue_num_s.strip() if is_string(issue_num_s) else ''
   title_s = issue.name.strip() if is_string(issue.name) else ''
   return IssueRef(issue_num_s, issue.id, title_s, __parse_image_url(issue))


# =============================================================================
def query_issue_ref(series_ref, issue_num_s):
   ''' ComicVine implementation of the identically named method in the db.py '''
   series_key = series_ref.series_key  
   dom = cvconnection._query_issue_id_dom(__api_key, series_key, issue_num_s)
   num_results_n = int(dom.number_of_total_results) if dom else 0
   attempts = 1

   # try again if we didn't find anything
   while num_results_n == 0 and attempts <= 3:
      attempts += 1
      new_issue_num_s = __alternate_issue_num_s(issue_num_s)
      if new_issue_num_s == issue_num_s:
         break
      else:
         issue_num_s = new_issue_num_s
         dom = cvconnection._query_issue_id_dom(
                  __api_key, series_key, issue_num_s)
         num_results_n = int(dom.number_of_total_results) if dom else 0
         
   return __issue_to_issueref(dom.results.issue) if num_results_n==1 else None 


# =============================================================================
def __alternate_issue_num_s(issue_num_s):
   ''' 
   Computes an alternative form of the given issue number, i.e. '5.5' becomes
   '5½'.  If no alterative form is available, return the given issue_num_s.
   '''
   if re.match(r"0*.50*", issue_num_s):
      issue_num_s = "0½"
   elif issue_num_s == "½":
      issue_num_s = "0½"
   elif issue_num_s == "0½":
      issue_num_s = "½"
   else:
      issue_num_s = issue_num_s.replace(r'\.50*[^0-9]*$', '½')
      issue_num_s = issue_num_s.replace(r'\.250*[^0-9]*$', '¼')
      issue_num_s = issue_num_s.replace(r'\.750*[^0-9]*$', '¾')
   return issue_num_s

# =============================================================================
def _query_image( ref, lasttry = False ):
   ''' ComicVine implementation of the identically named method in the db.py '''
   
   retval = None # the Image object that we will return

   # 1. determine the URL   
   image_url_s = None
   if isinstance(ref, SeriesRef):
      image_url_s = ref.thumb_url_s
   elif isinstance(ref, IssueRef):
      image_url_s = ref.thumb_url_s
   elif is_string(ref):
      image_url_s = ref
   
   # 2. attempt to load the image for the URL
   if image_url_s:
      response = None
      response_stream = None
      try:
         cvconnection.wait_until_ready() # throttle our request speed 
         request = WebRequest.Create(image_url_s)
         request.UserAgent = "[ComicVineScraper, version " + \
         Resources.SCRIPT_VERSION + "]"
         response = request.GetResponse()
         response_stream = response.GetResponseStream()
         retval = Image.FromStream(response_stream)
      except:
         if lasttry:
            log.debug_exc('ERROR retry image load failed:')
            retval = None
         else:
            log.debug('RETRY loading image -> ', image_url_s)
            retval = _query_image( ref, True )
      finally: 
         if response: response.Dispose()
         if response_stream: response_stream.Dispose()

   # if this value is stil None, it means an error occurred, or else comicvine 
   # simply doesn't have any Image for the given ref object             
   return retval 


# =============================================================================
def _query_issue(issue_ref, slow_data):
   ''' ComicVine implementation of the identically named method in the db.py '''
   
   del slow_data; # unused 

   # interesting: can we implement a cache here?  could speed things up...
   issue = Issue(issue_ref)
   
   dom = cvconnection._query_issue_details_dom(
            __api_key, sstr(issue_ref.issue_key))
   __issue_parse_simple_stuff(issue, dom)
   __issue_parse_series_details(issue, dom)
   __issue_parse_story_credits(issue, dom)
   __issue_parse_summary(issue, dom)
   __issue_parse_roles(issue, dom)
   
   
   #    the commented code below once scraped additional cover images and 
   #    the community rating from Comic Vine directly. it did this by reading 
   #    in the contents of an html page on the Comic Vine website, rather
   #    than using part of the Comic Vine API.   This is against Comic 
   #    Vine's acceptable use policy (see issue 421, 
   #        https://github.com/cbanack/comic-vine-scraper/issues/421 )
   #
   #    I have removed this code to address this issue, but if Comic Vine
   #    ever gives us the option to access additional cover art or community
   #    ratings directly, the code below could be rewritten to get those details
   #    again, and then the features that rely on it will start using that data
   #    and working as they used to (the features affected are:  scraping
   #    community rating, auto-identification of comic series, and searching
   #    for additional covers for a particular issue.) 
   
   #if slow_data:
      # grab extra cover images and a community rating score
   #   page = cvconnection._query_issue_details_page(
   #             __api_key, sstr(issue_ref.issue_key))
   #   __issue_scrape_extra_details( issue, page )
   
   return issue


#===========================================================================
def __issue_parse_simple_stuff(issue, dom):
   ''' Parses in the 'easy' parts of the DOM '''

   if is_string(dom.results.id):
      issue.issue_key = dom.results.id
   if is_string(dom.results.volume.id):
      issue.series_key = dom.results.volume.id
   if is_string(dom.results.volume.name):
      issue.series_name_s = dom.results.volume.name.strip()
   if is_string(dom.results.issue_number):
      issue.issue_num_s = dom.results.issue_number.strip()
   if is_string(dom.results.site_detail_url) and \
         dom.results.site_detail_url.startswith("http"):
      issue.webpage_s = dom.results.site_detail_url
   if is_string(dom.results.name):
      issue.title_s = dom.results.name.strip();
      
   # grab the published (front cover) date
   if "cover_date" in dom.results.__dict__ and \
      is_string(dom.results.cover_date) and \
      len(dom.results.cover_date) > 1:
      try:
         parts = [int(x) for x in dom.results.cover_date.split('-')]
         issue.pub_year_n = parts[0] if len(parts) >= 1 else None
         issue.pub_month_n = parts[1] if len(parts) >=2 else None
         issue.pub_day_n = parts[2] if len(parts) >= 3 else None
      except:
         pass # got an unrecognized date format...? should be "YYYY-MM-DD"
      
   # grab the released (in store) date
   if "store_date" in dom.results.__dict__ and \
      is_string(dom.results.store_date) and \
      len(dom.results.store_date) > 1:
      try:
         parts = [int(x) for x in dom.results.store_date.split('-')]
         issue.rel_year_n = parts[0] if len(parts) >= 1 else None
         issue.rel_month_n = parts[1] if len(parts) >=2 else None
         issue.rel_day_n = parts[2] if len(parts) >= 3 else None
      except:
         pass # got an unrecognized date format...? should be "YYYY-MM-DD"
      
   # grab the image for this issue and store it as the first element
   # in the list of issue urls.
   image_url_s = __parse_image_url(dom.results)
   if image_url_s:
      issue.image_urls_sl.append(image_url_s)
      

#===========================================================================
def __issue_parse_series_details(issue, dom):
   ''' Parses the current comic's series details out of the DOM '''
   
   series_id = dom.results.volume.id
   
   # if the start year and publisher_s have been cached (because we already
   # accessed them once this session) use the cached values.  else
   # grab those values from comicvine, and cache em so we don't have to
   # hit comic vine for them again (at least not in this session)
   global __series_details_cache
   if __series_details_cache == None:
      raise Exception(__name__ + " module isn't initialized!")
   cache = __series_details_cache
   if series_id in cache:
      volume_year_n = cache[series_id][0]
      publisher_s = cache[series_id][1]
   else: 
      # contact comicvine to extract details for this comic book 
      series_dom = cvconnection._query_series_details_dom(__api_key, series_id)
      if series_dom is None:
         raise Exception("can't get details about series " + series_id)

      # start year
      volume_year_n = -1
      if "start_year" in series_dom.results.__dict__ and \
            is_string(series_dom.results.start_year):
         try:
            volume_year_n = int(series_dom.results.start_year)
         except:
            pass # bad start year format...just keep going
      
      # publisher
      publisher_s = ''
      if "publisher" in series_dom.results.__dict__ and \
         "name" in series_dom.results.publisher.__dict__ and \
         is_string(series_dom.results.publisher.name):
         publisher_s = series_dom.results.publisher.name
      
      cache[series_id] = (volume_year_n, publisher_s)
   
   # check if there's the current publisher really is the true publisher, or
   # if it's really an imprint of another publisher.
   issue.publisher_s = cvimprints.find_parent_publisher(publisher_s)
   if issue.publisher_s != publisher_s:
      issue.imprint_s = publisher_s
   issue.volume_year_n = volume_year_n


            
#===========================================================================               
def __issue_parse_story_credits(issue, dom):
   ''' 
   Parse the current comic's story arc/character/team/location 
   credits from the DOM. 
   '''

   # get any crossover details that might exist
   if ("story_arc_credits" in dom.results.__dict__) and \
      ("story_arc" in dom.results.story_arc_credits.__dict__) :
      issue.crossovers_sl = map( lambda x: x.name,
         __as_list(dom.results.story_arc_credits.story_arc) )

   # get any character details that might exist
   if ("character_credits" in dom.results.__dict__) and \
      ("character" in dom.results.character_credits.__dict__):
      issue.characters_sl = map( lambda x: x.name,
         __as_list(dom.results.character_credits.character) )
         
   # get any team details that might exist
   if ("team_credits" in dom.results.__dict__) and \
      ("team" in dom.results.team_credits.__dict__):
      issue.teams_sl = map( lambda x: x.name,
         __as_list(dom.results.team_credits.team) )
         
   # get any location details that might exist
   if ("location_credits" in dom.results.__dict__) and \
      ("location" in dom.results.location_credits.__dict__):
      issue.locations_sl = map( lambda x: x.name,
         __as_list(dom.results.location_credits.location) )


#===========================================================================            
def __issue_parse_summary(issue, dom):
   ''' Parse the current comic's summary details from the DOM. '''

   # grab the issue description, and do a bunch of modifications and 
   # replaces to massage it into a nicer "summary" text
#   PARAGRAPH = re.compile(r'<br />')
   OVERVIEW = re.compile('Overview')
   PARAGRAPH = re.compile(r'<[bB][rR] ?/?>|<[Pp] ?>')
   NBSP = re.compile('&nbsp;?')
   MULTISPACES = re.compile(' {2,}')
   STRIP_TAGS = re.compile('<.*?>')
   LIST_OF_COVERS = re.compile('(?is)list of covers.*$')
   if is_string(dom.results.description):
      summary_s = OVERVIEW.sub('', dom.results.description)
      summary_s = PARAGRAPH.sub('\n', summary_s)
      summary_s = STRIP_TAGS.sub('', summary_s)
      summary_s = MULTISPACES.sub(' ', summary_s)
      summary_s = NBSP.sub(' ' , summary_s)
      summary_s = PARAGRAPH.sub('\n', summary_s)
      summary_s = summary_s.replace(r'&amp;', '&')
      summary_s = summary_s.replace(r'&quot;', '"')
      summary_s = summary_s.replace(r'&lt;', '<')
      summary_s = summary_s.replace(r'&gt;', '>')
      summary_s = LIST_OF_COVERS.sub('', summary_s);
      issue.summary_s = summary_s.strip()
      
#===========================================================================         
def __issue_parse_roles(issue, dom):
   ''' Parse the current comic's creator roles from the DOM. '''
   
   # this is a dictionary of comicvine role descriptors, mapped to the 
   # 'issue' attribute names of the member variables that we want to 
   # assign the associated values to.  so any comicvine person with the
   # 'cover' role will, for example, be assigned to the issue.cover_artists
   #  attribute.
   ROLE_DICT = {'writer':['writers_sl'], 'penciler':['pencillers_sl'], \
      'artist':['pencillers_sl','inkers_sl'], 'inker':['inkers_sl'],\
      'cover':['cover_artists_sl'], 'editor':['editors_sl'],\
      'colorer':['colorists_sl'], 'colorist':['colorists_sl'],\
      'letterer':['letterers_sl']} 
   
   # a simple test to make sure that all the values in ROLE_DICT match up 
   # with members (symbols) in 'issue'.  this is to protect against renaming!
   test_symbols = [y for x in ROLE_DICT.values() for y in x]
   for symbol in test_symbols:
      if not hasattr(issue, symbol):
         raise Exception("missing symbol: " + symbol)
   
   # keep in mind that for creators, there are several different situations:
   #   1) there is zero, one or more than one creator for a given role
   #   2) a given creator has one or more than one role (comma separated)
   #   3) a single comicvine role role maps to more than one comicrack role
   
   rolemap = dict([(r, []) for l in ROLE_DICT.values() for r in l])
   if "person_credits" in dom.results.__dict__ and \
      "person" in dom.results.person_credits.__dict__:
      
      people = __as_list(dom.results.person_credits.person)
      for person in people:
         if "role" in person.__dict__:
            for role in [r.strip() for r in sstr(person.role).split(',')]:
               if role in ROLE_DICT:
                  for cr_role in ROLE_DICT[role]:
                     rolemap[cr_role].append(person.name)
                   
   for role in rolemap:
      setattr(issue, role, rolemap[role] )
      
      
#===========================================================================         
def __issue_scrape_extra_details(issue, page):
   ''' Parse additional details from the issues ComicVine webpage. '''
   if page:
      
      # first pass:  find all the alternate cover image urls
      regex = re.compile( \
         r'(?mis)\<\s*div[^\>]*img imgboxart issue-cover[^\>]+\>(.*?)div\s*>')
      for div_s in re.findall( regex, page )[1:]:
         inner_search_results = re.search(\
            r'(?i)\<\s*img\s+.*src\s*=\s*"([^"]*)', div_s)
         if inner_search_results:
            image_url_s = inner_search_results.group(1)
            if image_url_s:
               issue.image_urls_sl.append(image_url_s)
               

      # second pass:  find the community rating (stars) for this comic
      regex = re.compile(\
         r'(?mis)\<span class="average-score"\>(\d+\.?\d*) stars?\</span\>')
      results = re.search( regex, page )
      if results:
         try:
            rating = float(results.group(1))
            if rating > 0:
               issue.rating_n = rating
         except:
            log.debug_exc("Error parsing rating for " + sstr(issue) + ": ")
         

#===========================================================================
def __parse_image_url(dom):
   ''' Grab the image for this issue out of the given DOM fragment. '''
   
   imgurl_s = None
   if "image" in dom.__dict__:
      
      if "small_url" in dom.image.__dict__ and \
            is_string(dom.image.small_url):
         imgurl_s = dom.image.small_url  
      elif "medium_url" in dom.image.__dict__ and \
            is_string(dom.image.medium_url):
         imgurl_s = dom.image.medium_url  
      elif "large_url" in dom.image.__dict__ and \
            is_string(dom.image.large_url):
         imgurl_s = dom.image.large_url
      elif "super_url" in dom.image.__dict__ and \
            is_string(dom.image.super_url):
         imgurl_s = dom.image.super_url
      elif "thumb_url" in dom.image.__dict__ and \
            is_string(dom.image.thumb_url):
         imgurl_s = dom.image.thumb_url
         
   return imgurl_s          


#===========================================================================
def __as_list(dom):
   ''' 
   Returns the given dom element if it is a list, or returns it as the
   only element in a list if it is not.  Return [] if dom is None.
   '''  
   return dom if isinstance(dom, list) else [] if dom is None else [dom]
                       

