'''
This module contains useful canned methods for accessing the Comic Vine
database (API) over the Internet.  The documentation for this API and the 
related queries can be found at:  http://api.comicvine.com/documentation/

@author: Cory Banack
'''

import clr
import log
import xml2py
from utils import sstr
from dberrors import DatabaseConnectionError
import utils

clr.AddReference('System')
from System.Net import WebException
from System.IO import IOException
from System.Web import HttpUtility


# This is the api key needed to access the comicvine website.
# This key belongs to Cory Banack.  If you fork this code to make your
# own scraper, please obtain and use your own (free) API key from ComicVine
__API_KEY = '4192f8503ea33364a23035827f40d415d5dc5d18'

# =============================================================================
def _query_series_ids_dom(searchterm_s, page_n=1):
   ''' 
   Performs a query that will obtain a dom containing all the comic book series
   from ComicVine that match a given search string.  You can also provide a 
   second argument that specifies the page of the results (each page contains
   100 results) to display. This is useful, because this query will not 
   necessarily return all available results.
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   
   # {0} is the search string, {1} is the page number of the results we want
   QUERY = 'http://api.comicvine.com/search/?api_key=' + __API_KEY + \
      '&format=xml&limit=100&resources=volume' + \
      '&field_list=name,start_year,publisher,id,image,count_of_issues' + \
      '&query={0}&page={1}'
      
   if searchterm_s is None or searchterm_s == '' or page_n < 0:
      raise ValueError('bad parameters')
   return __get_dom( QUERY.format(
      HttpUtility.UrlPathEncode(searchterm_s), page_n) )



# =============================================================================
def _query_series_details_dom(seriesid_s):
   '''
   Performs a query that will obtain a dom containing the start year and 
   publisher for the given series ID.
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   # {0} is the series id, an integer.
   QUERY = 'http://api.comicvine.com/volume/4050-{0}/?api_key=' + __API_KEY + \
     '&format=xml&field_list=name,start_year,publisher,image,count_of_issues,id'
      # parsing relies on 'field_list' specifying 2 or more elements!!
      
   if seriesid_s is None or seriesid_s == '':
      raise ValueError('bad parameters')
   return __get_dom( QUERY.format(sstr(seriesid_s) ) )


# =============================================================================
def _query_issue_ids_dom(seriesid_s, page_n=1):
   '''
   Performs a query that will obtain a dom containing all of the issue IDs
   for the given series id.  You can also provide a second argument that 
   specifies the page of the results (each page contains
   100 results) to display. This is useful, because this query will not 
   necessarily return all available results.
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   
   # {0} is the series ID, an integer     
   QUERY = 'http://api.comicvine.com/issues/?api_key=' + __API_KEY + \
      '&format=xml&field_list=name,issue_number,id,image&filter=volume:{0}' +\
      '&page={1}&offset={2}'
   
   if seriesid_s is None or seriesid_s == '':
      raise ValueError('bad parameters')
   return __get_dom( QUERY.format(sstr(seriesid_s), page_n, (page_n-1)*100 ) )


# =============================================================================
def _query_issue_id_dom(seriesid_s, issue_num_s):
   '''
   Performs a query that will obtain a dom containing the issue ID for the 
   given issue number in the given series id.  
   
   This method doesn't return null, but it may throw Exceptions.
   '''
   
   # {0} is the series ID, an integer, and {1} is issue number, a string     
   QUERY = 'http://api.comicvine.com/issues/?api_key=' + __API_KEY + \
      '&format=xml&field_list=name,issue_number,id,image' + \
      '&filter=volume:{0},issue_number:{1}'
   
   if not seriesid_s or not issue_num_s:
      raise ValueError('bad parameters')
   return __get_dom( QUERY.format(sstr(seriesid_s), 
      HttpUtility.UrlPathEncode(sstr(issue_num_s)) ) )



# =============================================================================
def _query_issue_details_dom(issueid_s):
   ''' 
   Performs a query that will obtain a dom containing the ComicVine API details
   for given issue.
   
   Never returns null, but may throw exceptions if there are problems.
   '''
   
   # {0} is the issue ID 
   QUERY = 'http://api.comicvine.com/issue/4000-{0}/?api_key=' \
      + __API_KEY + '&format=xml'
      
   if issueid_s is None or issueid_s == '':
      raise ValueError('bad parameters')
   url = QUERY.format(sstr(issueid_s) )
   return __get_dom(url)



# =============================================================================
def _query_issue_details_page(issueid_s):
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
def _query_issue_image_dom(issueid_s):
   '''
   Performs a query that will obtain a dom containing the issue image url 
   for the given issue ID.
   '''
   
   # {0} is the issue ID
   QUERY = 'http://api.comicvine.com/issue/4000-{0}/?api_key=' + __API_KEY + \
      '&format=xml&field_list=image'
   
   if issueid_s is None or issueid_s == '':
      raise ValueError('bad parameters')
   return __get_dom( QUERY.format(sstr(issueid_s) ) )



# =============================================================================
def __get_dom(url, lasttry=False):
   ''' 
   Obtains a parsed comicvine-formatted DOM tree from the XML at the given URL. 
   Never returns null, but may throw an exception if it has any problems
   downloading or parsing the XML.
   '''
   
   retval = None
   xml = __get_page( url )
   if xml is None or not xml.strip():
      msg = 'comicvine query returned an empty document: ' + url
      if lasttry:
         raise Exception(msg)
      else:
         log.debug('ERROR: ', msg)
         retval = None
   else:
      try:
         xml = __strip_invalid_xml_chars(xml)
         dom = xml2py.parseString(xml)
         
         # for some reason, the comicvine server will return invalid xml
         # for a while, I think just before it goes totally down.  bug 194
         # describes why this is ugly, and it why we handle that specially here
         if not "status_code" in dom.__dict__:
            raise DatabaseConnectionError(
               "Comic Vine", url, "empty comicvine dom: see bug 194")
         
         if int(dom.status_code) == 1:
            retval = dom # success
         else:
            if lasttry:
               raise _ComicVineError(dom.status_code, dom.error, url)
            else:
               log.debug()
               retval = None
      except Exception, ex:
         if lasttry:
            raise ex
         else:
            log.debug_exc('ERROR: cannot parse results from comicvine: ' + url)
            retval = None
      
   # this next is an attempt to deal with issues #28 and #39.  sometimes 
   # read_url does not seem to get a fully formed version of the xml file,
   # or it even gets and empty file.  in such cases, a re-query normally 
   # solves the problem.
   if not retval and not lasttry:   
      log.debug('RETRYING the query...')
      retval = __get_dom(url, True)
            
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
   
