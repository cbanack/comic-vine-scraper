'''
This module contains the MatchScore class, which is used for computing how well
a given SeriesRef "matches" the a particular ComicBook.

Created on Mar 3, 2012
@author: cbanack
'''
import re
import datetime
import log

#==============================================================================
class MatchScore(object):
   '''
   Instances of this class can compute how well a SeriesRef "matches" a 
   particular ComicBook.  This class maintains its own state, and does 
   file IO to record that state for future instances.  Therefore, there
   should only ever be one one instance of this class in existence!
   '''
   
   #=========================================================================== 
   def __init__(self):
      ''' Initializes a new Configuration object with default settings '''
      # coryhigh: read in prior series here
      pass
   
   
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
      namescore_n -= len(serieswords)
      
      # 2. if the series was one that the user has chosen in the past, give it's
      #    score a very small boost (about the equivalent of it matching one 
      #    more word on the namescore  
      priorscore_n = 0
      
      # 3. get the 'bookscore', which compares our book's issue number
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
      

      # 4. get the 'yearscore', which severely penalizes (-500) any series 
      #    that started after the year that the current book was published.
      current_year_n = datetime.datetime.now().year
      def valid_year_b(year_n):
         return year_n > 1900 and year_n <= current_year_n+1
      
      series_year_n = series_ref.start_year_n
      yearscore_n = 0
      if valid_year_b(book.year_n):
         if not valid_year_b(series_year_n):
            yearscore_n = -100
         elif series_year_n > book.year_n:
            yearscore_n = -500
            
      # 5. get the 'recency score', which is a tiny negative value (usually
      #    around on the range [-0.50, 0]) that gets worse (smaller) the older 
      #    the series is.   this is really a tie-breaker for series with 
      #    otherwise identical scores. 
      if valid_year_b(series_year_n):
         recency_score_n = -(current_year_n - series_year_n) / 100.0;
      else:
         recency_score_n = -1.0
         
      # 6. add up and return all the scores
      return bookscore_n + namescore_n + \
         priorscore_n + yearscore_n + recency_score_n



   #===========================================================================
   def record_choice(self, series_ref):
      '''
      Records the fact that the given SeriesRef was selected by the user.  
      Future MatchScore objects will have this information, which they can
      use to compute more accurate scores.
      '''
      # coryhigh: implement this!
      log.debug("RECORDED: ", series_ref)

