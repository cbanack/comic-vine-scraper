'''
This module contains functions for extracting and parsing details out
of comic book filenames.
Created on Oct 23, 2011
@author: cbanack
'''
import re
import utils

#==============================================================================
def extract( filename_s ):
   '''
   Takes the filename of a comic book, and extracts two strings out of it, the 
   series name, and the issue number. These two pieces of information are 
   returned as a tuple, i.e. ("batman", "344")
   ''' 
   series_s = ""
   issue_num_s = ""
   s = filename_s
   
   # 1. find the last period, and remove everything after it.  it's not a 
   #    valid comicbook file if it doesn't have an extension.
   last_period = s.rfind(r".")
   if last_period > 0:
      s = s[0:last_period]
      
   # 2. strip out all bracketed data from the name, as well as all volume info
   #    gotta handle things like "vol. 2a" and "vol -3.1"
   def recurse_sub(pattern, s):
      while re.search(pattern, s):
         s = re.sub(pattern, "", s)
      return s
   s = recurse_sub(r"\([^\(]*?\)", s)
   s = recurse_sub(r"\{[^\{]*?\}", s)
   s = recurse_sub(r"\[[^\[]*?\]", s)
   s = re.sub(r"(?i)((v|vol)\.?|volume)\s*-?\s*[0-9]+[.0-9a-z]*", "", s)
   
   
   # 3. clean up whitespace
   s = re.sub(r"_", " ", s) 
   s = re.sub(r"\s{2,}", " ", s) 
   s = s.strip()
   
   # coryhigh: start here, count the number of "numbers", pick and remove
   match = re.match(r"^(.*?)#?\s*(-?\s*[0-9]+[.0-9a-z]*)\s*$", s)
   if match:
      series_s = match.group(1).strip()
      issue_num_s = match.group(2).strip().replace(" ", "")
      if re.match("^[-.0-9]+$", issue_num_s):
         issue_num_s = float(issue_num_s) \
            if '.' in issue_num_s else int(issue_num_s)
      issue_num_s = utils.sstr(issue_num_s) 
   else:
      series_s = s
      issue_num_s = ""
      
   return [series_s, issue_num_s]