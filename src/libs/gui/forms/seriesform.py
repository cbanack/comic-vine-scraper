''' 
This module is home to the SeriesForm and SeriesFormResult classes.

@author: Cory Banack
'''

import re
import clr
from buttondgv import ButtonDataGridView
from cvform import CVForm
from dbpicturebox import DBPictureBox
from utils import sstr

clr.AddReference('System')
from System.ComponentModel import ListSortDirection

clr.AddReference('System.Drawing')
from System.Drawing import Point, Size

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import AutoScaleMode, Button, CheckBox, \
   DataGridViewAutoSizeColumnMode, DataGridViewContentAlignment, \
   DataGridViewSelectionMode, DialogResult, FlatStyle, Label

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
      'book' -> the comic book being scraped
      'series_refs' -> set or list containing the SeriesRefs to display
      'search_terms_s' -> the user's search string that found the series models
      '''
      
      # the the shared global configuration
      self.__config = scraper.config
      
      # a list of SeriesRef objects that back this form; one ref per table
      # row, where each SeriesRef represents a series the user can pick
      self.__series_refs = list(series_refs)
      
      # the 'ok' button for this dialog
      self.__ok_button = None
      
      # the 'show issues' button for this dialog
      self.__issues_button = None
      
      # the table that displays series (on per row) for the user to pick from
      self.__table = None
      
      # a PictureBox that displays the cover art for the current selected series
      self.__cover_image = None
      
      # a checkbox for toggling the display of the cover image on/off
      self.__checkbox = None
      
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
      skip_button = self.__build_skipbutton()
      search_button = self.__build_searchbutton()
      self.__issues_button = self.__build_issuesbutton()
      label = self.__build_label(search_terms_s, len(self.__series_refs)) 
      self.__table = self.__build_table(
         self.__series_refs, book, self.__ok_button)
      self.__cover_image = self.__build_coverimage(self.__series_refs)
      self.__checkbox = self.__build_checkbox(self.__config)

      # 2. --- configure this form, and add all the gui components to it
      self.AutoScaleMode = AutoScaleMode.Font
      self.ClientSize = Size(730, 395)
      self.Text = 'Choose a Comic Book Series'
      self.FormClosed += self.__form_closed_fired
      
      self.Controls.Add (label)
      self.Controls.Add(self.__table)
      self.Controls.Add (self.__ok_button)
      self.Controls.Add (skip_button)
      self.Controls.Add (search_button)
      self.Controls.Add (self.__issues_button)
      self.Controls.Add(self.__cover_image)
      self.Controls.Add(self.__checkbox)
      
      # 3. --- define the keyboard focus tab traversal ordering
      self.__ok_button.TabIndex = 1
      skip_button.TabIndex = 2
      search_button.TabIndex = 3
      self.__issues_button.TabIndex = 4
      self.__checkbox.TabIndex = 5
      self.__table.TabIndex = 6
      
      # 4. --- make sure the UI goes into a good initial state
      self.__change_table_selection_fired(None, None)
      self.__toggle_checkbox_fired(None, None)



   # ==========================================================================
   def __build_table(self, series_refs, book, enter_button):
      ''' 
      Builds and returns the table for this form.
      'series_refs' -> a list with one SeriesRef object for each found series
      'book' -> the comic book being scraped
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
      table.AutoResizeColumns

      table.Location = Point(10, 60)
      table.Size = Size(1,1) # gets updated by "__change_table_selection_fired"

      # 2. --- build columns
      table.ColumnCount = 7
      
      table.Columns[0].Name = "Series"
      table.Columns[0].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleLeft
      table.Columns[0].AutoSizeMode = \
         DataGridViewAutoSizeColumnMode.Fill
      
      table.Columns[1].Name = "Year"
      table.Columns[1].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[1].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells
      
      table.Columns[2].Name = "Issues"
      table.Columns[2].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[2].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells
         
      table.Columns[3].Name = "Publisher"
      table.Columns[3].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleLeft
      table.Columns[3].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells
         
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
         if ref.start_year_s:
            table.Rows[i].Cells[1].Value = int(ref.start_year_s)
         table.Rows[i].Cells[2].Value = ref.issue_count_n
         table.Rows[i].Cells[3].Value = ref.publisher_s
         table.Rows[i].Cells[4].Value = ref.series_key
         table.Rows[i].Cells[5].Value = self.__compute_match_score_n(book, ref)
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
      button.Size = Size(80, 24)
      button.Text = '&Ok'
      return button
   
   
   # ==========================================================================
   def __build_skipbutton(self):
      ''' builds and return the skip button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Ignore
      button.Location = Point(100, 362)
      button.Size = Size(80, 24)
      button.Text = '&Skip'
      return button


   # ==========================================================================
   def __build_searchbutton(self):
      ''' builds and return the 'search again' button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Retry
      button.Location = Point(325, 362)
      button.Size = Size(90, 24)
      button.Text = 'Search &Again'
      return button
   
   # ==========================================================================
   def __build_issuesbutton(self):
      ''' builds and return the 'show issues' button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Yes
      button.Location = Point(420, 362)
      button.Size = Size(90, 24)
      button.Text = 'Show &Issues...'
      return button
   
   
   # ==========================================================================
   def __build_label(self, search_terms_s, num_matches_n):
      ''' 
      Builds and return the text label for this form.
      'search_terms_s' -> user's search string that was used to find series
      'num_matches_n' -> number of series (table rows) the user's search matched
      '''
      
      label = Label()
      label.AutoSize = True
      label.Location = Point(10, 20)
      if num_matches_n > 1:
         label.Text = "Searched for '{0}' and found {1} matching series.\n"\
            'Please choose one from the list below, '\
            "or click 'Skip' to scrape this comic later.".format( 
            search_terms_s, num_matches_n )
      else:
         label.Text = "Searched for '{0}' and found one matching series.\n"\
            "Click 'OK' to confirm that this is correct, "\
            "or click 'Skip' to scrape this comic later.".format(search_terms_s)
      return label
   

   # ==========================================================================
   def __build_coverimage(self, series_refs):
      ''' 
      Builds and returns the cover image PictureBox for this form.
      'series_refs' -> a list with one SeriesRef object for each found series
      '''
      
      cover = DBPictureBox()
      cover.Location = Point(523, 31)
      cover.Size = Size(195, 320)
      return cover

   # ==========================================================================
   def __build_checkbox(self, config):
      ''' 
      Builds and return the checkbox for toggling cover image display.
      ''config' -> the shared global Configuration object 
      '''
      
      checkbox = CheckBox()
      checkbox.Name = 'seriesThumbs'
      checkbox.AutoSize = True
      checkbox.Checked = config.show_covers_b
      checkbox.FlatStyle = FlatStyle.System
      checkbox.Location = Point(580, 365)
      checkbox.Size = Size(100, 17)
      checkbox.Text = 'Show Series Art'
      checkbox.UseVisualStyleBackColor = True
      checkbox.CheckedChanged += self.__toggle_checkbox_fired
      return checkbox
   
   #===========================================================================
   def __compute_match_score_n(self, book, series_ref):
      '''
      Computes a score for the given SeriesRef, which describes how closely
      that ref matches the given book.   The higher the score, the closer
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
      #    our book name match words in the series' name
      bookname_s = '' if not book.ShadowSeries else book.ShadowSeries
      if bookname_s and book.ShadowFormat:
         bookname_s += ' ' + sstr(book.ShadowFormat)
      bookwords = split(bookname_s)   
      serieswords = split(series_ref.series_name_s)
      
      namescore_n = 0
      for word in bookwords:
         if word in serieswords:
            namescore_n += 5
            serieswords.remove(word)
      namescore_n -= len(serieswords)
      
      
      # 2. now get the 'bookscore', which compares our books issue number
      #    with the number of issues in the series
      booknumber_n = book.ShadowNumber if book.ShadowNumber else '-1000'
      booknumber_n = re.sub('[^\d.-]+', '', booknumber_n)
      try:
         booknumber_n = float(booknumber_n)
      except:
         booknumber_n = -999
         
      bookscore_n = 0
      try: 
         bookscore_n += 100 if booknumber_n<=series_ref.issue_count_n else - 100
      except:
         bookscore_n = 0

      # 3. now get the 'yearscore', which compares the year of the book 
      #    (if available) to the year of the series.
      def valid_year_b(year_n):
         return year_n > 1900 and year_n < 2100
      try:
         series_year_n = int(series_ref.start_year_s)
         if not valid_year_b(series_year_n):
            series_year_n = 0
      except:
         series_year_n = 0
         
      yearscore_n = 0
      if valid_year_b(book.ShadowYear):
         if valid_year_b(series_year_n):
            yearscore_n -= abs(series_year_n - book.ShadowYear)
            yearscore_n -= 50 if yearscore_n < -2 else 0
         else:
            yearscore_n = -100
         
      #4. add up and return all the scores
      return bookscore_n + namescore_n + yearscore_n
   
   
   # ==========================================================================
   def show_form(self):
      '''
      Displays this form, blocking until the user closes it.  When it is closed,
      it will return a SeriesFormResult describing how it was closed, and any
      SeriesRef that may have been chosen when it was closed. 
      '''
      
      dialogAnswer = self.ShowDialog(self.Owner) # blocks
      
      if dialogAnswer == DialogResult.OK:
         result = SeriesFormResult( SeriesFormResult.OK,
               self.__series_refs[self.__chosen_index] )
      elif dialogAnswer == DialogResult.Yes:
         result = SeriesFormResult( SeriesFormResult.SHOW,
               self.__series_refs[self.__chosen_index] )
      elif dialogAnswer == DialogResult.Cancel: 
         result = SeriesFormResult( SeriesFormResult.CANCEL)
      elif dialogAnswer == DialogResult.Ignore:
         result = SeriesFormResult( SeriesFormResult.SKIP)
      elif dialogAnswer == DialogResult.Retry:
         result = SeriesFormResult( SeriesFormResult.SEARCH)
      else:
         raise Exception()
      
      return result


   #===========================================================================
   def __form_closed_fired(self, sender, args):
      ''' this method is called whenever this SeriesForm is closed. '''
      
      self.__table.Dispose()
      self.__cover_image.free()      
      self.Closed -= self.__form_closed_fired


   #===========================================================================
   def __toggle_checkbox_fired(self, sender, args):
      ''' this method is called when the form's checkbox is toggled '''
      
      self.__config.show_covers_b = self.__checkbox.Checked
      if self.__config.show_covers_b:
         self.__cover_image.Show()
         self.__table.Size = Size(500, 290)
      else:
         self.__cover_image.Hide()
         self.__table.Size = Size(710, 290)
      
      
   #===========================================================================         
   def __change_table_selection_fired(self, sender, args):
      ''' this method is called whenever the table's selected row changes. '''
      
      # update __chosen_index (eventually used as this dialog's return value)
      # and then also use it to update the displayed cover image.
      selected_rows = self.__table.SelectedRows
      if selected_rows.Count == 1:
         self.__chosen_index = selected_rows[0].Cells[6].Value
         self.__cover_image.set_image_ref(
            self.__series_refs[self.__chosen_index])
      else:
         self.__chosen_index = None
         self.__cover_image.set_image_ref(None)
     
      # don't let the user click 'ok' or 'show issue' if no row is selected!    
      self.__ok_button.Enabled = selected_rows.Count == 1
      self.__issues_button.Enabled = selected_rows.Count == 1

      
#==============================================================================      
class SeriesFormResult(object):
   '''
   Results that can be returned from the SeriesForm.show_form() method.  The
   'name' of this object describes the manner in which the user closed the 
   dialog:
   
   1) SeriesFormResult.CANCEL  means the user cancelled this scrape operation.
   2) SeriesormResult.SKIP means the user elected to skip the current book.
   3) SeriesFormResult.SEARCH means the user chose to 'search again'
   4) SeriesFormResult.OK means the user chose a SeriesRef, and the script
      should try to automatically choose the correct issue for that SeriesRef.
   5) SeriesFormResult.SHOW means the user chose a SeriesRef, and the script
      should NOT automatically choose issue for that SeriesRef--it should 
      show the IssueForm and let the user choose manually.
      
   Note that if the SeriesFormResult has a name of 'OK' or 'SHOW', it should
   also have a non-None 'ref', which is of course the actual SeriesRef that 
   the user chose.    
   '''
   
   OK = "ok"
   SHOW = "show"
   CANCEL = "cancel"
   SKIP = "skip"
   SEARCH = "search"
   
   #===========================================================================         
   def __init__(self, name, ref=None):
      ''' 
      Creates a new SeriesFormResult.
      name -> the name of the result, i.e. based on what button the user pressed
      ref -> the reference that the user chose, if they chose one at all.
      '''  
            
      if name != self.OK and name != self.SHOW and name != self.CANCEL and \
         name != self.SKIP and name != self.SEARCH:
         raise Exception();
      
      self.__ref = ref if name == self.OK or name == self.SHOW else None;
      self.__name = name;

      
   #===========================================================================         
   def get_name(self):
      ''' Gets the 'name' portion of this result (see possibilities above) '''
      return self.__name;

   
   #===========================================================================         
   def get_ref(self):
      ''' 
      Gets the SeriesRef portion of this result, i.e. the one the user picked.
      This is only defined when the'name' of this result is "OK" or "SHOW".
      '''
      return self.__ref;

   
   #===========================================================================         
   def get_debug_string(self):
      ''' Gets a simple little debug string summarizing this result.'''
      
      if self.get_name() == self.SKIP:
         return "SKIP scraping this book"
      elif self.get_name() == self.CANCEL:
         return "CANCEL this scrape operation"
      elif self.get_name() == self.SEARCH:
         return "SEARCH AGAIN for more series"
      elif self.get_name() == self.SHOW:
         return "SHOW ISSUES for: '" + sstr(self.get_ref()) + "'"
      elif self.get_name() == self.OK:
         return "SCRAPE using: '" + sstr(self.get_ref()) + "'"
      else:
         raise Exception()
