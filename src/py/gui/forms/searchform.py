''' 
This module is home to the SearchForm class.

@author: Cory Banack
'''

import clr
import i18n
from cvform import CVForm
import utils

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import AutoScaleMode, Button, \
    DialogResult, Keys, Label, TextBox

clr.AddReference('System.Drawing')
from System.Drawing import Point, Size

#==============================================================================
class SearchForm(CVForm):
   '''
   This class is a popup, modal dialog with a text field that asks the user to 
   specify search terms for a search query on the Comic Vine database.  It may
   also display an error message describing previous search terms that failed.
   '''
   
   #===========================================================================
   def __init__(self, scraper, initial_search_s, failed_search_s=""):
      '''
      Initializes this form.
      
      'scraper' -> the currently running ScrapeEngine
      'initial_search_s' -> the initial value in this form's text field.
      'failed_search_s' -> (optional) the failed search terms associated with
         this SearchForm.  If this is NOT empty, the search dialog will display
         an error message about the failed search terms couldn't be found
      ''' 
      # the text label for this form (displays regular message)
      self.__label = None
      
      # the fail label for this form (display 'search failed' message)
      self.__fail_label = None
      
      # whether or not the fail label should be visible
      self.__fail_label_is_visible = failed_search_s and failed_search_s.strip()
      
      # the search button (i.e. the 'ok' button) for this form
      self.__search_button = None
            
      # true when the user is pressing the control key, false otherwise
      self.__pressing_controlkey = False;
      
      # the skip button for this form
      self.__skip_button = None
      
      # the cancel button for this form
      self.__cancel_button = None
      
      # the textbox for this form
      self.__textbox = None
      
      
      CVForm.__init__(self, scraper.comicrack.MainWindow, "searchformLocation")
      scraper.cancel_listeners.append(self.Close)
      self.__build_gui(initial_search_s, failed_search_s)
      

   #===========================================================================      
   def __build_gui(self, initial_search_s, failed_search_s):
      ''' Constructs and initializes the gui for this form. '''
      
      # build each gui component.
      self.__fail_label = self.__build_fail_label(failed_search_s)
      self.__label = self.__build_label()
      self.__search_button = self.__build_searchbutton()
      self.__skip_button = self.__build_skipbutton()
      self.__cancel_button = self.__build_cancelbutton()
      self.__textbox = self.__build_textbox(
         initial_search_s, self.__search_button, self.__cancel_button)
      
      # configure this form, and add all gui components to it
      self.AutoScaleMode = AutoScaleMode.Font
      self.ClientSize = Size(435, 200 if self.__fail_label_is_visible else 100)
      self.Text = i18n.get("SeriesSearchFailedTitle") \
         if self.__fail_label_is_visible else i18n.get("SearchFormTitle")
      self.KeyDown += self.__key_was_pressed
      self.KeyUp += self.__key_was_released
      self.__textbox.KeyDown += self.__key_was_pressed
      self.__textbox.KeyUp += self.__key_was_released
      self.Deactivate += self.__was_deactivated
      
      self.Controls.Add(self.__fail_label)
      self.Controls.Add(self.__label)
      self.Controls.Add(self.__textbox)
      self.Controls.Add(self.__search_button)
      self.Controls.Add(self.__skip_button)
      self.Controls.Add(self.__cancel_button)
      
      # define the keyboard focus tab traversal ordering
      self.__textbox.TabIndex = 0
      self.__search_button.TabIndex = 1
      self.__skip_button.TabIndex = 2 
      self.__cancel_button.TabIndex = 3


   #===========================================================================      
   def __build_fail_label(self, failed_search_s):
      ''' builds and returns the 'search failed' text label for this form.
          if there is no failed search terms, this returns None. '''

      label = Label()
      label.Location = Point(10, 10)
      label.Size = Size(415, 100)
      label.Visible = self.__fail_label_is_visible   
      if self.__fail_label_is_visible:
         label.Text = i18n.get("SeriesSearchFailedText").format(failed_search_s)
         
      return label

   
   #===========================================================================      
   def __build_label(self):
      ''' builds and returns the text label for this form '''

      label = Label()
      label.Location = Point(10, 110 if self.__fail_label_is_visible else 10)
      label.Size = Size(415, 20)
      label.Text = i18n.get("SearchFormText")
      return label

         
   #===========================================================================      
   def __build_searchbutton(self):
      ''' builds and returns the search button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.OK
      button.Location = Point(125, 170 if self.__fail_label_is_visible else 70)
      button.Size = Size(100, 23)
      button.Text = i18n.get("SearchFormSearch")
      button.UseVisualStyleBackColor = True
      return button
   
   
   #===========================================================================      
   def __build_skipbutton(self):
      ''' builds and returns the skip button for this form '''

      button = Button()
      button.DialogResult = DialogResult.Ignore
      button.Location = Point(235, 170 if self.__fail_label_is_visible else 70)
      button.Size = Size(90, 23)
      button.Text = i18n.get("SearchFormSkip")
      button.UseVisualStyleBackColor = True
      return button
   
   
   #===========================================================================      
   def __build_cancelbutton(self):
      ''' builds and returns the cancel button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Cancel
      button.Location = Point(335, 170 if self.__fail_label_is_visible else 70)
      button.Size = Size(90, 23)
      button.Text = i18n.get("SearchFormCancel")
      button.UseVisualStyleBackColor = True
      return button
   
   
   #===========================================================================      
   def __build_textbox(self, initial_text_s, searchbutton, cancelbutton):
      ''' 
      Builds and returns the textbox for this form.
      initial_text_s -> the starting text for the textbox
      searchbutton -> the 'search' button from the containing Form  
      cancelbutton -> the 'cancel' button from the containing Form  
      '''
      
      # make a special subclass of TextBox in order to...
      class SearchTextBox(TextBox):
         # ... capture ESCAPE and ENTER keypresses
         def OnKeyPress(self, args):
            if args.KeyChar == chr(13):
               searchbutton.PerformClick()
               args.Handled = True
            elif args.KeyChar == chr(27):
               cancelbutton.PerformClick()
               args.Handled = True
            else:
               TextBox.OnKeyPress(self, args)
               
         # ... disable the Search button if the textbox is empty
         def OnTextChanged(self, args):
            searchbutton.Enabled = bool(self.Text.strip())
            
      textbox = SearchTextBox()
      textbox.Location = Point(10, 135 if self.__fail_label_is_visible else 35)
      textbox.Size = Size(415, 1)
      if initial_text_s:
         textbox.Text = initial_text_s
      textbox.SelectAll()
      return textbox



   #===========================================================================      
   def show_form(self):
      '''
      Displays this form, blocking until the user closes it.  When it is closed, 
      a SearchFormResult will be returned indicating what the user chose.
      '''
      
      dialogAnswer = self.ShowDialog( self.Owner ) # blocks
      if dialogAnswer == DialogResult.OK:
         search_terms_s = self.__textbox.Text.strip()
         return SearchFormResult("SEARCH", search_terms_s) if search_terms_s \
             else SearchFormResult("CANCEL")
      elif dialogAnswer == DialogResult.Ignore:
         if self.ModifierKeys == Keys.Control:
            return SearchFormResult("PERMSKIP")
         else:
            return SearchFormResult("SKIP")
      else:
         return SearchFormResult("CANCEL")
 
 
   #===========================================================================         
   def __key_was_pressed(self, sender, args):
      ''' Called whenever the user presses any key on this form. '''
      
      # highlight the skip button whenever the user presses control key
      if args.KeyCode == Keys.ControlKey and not self.__pressing_controlkey:
         self.__pressing_controlkey = True;
         self.__skip_button.Text = "- " + i18n.get("SearchFormSkip") + " -"
   
         
   #===========================================================================         
   def __key_was_released(self, sender, args):
      ''' Called whenever the user releases any key on this form. '''
      
      # unhighlight the skip button bold whenever the user releases control key
      if args.KeyCode == Keys.ControlKey:
         self.__pressing_controlkey = False;
         self.__skip_button.Text = i18n.get("SearchFormSkip")
         
   #===========================================================================         
   def __was_deactivated(self, sender, args):
      ''' Called whenever this form gets deactivated, for any reason '''
      
      # unhighlight the skip button bold whenever we deactivate
      if self.__pressing_controlkey:
         self.__pressing_controlkey = False;
         self.__skip_button.Text = i18n.get("SearchFormSkip")
      
      
#===========================================================================      
class SearchFormResult(object):
   ''' Results that can be returned from the SearchForm.show_form() method. '''
   
   CANCEL = "cancel"
   SKIP = "skip"
   PERMSKIP = "permskip"
   
   def __init__(self, id, search_terms_s=""):
      '''
      Creates a new SearchFormResult object with the given ID.
      
      id -> the result ID.  Must be one of "SEARCH" (proceed with search), 
            "CANCEL" (cancel entire scrape operation), "SKIP" (skip this book) 
            or "PERMSKIP" (permanently skip this book)
            
      search_terms_s -> the search terms to search on when our ID is "SEARCH". 
            This value should be empty for all other IDs.
      '''
      if id != "SEARCH" and id != "CANCEL" and \
            id != "SKIP" and id != "PERMSKIP":
         raise Exception()
      
      search_terms_s = search_terms_s.strip()
      if id=="SEARCH" and not search_terms_s:
         raise Exception()
      
      self.__id = id
      self.__search_terms_s = search_terms_s \
          if id=="SEARCH" and utils.is_string(search_terms_s) else ""
      
      
   #===========================================================================         
   def equals(self, id):
      ''' 
      Returns True iff this SearchFormResult has the given ID (i.e. one of 
      "SEARCH", "CANCEL", "SKIP", or "PERMSKIP". 
      '''
      return self.__id == id

  
   #===========================================================================         
   def get_search_terms_s(self):
      '''
      Get the series search terms for this SearchFormResult. This value will be
      non-empty if our id is "SEARCH", and it will be empty ("") otherwise.  
      '''
      return self.__search_terms_s
   
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
         return "SEARCH using: '" + self.get_search_terms_s() + "'"
      else:
         raise Exception()  
      