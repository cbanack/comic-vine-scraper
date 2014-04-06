'''
This module contains useful canned methods for accessing the Comic Vine
database (API) over the Internet.  The documentation for this API and the 
related queries can be found at:  http://comicvine.com/api/documentation/

All public methods in this module require you to pass in a valid ComicVine
API key as their first argument.  Please do not use my API key!
You can easily obtain your own key for free at: http://api.comicvine.com/

@author: Cory Banack
'''

import clr
import log
import xml2py
from utils import sstr
from dberrors import DatabaseConnectionError
import utils
import re

clr.AddReference('System')
from System.Net import WebException
from System.IO import IOException
from System.Web import HttpUtility

clr.AddReference('IronPython')
from System.Threading import Thread, ThreadStart

__CLIENTID = '&client=cvscraper'

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
   QUERY = 'http://comicvine.com/api/search/?api_key=' + API_KEY + \
      __CLIENTID + '&format=xml&limit=100&resources=volume' + \
      '&field_list=name,start_year,publisher,id,image,count_of_issues' + \
      '&query={0}'
   # leave "page=1" off of query to fix a bug, e.g. search for 'bprd vampire'
   PAGE = "" if page_n == 1 else "&page={0}".format(page_n)
      
   if searchterm_s is None or searchterm_s == '' or page_n < 0:
      raise ValueError('bad parameters')
   searchterm_s = " AND ".join( re.split(r'\s+', searchterm_s) ); # issue 349
   return __get_dom(QUERY.format(HttpUtility.UrlPathEncode(searchterm_s))+PAGE)



# =============================================================================
def _query_series_details_dom(API_KEY, seriesid_s):
   '''
   Performs a query that will obtain a dom containing the start year and 
   publisher for the given series ID.
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   # {0} is the series id, an integer.
   QUERY = 'http://comicvine.com/api/volume/4050-{0}/?api_key=' \
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
   QUERY = 'http://comicvine.com/api/issues/?api_key=' + API_KEY + __CLIENTID +\
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
   QUERY = 'http://comicvine.com/api/issues/?api_key=' + API_KEY + \
      __CLIENTID + '&format=xml&field_list=name,issue_number,id,image' + \
      '&filter=volume:{0},issue_number:{1}'
   
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
   QUERY = 'http://comicvine.com/api/issue/4000-{0}/?api_key=' \
      + API_KEY + __CLIENTID + '&format=xml'
      
   if issueid_s is None or issueid_s == '':
      raise ValueError('bad parameters')
   url = QUERY.format(sstr(issueid_s) )
   return __get_dom(url)



# =============================================================================
def _query_issue_details_page(API_KEY, issueid_s):
   '''
   Performs a query that will obtain the the ComicVine website details for the
   given issue.  The details are returned in the form of an html string (a 
   page) that can be scraped for info.
   
   Never returns null, but may throw exceptions if there are problems.
   '''
   
   # {0} is the issue ID 
   QUERY = 'http://www.comicvine.com/issue/4000-{0}/' 
      
   if issueid_s is None or issueid_s == '':
      return None
   url = QUERY.format(sstr(issueid_s))
   retval = __get_page(url)
   if retval:
      return retval
   else:
      raise DatabaseConnectionError('comicvine', url, 
         Exception('comicvine website returned an empty document'))


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
      if not dom or not "status_code" in dom.__dict__:
         if lasttry: raise DatabaseConnectionError(
            "Comic Vine", url, "empty comicvine dom: see bug 194")
         else: error_occurred = True

   # 5. make sure the dom is valid             
   if not error_occurred:
      if int(dom.status_code) == 1:
         retval = dom # success
      else:
         if lasttry: raise _ComicVineError(dom.status_code, dom.error, url)
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
   represents an actual network problem connecting to the Comic Vine database.
   '''
   
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
class _ComicVineError(Exception):
   ''' 
   A special exception that gets thrown anytime when there is a semantic error
   with a query to the comicvine database; that is, an error wherein comic
   vine returns an error code.
   
   You can get the error code and name as a tuple via the get_error() method.
   '''
   
   def __init__(self, error_code, error_name, url):
      ''' 
      error_code => the integer comic vine error code
      error_name => the string name of the comic vine error code
      url => the url that caused the problem
      '''
      self._error = int(error_code), error_name
      msg = 'code {0}: "{1}" for: {2}'.format(error_code, error_name, url)
      super(Exception,self).__init__( msg )
      
      
   # ==========================================================================
   def get_error(self):
      '''
      Returns a tuple containing the integer comic vine error code that was used
      to construct this object, followed by the associated string error name.
      '''  
      return self._error
   
