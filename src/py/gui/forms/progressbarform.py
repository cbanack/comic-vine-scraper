#corylow: comment and cleanup this file

'''

@author: Cory Banack
'''


import clr
from cvform import CVForm

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import ProgressBar


clr.AddReference('IronPython')
class ProgressBarForm(CVForm): 

   def __init__(self, owner, scraper, maximum): 
      CVForm.__init__(self, owner, "pbformLocation")
      
      pb = ProgressBar()
      pb.Name = 'pb'
      pb.Minimum = 0
      pb.Maximum = maximum
      pb.Step = 1
      pb.Value = 0

      pb.Width = 400
      self.Controls.Add(pb)
      self.Height = 45
      self.Width = 400
      self.prog = pb
      self.scraper = scraper
      self.cancel_on_close = True
      
   def show_form(self):
      self.Show(self.Owner)
      
   def OnClosed(self, args):
      # if this close occurred as the result of the user manually closing the
      # window, that's a 'cancel' request; flip the scraper's cancelled switch.
      if self.cancel_on_close:
         self.scraper.cancel()
                  
      CVForm.OnClosed(self, args)
        
   def __enter__(self):
      return self
   
   def __exit__(self, type, value, traceback):
      self.cancel_on_close = False
      self.Close()
      

