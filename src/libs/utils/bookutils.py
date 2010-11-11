''' 
This module contains utility methods for working with ComicRack
ComicBook objects (i.e. 'book' objects).
'''

import re
import log
from time import strftime
from utils import sstr
from dbmodels import IssueRef
import db

# =============================================================================
def extract_issue_ref(book):
   '''
   This method looks in the tags and notes fields of the given book for 
   evidence that this book has been scraped before.   If possible, it will 
   construct an IssueRef based on that evidence, and return it.  If not, it 
   will return None.   
   
   If the user has manually added a "skip" flag to one of those fields, this
   method will return the string "skip", which should be interpreted as 
   "never scrape this book".
   '''
   
   # ===== corylow: SEPARATION OF CONCERNS: this assumes CV! ==================
   tag_found = re.search(r'(?i)CVDB(\d{1,}|SKIP)', book.Tags)
   if not tag_found:
      tag_found = re.search(r'(?i)CVDB(\d{1,}|SKIP)', book.Notes)
      if not tag_found:
         tag_found = re.search(r'(?i)ComicVine.?\[(\d{1,})', book.Notes)

   retval = None
   if tag_found:
      retval = tag_found.group(1).lower()
      try:
         if retval != 'skip':
            retval = IssueRef(sstr(book.Number), int(retval))
      except:
         retval = None

   return retval


#==============================================================================
def save_issue_to_book(issue, book, scraper):
   '''
   Copies all data in the given issue into the given ComicRack comic book 
   object, respecting all of the overwrite/ignore rules defined in the given 
   Configuration object.
   
   As a side-effect, some detailed debug log information about the new values
   is also produced.
   '''
   
   config = scraper.config
   log.debug("setting values for this comic book ('*' = changed):")
   
   # series ---------------------
   value = __massage_new_string("Series", issue.series_name_s, \
      book.Series, config.update_series_b, config.ow_existing_b, \
      True ) # note: we ALWAYS ignore blanks for 'series'!
   if ( value is not None ) :  book.Series = value
   
   # issue number ---------------
   value = __massage_new_string("Issue Number", issue.issue_num_s, \
      book.Number, config.update_number_b, config.ow_existing_b, \
      True ) # note: we ALWAYS ignore blanks for 'issue number'!
   if ( value is not None ) :  book.Number = value
   
   # title ----------------------
   value = __massage_new_string("Title", issue.title_s, book.Title, \
      config.update_title_b, config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Title = value
      
   # alternate series -----------
   value = __massage_new_string("Alt/Arc", issue.alt_series_name_s, \
      book.AlternateSeries, config.update_alt_series_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.AlternateSeries = value
   
   # summary --------------------
   value = __massage_new_string("Summary", issue.summary_s, \
      book.Summary, config.update_summary_b, config.ow_existing_b, \
      config.ignore_blanks_b )
   if ( value is not None ) :  book.Summary = value
   
   # year -----------------------
   value = __massage_new_number("Year", issue.year_s, \
      book.Year, config.update_year_b, config.ow_existing_b, \
      True, -1, lambda x : x > 0 ) # note: we ALWAYS ignore blanks for 'year'
   if ( value is not None ) :  book.Year = value
   
   # month ----------------------
   def remap(month):
      # months 1 to 12 are straightforward, but the remaining possible
      # values (listed below) must be converted into the range 1-12:
      # 13 - Spring   18 - None      23 - Sep/Oct   28 - Apr/May
      # 14 - Summer   19 - Jan/Feb   24 - Nov/Dec   29 - Jun/Jul
      # 15 - Fall     20 - Mar/Apr   25 - Holiday   30 - Aug/Sep
      # 16 - Winter   21 - May/Jun   26 - Dec/Jan   31 - Oct/Nov
      # 17 - Annual   22 - Jul/Aug   27 - Feb/Mar  
      remap={ 1:1, 26:1, 2:2, 19:2, 3:3, 13:3, 27:3, 4:4, 20:4, 5:5, 28:5, \
              6:6, 14:6, 21:6, 7:7, 29:7, 8:8, 22:8, 9:9, 15:9, 30:9, 10:10,\
              23:10, 11:11, 31:11, 12:12, 16:12, 24:12, 25:12 }
      retval = -1;
      if month in remap:
         retval = remap[month]
      return retval
      
   value = __massage_new_number("Month", issue.month_s, book.Month, \
      config.update_month_b, config.ow_existing_b, True, -1, \
      lambda x : x>=1 and x <=12, remap ) # ALWAYS ignore blanks for 'month'
   if ( value is not None ) :  book.Month = value
   
   # volume --------------------
   value = __massage_new_number("Volume", issue.start_year_s, \
   book.Volume, config.update_volume_b, config.ow_existing_b, \
   config.ignore_blanks_b, -1, lambda x : x > 0 )
   if ( value is not None ) :  book.Volume = value
    
   # if we found an imprint for this issue, the user may prefer that the 
   # imprint be listed as the publisher (instead). if so, make that change
   # before writing the 'imprint' and 'publisher' fields out to the book:
   if not config.convert_imprints_b and issue.imprint_s:
      issue.publisher_s = issue.imprint_s
      issue.imprint_s = ''                                   
         
   # imprint -------------------
   value = __massage_new_string("Imprint", issue.imprint_s, \
      book.Imprint, config.update_imprint_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Imprint = value
         
   # publisher -----------------
   value = __massage_new_string("Publisher", issue.publisher_s, \
      book.Publisher, config.update_publisher_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Publisher = value
   
   # characters ----------------
   value = __massage_new_string("Characters", issue.characters_s, \
      book.Characters, config.update_characters_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Characters = value
   
   # teams ----------------
   value = __massage_new_string("Teams", issue.teams_s, \
      book.Teams, config.update_teams_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Teams = value
   
   # locations ----------------
   value = __massage_new_string("Locations", issue.locations_s, \
      book.Locations, config.update_locations_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Locations = value
   
   # webpage ----------------
   value = __massage_new_string("Webpage", issue.webpage_s, \
      book.Web, config.update_webpage_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Web = value
   
   # rating -----------------------
   value = __massage_new_number("Rating", issue.rating_n, \
      float(book.CommunityRating), config.update_rating_b, 
      config.ow_existing_b, config.ignore_blanks_b, 0.0,
      lambda x: x >= 0 and x <= 5, lambda x : max(0.0,min(5.0,x)) )
   if ( value is not None ) :  book.CommunityRating = value
   
   # writer --------------------
   value = __massage_new_string("Writers", issue.writer_s, \
      book.Writer, config.update_writer_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Writer = value
      
   # penciller -----------------
   value = __massage_new_string("Pencillers", issue.penciller_s, \
      book.Penciller, config.update_penciller_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Penciller = value
   
   # inker ---------------------
   value = __massage_new_string("Inkers", issue.inker_s, \
      book.Inker, config.update_inker_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Inker = value
      
   # colorist -----------------
   value = __massage_new_string("Colorists", issue.colorist_s, \
      book.Colorist, config.update_colorist_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Colorist = value
      
   # letterer -----------------
   value = __massage_new_string("Letterers", issue.letterer_s, \
      book.Letterer, config.update_letterer_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Letterer = value
      
   # coverartist --------------
   value = __massage_new_string("CoverArtists", issue.cover_artist_s, \
      book.CoverArtist, config.update_cover_artist_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.CoverArtist = value
      
   # editor -------------------   
   value = __massage_new_string("Editors", issue.editor_s, \
      book.Editor, config.update_editor_b, \
      config.ow_existing_b, config.ignore_blanks_b )
   if ( value is not None ) :  book.Editor = value

   # tag ----------------------
   # ===== corylow: SEPARATION OF CONCERNS: this assumes CV! ==================
   # add in our own special tag that can be parsed back in when the user
   # rescrapes this book.  we assume any other existing tags were either 1)
   # added by the user (so instead of replacing them, we append to them) or
   # 2) added by this script (so we replace the part we added with our new 
   # tag, instead of appending.)
   new_tag = 'CVDB' + sstr(issue.issue_key)
   if book.Tags:
      book.Tags = book.Tags.strip()
      regexp = re.compile(r"(?i)CVDB(\d+|SKIP)")
      matches = regexp.search(book.Tags)
      if matches:
         new_tag = re.sub(regexp, new_tag, book.Tags)
      else:
         if book.Tags[-1] == ",":
            book.Tags = book.Tags[:-1]
         new_tag = book.Tags +", " + new_tag
         
   value = __massage_new_string("Tags", new_tag, \
      book.Tags, config.rescrape_tags_b, config.ow_existing_b, \
      config.ignore_blanks_b )
   if ( value is not None ) :  book.Tags = value
   
   # notes --------------------
   # ===== corylow: SEPARATION OF CONCERNS: this assumes CV! ==================
   # add in our own special sentence that can be parsed back in when the user
   # rescrapes this book.  we assume any other existing characters were 
   # either 1) added by the user (so instead of replacing them, we append 
   # to them) or 2) added by this script (so we replace the part we added 
   # with our new sentence, instead of appending.)
   new_notes = 'Scraped metadata from ComicVine [%s] on %s.' % \
      ('CVDB' + sstr(issue.issue_key), strftime(r'%Y.%m.%d %X'))
   if book.Notes:
      book.Notes = book.Notes.strip()
      regexp = re.compile(
         r"(?i)Scraped.*?CVDB(\d+|SKIP).*?[\d\.]{8,} [\d:]{6,}\.")
      matches = regexp.search(book.Notes)
      if matches:
         # found the 'standard' embedded CVDB tag; update it
         new_notes = re.sub(regexp, new_notes, book.Notes)
      else:
         regexp = re.compile(r"(?i)CVDB(\d+|SKIP)")
         matches = regexp.search(book.Notes)
         if matches:
            # found a custom embedded CVDB tag; update it
            new_notes = 'CVDB' + sstr(issue.issue_key)
            new_notes = re.sub(regexp, new_notes, book.Notes)
         else:
            # found no embedded CVDB tag; add it
            new_notes = book.Notes + "\n\n" + new_notes
         
   value = __massage_new_string("Notes", new_notes, \
      book.Notes, config.rescrape_notes_b, config.ow_existing_b, \
      config.ignore_blanks_b )
   if ( value is not None ) :  book.Notes = value
   del value
   book.WriteProposedValues(False)

   __maybe_download_thumbnail(book, issue, scraper)


#===========================================================================
def __maybe_download_thumbnail(book, issue, scraper):
   '''
   Iff the given book is a 'fileless' comic, this method will download and 
   write the cover image for that comic into the book object (assuming the 
   given scraper's config settings permit it.)
   
   'book' -> the book whose thumbnail we might update
   'issue' -> the Issue for the book that we are updating
   'scraper' -> the ScraperEnginer that's current running
   '''
   
   config = scraper.config
   label = "Thumbnail"
   already_has_thumb = book and book.CustomThumbnailKey
   book_is_fileless = book and not book.FilePath
   
   # don't download the thumbnail if the book has a backing file (cause that's
   # where the thumbnail will come from!) or if the user has specified in 
   # config that we shouldn't.
   if not book_is_fileless or not config.download_thumbs_b or \
            (already_has_thumb and config.preserve_thumbs_b):
         log.debug("-->  ", label.ljust(15), ": --- skipped ---")
   else:
      # get the url for this issue's cover art.  check to see if the user
      # picked an alternate cover back when they closed the IssueForm, and if
      # not, just grab the url for the default cover art.
      url = None
      alt_cover_key = sstr(issue.issue_key)+"-altcover"
      if alt_cover_key in config.session_data_map:
         url = config.session_data_map[alt_cover_key]
      if not url and len(issue.image_urls):  
         url = issue.image_urls[0]
         
      if not url:
         # there is no image url available for this issue 
         log.debug("-->  ", label.ljust(15),": --- not available! ---")
      else:
         image = db.query_image(url)
         if not image:
            log.debug("ERROR: couldn't download thumbnail: ", url)
         else:
            success = scraper.comicrack.App.SetCustomBookThumbnail(book, image)
            if success:
               # it worked!
               log.debug("--> *", label.ljust(15),": ", url)
            else:
               log.debug("ERROR: comicrack can't set thumbnail!")



#===========================================================================
def __massage_new_string(
      label, new_value, old_value, update, overwrite, ignoreblanks):
   ''' 
   Returns a string value that should be copied into a ComicRack comic book
   object, IFF that string value is not None.   Uses a number of rules to
   decide what value to return.
   
   label - a human readable description of the given string being changed.
   new_value - the proposed new string value to copy over.
   old_value - the original value that the new value would copy over.
   update - if false, this method always returns None
   overwrite - whether it's acceptable to overwrite the old value with the
               new value when the old value is non-blank.
   ignoreblanks - if true, we'll never overwrite with an old non-blank value
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
def __massage_new_number(label, new_value, old_value, update, overwrite, \
   ignoreblanks, blank_value, is_valid=None, remap_invalid=None):
   ''' 
   Returns an number (int or float) value that should be copied into a ComicRack
   comic book object, IFF that value is not None.   Uses a number of rules to
   decide what value to return.
   
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
      
   # last minute type checking, just to be sure the returned value type is good
   if retval != None:
      retval = float(retval) if type(old_value) == float else int(retval)
   return retval