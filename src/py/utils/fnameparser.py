'''
This module contains functions for extracting and parsing details out
of comic book filenames.

Created on Oct 23, 2011
@author: cbanack
'''
import re
import utils
import log

#==============================================================================
def extract( filename_s ):
   '''
   Takes the filename of a comic book, and extracts two strings out of it, the 
   series name, and the issue number. These two pieces of information are 
   returned as a tuple, i.e. ("batman", "344")
   ''' 
   
   # remove the file extension, unless it's the whole filename
   name_s = filename_s.strip()
   last_period = name_s.rfind(r".")
   name_s = name_s if last_period <= 0 else name_s[0:last_period]
   
   # try the extraction.  if anything goes wrong, or if we come up with a blank
   # series name, revert to the filename (without extension) as series name
   try:
      retval = __extract(name_s)
      if retval[0].strip() == "":
         raise Exception("parsed blank series name")
   except:
      log.debug_exc("Recoverable error extracting from '" + filename_s + "':")
      retval = name_s, ""
   return retval
      
   
   
#==============================================================================
def __extract(name_s):
   ''' Internal implementation of the similarly named method in this package '''
   
   # 1. 's' is the name of our 'working' series name.  we'll slowly strip the
   #    'non-series name' data out of it, til what's left is the series name
   s = name_s
      
   # 2. strip out all bracketed data from the name
   def recurse_sub(pattern, s):
      while re.search(pattern, s):
         s = re.sub(pattern, "", s)
      return s
   s = recurse_sub(r"\([^\(]*?\)", s)
   s = recurse_sub(r"\{[^\{]*?\}", s)
   s = recurse_sub(r"\[[^\[]*?\]", s)
   
   # 3. remove of trace of volume from the name (like "vol. 2a" and "vol -3.1")
   s = re.sub(r"(?i)((v|vol)\.?|volume)\s*-?\s*[0-9]+[.0-9a-z]*", "", s)
   
   # 4. if the name has things like "4 of 5", remove the " of 5" part
   #    also, if the name has 3-6, remove the -6 part.
   s = re.sub(r"(?i)(?<=\d)(\s*of\s*\d+)", "", s)
   s = re.sub(r"(?<=\d)(-\d+)", "", s)
   
   # 5. clean up excess whitespace and underscores
   s = re.sub(r"_", " ", s) 

   # 6. get an ordered list of issue number-like strings in the filename
   #    for example:  3, #4, 5a, 6.00, 10.0b, .5, -1.0   
   #    also, remove numbers that look like years, EXCEPT on the "2000AD" series
   matches = __extract_numbers(s)
      
   # 7. if there's multiple numbers in the filename, and it starts with 
   #    something like "05. " or "12 - " we assuming these files are part of 
   #    a reading list, and we strip out that first part.
   pattern = r"^\s*\d+(\.\s+|\s*-\s*(?=\D))"
   if len(matches) > 1 and re.match(pattern,s):
      s = re.sub(pattern, "", s, 1)
      matches = __extract_numbers(s)
      
   # 8. if we parsed out some potential issue numbers, designate the LAST 
   #    (rightmost) one s the actual issue number, and remove it from the name
   if len(matches) > 0: 
      issue_num_s = matches[-1].group(2)
      series_s = s[:matches[-1].start(0)] +s[matches[-1].end(0):]
      if re.match("^[-.0-9]+$", issue_num_s):
         # 7a. strip of leading zeroes if this is an int/float
         issue_num_s = utils.sstr(float(issue_num_s) \
            if '.' in issue_num_s else int(issue_num_s))
   else:
      issue_num_s = ""
      series_s = s

   # 9. contract repeating whitespace, and strip bad chars off the ends      
   series_s = re.sub(r"\s{2,}", " ", series_s).strip(" ,-_").strip() 
      
   return [series_s, issue_num_s]


#==============================================================================
def __extract_numbers(s):
   '''  
   Searches through the given string left-to-right, building an ordered list of
   "issue number-like" substrings.  For example, this method finds substrings 
   like:  3, #4, 5a, 6.00, 10.0b, .5, -1.0
   '''   
   matches = list(re.finditer(r"(?u)(^|[\s#])(-?\d*\.?\d\w*)", s))
   # remove matches that look like years, EXCEPT on the "2000AD" series
   is2000AD = re.match(r"(?i)\s*2000[\s\.-_]*a[\s.-_]*d.*", s) 
   if not is2000AD:
      def isYear(d): 
         return re.match(r"^\d{4}$",d) and int(d) > 1950 and int(d) < 2100 
      matches = [x for x in matches if not isYear(x.group(2))]
   return matches  
