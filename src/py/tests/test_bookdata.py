'''
This module contains all unittests for the fnameparser module.

Created on Jan 5, 2012
@author: cbanack
'''

from unittest import TestCase
from unittest.loader import TestLoader
from bookdata import BookData

#==============================================================================
def load_tests(loader, tests, pattern): #pylint: disable=W0613
   ''' Returns all of the testcases in this module as a testsuite '''
   return TestLoader().loadTestsFromTestCase(TestBookData)

#==============================================================================
class TestBookData(TestCase):

   # --------------------------------------------------------------------------
   def test_series_s(self):
      ''' Checks to see if the BookData's series_s property works. '''
      book = BookData()
      self.assertEquals(book.series_s, BookData.blank("series_s"))
      book.series_s = "bob"
      self.assertEquals(book.series_s, "bob")
      del book.series_s
      self.assertEquals(book.series_s, BookData.blank("series_s"))
      
   # --------------------------------------------------------------------------
   def test_issue_num_s(self):
      ''' Checks to see if the BookData's issue_num_s property works. '''
      book = BookData()
      self.assertEquals(book.issue_num_s, BookData.blank("issue_num_s"))
      book.issue_num_s = "1a"
      self.assertEquals(book.issue_num_s, "1a")
      del book.issue_num_s
      self.assertEquals(book.issue_num_s, BookData.blank("issue_num_s"))
      
   # --------------------------------------------------------------------------
   def test_volume_year_n(self):
      ''' Checks to see if the BookData's volume_year_n property works. '''
      book = BookData()
      self.assertEquals(book.volume_year_n, BookData.blank("volume_year_n"))
      book.volume_year_n = 1934
      self.assertEquals(book.volume_year_n, 1934)
      book.volume_year_n = "2015"
      self.assertEquals(book.volume_year_n, 2015)
      book.volume_year_n = None
      self.assertEquals(book.volume_year_n, BookData.blank("volume_year_n"))
      del book.volume_year_n
      self.assertEquals(book.volume_year_n, BookData.blank("volume_year_n"))
      
   # --------------------------------------------------------------------------
   def test_pub_year_n(self):
      ''' Checks to see if the BookData's pub_year_n property works. '''
      book = BookData()
      self.assertEquals(book.pub_year_n, BookData.blank("pub_year_n"))
      book.pub_year_n = 2012
      self.assertEquals(book.pub_year_n, 2012)
      book.pub_year_n = "2013"
      self.assertEquals(book.pub_year_n, 2013)
      book.pub_year_n = None
      self.assertEquals(book.pub_year_n, BookData.blank("pub_year_n"))
      del book.pub_year_n
      self.assertEquals(book.pub_year_n, BookData.blank("pub_year_n"))
      
   # --------------------------------------------------------------------------
   def test_pub_month_n(self):
      ''' Checks to see if the BookData's pub_month_n property works. '''
      book = BookData()
      self.assertEquals(book.pub_month_n, BookData.blank("pub_month_n"))
      book.pub_month_n = 9
      self.assertEquals(book.pub_month_n, 9)
      book.pub_month_n = " 11 "
      self.assertEquals(book.pub_month_n, 11)
      book.pub_month_n = None
      self.assertEquals(book.pub_month_n, BookData.blank("pub_month_n"))
      del book.pub_month_n
      self.assertEquals(book.pub_month_n, BookData.blank("pub_month_n"))
      
   # --------------------------------------------------------------------------
   def test_pub_day_n(self):
      ''' Checks to see if the BookData's pub_day_n property works. '''
      book = BookData()
      self.assertEquals(book.pub_day_n, BookData.blank("pub_day_n"))
      book.pub_day_n = 15
      self.assertEquals(book.pub_day_n, 15)
      book.pub_day_n = "16"
      self.assertEquals(book.pub_day_n, 16)
      book.pub_day_n = None
      self.assertEquals(book.pub_day_n, BookData.blank("pub_day_n"))
      del book.pub_year_n
      self.assertEquals(book.pub_day_n, BookData.blank("pub_day_n"))

   # --------------------------------------------------------------------------
   def test_rel_year_n(self):
      ''' Checks to see if the BookData's rel_year_n property works. '''
      book = BookData()
      self.assertEquals(book.rel_year_n, BookData.blank("rel_year_n"))
      book.rel_year_n = 2012
      self.assertEquals(book.rel_year_n, 2012)
      book.rel_year_n = "2013"
      self.assertEquals(book.rel_year_n, 2013)
      book.rel_year_n = None
      self.assertEquals(book.rel_year_n, BookData.blank("rel_year_n"))
      del book.rel_year_n
      self.assertEquals(book.rel_year_n, BookData.blank("rel_year_n"))
      
   # --------------------------------------------------------------------------
   def test_rel_month_n(self):
      ''' Checks to see if the BookData's rel_month_n property works. '''
      book = BookData()
      self.assertEquals(book.rel_month_n, BookData.blank("rel_month_n"))
      book.rel_month_n = 9
      self.assertEquals(book.rel_month_n, 9)
      book.rel_month_n = " 11 "
      self.assertEquals(book.rel_month_n, 11)
      book.rel_month_n = None
      self.assertEquals(book.rel_month_n, BookData.blank("rel_month_n"))
      del book.rel_month_n
      self.assertEquals(book.rel_month_n, BookData.blank("rel_month_n"))
      
   # --------------------------------------------------------------------------
   def test_rel_day_n(self):
      ''' Checks to see if the BookData's rel_day_n property works. '''
      book = BookData()
      self.assertEquals(book.rel_day_n, BookData.blank("rel_day_n"))
      book.rel_day_n = 15
      self.assertEquals(book.rel_day_n, 15)
      book.rel_day_n = "16"
      self.assertEquals(book.rel_day_n, 16)
      book.rel_day_n = None
      self.assertEquals(book.rel_day_n, BookData.blank("rel_day_n"))
      del book.rel_year_n
      self.assertEquals(book.rel_day_n, BookData.blank("rel_day_n"))

   # --------------------------------------------------------------------------
   def test_format_s(self):
      ''' Checks to see if the BookData's format_s property works. '''
      book = BookData()
      self.assertEquals(book.format_s, BookData.blank("format_s"))
      book.format_s = "BIG"
      self.assertEquals(book.format_s, "BIG")
      del book.format_s
      self.assertEquals(book.format_s, BookData.blank("format_s"))
      
   # --------------------------------------------------------------------------
   def test_title_s(self):
      ''' Checks to see if the BookData's title_s property works. '''
      book = BookData()
      self.assertEquals(book.title_s, BookData.blank("title_s"))
      book.title_s = "    Batman!!   "
      self.assertEquals(book.title_s, "Batman!!")
      del book.title_s
      self.assertEquals(book.title_s, BookData.blank("title_s"))
      
   # --------------------------------------------------------------------------
   def test_crossovers_sl(self):
      ''' Checks to see if the BookData's crossovers_sl property works. '''
      book = BookData()
      self.assertEquals(book.crossovers_sl, BookData.blank("crossovers_sl"))
      book.crossovers_sl = ["Killing Joke", None, "", "The Last Laugh"]
      self.assertEquals(book.crossovers_sl, ["Killing Joke", "The Last Laugh"])
      del book.crossovers_sl
      self.assertEquals(book.crossovers_sl, BookData.blank("crossovers_sl"))
            
   # --------------------------------------------------------------------------
   def test_summary_s(self):
      ''' Checks to see if the BookData's summary_s property works. '''
      book = BookData()
      self.assertEquals(book.summary_s, BookData.blank("summary_s"))
      book.summary_s = "    Batman beats up people!"
      self.assertEquals(book.summary_s, "Batman beats up people!")
      del book.summary_s
      self.assertEquals(book.summary_s, BookData.blank("summary_s"))
            
   # --------------------------------------------------------------------------
   def test_publisher_s(self):
      ''' Checks to see if the BookData's publisher_s property works. '''
      book = BookData()
      self.assertEquals(book.publisher_s, BookData.blank("publisher_s"))
      book.publisher_s = " DC "
      self.assertEquals(book.publisher_s, "DC")
      del book.publisher_s
      self.assertEquals(book.publisher_s, BookData.blank("publisher_s"))
      
   # --------------------------------------------------------------------------
   def test_imprint_s(self):
      ''' Checks to see if the BookData's imprint_s property works. '''
      book = BookData()
      self.assertEquals(book.imprint_s, BookData.blank("imprint_s"))
      book.imprint_s = "Wildstorm"
      self.assertEquals(book.imprint_s, "Wildstorm")
      del book.imprint_s
      self.assertEquals(book.imprint_s, BookData.blank("imprint_s"))
      
   # --------------------------------------------------------------------------
   def test_characters_sl(self):
      ''' Checks to see if the BookData's characters_sl property works. '''
      book = BookData()
      self.assertEquals(book.characters_sl, BookData.blank("characters_sl"))
      book.characters_sl = ["Hawkgirl", "", "Batman"]
      self.assertEquals(book.characters_sl, ["Hawkgirl", "Batman"])
      del book.characters_sl
      self.assertEquals(book.characters_sl, BookData.blank("characters_sl"))
      
   # --------------------------------------------------------------------------
   def test_teams_sl(self):
      ''' Checks to see if the BookData's teams_sl property works. '''
      book = BookData()
      self.assertEquals(book.teams_sl, BookData.blank("teams_sl"))
      book.teams_sl = [None, "The Avengers", "Justice League"]
      self.assertEquals(book.teams_sl, ["The Avengers", "Justice League"])
      del book.teams_sl
      self.assertEquals(book.teams_sl, BookData.blank("teams_sl"))
      
   # --------------------------------------------------------------------------
   def test_locations_sl(self):
      ''' Checks to see if the BookData's locations_sl property works. '''
      book = BookData()
      self.assertEquals(book.locations_sl, BookData.blank("locations_sl"))
      book.locations_sl = [None, "Edmonton"]
      self.assertEquals(book.locations_sl, ["Edmonton"])
      del book.locations_sl
      self.assertEquals(book.locations_sl, BookData.blank("locations_sl"))
      
   # --------------------------------------------------------------------------
   def test_writers_sl(self):
      ''' Checks to see if the BookData's writers_sl property works. '''
      book = BookData()
      self.assertEquals(book.writers_sl, BookData.blank("writers_sl"))
      book.writers_sl = [None, "Warren Ellis", "", "" ]
      self.assertEquals(book.writers_sl, ["Warren Ellis"])
      del book.writers_sl
      self.assertEquals(book.writers_sl, BookData.blank("writers_sl"))
      
   # --------------------------------------------------------------------------
   def test_pencillers_sl(self):
      ''' Checks to see if the BookData's pencillers_sl property works. '''
      book = BookData()
      self.assertEquals(book.pencillers_sl, BookData.blank("pencillers_sl"))
      book.pencillers_sl = [None, "Warren Ellis", "", "" ]
      self.assertEquals(book.pencillers_sl, ["Warren Ellis"])
      del book.pencillers_sl
      self.assertEquals(book.pencillers_sl, BookData.blank("pencillers_sl"))
      
   # --------------------------------------------------------------------------
   def test_inkers_sl(self):
      ''' Checks to see if the BookData's inkers_sl property works. '''
      book = BookData()
      self.assertEquals(book.inkers_sl, BookData.blank("inkers_sl"))
      book.inkers_sl = [None, "Warren Ellis", "", "" ]
      self.assertEquals(book.inkers_sl, ["Warren Ellis"])
      del book.inkers_sl
      self.assertEquals(book.inkers_sl, BookData.blank("inkers_sl"))
      
   # --------------------------------------------------------------------------
   def test_colorists_sl(self):
      ''' Checks to see if the BookData's colorists_sl property works. '''
      book = BookData()
      self.assertEquals(book.colorists_sl, BookData.blank("colorists_sl"))
      book.colorists_sl = [None, "Warren Ellis", "", "" ]
      self.assertEquals(book.colorists_sl, ["Warren Ellis"])
      del book.colorists_sl
      self.assertEquals(book.colorists_sl, BookData.blank("colorists_sl"))
      
   # --------------------------------------------------------------------------
   def test_letterers_sl(self):
      ''' Checks to see if the BookData's letterers_sl property works. '''
      book = BookData()
      self.assertEquals(book.letterers_sl, BookData.blank("letterers_sl"))
      book.letterers_sl = [None, "Warren Ellis", "", "" ]
      self.assertEquals(book.letterers_sl, ["Warren Ellis"])
      del book.letterers_sl
      self.assertEquals(book.letterers_sl, BookData.blank("letterers_sl"))
      
   # --------------------------------------------------------------------------
   def test_cover_artists_sl(self):
      ''' Checks to see if the BookData's cover_artists_sl property works. '''
      book = BookData()
      self.assertEquals(
         book.cover_artists_sl, BookData.blank("cover_artists_sl"))
      book.cover_artists_sl = [None, "Warren Ellis", "", "" ]
      self.assertEquals(book.cover_artists_sl, ["Warren Ellis"])
      del book.cover_artists_sl
      self.assertEquals(
         book.cover_artists_sl, BookData.blank("cover_artists_sl"))
      
   # --------------------------------------------------------------------------
   def test_editors_sl(self):
      ''' Checks to see if the BookData's editors_sl property works. '''
      book = BookData()
      self.assertEquals(book.editors_sl, BookData.blank("editors_sl"))
      book.editors_sl = [None, "Warren Ellis", "", "" ]
      self.assertEquals(book.editors_sl, ["Warren Ellis"])
      del book.editors_sl
      self.assertEquals(book.editors_sl, BookData.blank("editors_sl"))
      
   # --------------------------------------------------------------------------
   def test_tags_sl(self):
      ''' Checks to see if the BookData's tags_sl property works. '''
      book = BookData()
      self.assertEquals(book.tags_sl, BookData.blank("tags_sl"))
      book.tags_sl = [None, "Hentai", "Marvel", "" ]
      self.assertEquals(book.tags_sl, ["Hentai", "Marvel"])
      del book.tags_sl
      self.assertEquals(book.tags_sl, BookData.blank("tags_sl"))
      
   # --------------------------------------------------------------------------
   def test_notes_s(self):
      ''' Checks to see if the BookData's notes_s property works. '''
      book = BookData()
      self.assertEquals(book.notes_s, BookData.blank("notes_s"))
      book.notes_s = " A nice note"
      self.assertEquals(book.notes_s, "A nice note")
      del book.notes_s
      self.assertEquals(book.notes_s, BookData.blank("notes_s"))
      
   # --------------------------------------------------------------------------
   def test_path_s(self):
      ''' Checks to see if the BookData's path_s property works. '''
      book = BookData()
      self.assertEquals(book.path_s, BookData.blank("path_s"))
      book.path_s = "d:\bob\bob2\file.cbz"
      self.assertEquals(book.path_s, "d:\bob\bob2\file.cbz")
      del book.path_s
      self.assertEquals(book.path_s, BookData.blank("path_s"))
      
   # --------------------------------------------------------------------------
   def test_webpage_s(self):
      ''' Checks to see if the BookData's webpage_s property works. '''
      book = BookData()
      self.assertEquals(book.webpage_s, BookData.blank("webpage_s"))
      book.webpage_s = "http:\\batman.com"
      self.assertEquals(book.webpage_s, "http:\\batman.com")
      del book.webpage_s
      self.assertEquals(book.webpage_s, BookData.blank("webpage_s"))
      
   # --------------------------------------------------------------------------
   def test_cover_url_s(self):
      ''' Checks to see if the BookData's cover_url_s property works. '''
      book = BookData()
      self.assertEquals(book.cover_url_s, BookData.blank("cover_url_s"))
      book.cover_url_s = "http:\\batman.com\pic.jpg"
      self.assertEquals(book.cover_url_s, "http:\\batman.com\pic.jpg")
      del book.cover_url_s
      self.assertEquals(book.cover_url_s, BookData.blank("cover_url_s"))
      
   # --------------------------------------------------------------------------
   def test_rating_n(self):
      ''' Checks to see if the BookData's rating_n property works. '''
      book = BookData()
      self.assertEquals(book.rating_n, BookData.blank("rating_n"))
      book.rating_n = 3.4
      self.assertEquals(book.rating_n, 3.4)
      book.rating_n = "2.42"
      self.assertEquals(book.rating_n, 2.42)
      book.rating_n = None
      self.assertEquals(book.rating_n, BookData.blank("rating_n"))
      del book.rating_n
      self.assertEquals(book.rating_n, BookData.blank("rating_n"))
      
   # --------------------------------------------------------------------------
   def test_page_count_n(self):
      ''' Checks to see if the BookData's page_count_n property works. '''
      book = BookData()
      self.assertEquals(book.page_count_n, BookData.blank("page_count_n"))
      book.page_count_n = 3.4
      self.assertEquals(book.page_count_n, 3)
      book.page_count_n = "44"
      self.assertEquals(book.page_count_n, 44)
      book.page_count_n = None
      self.assertEquals(book.page_count_n, BookData.blank("page_count_n"))
      del book.page_count_n
      self.assertEquals(book.page_count_n, BookData.blank("page_count_n"))
      
      
   # --------------------------------------------------------------------------
   def test_issue_key_s(self):
      ''' Checks to see if the BookData's issue_key_s property works. '''
      book = BookData()
      self.assertEquals(book.issue_key_s, BookData.blank("issue_key_s"))
      book.issue_key_s = "9393"
      self.assertEquals(book.issue_key_s, "9393")
      del book.issue_key_s
      self.assertEquals(book.issue_key_s, BookData.blank("issue_key_s"))
      
      
   # --------------------------------------------------------------------------
   def test_series_key_s(self):
      ''' Checks to see if the BookData's series_key_s property works. '''
      book = BookData()
      self.assertEquals(book.series_key_s, BookData.blank("series_key_s"))
      book.series_key_s = "9393"
      self.assertEquals(book.series_key_s, "9393")
      del book.series_key_s
      self.assertEquals(book.series_key_s, BookData.blank("series_key_s"))
