'''
This module contains the ComicBook class, which represents a comic book
from ComicRack that we are scraping data into.

@author: Cory Banack
'''

import re
from time import strftime
from dbmodels import IssueRef, SeriesRef
from pluginbookdata import PluginBookData
import utils
from utils import sstr, is_number
import clr
import db
import fnameparser 
import log 
from bookdata import BookData

clr.AddReference('System')
from System.IO import Path
from System.Security.Cryptography import MD5
from System.Text import Encoding

#==============================================================================
class ComicBook(object):
   '''
   This class is a wrapper for the ComicRack ComicBook object, which adds 
   additional, scraper-oriented functionality to the object, and provides 
   read-only access to some of its data.
   '''
   
   # This is the magic 'tag' string we use (in the "Tags" or "Notes" fields of 
   # this comic book) to denote that this comic should always be skipped 
   # automatically, instead of scraped.  Despite the CV in the name, 
   # this is a database independent magic value.
   CVDBSKIP = 'CVDBSKIP'

   #===========================================================================   
   def __init__(self, crbook, scraper):
      '''
      Initializes this ComicBook object based on an underlying ComicRack 
      ComicBook object (the crbook) parameter and the the given ScrapeEngine.
      '''
      self.__scraper = scraper;
      self.__bookdata = PluginBookData(crbook, scraper)
      self.__parse_extra_details_from_path()

   
   #===========================================================================

   # Series name of this book.  Not None, may be empty.
   series_s = property( lambda self : self.__bookdata.series_s )
   
   # Issue number (string) of this book. Not None, may be empty.
   issue_num_s = property( lambda self : self.__bookdata.issue_num_s )
   
   # Volume (start year) of this book as an int >= -1, where -1 is unknown.
   volume_year_n = property( lambda self :  self.__bookdata.volume_year_n )
   
   # Publication year of this book, as an int >= -1, where -1 is unknown
   pub_year_n = property( lambda self : self.__bookdata.pub_year_n )
   
   # Release year of this book, as an int >= -1, where -1 is unknown
   rel_year_n = property( lambda self : self.__bookdata.rel_year_n )
   
   # The format of this book (giant, annual, etc.)  Not None, may be empty.
   format_s = property( lambda self : self.__bookdata.format_s )
   
   # The underlying path for this book (full path, including extension), 
   # or "" if it is a fileless book.  Will never be None.
   path_s = property(lambda self : self.__bookdata.path_s )
   
   # The number of pages in this book, an integer >= 0.
   page_count_n = property( lambda self : self.__bookdata.page_count_n )
   
   # the unique id string associated with this comic book's series.  all comic
   # books that appear to be from the same series will have the same id string,
   # which will be different for each series. will not be null or None.
   unique_series_s = property( lambda self : self.__unique_series_s() )  

   # an IssueRef object identifying this book in the database, if available.
   # will be None if not available, which is always the case for books that 
   # haven't been scraped before.
   issue_ref = property( lambda self : None if 
      self.__extract_issue_ref() == 'skip' else self.__extract_issue_ref() )
   
   # a SeriesRef object identifying this book's series in the database, if 
   # available.  will be None if not available, which is always the case for 
   # books that haven't been scraped before.
   series_ref = property( lambda self : self.__extract_series_ref() )
    
   # true if this book as has been marked to "skip forever" (the scraper should
   # silently skip this book if this value is true, regardless of self.issue_ref
   skip_b = property( lambda self : self.__extract_issue_ref() == 'skip' ) 

   #==========================================================================
   def create_image_of_page(self, page_index):
      ''' 
      Retrieves an COPY of a single page (a .NET "Image" object) for this 
      ComicBook.  Returns None if the requested page could not be obtained.
      
      page_index --> the index of the page to retrieve; a value on the range
                  [0, n-1], where n is self.page_count_n.
      '''
      return self.__bookdata.create_image_of_page(page_index)

   #===========================================================================
   def skip_forever(self):
      ''' 
      This method causes this book to be marked with the magic CVDBSKIP
      flag, which means that from now on, self.issue_ref will always be 
      "skip", which tells the scraper to automatically skip over this book
      without even asking the user.  
      '''
      
      # try to make everyone happy here: if notes and tags "rescrape saving"
      # are both turned on, or both turned off, then this command should just
      # write CVDBSKIP to both of them (users who turn off both still might
      # want CVDBSKIP to work!) otherwise, use the values of these 2 prefs to
      # determine which fields to write the CVDBSKIP to.
      
      bd = self.__bookdata
      notes = self.__scraper.config.rescrape_notes_b
      tags = self.__scraper.config.rescrape_tags_b
      
      if notes == tags or tags:
         bd.tags_sl = self.__add_key_to_tags(bd.tags_sl, None);
         log.debug("Added ", ComicBook.CVDBSKIP, " flag to comic book 'Tags'")
      
      if notes == tags or notes:
         bd.notes_s =self.__add_key_to_notes(bd.notes_s, None)
         log.debug("Added ", ComicBook.CVDBSKIP, " flag to comic book 'Notes'")
         
      bd.update()
         

   # =============================================================================
   def __extract_issue_ref(self): 
      '''
      This method attempts to rebuild the IssueRef that the user chose the 
      last time that they scraped this comic.  If it can do so, it will 
      return that IssueRef. If not, it will return None, or the 
      string "skip" (see below).   
      
      If the user has manually added the magic CVDBSKIP flag to the tags or 
      notes for this book, then this method will return the string "skip", 
      which should be interpreted as "never scrape this book".
      '''
      
      # in this method, its easier to work with tags as a single string
      bd = self.__bookdata
      tagstring = ', '.join(bd.tags_sl)
      
      # check for the magic CVDBSKIP skip flag
      skip_found = re.search(r'(?i)'+ComicBook.CVDBSKIP, tagstring)
      if not skip_found:
         skip_found = re.search(r'(?i)'+ComicBook.CVDBSKIP, bd.notes_s)
      retval = "skip" if skip_found else None
   
      if retval is None:   
         # if no skip tag, see if there's a key tag in the tags or notes
         issue_key = db.parse_key_tag(tagstring)
         
         if issue_key == None:
            issue_key = db.parse_key_tag(bd.notes_s)
      
         if issue_key == None:
            issue_key = int(bd.issue_key_s) if \
               utils.is_number(bd.issue_key_s) else None
      
         if issue_key != None:
            # found a key tag! convert to an IssueRef
            retval = IssueRef(self.issue_num_s, issue_key, 
               self.__bookdata.title_s, self.__bookdata.cover_url_s);
   
      return retval
   
   # =============================================================================
   def __extract_series_ref(self): 
      '''
      This method attempts to rebuild the SeriesRef that the user chose the 
      last time that they scraped this comic.  If it can do so, it will 
      return that SeriesRef, otherwise it will return None.
      '''
      
      # in this method, its easier to work with tags as a single string
      bd = self.__bookdata
      retval = None
      series_key = int(bd.series_key_s) if \
         utils.is_number(bd.series_key_s) else None
      
      if series_key != None:
         # found a key tag! convert to a sparse SeriesRef
         retval = SeriesRef(series_key, None, -1, '', -1, None);
          
      return retval
   

   #==========================================================================
   def __unique_series_s(self):
      '''
      Gets the unique series name for this ComicBook.   This is a special 
      string that will be identical for (and only for) any comic books that 
      "appear" to be from the same series.
      
      The unique series name is meant to be used internally (i.e. the key for
      a map, or for grouping ComicBooks), not for displaying to users.
      
      This value is NOT the same as the series_s property.
      '''
      bd = self.__bookdata
      sname = '' if not bd.series_s else bd.series_s
      if sname and bd.format_s:
         sname += bd.format_s
      sname = re.sub('\W+', '', sname).lower()

      svolume = ''
      if sname:
         if bd.volume_year_n and bd.volume_year_n > 0:
            svolume = sstr(bd.volume_year_n)
      else:
         # if we can't find a name at all (very weird), fall back to the
         # memory ID, which is be unique and thus ensures that this 
         # comic doesn't get lumped in to the same series choice as any 
         # other unnamed comics! 
         sname = "uniqueid-" + utils.sstr(id(self))
      
      
      # generate a hash to add onto the string.  the hash should be identical 
      # for all comics that belong to the same series, and different otherwise.
      # not how by default, comics that are in different directories are always
      # considered to belong to different series. 
      location = Path.GetDirectoryName(bd.path_s) if bd.path_s else None
      location = location if location else ''
      hash = svolume if self.__scraper.config.ignore_folders_b \
         else location + svolume
      if hash:  
         with MD5.Create() as md5:
            bytes = md5.ComputeHash(Encoding.UTF8.GetBytes(hash))
            hash = ''.join( [ "%02X" % x for x in bytes[:5] ] ).strip()
      return sname + hash 

   #===========================================================================
   def update(self, issue):
      '''
      Copies all data in the given issue into this ComicBook object and its 
      backing data source, respecting all of the overwrite/ignore rules 
      defined in the the ScrapeEngine's Configuration object.  
      
      As a side-effect, some detailed debug log information about the new values
      is also emitted.
      '''
      log.debug("setting values for this comic book ('*' = changed):")
      config = self.__scraper.config
      bd = self.__bookdata
      
      # series ---------------------
      value = self.__massage_new_string("Series", issue.series_name_s, \
         bd.series_s, config.update_series_b, config.ow_existing_b, \
         True ) # note: we ALWAYS ignore blanks for 'series'!
      if value is None: bd.dont_update("series_s") 
      else: bd.series_s = value
      
      # issue number ---------------
      value = self.__massage_new_string("Issue Number", issue.issue_num_s, \
         bd.issue_num_s, config.update_number_b, config.ow_existing_b, \
         True ) # note: we ALWAYS ignore blanks for 'issue number'!
      if value is None: bd.dont_update("issue_num_s") 
      else: bd.issue_num_s = value
      
      # title ----------------------
      value = self.__massage_new_string("Title", issue.title_s, bd.title_s, \
         config.update_title_b, config.ow_existing_b, config.ignore_blanks_b )
      if value is None: bd.dont_update("title_s") 
      else: bd.title_s = value
      
      # crossovers -----------
      value = self.__massage_new_string_list("Crossovers", 
         issue.crossovers_sl, bd.crossovers_sl, config.update_crossovers_b,
         config.ow_existing_b, config.ignore_blanks_b )
      if value is None: bd.dont_update("crossovers_sl")
      else: bd.crossovers_sl = value
      
      # summary --------------------
      value = self.__massage_new_string("Summary", issue.summary_s, \
         bd.summary_s, config.update_summary_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("summary_s")
      else: bd.summary_s = value
      
      # release (in store) date -----------------------
      value = self.__massage_new_date("Release Date", 
         (issue.rel_year_n, issue.rel_month_n, issue.rel_day_n),
         (bd.rel_year_n, bd.rel_month_n, bd.rel_day_n), 
         config.update_released_b, config.ow_existing_b, 
         config.ignore_blanks_b, -1)
      if value is None: 
         bd.dont_update("rel_year_n")
         bd.dont_update("rel_month_n")
         bd.dont_update("rel_day_n")
      else:
         bd.rel_year_n, bd.rel_month_n, bd.rel_day_n = value
         
      # published (cover) date -----------------------
      value = self.__massage_new_date("Publish Date", 
         (issue.pub_year_n, issue.pub_month_n, issue.pub_day_n),
         (bd.pub_year_n, bd.pub_month_n, bd.pub_day_n), 
         config.update_published_b, config.ow_existing_b, 
         config.ignore_blanks_b, -1)
      if value is None: 
         bd.dont_update("pub_year_n")
         bd.dont_update("pub_month_n")
         bd.dont_update("pub_day_n")
      else:
         bd.pub_year_n, bd.pub_month_n, bd.pub_day_n = value
      
      # volume --------------------
      value = self.__massage_new_number("Volume", issue.volume_year_n, \
      bd.volume_year_n, config.update_volume_b, config.ow_existing_b, \
      config.ignore_blanks_b, -1, lambda x : x > 0 )
      if value is None: bd.dont_update("volume_year_n")
      else: bd.volume_year_n = value
       
      # publisher and imprint -----
      self.__update_publishers(issue, config)
      
      # characters ----------------
      value = self.__massage_new_string_list("Characters", \
         issue.characters_sl, bd.characters_sl, config.update_characters_b, \
         config.ow_existing_b, config.ignore_blanks_b )
      if value is None: bd.dont_update("characters_sl")
      else: bd.characters_sl = value
      
      # teams --------------------
      value = self.__massage_new_string_list("Teams", issue.teams_sl, bd.teams_sl,\
         config.update_teams_b, config.ow_existing_b, config.ignore_blanks_b )
      if value is None: bd.dont_update("teams_sl")
      else: bd.teams_sl = value
      
      # locations ----------------
      value = self.__massage_new_string_list( "Locations", issue.locations_sl, \
         bd.locations_sl, config.update_locations_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("locations_sl")
      else: bd.locations_sl = value
      
      # writer --------------------
      value = self.__massage_new_string_list("Writers", issue.writers_sl, \
         bd.writers_sl, config.update_writer_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("writers_sl")
      else: bd.writers_sl = value
         
      # penciller -----------------
      value = self.__massage_new_string_list("Pencillers", issue.pencillers_sl, \
         bd.pencillers_sl, config.update_penciller_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("pencillers_sl")
      else: bd.pencillers_sl = value
      
      # inker ---------------------
      value = self.__massage_new_string_list("Inkers", issue.inkers_sl, \
         bd.inkers_sl, config.update_inker_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("inkers_sl")
      else: bd.inkers_sl = value
         
      # colorist -----------------
      value = self.__massage_new_string_list("Colorists", issue.colorists_sl, \
         bd.colorists_sl, config.update_colorist_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("colorists_sl")
      else: bd.colorists_sl = value
         
      # letterer -----------------
      value = self.__massage_new_string_list("Letterers", issue.letterers_sl, \
         bd.letterers_sl, config.update_letterer_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("letterers_sl")
      else: bd.letterers_sl = value
         
      # coverartist --------------
      value = self.__massage_new_string_list("CoverArtists", 
         issue.cover_artists_sl, bd.cover_artists_sl, \
         config.update_cover_artist_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("cover_artists_sl")
      else: bd.cover_artists_sl = value
         
      # editor -------------------   
      value = self.__massage_new_string_list("Editors", issue.editors_sl, \
         bd.editors_sl, config.update_editor_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("editors_sl")
      else: bd.editors_sl = value
   
      # webpage ----------------
      value = self.__massage_new_string("Webpage", issue.webpage_s, \
         bd.webpage_s, config.update_webpage_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("webpage_s")
      else: bd.webpage_s = value
           
      # rating -----------------
      value = self.__massage_new_number("Rating", issue.rating_n, \
         bd.rating_n, config.update_rating_b, config.ow_existing_b, \
         config.ignore_blanks_b, 0.0, lambda x: x >= 0 and x <= 5 )
      if value is None: bd.dont_update("rating_n")
      else: bd.rating_n = value
         
      # tags -------------------
      new_tags = self.__add_key_to_tags(bd.tags_sl, issue.issue_key)
      value = self.__massage_new_string_list("Tags", new_tags, \
         bd.tags_sl, config.rescrape_tags_b, True, False )
      if value is None: bd.dont_update("tags_sl")
      else: bd.tags_sl = value
      
      # notes ------------------
      new_notes = self.__add_key_to_notes(bd.notes_s, issue.issue_key)
      value = self.__massage_new_string("Notes", new_notes, \
         bd.notes_s, config.rescrape_notes_b, True, False )
      if value is None: bd.dont_update("notes_s")
      else: bd.notes_s = value
      
      # issue_key ---------------------
      value = self.__massage_new_string("Issue Key", issue.issue_key, \
         bd.issue_key_s, True, True, False )
      if value is None: bd.dont_update("issue_key_s") 
      else: bd.issue_key_s = value
      
      # series_key ---------------------
      value = self.__massage_new_string("Series Key", issue.series_key, \
         bd.series_key_s, True, True, False )
      if value is None: bd.dont_update("series_key_s") 
      else: bd.series_key_s = value
      
      # cover url -------------
      self.__update_cover_url(issue)
      
      bd.update();
   
   #===========================================================================
   def __update_publishers(self, issue, config):
      '''
      Uses the given Configuration to copy the publisher and imprint data in
      the given issue into the underlying BookData (changing them as required
      by the Configuration).  Prints out a debug line for each value.
      '''
       
      bd = self.__bookdata
      publisher_s = issue.publisher_s # publisher and (maybe) imprint owner
      imprint_s = issue.imprint_s # imprint, or '' if one there isn't one
      
      # 1. the user may have defined their own custom imprint mappings.  
      # if so, they will override any previously applied imprints
      key = imprint_s if imprint_s else publisher_s
      if key and key.lower() in config.user_imprints_sm:
         publisher_s = config.user_imprints_sm[key.lower()]
         imprint_s = key
               
      # 2. if we found an imprint, the user may prefer that it be listed as 
      #    the publisher (i.e. if we DON'T convert imprints).
      if not config.convert_imprints_b and imprint_s:
         publisher_s = imprint_s
         imprint_s = ''
         
      # 3. the user may have defined publisher aliases. deal with that here.
      aliases = config.publisher_aliases_sm;
      if publisher_s.lower() in aliases:
         publisher_s = aliases[publisher_s.lower()]
      if imprint_s.lower() in aliases:
         imprint_s = aliases[imprint_s.lower()]
         
      # 4. if the imprint and the publisher are identical, the user is trying
      #    to nullify an existing imprint by overriding it to be equal to
      #    itself. in that case, only keep the publisher.
      if publisher_s == imprint_s:
         imprint_s = ''
      
      # imprint -------------------
      value = self.__massage_new_string("Imprint", imprint_s, \
         bd.imprint_s, config.update_imprint_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("imprint_s")
      else: bd.imprint_s = value
            
      # publisher -----------------
      value = self.__massage_new_string("Publisher", publisher_s, \
         bd.publisher_s, config.update_publisher_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("publisher_s")
      else: bd.publisher_s = value
   
   #===========================================================================
   def __update_cover_url(self, issue):
      '''
      Obtains the appropriate cover art url for this book (if available), based
      on the given Issue object.  Sets value in the underlying BookData, and 
      prints out a debug line about it.  The implementing instance of BookData
      may or may not use this URL to install a cover image when saved out.
      '''
      config = self.__scraper.config
      bd = self.__bookdata
      
      url_s = None
      alt_cover_key = sstr(issue.issue_key)+"-altcover"
      if alt_cover_key in config.session_data_map:
         url_s = config.session_data_map[alt_cover_key]
      if not url_s and len(issue.image_urls_sl):  
         url_s = issue.image_urls_sl[0]
         
      label = "Cover Art URL"
      if not url_s:
         log.debug("-->  ", label.ljust(15),": --- not available! ---")
         bd.dont_update("cover_url_s")
      else:
         log.debug("-->  ", label.ljust(15),": ", url_s)
         bd.cover_url_s = url_s
            
      
   #===========================================================================
   def __add_key_to_tags(self, tags_sl, issue_key):
      '''
      Returns the given tag list, but with a "key tag" for the given issue_key 
      added in (iff key tags are supported by the current database 
      implementation.)  If the given string already contains a valid 
      key tag, the tag will be REPLACED with the new one, otherwise the new key 
      tag will be appended to the end of the list.
      
      If the given issue_key is None, the tags will be updated with the
      magic CVDBSKIP tag instead of a regular key tag.
      
      This method never returns None. 
      '''
      
      updated_tagstring_s = None   # our return value
      
      # 1. clean up whitespace and None in our tagstring parameter
      tagstring_s = ', '.join(tags_sl).strip() if tags_sl else ''
      
      key_tag_s = db.create_key_tag_s(issue_key) \
         if issue_key != None else ComicBook.CVDBSKIP 
      if key_tag_s and tagstring_s:
         # 2. we have both a new key tag AND a non-empty tagstring; find and 
         #    replace the existing tag (if it exists in the tagtring) 
         #    with the new one. 
         matches = False
         prev_issue_key = db.parse_key_tag(tagstring_s)
         if prev_issue_key:
            prev_key_tag_s = db.create_key_tag_s(prev_issue_key)
            if prev_key_tag_s:
               regexp = re.compile(r"(?i)" + prev_key_tag_s)
               matches = regexp.search(tagstring_s)
         if matches:
            # 2a. yup, found an existing key tag--replace it with the new one
            updated_tagstring_s = re.sub(regexp, key_tag_s, tagstring_s)
         else:
            # 2b. nope, no previous key tag found--just append the new key tag
            if tagstring_s[-1] == ",":
               tagstring_s = tagstring_s[:-1]
            updated_tagstring_s = tagstring_s +", " + key_tag_s
      elif key_tag_s:
         # 3. no previous tagstring, so the key tag *becomes* the new tagstring
         updated_tagstring_s = key_tag_s
      else:
         # 4. there's no key tag available, so don't change the tagstring.
         updated_tagstring_s = tagstring_s
   
      return updated_tagstring_s.split(", ")
   
   
   #===========================================================================
   def __add_key_to_notes(self, notestring_s, issue_key):
      '''
      Returns a copy of the given comic book note string, but with a "key tag" 
      for the given issue_key appended onto the end (iff key tags are
      supported by the current database implementation.)  If the given 
      notes string already contains a valid key tag, the existing tag will be 
      REPLACED with the new one.
      
      If the given issue_key is None, the note string will be updated with the
      magic CVDBSKIP tag instead of a regular key tag.
      
      This method never returns None. 
      '''
      updated_notestring_s = None # our return value
      
      # 1. clean up whitespace and None in our notestring parameter
      notestring_s = notestring_s.strip() if notestring_s else ''
      
      # Create a key-note that looks like either:
      # 1) Scraped metadata from ComicVine [CVDB9999]. 
      # 2) Scraped metadata from ComicVine [CVDB9999] on 2013.05.14 21:43:06. 
      key_tag_s = db.create_key_tag_s(issue_key) \
         if issue_key != None else ComicBook.CVDBSKIP
      date_s = " on "+strftime(r'%Y.%m.%d %X') \
         if self.__scraper.config.note_scrape_date_b else "" 
      key_note_s = 'Scraped metadata from {0} [{1}]{2}.'.format(
         "ComicVine", key_tag_s, date_s) if key_tag_s else ''
         
      if key_note_s and notestring_s:
         # 2. we have both a new key-note (based on the key tag), AND a 
         #    non-empty notestring; find and replace the existing key-note (if 
         #    it exists in the notestring) with the new one. 
         matches = False
         prev_issue_key = db.parse_key_tag(notestring_s)
         if prev_issue_key:
            prev_key_tag = db.create_key_tag_s(prev_issue_key)
            if prev_key_tag:
               regexp = re.compile( r"(?i)Scraped.*?" + prev_key_tag \
                   + "(]\.|.*?[\d\.]{8,} [\d:]{6,}\.)")                                   
               matches = regexp.search(notestring_s) 
         if matches:
            # 2a. yup, found an existing key-note--replace it with the new one
            updated_notestring_s = re.sub(regexp, key_note_s, notestring_s)
         else:
            # 2b. nope, no previous key-note found.  try looking for the key
            #     tag on it's own (i.e. if the user added it by hand)
            if prev_issue_key:
               prev_key_tag = db.create_key_tag_s(prev_issue_key)
               if prev_key_tag:
                  regexp = re.compile(r"(?i)" + prev_key_tag)
                  matches = regexp.search(notestring_s)
            if matches:
               # 2c. yup, found a key tag--replace it with the new one
               updated_notestring_s = re.sub(regexp, key_tag_s, notestring_s)
            else:
               # 2b. nope, no previous key found--just append the new key-note
               updated_notestring_s = notestring_s + "\n\n" + key_note_s 
      elif key_note_s:  
         # 3. no previous notestring, so the key-note *becomes* the new string
         updated_notestring_s = key_note_s
      else:
         # 4. there's no key tag available, so don't change the tagstring.
         updated_notestring_s = notestring_s
   
      return updated_notestring_s
   
   

   
   
   
   #===========================================================================
   @staticmethod 
   def __massage_new_string( 
         label, new_value, old_value, update, overwrite, ignoreblanks):
      ''' 
      Returns a string value that should be copied into our backing ComicBook
      object, IFF that string value is not None.   Uses a number of rules to
      decide what value to return.
      
      label - a human readable description of the given string being changed.
      new_value - the proposed new string value to copy over.
      old_value - the original value that the new value would copy over.
      update - if false, this method always returns None
      overwrite - whether it's acceptable to overwrite the old value with the
                  new value when the old value is non-blank.
      ignoreblanks - if true, we'll never overwrite an old non-blank value
                     with a new, blank value..
      ''' 
      
      # first, a little housekeeping so that we stay really robust
      if new_value is None:
         new_value = ''
      if old_value is None:
         old_value = ''
      if not isinstance(new_value, basestring) or \
         not isinstance(old_value,basestring):
         raise TypeError("wrong types for this method (" + label +")")
      old_value = old_value.strip();
      new_value = new_value.strip();
      
      # now decide about whether or not to actually do the update
      # only update if all of the following are true:
      #  1) the update option is turned on for this particular field
      #  2) we can overwrite the existing value, or there is no existing value
      #  3) we're not overwriting with a blank value unless we're allowed to
      retval = None;      
      if update and (overwrite or not old_value) and \
         not (ignoreblanks and not new_value):
          
         retval = new_value
         
         marker = ' '
         if old_value != new_value:
            marker = '*'
         
         chars = retval.replace('\n', ' ')
         if len(chars) > 70:
            chars = chars[:70] + " ..."
         log.debug("--> ", marker, label.ljust(15), ": ", chars)
      else:
         log.debug("-->  ", label.ljust(15), ": --- skipped ---")
      return retval
   
   
   #===========================================================================
   @staticmethod 
   def __massage_new_string_list( 
         label, new_list, old_list, update, overwrite, ignoreblanks):
      ''' 
      Returns a string list [] that should be copied into our backing ComicBook
      object, IFF that string list is not None.   Uses a number of rules to
      decide what value to return.
      
      label - a human readable description of the given string being changed.
      new_list - the proposed new string list to copy over.
      old_list - the original list that the new list would copy over.
      update - if false, this method always returns None
      overwrite - whether it's acceptable to overwrite the old list with the
                  new list when the old list is not empty.
      ignoreblanks - if true, we'll never overwrite an old non-empty list
                     with a new, empty one.
      ''' 
      
      # first, a little housekeeping so that we stay really robust
      new_list = [] if new_list is None else list(new_list)
      new_list = [x for x in new_list if x != None and len(x.strip())>0]
      old_list = [] if old_list is None else list(old_list)
      old_list = [x for x in old_list if x != None and len(x.strip())>0]
      
      
      # now decide about whether or not to actually do the update
      # only update if all of the following are true:
      #  1) the update option is turned on for this particular field
      #  2) we can overwrite the existing value, or there is no existing value
      #  3) we're not overwriting with a blank value unless we're allowed to
      retval = None;      
      if update and (overwrite or len(old_list)==0) and \
            (not ignoreblanks or len(new_list) > 0):
          
         retval = new_list
         
         marker = ' '
         if old_list != new_list:
            marker = '*'
         
         chars = ', '.join(retval).replace('\n', ' ')
         if len(chars) > 70:
            chars = chars[:70] + " ..."
         log.debug("--> ", marker, label.ljust(15), ": ", chars)
      else:
         log.debug("-->  ", label.ljust(15), ": --- skipped ---")
      return retval
   
   
   #===========================================================================
   @staticmethod 
   def __massage_new_number(label, new_value, old_value, update, overwrite, \
      ignoreblanks, blank_value, is_valid=None, remap_invalid=None):
      ''' 
      Returns an number (int or float) value that should be copied into our 
      backing ComicBook object, IFF that value is not None.   Uses a number of 
      rules to decide what value to return.
      
      label - a human readable description of the given number being changed.
      new_value - the proposed new number value to copy over.
      old_value - the original value that the new value would copy over.
      update - if false, this method always returns None
      overwrite - whether it's acceptable to overwrite the old value with the
            new value when the old value is non-blank.
      ignoreblanks - if true, we'll never overwrite with an old non-blank value
            with a new, blank value.
      blank_value - the number value that should be considered 'blank' (0? -1?)
      is_valid - an optional single argument function that decides if the given
            int return value is valid.  If not, it is changed to 'blank_value' 
            before it is returned, OR if possible it is remapped with...
      remap_invalid - an optional single argument function that converts the 
            given invalid return value (according to 'is_valid') into a 
            new, valid return value.
      ''' 
      
      
      # first, a little housekeeping so that we stay really robust
      if new_value is None:
         new_value = blank_value;
      if old_value is None:
         old_value = blank_value;
      if type(blank_value) != int and type(blank_value) != float:
         raise TypeError("wrong type for blank value");
      if type(old_value) != int and type(old_value) != float:
         raise TypeError("wrong type for old value");
      if type(old_value) != type(blank_value):
         raise TypeError("blank type is invalid type");
      if type(old_value) != type(new_value):
         try:
            if isinstance(old_value, int):
               new_value = int(new_value)
            else:
               new_value = float(new_value)
         except:
            log.debug("--> WARNING: can't convert '", new_value,
                "' into a ", type(old_value) )
            new_value = blank_value
            
      # check for (and possibly repair) the validity of the new_value
      if is_valid:
         if not is_valid(new_value):
            if remap_invalid:  
               new_value = remap_invalid(new_value)
         if not is_valid(new_value):
            new_value = blank_value
           
      # now decide about whether or not to actually do the update
      # only update if all of the following are true:
      #  1) the update option is turned on for this particular field
      #  2) we can overwrite the existing value, or there is no existing value
      #  3) we're not overwriting with a blank value unless we're allowed to
      retval = None;  
      if update and (overwrite or old_value == blank_value) and \
         not (ignoreblanks and new_value == blank_value):
         retval = new_value
         
         marker = ' '
         if old_value != new_value:
            marker = '*'
            
         if retval == blank_value:
            log.debug("--> ", marker, label.ljust(15), ": ")
         else: 
            log.debug("--> ", marker, label.ljust(15), ": ", retval)
      else:
         log.debug("-->  ", label.ljust(15), ": --- skipped ---")
         
      # last minute type checking, just to be sure the returned value type is ok
      if retval != None:
         retval = float(retval) if type(old_value) == float else int(retval)
      return retval
   
   #===========================================================================
   @staticmethod 
   def __massage_new_date(label, new_value, old_value, update, overwrite, \
      ignoreblanks, blank_value):
      ''' 
      Returns a date tuple of three ints (YYYY,MM,DD) that should be copied into
      our backing ComicBook object, IFF that tuple is not None.   Uses a number
      of rules to decide what to return.
      
      label - a human readable description of the given date being changed.
      new_value - proposed new date to copy over. a tuple of ints (YYYY,MM,DD)
      old_value - original date.  a tuple of ints (YYYY,MM,DD)
      update - if false, this method always returns None
      overwrite - whether it's acceptable to overwrite the old value with the
            new value when the old value is non-blank.
      ignoreblanks - if true, we'll never overwrite with an old non-blank date
            with a new date that has any blank values.
      blank_value - the value that should be considered 'blank' for
            any of the individual elements in the given date tuples.  
      ''' 
      
      
      # first, a little housekeeping so that we stay really robust
      blank_date = (blank_value,blank_value,blank_value)
      new_value = blank_date if not new_value else new_value
      old_value = blank_date if not old_value else old_value
      if type(blank_value) != int:
         raise TypeError("wrong type for blank value");
      if len(old_value) != 3 or type(old_value[2]) != int:
         raise TypeError("wrong type for old value");
      if len(new_value) != 3 or type(new_value[2]) != int:
         raise TypeError("wrong type for new value");
            
      # now decide about whether or not to actually do the update
      # only update if all of the following are true:
      #  1) the update option is turned on for this particular field
      #  2) we can overwrite the existing value, or there is no existing value
      #  3) we're not overwriting with a blank value unless we're allowed to
      retval = None;
      if update and (overwrite or old_value == blank_date) and \
            not (ignoreblanks and new_value == blank_date):
         retval = new_value
         
         marker = ' '
         if old_value != new_value:
            marker = '*'
            
         if retval == blank_date: 
            log.debug("--> ", marker, label.ljust(15), ": ")
         else: 
            log.debug("--> ", marker, label.ljust(15), ": ", '-'.join(
               ['??' if x == blank_value else sstr(x) for x in retval]) )
      else:
         log.debug("-->  ", label.ljust(15), ": --- skipped ---")
         
      return retval
   
   
   # ==========================================================================
   def __parse_extra_details_from_path(self):
      ''' 
      Series name, issue number, and volume year are all critical bits of data 
      for scraping purposes--yet fresh, unscraped files often do not have them.
      So when some or all of these values are missing, this method tries to fill
      them in by parsing them out of the comic's path.
      '''
      
      bd  = self.__bookdata
      no_series = BookData.blank("series_s") == bd.series_s
      no_issuenum = BookData.blank("issue_num_s") == bd.issue_num_s
      no_year = BookData.blank("pub_year_n") == bd.pub_year_n
      if no_series or no_issuenum or no_year:
         if bd.path_s:
            # 1. at least one detail is missing, and we have a path name to
            #    work with, so lets try to extract some details that way.
            filename = Path.GetFileName(bd.path_s)
            config = self.__scraper.config
            regex = config.alt_search_regex_s
            extracted = None
            
            # 2. first, extract using the user specified regex, if there is one
            if regex:
               extracted = fnameparser.regex(filename, regex) 
            if not extracted:
               extracted = fnameparser.extract(filename) # never fails
               
            # 3. now that we have some extracted data, use it to fill in
            #    any gaps in our details.
            if no_series:
               bd.series_s = extracted[0]
            if no_issuenum:
               bd.issue_num_s = extracted[1]
            if no_year:
               bd.pub_year_n = int(extracted[2]) \
                  if is_number(extracted[2])\
                     else BookData.blank("pub_year_n")
               
               