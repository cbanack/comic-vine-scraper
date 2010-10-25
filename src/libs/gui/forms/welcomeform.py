'''
This module is home to the WelcomeForm class.

Created on June 2, 2010
@author: cbanack
'''

import clr
import resources
from cvform import CVForm 
from configuration import Configuration
from configform import ConfigForm

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import AutoScaleMode, Button, DialogResult, Label

clr.AddReference('System.Drawing')
from System.Drawing import Point, Size

# =============================================================================
class WelcomeForm(CVForm):
   '''
   This is the first modal popup dialog that you see when you run the scraper.
   It welcomes you to the program, and offers you the ability to change
   script settings before continuing.
   '''
   
   #===========================================================================
   def __init__(self, owner, books):
      CVForm.__init__(self, owner, "welcomeformLocation")
      '''
      Initializes this form.
      
      'owner' -> this form's owner window/dialog
      'books' -> a list of all the comic books being scraped.
      '''
      
      self.__build_gui(books);

      
   # ==========================================================================
   def __build_gui(self, books):
      '''
       Constructs and initializes the gui for this form.
      'books' -> a list of all the comic books being scraped.
      '''
      
      # 1. --- build each gui component
      label = self.__build_label(books)
      ok = self.__build_okbutton()
      settings = self.__build_settingsbutton()
      cancel = self.__build_cancelbutton()
   
      # 2. --- configure this form, and add all the gui components to it
      self.AcceptButton = ok
      self.CancelButton = cancel
      self.AutoScaleMode = AutoScaleMode.Font
      self.Text = 'Comic Vine Scraper - v' + resources.SCRIPT_VERSION
      self.ClientSize = Size(396, 100)
   
      self.Controls.Add(label)
      self.Controls.Add(ok)
      self.Controls.Add(cancel)
      self.Controls.Add(settings)
      
      # 3. --- define the keyboard focus tab traversal ordering
      ok.TabIndex = 0
      cancel.TabIndex = 1
      label.TabIndex = 2
      settings.TabIndex = 3
      
      
   # ==========================================================================
   def __build_label(self, books):
      ''' 
      Builds and returns the Label for this form.
      'books' -> a list of all the comic books being scraped. 
      '''

      plural = len(books) > 1
      
      label = Label()
      label.AutoSize = True
      label.Location = Point(9, 10)
      label.Size = Size(299, 13)
      label.Text = ("You are about to download and store details "+\
         'for {0} comic book{1}.\n\n'+\
         "Click 'Start Scraping...' to begin.").format(len(books),  
         "s" if plural else "") 
      return label
   
   
   # ==========================================================================
   def __build_settingsbutton(self):
      ''' Builds and returns the settings button for this form. '''
     
      button = Button()
      button.Click += self.__show_configform
      button.Location = Point(10, 68)
      button.Size = Size(80, 23)
      button.Text = 'Settings...'
      button.UseVisualStyleBackColor = True
      return button

   
   # ==========================================================================
   def __build_cancelbutton(self):
      ''' Builds and returns the cancel button for this form. '''
      
      button = Button()
      button.DialogResult = DialogResult.Cancel
      button.Location = Point(309, 68)
      button.Size = Size(75, 23)
      button.Text = 'Cancel'
      button.UseVisualStyleBackColor = True
      return button

   
   # ==========================================================================
   def __build_okbutton(self):
      ''' Builds and returns the ok button for this form. '''

      button = Button()
      button.DialogResult = DialogResult.OK
      button.Location = Point(208, 68)
      button.Size = Size(95, 23)
      button.Text = 'Start Scraping...'
      button.UseVisualStyleBackColor = True
      return button

      
   # ==========================================================================
   def show_form(self):
      '''
      Displays this form, blocking until the user closes it.  When it is closed,
      it will either return None, which indicates that the user cancelled the
      dialog, and that the script should be cancelled, or it returns the 
      Configuration object that should be used for the remainder of the 
      script's execution.
      '''
      
      dialogAnswer = self.ShowDialog() # blocks
      if dialogAnswer == DialogResult.OK:
         config = Configuration()
         config.load_defaults()
      else:
         config = None
      return config
      
      
   # ==========================================================================
   def __show_configform(self, sender, args):
      '''
      Displays the configform, blocking until the user closes it.   Changes made
      to the settings in that form will be propogated to the return value of the
      show_form() method.
      '''
      
      with ConfigForm(self) as config_form:
         config_form.show_form() # blocks
   