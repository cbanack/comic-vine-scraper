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
   first_bracket_idx = filename_s.find('(')
   if first_bracket_idx > 0: 
      s = filename_s[0:first_bracket_idx]
      match = re.match(r"^(.*?)#?\s*(-?[0-9]+[.0-9]*)\s*$", s)
      if match:
         series_s = match.group(1).strip()
         issue_num_s = float(match.group(2).strip()) \
            if '.' in match.group(2) else int(match.group(2).strip())
         issue_num_s = utils.sstr(issue_num_s) 
   return [series_s, issue_num_s]