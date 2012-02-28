'''
This module contains the ComicBook class, which represents a comic book
from ComicRack that we are scraping data into.

@author: Cory Banack
'''
from dbmodels import IssueRef
from pluginbookdata import PluginBookData
from time import strftime
from utils import sstr
import db
import fnameparser 
import log 
import re
import utils
from bookdata import BookData

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
      self.__parse_extra_details_from_filename()

   
   #===========================================================================

   # Series name of this book.  Not None, may be empty.
   series_s = property( lambda self : self.__bookdata.series_s )
   
   # Issue number (string) of this book. Not None, may be empty.
   issue_num_s = property( lambda self : self.__bookdata.issue_num_s )
   
   # Volume (start year) of this book as an int >= -1, where -1 is unknown.
   volume_year_n = property( lambda self :  self.__bookdata.volume_year_n )
   
   # Publication year of this book, as an int >= -1, where -1 is unknown
   year_n = property( lambda self : self.__bookdata.year_n )
   
   # The format of this book (giant, annual, etc.)  Not None, may be empty.
   format_s = property( lambda self : self.__bookdata.format_s )
   
   # The underlying filename for this book, or "" if it is a fileless book.
   # Will never be None.
   filename_s = property(lambda self : self.__bookdata.filename_s )
   
   # The number of pages in this book, an integer >= 0.
   page_count_n = property( lambda self : self.__bookdata.page_count_n )
   
   # the unique id string associated with this comic book's series.  all comic
   # books that appear to be from the same series will have the same id string,
   # which will be different for each series. will not be null or None.
   unique_series_s = property( lambda self : self.__unique_series_s() )  

   # a comicvine IssueRef object based if this book has been scraped before,
   # or None if it hasn't. 
   issue_ref = property( lambda self : None if 
      self.__extract_issue_ref() == 'skip' else self.__extract_issue_ref() )
    
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
         bd.tags_sl = self.__update_tags_sl(bd.tags_sl, None);
         log.debug("Added ", ComicBook.CVDBSKIP, " flag to comic book 'Tags'")
      
      if notes == tags or notes:
         bd.notes_s =self.__update_notes_s(bd.notes_s, None)
         log.debug("Added ", ComicBook.CVDBSKIP, " flag to comic book 'Notes'")
         

   # =============================================================================
   def __extract_issue_ref(self): 
      '''
      This method looks in the tags and notes fields of the this book for 
      evidence that the it has been scraped before.   If possible, it will 
      construct an IssueRef based on that evidence, and return it. If not, 
      it will return None, or the string "skip" (see below).   
      
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
      
         if issue_key != None:
            # found a key tag! convert to an IssueRef
            retval = IssueRef(self.issue_num_s, issue_key, 
               self.__bookdata.title_s);
   
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
            svolume = "[v" + sstr(bd.volume_year_n) + "]"
      else:
         # if we can't find a name at all (very weird), fall back to the
         # memory ID, which is be unique and thus ensures that this 
         # comic doesn't get lumped in to the same series choice as any 
         # other unnamed comics! 
         sname = "uniqueid-" + utils.sstr(id(self))
      return sname + svolume


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
      
      # storyarc -------------------
      value = self.__massage_new_string("Story Arc", issue.storyarc_s, 
         bd.storyarc_s, config.update_storyarc_b, config.ow_existing_b, 
         config.ignore_blanks_b )
      if value is None: bd.dont_update("storyarc_s") 
      else: bd.storyarc_s = value
         
      # alternate series -----------
      value = self.__massage_new_string_list("Crossover", 
         issue.alt_series_names, bd.alt_series_sl, config.update_alt_series_b,
         config.ow_existing_b, config.ignore_blanks_b )
      if value is None: bd.dont_update("alt_series_sl")
      else: bd.alt_series_sl = value
      
      # summary --------------------
      value = self.__massage_new_string("Summary", issue.summary_s, \
         bd.summary_s, config.update_summary_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("summary_s")
      else: bd.summary_s = value
      
      # year -----------------------
      value = self.__massage_new_number("Year", issue.year_n, \
         bd.year_n, config.update_year_b, config.ow_existing_b, \
         True, -1, lambda x : x > 0 ) # note: we ALWAYS ignore blanks for 'year'
      if value is None: bd.dont_update("year_n")
      else: bd.year_n = value
      
      # month ----------------------
      value = self.__massage_new_number("Month", issue.month_n, bd.month_n, \
         config.update_month_b, config.ow_existing_b, True, -1, \
         lambda x : x>=1 and x <= 31 ) # ALWAYS ignore blanks for 'month'
      if value is None: bd.dont_update("month_n")
      else: bd.month_n = value
      
      # volume --------------------
      value = self.__massage_new_number("Volume", issue.start_year_n, \
      bd.volume_year_n, config.update_volume_b, config.ow_existing_b, \
      config.ignore_blanks_b, -1, lambda x : x > 0 )
      if value is None: bd.dont_update("volume_year_n")
      else: bd.volume_year_n = value
       
      # if we found an imprint for this issue, the user may prefer that the 
      # imprint be listed as the publisher (instead). if so, make that change
      # before writing the 'imprint' and 'publisher' fields out to the book:
      if not config.convert_imprints_b and issue.imprint_s:
         issue.publisher_s = issue.imprint_s
         issue.imprint_s = ''                                   
            
      # imprint -------------------
      value = self.__massage_new_string("Imprint", issue.imprint_s, \
         bd.imprint_s, config.update_imprint_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("imprint_s")
      else: bd.imprint_s = value
            
      # publisher -----------------
      value = self.__massage_new_string("Publisher", issue.publisher_s, \
         bd.publisher_s, config.update_publisher_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("publisher_s")
      else: bd.publisher_s = value
      
      # characters ----------------
      value = self.__massage_new_string_list("Characters", \
         issue.characters, bd.characters_sl, config.update_characters_b, \
         config.ow_existing_b, config.ignore_blanks_b )
      if value is None: bd.dont_update("characters_sl")
      else: bd.characters_sl = value
      
      # teams --------------------
      value = self.__massage_new_string_list("Teams", issue.teams, bd.teams_sl,\
         config.update_teams_b, config.ow_existing_b, config.ignore_blanks_b )
      if value is None: bd.dont_update("teams_sl")
      else: bd.teams_sl = value
      
      # locations ----------------
      value = self.__massage_new_string_list( "Locations", issue.locations, \
         bd.locations_sl, config.update_locations_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("locations_sl")
      else: bd.locations_sl = value
      
      # writer --------------------
      value = self.__massage_new_string_list("Writers", issue.writers, \
         bd.writers_sl, config.update_writer_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("writers_sl")
      else: bd.writers_sl = value
         
      # penciller -----------------
      value = self.__massage_new_string_list("Pencillers", issue.pencillers, \
         bd.pencillers_sl, config.update_penciller_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("pencillers_sl")
      else: bd.pencillers_sl = value
      
      # inker ---------------------
      value = self.__massage_new_string_list("Inkers", issue.inkers, \
         bd.inkers_sl, config.update_inker_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("inkers_sl")
      else: bd.inkers_sl = value
         
      # colorist -----------------
      value = self.__massage_new_string_list("Colorists", issue.colorists, \
         bd.colorists_sl, config.update_colorist_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("colorists_sl")
      else: bd.colorists_sl = value
         
      # letterer -----------------
      value = self.__massage_new_string_list("Letterers", issue.letterers, \
         bd.letterers_sl, config.update_letterer_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("letterers_sl")
      else: bd.letterers_sl = value
         
      # coverartist --------------
      value = self.__massage_new_string_list("CoverArtists", 
         issue.cover_artists, bd.cover_artists_sl, \
         config.update_cover_artist_b, config.ow_existing_b, \
         config.ignore_blanks_b )
      if value is None: bd.dont_update("cover_artists_sl")
      else: bd.cover_artists_sl = value
         
      # editor -------------------   
      value = self.__massage_new_string_list("Editors", issue.editors, \
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
      new_tags = self.__update_tags_sl(bd.tags_sl, issue.issue_key)
      value = self.__massage_new_string_list("Tags", new_tags, \
         bd.tags_sl, config.rescrape_tags_b, True, False )
      if value is None: bd.dont_update("tags_sl")
      else: bd.tags_sl = value
      
      # notes ------------------
      new_notes = self.__update_notes_s(bd.notes_s, issue.issue_key)
      value = self.__massage_new_string("Notes", new_notes, \
         bd.notes_s, config.rescrape_notes_b, True, False )
      if value is None: bd.dont_update("notes_s")
      else: bd.notes_s = value
      
      # cover url -------------
      self.__update_cover_url_s(issue)
      
      bd.update();
   
   
   #===========================================================================
   def __update_cover_url_s(self, issue):
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
      if not url_s and len(issue.image_urls):  
         url_s = issue.image_urls[0]
         
      label = "Cover Art URL"
      if not url_s:
         log.debug("-->  ", label.ljust(15),": --- not available! ---")
         bd.dont_update("cover_url_s")
      else:
         log.debug("-->  ", label.ljust(15),": ", url_s)
         bd.cover_url_s = url_s
            
      
   #===========================================================================
   def __update_tags_sl(self, tags_sl, issue_key):
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
   def __update_notes_s(self, notestring_s, issue_key):
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
      
      key_tag_s = db.create_key_tag_s(issue_key) \
         if issue_key != None else ComicBook.CVDBSKIP
      key_note_s = 'Scraped metadata from {0} [{1}] on {2}.'.format(
         "ComicVine", key_tag_s, strftime(r'%Y.%m.%d %X')) if key_tag_s else ''
         
      if key_note_s and notestring_s:
         # 2. we have both a new key-note (based on the key tag), AND a 
         #    non-empty notestring; find and replace the existing key-note (if 
         #    it exists in the notestring) with the new one. 
         matches = False
         prev_issue_key = db.parse_key_tag(notestring_s)
         if prev_issue_key:
            prev_key_tag = db.create_key_tag_s(prev_issue_key)
            if prev_key_tag:
               regexp = re.compile(
                  r"(?i)Scraped.*?"+prev_key_tag+".*?[\d\.]{8,} [\d:]{6,}\.")                                   
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
            (not ignoreblanks or len(new_list > 0)):
          
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
   
   
   # ==========================================================================
   def __parse_extra_details_from_filename(self):
      ''' 
      Series name, issue number, and volume year are all critical bits of data 
      for scraping purposes--yet fresh, unscraped files often do not have them.
      So when some or all of these values are missing, this method tries to fill
      them in by parsing them out of the comic's filename.
      '''
      
      bd  = self.__bookdata
      no_series = BookData.blank("series_s") == bd.series_s
      no_issuenum = BookData.blank("issue_num_s") == bd.issue_num_s
      no_volyear = BookData.blank("volume_year_n") == bd.volume_year_n
      if no_series or no_issuenum or no_volyear:
         if bd.filename_s:
            extracted = fnameparser.extract(bd.filename_s)
            if no_series:
               bd.series_s = extracted[0]
            if no_issuenum:
               bd.issue_num_s = extracted[1]
            if no_volyear:
               bd.volume_year_n = extracted[2]
               
               