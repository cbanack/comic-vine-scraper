'''
This module is home to the IssuesForm and IssuesFormResult classes. 

@author: Cory Banack
'''

from utils import sstr, is_number
import clr
import i18n
from buttondgv import ButtonDataGridView
from issuecoverpanel import IssueCoverPanel
from cvform import CVForm

clr.AddReference('Microsoft.VisualBasic')
from System.ComponentModel import ListSortDirection

clr.AddReference('System.Drawing')
from System.Drawing import Point, Size

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import AutoScaleMode, Button, \
   DataGridViewAutoSizeColumnMode, DataGridViewContentAlignment, \
   DataGridViewSelectionMode, DialogResult, Keys, Label
from System import String



#==============================================================================
class IssueForm(CVForm):
   '''
   This class is a popup, modal dialog that displays all of the Comic Book
   issues in a series.  The issues are shown in a table, which the user can 
   navigate through, browsing the cover art for each issue. Once the user has 
   selected the issue that matches the comic that she is scraping, she clicks 
   the ok button to close this dialog and continue scraping her comic using the 
   identified IssueRef.
   '''
   
   #===========================================================================
   def __init__(self, scraper, issue_ref_hint, issue_refs, series_name_s):
      ''' 
      Initializes this form.  If a good issue key hint is given, that issue will
      be preselected in the table if possible.
      
      'scraper' -> the currently running ScrapeEngine
      'issue_ref_hint' -> may be the issue id for the given book (or may not!)
      'issue_refs' -> a set or list containing the IssueRefs to display
      'series_name_s' -> the name of the series that the given issues belong to
      '''
      
      # the the shared global configuration
      self.__config = scraper.config
      
      # a list of IssueRef objects that back this form; one ref per table row,
      # where each IssueRef represents an issue that the user can pick
      self.__issue_refs = list(issue_refs)
      
      # true when the user is pressing the control key, false otherwise
      self.__pressing_controlkey = False;
      
      # the ok button for this dialog
      self.__ok_button = None
      
      # the skip button for this dialog
      self.__skip_button = None
      
      # the label for this dialog
      self.__label = None
      
      # the table that displays issues (one per row) for the user to pick from
      self.__table = None
      
      # whether or no we were able to pre-select the "hinted" issue in the table
      self.__found_issue_in_table = False
      
      # IssueCoverPAnel that shows the cover for the currently selected IssueRef
      self.__coverpanel = None
      
      ## the index (into self.__issue_refs) of the currently selected IssueRef
      self.__chosen_index = None
      
      if len(issue_refs) <= 0:
         raise Exception("do not invoke the IssueForm with no IssueRefs!")
      CVForm.__init__(self, scraper.comicrack.MainWindow, "issueformLocation")
      self.__build_gui(issue_ref_hint, series_name_s)
      scraper.cancel_listeners.append(self.Close)
      
   # ==========================================================================
   def __build_gui(self, issue_ref_hint, series_name_s):
      ''' Constructs and initializes the gui for this form. '''
      
      # 1. --- build each gui component
      self.__ok_button = self.__build_okbutton()
      self.__skip_button = self.__build_skipbutton()
      back_button = self.__build_backbutton()
      self.__table = self.__build_table(
         self.__issue_refs, issue_ref_hint, series_name_s, self.__ok_button)
      self.__label = self.__build_label() # must build AFTER table is built!
      self.__coverpanel = self.__build_coverpanel()
      
      # 2. --- configure this form, and add all the gui components to it      
      self.AutoScaleMode = AutoScaleMode.Font
      self.ClientSize = Size(730, 395)
      self.Text = i18n.get("IssueFormTitle")
      self.FormClosed += self.__form_closed_fired
      self.KeyPreview = True;
      self.KeyDown += self.__key_was_pressed
      self.KeyUp += self.__key_was_released
      
      self.Controls.Add (self.__label)
      self.Controls.Add(self.__table)
      self.Controls.Add(self.__ok_button)
      self.Controls.Add(self.__skip_button)
      self.Controls.Add(back_button)
      self.Controls.Add(self.__coverpanel) # must be added LAST

      # 3. --- define the keyboard focus tab traversal ordering      
      self.__ok_button.TabIndex = 1
      self.__skip_button.TabIndex = 2
      back_button.TabIndex = 3
      self.__coverpanel.TabIndex = 4
      self.__table.TabIndex = 5

      #4. --- make sure the UI goes into a good initial state
      self.__change_table_selection_fired(None, None)


   # ==========================================================================   
   def __build_table(self, issue_refs, issue_ref_hint,
         series_name_s, enter_button):
      '''
      Builds and returns the table for this form. If a good issue key hint is 
      given, that issue will be preselected in the table if possible.
      
      'issue_refs' -> a list with one IssueRef object for each row in the table
      'issue_ref_hint' -> may be the issue key for the given book (or may not!)
      'series_name_s' -> the name of the series to which all issues belong
      'enter_button' -> the button to "press" if the user hits enter
      '''
      
      # 1. --- configure the table itself
      table = ButtonDataGridView(enter_button)
      table.SortCompare += self.__sort_compare_fired
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
      if self.__config.show_covers_b:
         table.Size = Size(500, 290)
         table.Location = Point(218, 60)
      else:
         table.Size = Size(708, 290)
         table.Location = Point(10, 60)
         
      # 2. --- build columns
      table.ColumnCount = 4
      table.Columns[0].Name = i18n.get("IssueFormSeriesCol")
      table.Columns[0].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleLeft
      table.Columns[0].AutoSizeMode = \
         DataGridViewAutoSizeColumnMode.Fill
      
      table.Columns[1].Name = i18n.get("IssueFormIssueCol")
      table.Columns[1].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[1].AutoSizeMode = \
         DataGridViewAutoSizeColumnMode.AllCells
         
      table.Columns[2].Name = "ID"
      table.Columns[2].Visible = False
      table.Columns[2].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[2].AutoSizeMode = \
         DataGridViewAutoSizeColumnMode.AllCells
         
      table.Columns[3].Name = "Model ID"
      table.Columns[3].Visible = False
      table.Columns[3].DefaultCellStyle.Alignment =\
         DataGridViewContentAlignment.MiddleCenter
      table.Columns[3].AutoSizeMode =\
         DataGridViewAutoSizeColumnMode.AllCells

      # 3. --- copy model data into the table, each issue is a row
      for i in range(len(issue_refs)):
         name = series_name_s
         key = issue_refs[i].issue_key
         issue_num_s = issue_refs[i].issue_num_s   
         
         table.Rows.Add()
         table.Rows[i].Cells[0].Value = name
         table.Rows[i].Cells[1].Value = issue_num_s if issue_num_s else ''
         table.Rows[i].Cells[2].Value = key
         table.Rows[i].Cells[3].Value = i

      # 4. --- sort on the "Issue" column, and then preselect a row based on
      #    the give issue ID hint, or at least the first row if nothing else
      table.Sort(table.Columns[1], ListSortDirection.Ascending)
      if issue_ref_hint: 
         for i in range(len(issue_refs)):
            if table.Rows[i].Cells[2].Value == issue_ref_hint.issue_key:
               table.CurrentCell = table.Rows[i].Cells[0]
               self.__found_issue_in_table = True
               break
      if not self.__found_issue_in_table:
         table.CurrentCell = table.Rows[0].Cells[0]
         
         
      table.SelectionChanged += self.__change_table_selection_fired
      return table
      

   # ==========================================================================
   def __build_okbutton(self):
      ''' builds and returns the ok button for this form '''
      
      button = Button() 
      button.DialogResult = DialogResult.OK
      button.Location = Point(223, 362)
      button.Size = Size(90, 24)
      button.Text = i18n.get("IssueFormOK")
      return button


   # ==========================================================================
   def __build_skipbutton(self):
      ''' builds and returns the skip button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Ignore
      button.Location = Point(318, 362)
      button.Size = Size(90, 24)
      button.Text = i18n.get("IssueFormSkip")
      return button
      
   
   # ==========================================================================
   def __build_backbutton(self):
      ''' builds and returns the back button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Retry
      button.Location = Point(598, 362)
      button.Size = Size(125, 24)
      button.Text = i18n.get("IssueFormGoBack")
      return button


   # ==========================================================================
   def __build_label(self):
      ''' builds and returns the main text label for this form '''
   
      label = Label()
      label.Text = i18n.get("IssueFormChooseText") \
         if self.__found_issue_in_table else \
         i18n.get("IssueFormChooseUnknownText")
         
      if self.__config.show_covers_b:
         label.Location = Point(218, 20)
         label.Size = Size(480, 40)
      else:
         label.Location = Point(10, 20)
         label.Size = Size(680, 40)
      
      return label
   
   
   # ==========================================================================
   def __build_coverpanel(self):
      ''' builds and returns the IssueCoverPanel for this form '''

      panel = IssueCoverPanel(self.__config)
      panel.Location = Point(10, 30)
      # panel size is determined by the panel itself
      
      return panel
   
   
   # ==========================================================================
   def show_form(self):
      '''
      Displays this form, blocking until the user closes it.  When it is closed,
      it will return an IssueFormResult describing how it was closed, and any
      IssueRef that may have been chosen when it was closed.
      '''
      
      dialogAnswer = self.ShowDialog(self.Owner) # blocks
      
      if dialogAnswer == DialogResult.OK:
         result = IssueFormResult( IssueFormResult.OK, 
            self.__issue_refs[self.__chosen_index] )
         alt_image_ref = self.__coverpanel.get_alt_cover_image_url()
         if alt_image_ref:
            # the user chose a non-default cover image for this issue.
            # we'll store that choice in the global "session data map",
            # in case any other part of the program wants to use it.
            alt_cover_key = sstr(result) + "-altcover"
            self.__config.session_data_map[alt_cover_key] = alt_image_ref
      elif dialogAnswer == DialogResult.Cancel:
         result = IssueFormResult( IssueFormResult.CANCEL )
      elif dialogAnswer == DialogResult.Ignore:
         if self.ModifierKeys == Keys.Control:
            result = IssueFormResult( IssueFormResult.PERMSKIP )
         else:
            result = IssueFormResult( IssueFormResult.SKIP )
      elif dialogAnswer == DialogResult.Retry:
         result = IssueFormResult( IssueFormResult.BACK )
      else:
         raise Exception()
      return result
   
   
   # ==========================================================================
   def __form_closed_fired(self, sender, args):
      ''' this method is called whenever this IssueForm is closed. '''
      
      self.__table.Dispose()
      self.__coverpanel.free()
      self.Closed -= self.__form_closed_fired
      

   # ==========================================================================
   def __change_table_selection_fired(self, sender, args):
      ''' this method is called whenever the table's selected row changes '''

      # update __chosen_index (eventually used as this dialog's return value)
      # and then also use it to update the displayed cover image      
      selected_rows = self.__table.SelectedRows
      if selected_rows.Count == 1:
         self.__chosen_index = selected_rows[0].Cells[3].Value
         self.__coverpanel.set_issue(
            self.__issue_refs[self.__chosen_index] )
      else:
         self.__chosen_index = None
         self.__coverpanel.set_issue( None ) 
                
      # don't let the user click 'ok' if no row is selected!
      self.__ok_button.Enabled = selected_rows.Count == 1
      
   # ==========================================================================
   def __sort_compare_fired(self, sender, args):
      ''' this method is called whenever the table is resorted '''
      
      # without this listener, issue number column would sort like this:
      #    1, 10, 12, 12, 2 ,3 ,4, 5, 6, 7, 8, 9
      # instead of this:
      #    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
      
      if args.Column.Index == 1: 
         a = args.CellValue1 # string NOT number
         b = args.CellValue2 # string NOT number
         a_isnum = is_number(a);
         b_isnum = is_number(b);
         
         args.SortResult = 0
         if a_isnum and b_isnum: 
            args.SortResult = -1 if float(a) < float(b) else 1 \
               if float(a) > float(b) else 0
         elif a_isnum and not b_isnum:
            args.SortResult = 1;
         elif not a_isnum and b_isnum:
            args.SortResult = -1;
         else:
            args.SortResult = String.Compare(a,b)
         args.Handled = True
         
   #===========================================================================         
   def __key_was_pressed(self, sender, args):
      ''' Called whenever the user presses any key on this form. '''
      
      # highlight the skip button whenever the user presses control key
      if args.KeyCode == Keys.ControlKey and not self.__pressing_controlkey:
         self.__pressing_controlkey = True;
         self.__skip_button.Text = "- " + i18n.get("IssueFormSkip") + " -"
         
   #===========================================================================         
   def __key_was_released(self, sender, args):
      ''' Called whenever the user releases any key on this form. '''
      
      # unhighlight the skip button bold whenever the user releases control key
      if args.KeyCode == Keys.ControlKey:
         self.__pressing_controlkey = False;
         self.__skip_button.Text = i18n.get("IssueFormSkip")
      
#==============================================================================      
class IssueFormResult(object):
   '''
   Results that can be returned from the IssueForm.show_form() method.  The
   'name' of this object describes the manner in which the user closed the 
   dialog:
   
   1) IssueFormResult.CANCEL means the user cancelled this scrape operation.
   2) IssueFormResult.SKIP means the user elected to skip the current book.
   3) IssueFormResult.PERMSKIP means the user elected to skip the current book
      during this scrape, AND all future scrapes (i.e. add a 'skip tag' to book)
   4) IssueFormResult.BACK means the user chose to return to the SeriesForm
   5) IssueFormResult.OK means the user chose an IssueRef from those displayed
      
   Note that if the IssueFormResult has a name of 'OK', it should also have a 
   non-None 'ref', which is of course the actual IssueRef that the user chose.    
   '''
   
   OK = "ok"
   CANCEL = "cancel"
   SKIP = "skip"
   PERMSKIP = "permskip"
   BACK = "back"
   
   #===========================================================================         
   def __init__(self, name, ref=None):
      ''' 
      Creates a new IssueFormResult.
      name -> the name of the result, i.e. based on what button the user pressed
      ref -> the reference that the user chose, if they chose one at all.
      '''  
            
      if name != self.OK and name != self.CANCEL and \
         name != self.SKIP and name != self.BACK and name != self.PERMSKIP:
         raise Exception();
      
      self.__ref = ref if name == self.OK else None;
      self.__name = name;

      
   #===========================================================================         
   def get_name(self):
      ''' Gets the 'name' portion of this result (see possibilities above) '''
      return self.__name;

   
   #===========================================================================         
   def get_ref(self):
      ''' 
      Gets the IssueRef portion of this result, i.e. the one the user picked.
      This is only defined when the'name' of this result is "OK".
      '''
      return self.__ref;

   
   #===========================================================================         
   def get_debug_string(self):
      ''' Gets a simple little debug string summarizing this result.'''
      
      if self.get_name() == self.SKIP:
         return "SKIP scraping this book"
      elif self.get_name() == self.PERMSKIP:
         return "ALWAYS SKIP scraping this book"
      elif self.get_name() == self.CANCEL:
         return "CANCEL this scrape operation"
      elif self.get_name() == self.BACK:
         return "GO BACK to the series dialog"
      elif self.get_name() == self.OK:
         return "SCRAPE using: '" + sstr(self.get_ref()) + "'"
      else:
         raise Exception()
   

