'''
This module contains the CVForm class.

@author: Cory Banack
'''

import clr
import log

clr.AddReference('System.Windows.Forms')

from System.Windows.Forms import FormBorderStyle, Keys
from persistentform import PersistentForm

#==============================================================================
class CVForm(PersistentForm):
   '''
   This class is the direct superclass of all Comic Vine Scraper forms.
   It contains functionality and default configuration that is common to
   all forms in this application.
   '''

   #===========================================================================
   def __init__(self, owner, persist_loc_key_s = "", persist_size_key_s = "" ):
      ''' 
      Constructs a new CVForm.
      Requires an owner parameter, which is the Form that will own this Form.
      The other two parameters are passed up to the PersistentForm superclass.
      '''
      super(CVForm, self).__init__( persist_loc_key_s, persist_size_key_s )
      
      # these are the default properties of all CVForms.
      self.Owner = owner 
      self.Modal = False
      self.MaximizeBox = False                                                
      self.MinimizeBox = False                                                
      self.ShowIcon = False                                                   
      self.ShowInTaskbar = False    
      self.FormBorderStyle = FormBorderStyle.FixedToolWindow
      

   #===========================================================================
   def __enter__(self):
      ''' Called automatically if you use this form in a python "with" block.'''
      return self
   
   
   #===========================================================================
   def __exit__(self, type, value, traceback):
      ''' Called automatically if you use this form in a python "with" block.'''
      
      # ensure that the form is closed and disposed in a timely manner.
      # this probably isn't strictly necessary, but it doesn't hurt.
      self.Close()
      self.Dispose()


   #===========================================================================
   def ProcessCmdKey(self, msg, keys):
      ''' Called anytime the user presses a key while this form has focus. '''
      
      # overidden to allow various "application wide" hotkeys
      if keys == Keys.Escape:
         # ensure that all CVForms close themselves if you press the escape key. 
         self.Close()
      elif keys == Keys.Control|Keys.Shift|Keys.L:
         # ensure that the use can manually save out an application log
         log.save()
      else:
         super(CVForm, self).ProcessCmdKey(msg, keys)
