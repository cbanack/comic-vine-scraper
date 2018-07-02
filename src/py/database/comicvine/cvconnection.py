'''
This module contains useful canned methods for accessing the Comic Vine
database (API) over the Internet.  The documentation for this API and the 
related queries can be found at: 
  
     http://comicvine.gamespot.com/api/documentation/

All public methods in this module require you to pass in a valid ComicVine
API key as their first argument.  Please do not use my API key!
You can easily obtain your own key for free at: 

     http://www.comicvine.gamespot.com/api

@author: Cory Banack
'''

import re
import clr
import log
import xml2py
import utils
from utils import sstr
from dberrors import DatabaseConnectionError

clr.AddReference('System')
from System import DateTime
from System.Net import WebException
from System.IO import IOException
from System.Web import HttpUtility

clr.AddReference('IronPython')
from System.Threading import Thread, ThreadStart

__CLIENTID = '&client=cvscraper'

# this value is used to throttle our query speeds
__next_query_time_ms = 0

# the amount of time to wait between queries
__QUERY_DELAY_MS = 1100 

# =============================================================================
def _query_series_ids_dom(API_KEY, searchterm_s, page_n=1):
   ''' 
   Performs a query that will obtain a dom containing all the comic book series
   from ComicVine that match a given search string.  You can also provide a 
   second argument that specifies the page of the results (each page contains
   100 results) to display. This is useful, because this query will not 
   necessarily return all available results.
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   
   # {0} is the search string, {1} is the page number of the results we want
   QUERY = 'http://comicvine.gamespot.com/api/search/?api_key=' + API_KEY + \
      __CLIENTID + '&format=xml&limit=100&resources=volume' + \
      '&field_list=name,start_year,publisher,id,image,count_of_issues' + \
      '&query={0}'
   # leave "page=1" off of query to fix a bug, e.g. search for 'bprd vampire'
   PAGE = "" if page_n == 1 else "&page={0}".format(page_n)
      
   if searchterm_s is None or searchterm_s == '' or page_n < 0:
      raise ValueError('bad parameters')
   searchterm_s = " ".join( re.split(r'\s+', searchterm_s) );
   return __get_dom(QUERY.format(HttpUtility.UrlPathEncode(searchterm_s))+PAGE)



# =============================================================================
def _query_series_details_dom(API_KEY, seriesid_s):
   '''
   Performs a query that will obtain a dom containing the start year and 
   publisher for the given series ID.
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   # {0} is the series id, an integer.
   QUERY = 'http://comicvine.gamespot.com/api/volume/4050-{0}/?api_key=' \
     + API_KEY + __CLIENTID + '&format=xml' \
     + '&field_list=name,start_year,publisher,image,count_of_issues,id'
      # parsing relies on 'field_list' specifying 2 or more elements!!
      
   if seriesid_s is None or seriesid_s == '':
      raise ValueError('bad parameters')
   return __get_dom( QUERY.format(sstr(seriesid_s) ) )


# =============================================================================
def _query_issue_ids_dom(API_KEY, seriesid_s, page_n=1):
   '''
   Performs a query that will obtain a dom containing all of the issue IDs
   for the given series id.  You can also provide a second argument that 
   specifies the page of the results (each page contains
   100 results) to display. This is useful, because this query will not 
   necessarily return all available results.
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   
   # {0} is the series ID, an integer     
   QUERY = 'http://comicvine.gamespot.com/api/issues/?api_key=' + API_KEY + __CLIENTID +\
      '&format=xml&field_list=name,issue_number,id,image&filter=volume:{0}'
   PAGE = "" if page_n == 1 \
      else "&page={0}&offset={1}".format(page_n, (page_n-1)*100)
   
   if seriesid_s is None or seriesid_s == '':
      raise ValueError('bad parameters')
   return __get_dom(QUERY.format(sstr(seriesid_s)) + PAGE )


# =============================================================================
def _query_issue_id_dom(API_KEY, seriesid_s, issue_num_s):
   '''
   Performs a query that will obtain a dom containing the issue ID for the 
   given issue number in the given series id.  
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   
   # {0} is the series ID, an integer, and {1} is issue number, a string     
   QUERY = 'http://comicvine.gamespot.com/api/issues/?api_key=' + API_KEY + \
      __CLIENTID + '&format=xml&field_list=name,issue_number,id,image' + \
      '&filter=volume:{0},issue_number:{1}'
   
   # cv does not play well with leading zeros in issue nums. see issue #403.
   issue_num_s = sstr(issue_num_s).strip()
   if len(issue_num_s) > 0:  # fix issue 411
      issue_num_s = issue_num_s.lstrip('0').strip()
      issue_num_s = issue_num_s if len(issue_num_s) > 0 else '0'
   
   
   if not seriesid_s or not issue_num_s:
      raise ValueError('bad parameters')
   return __get_dom( QUERY.format(sstr(seriesid_s), 
      HttpUtility.UrlPathEncode(sstr(issue_num_s)) ) )



# =============================================================================
def _query_issue_details_dom(API_KEY, issueid_s):
   ''' 
   Performs a query that will obtain a dom containing the ComicVine API details
   for given issue.
   
   Never returns null, but may throw exceptions if there are problems.
   '''
   
   # {0} is the issue ID 
   QUERY = 'http://comicvine.gamespot.com/api/issue/4000-{0}/?api_key=' \
      + API_KEY + __CLIENTID + '&format=xml'
      
   if issueid_s is None or issueid_s == '':
      raise ValueError('bad parameters')
   url = QUERY.format(sstr(issueid_s) )
   return __get_dom(url)


# =============================================================================
def __get_dom(url, lasttry=False):
   ''' 
   Obtains a parsed comicvine-formatted DOM tree from the XML at the given URL. 
   Never returns null, but may throw an exception if it has any problems
   downloading or parsing the XML.
   '''
   
   retval = None
   error_occurred = False
   
   #1. obtain xml from comicvine
   xml = None
   if not error_occurred:
      try: xml = __get_page( url )
      except Exception, ex:
         if lasttry: raise ex
         else: error_occurred = True
   
   #2. make the xml is not empty
   if not error_occurred:
      if xml is None or not xml.strip():
         msg = 'comicvine query returned an empty document: ' + url
         if lasttry: raise Exception(msg)
         else: error_occurred = True
         
   # 3. convert the xml into a dom
   dom = None   
   if not error_occurred:
      try:
         xml = __strip_invalid_xml_chars(xml)
         dom = xml2py.parseString(xml)
      except Exception, ex:
         if lasttry: raise ex
         else: error_occurred = True
   
   # 4. make sure the dom is valid (see bug 194)   
   if not error_occurred:
      if not dom or "status_code" not in dom.__dict__:
         if lasttry: raise DatabaseConnectionError(
            "Comic Vine", url, "empty comicvine dom: see bug 194")
         else: error_occurred = True

   # 5. make sure the dom is valid             
   if not error_occurred:
      if int(dom.status_code) == 1:
         retval = dom # success
      else:
         if lasttry: raise DatabaseConnectionError("Comic Vine", url, 
            'code {0}: "{1}"'.format(dom.status_code, dom.error),
            dom.status_code )
         else: error_occurred = True
      
   # 6. return the valid dom, or if error occurred, retry once
   if error_occurred:   
      log.debug('ERROR OCCURRED CONTACTING COMICVINE. RETRYING...')
      t = Thread(ThreadStart(lambda x=0: Thread.CurrentThread.Sleep(2500)))
      t.Start()
      t.Join()
      return __get_dom(url, True)
   else:            
      return retval
        
         
# =============================================================================
def __get_page(url):
   ''' 
   Reads the webpage at the given URL into a new string, which is returned.  
   The returned value may be None if a problem is encountered, OR an exception 
   may be thrown.   If the exception is a DatabaseConnectionError, that 
   represents an problem connecting to the Comic Vine database.
   '''
   wait_until_ready() # throttle request speed to make ComicVine happy

   try:
      return utils.get_html_string(url)
   except (WebException, IOException) as wex:
      # this type of exception almost certainly means that the user's internet
      # is broken or the comicvine website is down.  so wrap it in a nice, 
      # recognizable exception before rethrowing it, so that error handlers can
      # recognize it and handle it differently than other, more unexpected 
      # exceptions.
      raise DatabaseConnectionError("Comic Vine", url, wex)


# =============================================================================
def __strip_invalid_xml_chars(xml):
   '''
   Removes any invalid xml characters (unfortunately, Comic Vine DOES allow
   them, see issue 51) from the given xml string.  Thanks to:
      http://cse-mjmcl.cse.bris.ac.uk/blog/2007/02/14/1171465494443.html
   '''
   
   def is_valid_xml(c):
      return c == 0x9 or c == 0xA or c == 0xD or\
         (c >= 0x20 and c <= 0xD7FF) or\
         (c >= 0xE000 and c <= 0xFFFD) or\
         (c >= 0x10000 and c <= 0x10FFFF)

   if xml:
      xml = ''.join([c for c in xml if is_valid_xml(ord(c))])
   return xml

# =============================================================================
def wait_until_ready():
   '''
   Waits until a fixed amount of time has passed since this function was 
   last called.  Returns immediately if that much time has already passed.
   '''
   global __next_query_time_ms, __QUERY_DELAY_MS 
   time_ms = (DateTime.Now-DateTime(1970,1,1)).TotalMilliseconds
   wait_ms = __next_query_time_ms - time_ms
   if wait_ms > 0:
      t = Thread(ThreadStart(lambda x=0: Thread.CurrentThread.Sleep(wait_ms)))
      t.Start()
      t.Join()
   time_ms = (DateTime.Now-DateTime(1970,1,1)).TotalMilliseconds
   __next_query_time_ms = time_ms + __QUERY_DELAY_MS
