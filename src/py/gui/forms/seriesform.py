''' 
This module is home to the SeriesForm and SeriesFormResult classes.

@author: Cory Banack
'''

import clr
from buttondgv import ButtonDataGridView
from cvform import CVForm
from utils import sstr
from matchscore import MatchScore
import i18n
from issuecoverpanel import IssueCoverPanel
 
clr.AddReference('System')
from System.ComponentModel import ListSortDirection

clr.AddReference('System.Drawing')
from System.Drawing import Point, Size

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import AutoScaleMode, Button, \
   DataGridViewAutoSizeColumnMode, DataGridViewContentAlignment, \
   DataGridViewSelectionMode, DataGridViewTriState, DialogResult, \
   Keys, Label

#==============================================================================
class SeriesForm(CVForm):
   '''
   This class is a popup, modal dialog that displays all of the Comic Book
   series that match a particular search string.  The series are shown in a 
   table, which the user can navigate through, browsing the cover art for 
   the first issue of each series.  Once the user has selected the series that
   matches the comic that she is scraping, she clicks the ok button to close
   this dialog and continue scraping her comic using the identified SeriesRef.
   '''

   #===========================================================================
   def __init__(self, scraper, book, series_refs, search_terms_s):
      ''' 
      Initializes this form.
      
      'scraper' -> the currently running ScrapeEngine
      'book' -> the ComicBook being scraped
      'series_refs' -> set or list containing the SeriesRefs to display
      'search_terms_s' -> the user's search string that found the series models
      '''
      
      # the the shared global configuration
      self.__config = scraper.config
      
      # a list of SeriesRef objects that back this form; one ref per table
      # row, where each SeriesRef represents a series the user can pick
      self.__series_refs = list(series_refs)
      
      # the MatchScore object that we use to compute series match scores
      self.__matchscore = MatchScore()
      
      # true when the user is pressing the control key, false otherwise
      self.__pressing_controlkey = False;
      
      # the 'ok' button for this dialog
      self.__ok_button = None
      
      # the 'skip' button for this dialog
      self.__skip_button = None
      
      # the 'show issues' button for this dialog
      self.__issues_button = None
      
      # the table that displays series (on per row) for the user to pick from
      self.__table = None
      
      # IssueCoverPanel that shows cover art for the current selected SeriesRef
      self.__coverpanel = None
      
      # the index (in self.__series_refs) of the currently selected SeriesRef
      self.__chosen_index = None
      
      
      
      if len(series_refs) <= 0:
         raise Exception("do not invoke the SeriesForm with no series!")
      CVForm.__init__(self, scraper.comicrack.MainWindow, "seriesformLocation")
      self.__build_gui(book, search_terms_s);
      scraper.cancel_listeners.append(self.Close)
      
      
   #===========================================================================   
   def __build_gui(self, book, search_terms_s):
      ''' Constructs and initializes the gui for this form. '''
      
      # 1. --- build each gui component
      self.__ok_button = self.__build_okbutton()
      self.__skip_button = self.__build_skipbutton()
      search_button = self.__build_searchbutton()
      self.__issues_button = self.__build_issuesbutton()
      label = self.__build_label(search_terms_s, len(self.__series_refs)) 
      self.__table = self.__build_table(
         self.__series_refs, book, self.__ok_button)
      self.__coverpanel = self.__build_coverpanel(book)

      # 2. --- configure this form, and add all the gui components to it
      self.AutoScaleMode = AutoScaleMode.Font
      self.ClientSize = Size(730, 395)
      self.Text = i18n.get("SeriesFormTitle")
      self.FormClosed += self.__form_closed_fired
      self.KeyPreview = True;
      self.KeyDown += self.__key_was_pressed
      self.KeyUp += self.__key_was_released
      self.Deactivate += self.__was_deactivated
      
      self.Controls.Add (label)
      self.Controls.Add(self.__table)
      self.Controls.Add (self.__ok_button)
      self.Controls.Add (self.__skip_button)
      self.Controls.Add (search_button)
      self.Controls.Add (self.__issues_button)
      self.Controls.Add(self.__coverpanel) # must be added LAST
      
      # 3. --- define the keyboard focus tab traversal ordering
      self.__ok_button.TabIndex = 1
      self.__skip_button.TabIndex = 2
      search_button.TabIndex = 3
      self.__issues_button.TabIndex = 4
      self.__coverpanel.TabIndex = 5
      self.__table.TabIndex = 6
      
      # 4. --- make sure the UI goes into a good initial state
      self.Shown += self.__change_table_selection_fired



   # ==========================================================================
   def __build_table(self, series_refs, book, enter_button):
      ''' 
      Builds and returns the table for this form.
      'series_refs' -> a list with one SeriesRef object for each found series
      'book' -> the ComicBook being scraped
      'enter_button' -> the button to "press" if the user hits enter
      '''
      
      # 1. --- configure the table itself
      table = ButtonDataGridView(enter_button) 
      table.AllowUserToOrderColumns = True
      table.SelectionMode = DataGridViewSelectionMode.FullRowSelect
      table.MultiSelect = False
      table.ReadOnly = True
      table.RowHeadersVisible = False
      table.AllowUserToAddRows = False
      table.AllowUserToResizeRows = False
      table.AllowUserToResizeColumns = False
      table.DefaultCellStyle.NullValue = "--"

      table.Location = Point(10, 60)
      table.Size = Size(500, 290) \
         if self.__config.show_covers_b else Size(710, 290)

      # 2. --- build columns
      table.ColumnCount = 7
      
      table.Columns[0].Name = i18n.get("SeriesFormSeriesCol")
      table.Columns[0].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleLeft
      table.Columns[0].Resizable = DataGridViewTriState.True
      table.Columns[0].FillWeight = 200
      table.Columns[0].AutoSizeMode = \
         DataGridViewAutoSizeColumnMode.Fill
      
      table.Columns[1].Name = i18n.get("SeriesFormYearCol")
      table.Columns[1].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[1].Resizable = DataGridViewTriState.True
      table.Columns[1].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells
      
      table.Columns[2].Name = i18n.get("SeriesFormIssuesCol")
      table.Columns[2].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[2].Resizable = DataGridViewTriState.True
      table.Columns[2].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells
         
      table.Columns[3].Name = i18n.get("SeriesFormPublisherCol")
      table.Columns[3].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleLeft
      table.Columns[3].Resizable = DataGridViewTriState.True
      table.Columns[3].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.Fill
         
      table.Columns[4].Name = "ID"
      table.Columns[4].Visible = False
      table.Columns[4].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[4].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells
         
      table.Columns[5].Name = "Match"
      table.Columns[5].Visible = False
      table.Columns[5].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[5].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells
         
      table.Columns[6].Name = "Model ID"
      table.Columns[6].Visible = False
      table.Columns[6].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[6].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells

      # 3. --- copy model data into the table, each series is a row
      for i in range(len(series_refs)):
         table.Rows.Add()
         ref = series_refs[i] 
         table.Rows[i].Cells[0].Value = ref.series_name_s
         if ref.volume_year_n >= 0:
            table.Rows[i].Cells[1].Value = ref.volume_year_n
         table.Rows[i].Cells[2].Value = ref.issue_count_n
         table.Rows[i].Cells[3].Value = ref.publisher_s
         table.Rows[i].Cells[4].Value = ref.series_key
         table.Rows[i].Cells[5].Value = self.__matchscore.compute_n(book, ref)
         table.Rows[i].Cells[6].Value = i

      # 4. --- sort on the "match" colum
      table.Sort( table.Columns[5], ListSortDirection.Descending )
      table.SelectionChanged += self.__change_table_selection_fired
      return table


   # ==========================================================================
   def __build_okbutton(self):
      ''' builds and returns the ok button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.OK
      button.Location = Point(15, 362)
      button.Size = Size(90, 24)
      button.Text = i18n.get("SeriesFormOK")
      return button
   
   
   # ==========================================================================
   def __build_skipbutton(self):
      ''' builds and return the skip button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Ignore
      button.Location = Point(110, 362)
      button.Size = Size(90, 24)
      button.Text = i18n.get("SeriesFormSkip")
      return button


   # ==========================================================================
   def __build_searchbutton(self):
      ''' builds and return the 'search again' button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Retry
      button.Location = Point(275, 362) \
         if self.__config.show_covers_b else Point(485, 362) 
      button.Size = Size(115, 24)
      button.Text = i18n.get("SeriesFormAgain")
      return button
   
   # ==========================================================================
   def __build_issuesbutton(self):
      ''' builds and return the 'show issues' button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Yes
      button.Location = Point(395, 362) \
         if self.__config.show_covers_b else Point(605, 362) 
      button.Size = Size(115, 24)
      button.Text = i18n.get("SeriesFormIssues")
      return button
   
   
   # ==========================================================================
   def __build_label(self, search_terms_s, num_matches_n):
      ''' 
      Builds and return the text label for this form.
      'search_terms_s' -> user's search string that was used to find series
      'num_matches_n' -> number of series (table rows) the user's search matched
      '''
      
      label = Label()
      label.UseMnemonic = False
      label.Location = Point(10, 20)
      label.Size = Size(480, 40)
      if num_matches_n > 1:
         label.Text = i18n.get("SeriesFormChooseText")\
            .format(search_terms_s, num_matches_n )
      else:
         label.Text = i18n.get("SeriesFormConfirmText").format(search_terms_s)
      return label
   

   # ==========================================================================
   def __build_coverpanel(self, book):
      ''' 
      Builds and returns the cover image PictureBox for this form.
      'book' -> the ComicBook being scraped
      '''
      panel = IssueCoverPanel(self.__config, -9991 \
         if self.__config.force_series_art_b else book.issue_num_s) 
      panel.Location = Point(523, 30)
      # panel size is determined by the panel itself
      
      if self.__config.show_covers_b:
         panel.Show()
      else:
         panel.Hide()
      return panel
   
   # ==========================================================================
   def show_form(self):
      '''
      Displays this form, blocking until the user closes it.  When it is closed,
      it will return a SeriesFormResult describing how it was closed, and any
      SeriesRef that may have been chosen when it was closed. 
      '''
      
      dialogAnswer = self.ShowDialog(self.Owner) # blocks
      
      if dialogAnswer == DialogResult.OK:
         series = self.__series_refs[self.__chosen_index] 
         result = SeriesFormResult( "OK", series )
         alt_choice = self.__coverpanel.get_alt_issue_cover_choice()
         if alt_choice:
            issue_ref, image_ref = alt_choice
            # the user chose a non-default cover image for this issue.
            # we'll store that choice in the global "session data map",
            # in case any other part of the program wants to use it.
            alt_cover_key = sstr(issue_ref.issue_key) + "-altcover"
            self.__config.session_data_map[alt_cover_key] = image_ref
      elif dialogAnswer == DialogResult.Yes:
         series = self.__series_refs[self.__chosen_index] 
         result = SeriesFormResult( "SHOW", series )
      elif dialogAnswer == DialogResult.Cancel: 
         result = SeriesFormResult( "CANCEL")
      elif dialogAnswer == DialogResult.Ignore:
         if self.ModifierKeys == Keys.Control:
            result = SeriesFormResult( "PERMSKIP" )
         else:
            result = SeriesFormResult( "SKIP" )
      elif dialogAnswer == DialogResult.Retry:
         result = SeriesFormResult( "SEARCH" )
      else:
         raise Exception()
      
      return result


   #===========================================================================
   def __form_closed_fired(self, sender, args):
      ''' this method is called whenever this SeriesForm is closed. '''
      
      self.__table.Dispose()
      self.__coverpanel.free()      
      self.Closed -= self.__form_closed_fired


   #===========================================================================         
   def __change_table_selection_fired(self, sender, args):
      ''' this method is called whenever the table's selected row changes. '''
      
      # update __chosen_index (eventually used as this dialog's return value)
      # and then also use it to update the displayed cover image.
      selected_rows = self.__table.SelectedRows
      if selected_rows.Count == 1:
         self.__chosen_index = selected_rows[0].Cells[6].Value
         self.__coverpanel.set_ref(
            self.__series_refs[self.__chosen_index])
      else:
         self.__chosen_index = None
         self.__coverpanel.set_ref(None) 
     
      # don't let the user click 'ok' or 'show issue' if no row is selected!    
      self.__ok_button.Enabled = selected_rows.Count == 1
      self.__issues_button.Enabled = selected_rows.Count == 1
      
               
   #===========================================================================         
   def __key_was_pressed(self, sender, args):
      ''' Called whenever the user presses any key on this form. '''
      
      # highlight the skip button whenever the user presses control key
      if args.KeyCode == Keys.ControlKey and not self.__pressing_controlkey:
         self.__pressing_controlkey = True;
         self.__skip_button.Text = "- " + i18n.get("SeriesFormSkip") + " -"
         
   #===========================================================================         
   def __key_was_released(self, sender, args):
      ''' Called whenever the user releases any key on this form. '''
      
      # unhighlight the skip button bold whenever the user releases control key
      if args.KeyCode == Keys.ControlKey:
         self.__pressing_controlkey = False;
         self.__skip_button.Text = i18n.get("SeriesFormSkip")

   #===========================================================================         
   def __was_deactivated(self, sender, args):
      ''' Called whenever this form gets deactivated, for any reason '''
      
      # unhighlight the skip button bold whenever we deactivate
      if self.__pressing_controlkey:
         self.__pressing_controlkey = False;
         self.__skip_button.Text = i18n.get("SeriesFormSkip")
      
      
#==============================================================================      
class SeriesFormResult(object):
   '''
   Results that can be returned from the SeriesForm.show_form() method.  The
   'id' of this object describes the manner in which the user closed the 
   dialog:
   
   1) "CANCEL"  means the user cancelled this scrape operation.
   2) "SKIP" means the user elected to skip the current book.
   3) "PERMSKIP" means the user elected to skip the current book
      during this scrape, AND all future scrapes (i.e. add a 'skip tag' to book)
   4) "SEARCH" means the user chose to 'search again'
   5) "OK" means the user chose a SeriesRef, and the script
      should try to automatically choose the correct issue for that SeriesRef.
   6) "SHOW" means the user chose a SeriesRef, and the script
      should NOT automatically choose issue for that SeriesRef--it should 
      show the IssueForm and let the user choose manually.
      
   Note that if the SeriesFormResult has an id of 'OK' or 'SHOW', it must
   also have a non-None 'ref', which is of course the actual SeriesRef that 
   the user chose.    
   '''
   
   #===========================================================================         
   def __init__(self, id, ref=None): 
      ''' 
      Creates a new SeriesFormResult.
      id -> the id of the result, i.e. "OK", "SHOW", "CANCEL", "SKIP", etc.
      ref -> the reference that the user chose, if they chose one at all.
             (required for "SHOW" and "OK".)
      '''  
            
      if id != "OK" and id != "SHOW" and id != "CANCEL" and \
         id != "SKIP" and id != "SEARCH" and id != "PERMSKIP":
         raise Exception()
      if (id == "OK" or id == "SHOW") and ref == None:
         raise Exception()
      
      self.__ref = ref if id == "OK" or id == "SHOW" else None;
      self.__id = id;

      
   #===========================================================================         
   def equals(self, id): 
      ''' 
      Returns True iff this SeriesFormResult has the given ID (i.e. one of 
      "SHOW", "OK, "CANCEL", "SKIP", etc.)
      '''
      return self.__id == id

   
   #===========================================================================         
   def get_ref(self):
      ''' 
      Gets the SeriesRef portion of this result, i.e. the one the user picked.
      This is only defined when the id of this result is "OK" or "SHOW".
      '''
      return self.__ref;

   
   #===========================================================================         
   def get_debug_string(self):
      ''' Gets a simple little debug string summarizing this result.'''
      
      if self.equals("SKIP"):
         return "SKIP scraping this book"
      elif self.equals("PERMSKIP"):
         return "ALWAYS SKIP scraping this book"
      elif self.equals("CANCEL"):
         return "CANCEL this scrape operation"
      elif self.equals("SEARCH"):
         return "SEARCH AGAIN for more series"
      elif self.equals("SHOW"):
         return "SHOW ISSUES for: '" + sstr(self.get_ref()) + "'"
      elif self.equals("OK"):
         return "SCRAPE using: '" + sstr(self.get_ref()) + "'"
      else:
         raise Exception()
