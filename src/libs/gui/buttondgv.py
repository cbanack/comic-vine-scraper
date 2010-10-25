'''
Created on Feb 16, 2010

@author: cbanack
'''

#corylow: comment and cleanup this file

import clr

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import DataGridView

# a specialized DataGridView that replaces it's "enter" keystroke with a 
# click event on the button given in its constructor 
class ButtonDataGridView(DataGridView):
   def __init__(self, button):
      self._button = button
   
   def ProcessCmdKey(self, msg, key): 
      if key.ToString() == 'Return':
         self._button.PerformClick() 
         return True
      else:
         return super(ButtonDataGridView,self).ProcessCmdKey(msg, key)