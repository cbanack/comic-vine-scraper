'''
This module is home to the ButtonDataGridView class.

@author: Cory Banack
'''

import clr

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import DataGridView

# =============================================================================
class ButtonDataGridView(DataGridView):
   ''' 
   The ButtonDataGridView is a specialized DataGridView subclass that replaces 
   its regular "enter" keystroke behaviour with a mouse click event on a button.

   The clicked button is provided in the constructor of the ButtonDataGridView.
   '''  

   # ==========================================================================   
   def __init__(self, button):
      '''
      Initializes a new ButtonDataGridView.  The given button is the .NET
      Button object that should be 'clicked' anytime the user presses enter on
      this DataGridView.   It must not be None.
      '''
      if button is None:
         raise Exception("None is not allow as an argument here.")
      self.__button = button
   
   # ==========================================================================
   def ProcessCmdKey(self, msg, key): 
      ''' Overrides the superclass method to intercept 'enter' keystrokes. '''
      
      if key.ToString() == 'Return':
         self.__button.PerformClick() 
         return True
      else:
         return super(ButtonDataGridView,self).ProcessCmdKey(msg, key)
