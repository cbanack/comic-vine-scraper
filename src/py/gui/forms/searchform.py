''' 
This module is home to the SearchForm class.

@author: Cory Banack
'''

import clr
import i18n
from cvform import CVForm

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import AutoScaleMode, Button, \
    DialogResult, Label, TextBox

clr.AddReference('System.Drawing')
from System.Drawing import Point, Size

#==============================================================================
class SearchForm(CVForm):
   '''
   This class is a popup, modal dialog with a text field that asks the user to 
   specify search terms for a search query on the Comic Vine database.
   '''
   
   #===========================================================================
   def __init__(self, scraper, initial_search_s):
      '''
      Initializes this form.
      
      'scraper' -> the currently running ScrapeEngine
      'initial_search_s' -> the initial value in this form's text field.
      ''' 

      # the text label for this form
      self.__label = None
      
      # the search button (i.e. the 'ok' button) for this form
      self.__search_button = None
      
      # the skip button for this form
      self.__skip_button = None
      
      # the cancel button for this form
      self.__cancel_button = None
      
      # the textbox for this form
      self.__textbox = None
      
      
      CVForm.__init__(self, scraper.comicrack.MainWindow, "searchformLocation")
      scraper.cancel_listeners.append(self.Close)
      self.__build_gui(initial_search_s)
      

   #===========================================================================      
   def __build_gui(self, initial_search_s):
      ''' Constructs and initializes the gui for this form. '''
      
      # build each gui component
      self.__label = self.__build_label()
      self.__search_button = self.__build_searchbutton()
      self.__skip_button = self.__build_skipbutton()
      self.__cancel_button = self.__build_cancelbutton()
      self.__textbox = self.__build_textbox(
         initial_search_s, self.__search_button, self.__cancel_button)
      
      # configure this form, and add all gui components to it
      self.AutoScaleMode = AutoScaleMode.Font
      self.ClientSize = Size(405, 100)
      self.Text = i18n.get("SearchFormTitle")
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
   def __build_label(self):
      ''' builds and returns the text label for this form '''

      label = Label()
      label.Location = Point(10, 10)
      label.Size = Size(385, 20)
      label.Text = i18n.get("SearchFormText")
      return label

         
   #===========================================================================      
   def __build_searchbutton(self):
      ''' builds and returns the search button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.OK
      button.Location = Point(150, 70)
      button.Size = Size(75, 23)
      button.Text = i18n.get("SearchFormSearch")
      button.UseVisualStyleBackColor = True
      return button
   
   
   #===========================================================================      
   def __build_skipbutton(self):
      ''' builds and returns the skip button for this form '''

      button = Button()
      button.DialogResult = DialogResult.Ignore
      button.Location = Point(235, 70)
      button.Size = Size(75, 23)
      button.Text = i18n.get("SearchFormSkip")
      button.UseVisualStyleBackColor = True
      return button
   
   
   #===========================================================================      
   def __build_cancelbutton(self):
      ''' builds and returns the cancel button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Cancel
      button.Location = Point(320, 70)
      button.Size = Size(75, 23)
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
      textbox.Location = Point(10, 35)
      textbox.Size = Size(385, 1)
      if initial_text_s:
         textbox.Text = initial_text_s
      textbox.SelectAll()
      return textbox



   #===========================================================================      
   def show_form(self):
      '''
      Displays this form, blocking until the user closes it.  When it is 
      closed, one of three values will be returned.  If SearchFormResult.CANCEL
      is returned, it means the user has elected to cancel the scrape operation.
      If an SearchFormResults.SKIP is returned, it means the user has elected to
      skip the current book.   Finally, if anything else is returned it will be 
      a string that the user has entered--the string that the user wants to 
      search on.
      '''
      
      dialogAnswer = self.ShowDialog( self.Owner ) # blocks
      if dialogAnswer == DialogResult.OK:
         retval = self.__textbox.Text.strip()
         return retval if retval else SearchFormResult.CANCEL
      elif dialogAnswer == DialogResult.Ignore:
         return SearchFormResult.SKIP
      else:
         return SearchFormResult.CANCEL
      
      
#===========================================================================      
class SearchFormResult(object):
   ''' Results that can be returned from the SearchForm.show_form() method. '''
   
   CANCEL = "cancel"
   SKIP = "skip"