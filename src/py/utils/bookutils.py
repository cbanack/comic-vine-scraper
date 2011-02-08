''' 
This module contains utility methods for working with ComicRack
ComicBook objects (i.e. 'book' objects).

@author: Cory Banack
'''
import re
from dbmodels import IssueRef

# =============================================================================
def extract_issue_ref(book):
   '''
   This method looks in the tags and notes fields of the given book for 
   evidence that the given ComicBook has been scraped before.   If possible, 
   it will construct an IssueRef based on that evidence, and return it.  
   If not, it will return None.   
   
   If the user has manually added a "skip" flag to one of those fields, this
   method will return the string "skip", which should be interpreted as 
   "never scrape this book".
   '''
   
   # coryhigh: move this into comicbook.  or maybe the db layer?
   # ===== corylow: SEPARATION OF CONCERNS: this assumes CV! ==================
   tag_found = re.search(r'(?i)CVDB(\d{1,}|SKIP)', book.tags_s)
   if not tag_found:
      tag_found = re.search(r'(?i)CVDB(\d{1,}|SKIP)', book.notes_s)
      if not tag_found:
         tag_found = re.search(r'(?i)ComicVine.?\[(\d{1,})', book.notes_s)

   retval = None
   if tag_found:
      retval = tag_found.group(1).lower()
      try:
         if retval != 'skip':
            retval = IssueRef(book.issue_num_s, int(retval))
      except:
         retval = None

   return retval