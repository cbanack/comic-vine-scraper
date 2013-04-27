'''
This module contains code that search the database in an attempt to 
automatically find a good match for a given ComicBook object. 

@author: Cory Banack
'''
from dbmodels import IssueRef
import db
import dbutils
from matchscore import MatchScore
import log
import imagehash
import utils

#==============================================================================
def find_series_ref(book, config):
   ''' 
   Performs a number of queries on the database, in an attempt to find a 
   SeriesRef object that strongly matches the given book.  A variety of 
   techniques are employed, including checking for matching issue numbers in
   the prospective series, and image matching the cover of the prospective 
   issue in the prospective series.  The user's search and filtering 
   preferences (in 'config') are also taken into account.
      
   Returns None if no clear seroes identification could be made. 
   '''
   retval = None
   
   candidate_ref = None
   series_ref = __find_best_series(book, config)
   if series_ref:
      # match issue cover if we have an issue; match series cover only if 
      # we do NOT have an issue number for this comic (i.e. a oneshot)
      candidate_ref = db.query_issue_ref(series_ref, book.issue_num_s) \
         if book.issue_num_s else series_ref
   if candidate_ref and __cover_matches_database(book, candidate_ref):
      retval = series_ref
   return retval;


#==============================================================================
def __find_best_series(book, config):      
   ''' 
   Queries the databse to find a best guess for a series matching the given
   ComicBook, based on its name, year, issue number, and other text attributes.
   
   Returns SeriesRef if a reasonable guess was found, or None if one wasn't.
   '''
   series_refs = dbutils.filter_series_refs(
         db.query_series_refs(book.series_s),
         config.ignored_publishers_sl, 
         config.ignored_before_year_n,
         config.ignored_after_year_n,
         config.never_ignore_threshold_n)

   series_ref = None   
   if len(series_refs) > 0:
      mscore = MatchScore()
      series_ref = reduce( lambda x,y: 
         x if mscore.compute_n(book, x) >= mscore.compute_n(book,y) else y,
         series_refs)
      
      
   # coryhigh: we could add a test here to derail the found series if 
   # a) we have no issue number, or issue 0 or 1, and 
   # b) the second or third highest matchscore series have matching
   #    cover art or contain the words TPB?  
   return series_ref; 


#==============================================================================
def __cover_matches_database(book, ref):
   '''
   Checks to see if the cover of the given ComicBook "matches" the cover image
   associated with the given database ref, which can be either a SeriesRef or an 
   IssueRef.  This method may query the database multiple times.
   '''
   
   matches = False
   try:
      image = book.create_image_of_page(0)
      if image:
         matches = __matches(image, ref)
         # if the given ref is an IssueRef, we can try to load the issue's
         # additional cover images and see if any of them match, too.
         if not matches and type(ref) == IssueRef:  
            issue = db.query_issue(ref, True)
            if issue:
               for ref in issue.image_urls_sl:
                  matches = __matches(image, ref)
                  if matches: break
   finally:
      if "image" in locals() and image: image.Dispose()
   return matches


#==============================================================================
def __matches(image, image_ref):
   ''' 
   Compares the given image with the image loaded from the given image ref, 
   and returns a boolean indicating whether they are the same or not.
   
   'image' - a .NET Image object.  Will NOT be disposed by this method.
   'image_ref' - a remote image reference; an IssueRef, SeriesRef, or URL.
   ''' 
   matches = False
   try:
      image1 = image
      image2 = db.query_image(image_ref) if image1 and image_ref else None
      if image1 and image2:
         image1 = utils.strip_back_cover(image1) # dispose is handled when
         image2 = utils.strip_back_cover(image2) # a new image is created
         hash1 = imagehash.hash(image1)
         hash2 = imagehash.hash(image2)
         #log.debug("hash1: ", bin(hash1)[2:].zfill(64))
         #log.debug("hash2: ", bin(hash2)[2:].zfill(64)) 
         log.debug("similarity: ", imagehash.similarity(hash1, hash2) )
         matches = imagehash.similarity(hash1, hash2) > 0.85
   finally:
      if "image2" in locals() and image2: image2.Dispose() 
   return matches