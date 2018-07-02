'''
This module contains the MatchScore class, which is used for computing how well
a given SeriesRef "matches" the a particular ComicBook.

Created on Mar 3, 2012
@author: cbanack
'''
import re
import datetime
from resources import Resources
from utils import sstr
import utils

#==============================================================================
class MatchScore(object):
   '''
   Instances of this class can compute how well a SeriesRef "matches" a 
   particular ComicBook. 
   
   This class reads its internal state out of a file on the file system, and 
   records that state out via the record_choice() function.  Therefore, if 
   multiple instances of this class exist at the same time, only ONE of 
   them should ever call record_choice(), otherwise data may be lost.
   '''
   
   #=========================================================================== 
   def __init__(self):
      ''' Initializes a new Configuration object with default settings '''
      self.__prior_series_sl = set(utils.load_map(Resources.SERIES_FILE).keys())
   
   
   #===========================================================================
   def compute_n(self, book, series_ref):
      '''
      Computes a score for the given SeriesRef, which describes how closely
      that ref matches the given ComicBook.   The higher the score, the closer
      the match.  Scores can be negative.
      '''
      
      # this function splits up the given comic book series name into
      # separate words, so we can compare different series names word-by-word
      def split( name_s ):
         if name_s is None: name_s = ''
         name_s = re.sub('\'','', name_s).lower()
         name_s = re.sub(r'\W+',' ', name_s)
         name_s = re.sub(r'giant[- ]*sized?', r'giant size', name_s)
         name_s = re.sub(r'king[- ]*sized?', r'king size', name_s)
         name_s = re.sub(r'one[- ]*shot', r'one shot', name_s)
         return name_s.split()
      
      # 1. first, compute the 'namescore', which is based on how many words in
      #    our book name match words in the series' name (usually comes up with 
      #    a value on the range [5, 20], approximately.)  
      bookname_s = '' if not book.series_s else book.series_s
      if bookname_s and book.format_s:
         bookname_s += ' ' + book.format_s
      bookwords = split(bookname_s)   
      serieswords = split(series_ref.series_name_s)
      
      namescore_n = 0
      for word in bookwords:
         if word in serieswords:
            namescore_n += 5
            serieswords.remove(word)
         else:
            namescore_n -= 1
      namescore_n -= len(serieswords)
      
      # 2. if the series was one that the user has chosen in the past, give it's
      #    score a very small boost (about the equivalent of it matching one 
      #    more word on the namescore  
      priorscore_n = 7 if sstr(series_ref.series_key) \
          in self.__prior_series_sl else 0

      # 3. there are certain international "mirror" publishers that publish the
      #    same series as much more common US publishers.  these should be 
      #    penalized a bit, since we're rarely scraping comics from them          
      pub_s = series_ref.publisher_s.lower()
      publisherscore_n = -6 if "panini" in pub_s or "deagostina" in pub_s or \
         pub_s == "marvel italia" or pub_s == "marvel uk" or \
         pub_s == "semic_as" or pub_s == "abril" else 0
         
      # 4. get the 'bookscore', which compares our book's issue number
      #    with the number of issues in the series.  a step function that 
      #    returns a very high number (100) if the number of issues in the 
      #    series is compatible, and a very low one (-100) if it is not.  
      booknumber_n = book.issue_num_s if book.issue_num_s else '-1000'
      booknumber_n = re.sub('[^\d.-]+', '', booknumber_n)
      try:
         booknumber_n = float(booknumber_n)
      except:
         booknumber_n = -999
      series_count_n = series_ref.issue_count_n
      if series_count_n > 100:
         # all large series have a "good" bookscore, cause they are very 
         # long-running and popular. Also, we might overlook them in the 
         # bookscore because and databases will often not have all of issues, 
         # so their issue count will not be high enough.
         bookscore_n = 100
      else:    
         # otherwise, if we get a good score only if we have the right
         # number of books in the series to match the booknumber (-1 for
         # delayed updates of the database).
         bookscore_n = 100 if booknumber_n-1 <= series_count_n else -100
      

      # 5. get the 'yearscore', which severely penalizes (-500) any series 
      #    that started after the year that the current book was published.
      current_year_n = datetime.datetime.now().year
      is_valid_year_b = lambda y : y > 1900 and y <= current_year_n+1 
      
      series_year_n = series_ref.volume_year_n
      book_year_n = book.pub_year_n if is_valid_year_b(book.pub_year_n) \
         else book.rel_year_n
      yearscore_n = 0
      if is_valid_year_b(book_year_n):
         if not is_valid_year_b(series_year_n):
            yearscore_n = -100
         elif series_year_n > book_year_n:
            yearscore_n = -500
            
      # 6. get the 'recency score', which is a tiny negative value (usually
      #    around on the range [-0.50, 0]) that gets worse (smaller) the older 
      #    the series is.   this is really a tie-breaker for series with 
      #    otherwise identical scores. 
      if is_valid_year_b(series_year_n):
         recency_score_n = -(current_year_n - series_year_n) / 100.0;
      else:
         recency_score_n = -1.0
         
      # 7. add up and return all the scores
      return bookscore_n + namescore_n + publisherscore_n +\
         priorscore_n + yearscore_n + recency_score_n



   #===========================================================================
   def record_choice(self, series_ref):
      '''
      Records the fact that the given SeriesRef was selected by the user.  
      Future MatchScore objects will have this information, which they can
      use to compute more accurate scores.
      '''
      series_sl = self.__prior_series_sl
      key_s = sstr(series_ref.series_key) if series_ref else ""
      if key_s and not key_s in series_sl:
         series_sl.add(key_s)
         utils.persist_map({x:x for x in series_sl}, Resources.SERIES_FILE)

