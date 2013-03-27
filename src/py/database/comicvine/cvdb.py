'''
This module contains ComicVine=based implementations of the the functions 
described in the db.py module.  That module can delegate its function calls to
the functions in this module, but other than that, external modules should 
NOT call these functions directly.
  
@author: Cory Banack
'''

import clr
import cvconnection
import log
import re
import utils
from utils import is_string, sstr 
from dbmodels import IssueRef, SeriesRef, Issue
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

# =============================================================================
def _initialize():
   ''' ComicVine implementation of the identically named method in the db.py '''
   global __series_details_cache
   __series_details_cache = {}
   
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
   series_key_s = None
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
               match = re.match(r"^.*?\b(49|4050)-(\d{2,})\b.*$", line)
               line = match.group(2) if match else line
               if utils.is_number(line):
                  series_key_s = utils.sstr(int(line))
   except:
      log.debug_exc("bad cvinfo file: " + sstr(file_s))
      
   # 4. did we find a series key?  if so, query comicvine to build a proper
   #    SeriesRef object for that series key.
   series_ref = None
   if series_key_s:
      try:
         dom = cvconnection._query_series_details_dom(utils.sstr(series_key_s))
         num_results_n = int(dom.number_of_total_results)
         series_ref =\
            __volume_to_seriesref(dom.results) if num_results_n==1 else None
      except:
         log.debug_exc("error getting SeriesRef for: " + sstr(series_key_s))
         
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
      series_refs = __query_series_refs(search_s, callback_function)
      
      # 2. if first search failed, cleanup terms more aggressively, try again
      if not series_refs:
         altsearch_s = __cleanup_search_terms(search_s, True);
         if search_terms_s and altsearch_s != search_s:
            series_refs = __query_series_refs(altsearch_s, callback_function)
            
      # 3. if second search failed, try interpreting the search terms as 
      #    a comicvine ID or the URL for a comicvine volume's webpage
      if not series_refs:
         search_terms_s = search_terms_s.strip()
         pattern = r"(^(49-|4050-)?(?<num>\d+)$)|" + \
            r"(^https?://.*comicvine\.com/.*/(49-|4050-)(?<num>\d+)(/.*)?$)"
            
         match = re.match(pattern, search_terms_s, re.I)
         if match:
            series_key_s = match.group("num")
            try:
               dom = cvconnection._query_series_details_dom(series_key_s)
               num_results_n = int(dom.number_of_total_results)
               if num_results_n == 1:
                  series_refs.add(__volume_to_seriesref(dom.results))
            except:
               pass # happens when the user enters an non-existent key
      
   return series_refs


# =============================================================================
def __query_series_refs(search_terms_s, callback_function):
   ''' A private implementation of the public method with the same name. '''
   
   cancelled_b = [False]
   series_refs = set()
   
   # 1. do the initial query, record how many results in total we're getting
   num_results_n = 0
   if search_terms_s and search_terms_s.strip():
      dom = cvconnection._query_series_ids_dom(search_terms_s, 1)
      num_results_n = int(dom.number_of_total_results)
   
   if num_results_n > 0:

      # 2. convert the results of the initial query to SeriesRefs and then add
      #    them to the returned list. notice that the dom could contain single 
      #    volume OR a list of volumes in its 'volume' variable.  
      if not isinstance(dom.results.volume, list):
         series_refs.add( __volume_to_seriesref(dom.results.volume) )
      else:
         for volume in dom.results.volume:
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

            while iteration < num_results_n and not cancelled_b[0]:
               # 4. query for the next batch of results, in a new dom
               dom = cvconnection._query_series_ids_dom(
                  search_terms_s, sstr(iteration//RESULTS_PAGE_SIZE+1))
               iteration += RESULTS_PAGE_SIZE
               
               # 4a. do a callback for the most recent batch of results
               cancelled_b[0] = callback_function(
                  iteration, num_remaining_pages)

               if int(dom.number_of_page_results) < 1:
                  log.debug("WARNING: got empty results page") # issue 33
               else:
                  # 5. convert the current batch of results into SeriesRefs,
                  #    and then add them to the returned list.  Again, the dom
                  #    could contain a single volume, OR a list.
                  if not isinstance(dom.results.volume, list):
                     series_refs.add(__volume_to_seriesref(dom.results.volume))
                  else:
                     for volume in dom.results.volume:
                        series_refs.add( __volume_to_seriesref(volume) )
                        
   # 6. Done.  series_refs now contained whatever SeriesRefs we could find
   return set() if cancelled_b[0] else series_refs   


# ==========================================================================   
def __volume_to_seriesref(volume):
   ''' Converts a cvdb "volume" dom element into a SeriesRef. '''
   publisher = '' if len(volume.publisher.__dict__) <= 1 else \
      volume.publisher.name
   return SeriesRef( int(volume.id), sstr(volume.name), 
      sstr(volume.start_year), sstr(publisher), 
      sstr(volume.count_of_issues), __parse_image_url(volume))


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
   search_terms_s = search_terms_s.replace('.', '')
   search_terms_s = search_terms_s.replace('_', ' ')
   search_terms_s = search_terms_s.replace('-', ' ')
   search_terms_s = re.sub(r'\b(c2c|noads+)\b', '', search_terms_s)
   search_terms_s = re.sub(r'\b(vs\.?|versus|and|or|tbp|the|an|of|a|is)\b',
      '', search_terms_s)
   search_terms_s = re.sub(r'giantsize', r'giant size', search_terms_s)
   search_terms_s = re.sub(r'giant[- ]*sized', r'giant size', search_terms_s)
   search_terms_s = re.sub(r'kingsize', r'king size', search_terms_s)
   search_terms_s = re.sub(r'king[- ]*sized', r'king size', search_terms_s)
   search_terms_s = re.sub(r"directors", r"director's", search_terms_s)
   search_terms_s = re.sub(r"\bvolume\b", r"\bvol\b", search_terms_s)
   search_terms_s = re.sub(r"\bvol\.\b", r"\bvol\b", search_terms_s)
   
   # see issue 169.  search words with digits embedded between letters will
   # fail unless we escape the first digit with \.  so, for example,
   # se7en should be se\7en, revv3d should be rev\3d, etc.
   search_terms_s = \
      re.sub(r"(\b[a-z]+)(\d+)([a-z]+\b)", r"\1\\\2\3", search_terms_s)
   
   # if the alternate search terms is requested, try to expand single number
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
     
# =============================================================================
def __cleanup_trailing_zeroes(number_s):
   # deal with things like 1.00 -> 1 and 1.50 -> 1.5
   number_s = number_s.strip()
   if '.' in number_s:
      number_s = number_s.rstrip('0')
      number_s = number_s.rstrip('.')
   elif number_s.strip() != '0':
      number_s = number_s.lstrip('0') # leave '0.5' and '0' alone (issue 183)
   return number_s
      
# =============================================================================
def _query_issue_refs(series_ref, callback_function=lambda x : False):
   ''' ComicVine implementation of the identically named method in the db.py '''
   
   # a comicvine series key can be interpreted as an integer
   series_id_n = int(series_ref.series_key)
   issue_refs = set()

   # 1. do a query to comicvine to get all the issues in this series
   dom = cvconnection._query_issue_ids_dom(sstr(series_id_n)) 
   if dom is None:
      raise Exception("error getting issues in " + sstr(series_ref))
   else:
      # 2. parse the query results to find the total number of issues that 
      #    comic vine has for our series.  
      issues = []
      if hasattr(dom.results, "__dict__") and \
         "issues" in dom.results.__dict__ and \
          hasattr(dom.results.issues, "__dict__") and \
         "issue" in dom.results.issues.__dict__:
            issues = dom.results.issues.issue \
               if isinstance(dom.results.issues.issue, list) else \
               [dom.results.issues.issue]
      for issue in issues:
         issue_num_s = issue.issue_number
         if not is_string(issue_num_s): issue_num_s = ''
         issue_num_s = __cleanup_trailing_zeroes(issue_num_s)
         title_s = issue.name 
         if not is_string(title_s): title_s = ''
         issue_refs.add(IssueRef(issue_num_s, issue.id, title_s))
   return issue_refs


# =============================================================================
def _query_image(ref):
   ''' ComicVine implementation of the identically named method in the db.py '''
   
   retval = None # the Image object that we will return

   # 1. determine the URL   
   image_url_s = None
   if isinstance(ref, SeriesRef):
      image_url_s = ref.thumb_url_s
   elif isinstance(ref, IssueRef):
      dom = cvconnection._query_issue_image_dom(sstr(ref.issue_key))
      image_url_s = __parse_image_url(dom.results) if dom else None
   elif is_string(ref):
      image_url_s = ref
   
   # 2. attempt to load the image for the URL
   if image_url_s:
      try:
         request = WebRequest.Create(image_url_s)
         response = request.GetResponse()
         response_stream = response.GetResponseStream()
         retval = Image.FromStream(response_stream)
      except:
         log.debug_exc('ERROR loading cover image from comicvine:')
         log.debug('--> imageurl: ', image_url_s)
         retval = None

   # if this value is stil None, it means an error occurred, or else comicvine 
   # simply doesn't have any Image for the given ref object             
   return retval 


# =============================================================================
def _query_issue(issue_ref, slow_data):
   ''' ComicVine implementation of the identically named method in the db.py '''
   
   # interesting: can we implement a cache here?  could speed things up...
   issue = Issue(issue_ref)
   
   dom = cvconnection._query_issue_details_dom(sstr(issue_ref.issue_key))
   __issue_parse_simple_stuff(issue, dom)
   __issue_parse_series_details(issue, dom)
   __issue_parse_story_credits(issue, dom)
   __issue_parse_summary(issue, dom)
   __issue_parse_roles(issue, dom)
   
   if slow_data:
      # grab extra cover images and a community rating score
      page = cvconnection._query_issue_details_page(sstr(issue_ref.issue_key))
      __issue_scrape_extra_details( issue, page )
   
   return issue


#===========================================================================
def __issue_parse_simple_stuff(issue, dom):
   ''' Parses in the 'easy' parts of the DOM '''

   if is_string(dom.results.volume.name):
      issue.series_name_s = dom.results.volume.name.strip()
   if is_string(dom.results.name):
      issue.title_s = dom.results.name.strip()
   if is_string(dom.results.id):
      issue.issue_key = dom.results.id
   if is_string(dom.results.issue_number):
      issue.issue_num_s = __cleanup_trailing_zeroes( dom.results.issue_number )
   if is_string(dom.results.site_detail_url) and \
         dom.results.site_detail_url.startswith("http"):
      issue.webpage_s = dom.results.site_detail_url 
   
   # grab the published year, month and day
   if "publish_year" in dom.results.__dict__ and \
      is_string(dom.results.publish_year):
      try:
         issue.year_n = int(dom.results.publish_year)
      except:
         pass # got an unrecognized "year" format...?
   if "publish_month" in dom.results.__dict__ and \
      is_string(dom.results.publish_month):
      try:
         issue.month_n = int(dom.results.publish_month)
      except:
         pass # got an unrecognized "month" format...?
   if "publish_day" in dom.results.__dict__ and \
      is_string(dom.results.publish_day):
      try:
         issue.day_n = int(dom.results.publish_day)
      except:
         pass # got an unrecognized "day" format...?
      
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
      series_dom = cvconnection._query_series_details_dom(series_id)
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

   crossovers = []
   if ("story_arc_credits" in dom.results.__dict__) and \
      ("story_arc" in dom.results.story_arc_credits.__dict__) :
      if type(dom.results.story_arc_credits.story_arc) == type([]):
         for arc in dom.results.story_arc_credits.story_arc:
            crossovers.append(arc.name)
      elif is_string(dom.results.story_arc_credits.story_arc.name):
         crossovers.append(dom.results.story_arc_credits.story_arc.name)
      if len(crossovers) > 0:
         issue.crossovers_sl = crossovers

   # get any character details that might exist
   characters = []
   if ("character_credits" in dom.results.__dict__) and \
      ("character" in dom.results.character_credits.__dict__):
      if type(dom.results.character_credits.character) == type([]):
         for char in dom.results.character_credits.character:
            characters.append(char.name)
      elif is_string(dom.results.character_credits.character.name):
         characters.append( dom.results.character_credits.character.name )
      if len(characters) > 0:
         issue.characters_sl = characters
         
   # get any team details that might exist
   teams = []
   if ("team_credits" in dom.results.__dict__) and \
      ("team" in dom.results.team_credits.__dict__):
      if type(dom.results.team_credits.team) == type([]):
         for team in dom.results.team_credits.team:
            teams.append(team.name)
      elif is_string(dom.results.team_credits.team.name):
         teams.append( dom.results.team_credits.team.name )
      if len(teams) > 0:
         issue.teams_sl = teams
         
   # get any location details that might exist
   locations = []
   if ("location_credits" in dom.results.__dict__) and \
      ("location" in dom.results.location_credits.__dict__):
      if type(dom.results.location_credits.location) == type([]):
         for location in dom.results.location_credits.location:
            locations.append(location.name)
      elif is_string(dom.results.location_credits.location.name):
         locations.append( dom.results.location_credits.location.name )
      if len(locations) > 0:
         issue.locations_sl = locations 


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
      issue.summary_s = summary_s.strip()
      
      
#===========================================================================         
def __issue_parse_roles(issue, dom):
   ''' Parse the current comic's roles from the DOM. '''
   
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
      
   
   # For creators, there are several different situations:
   #   1) if there is one or more than one creator
   #   2) if a given creator has one or more than one role
   
   rolemap = dict([(r, []) for l in ROLE_DICT.values() for r in l])
   if "person_credits" in dom.results.__dict__ and \
      "person" in dom.results.person_credits.__dict__:
      people = []
      if type(dom.results.person_credits.person) == type([]):
         people = dom.results.person_credits.person # a list of 'persons'
      elif dom.results.person_credits.person is not None:
         people = [dom.results.person_credits.person] # a 'person'
      for person in people:
         roles = []
         if "roles" in person.__dict__:
            if "role" in person.roles.__dict__ and \
               type(person.roles.role) == type([]):
               roles = person.roles.role # a list of strings
            elif is_string(person.roles):
               roles = [person.roles] # a string
         for role in roles:
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
