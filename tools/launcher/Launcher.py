'''
This module's purpose is to launch the ComicVineScraper plugin from within the 
Eclipse IDE.  To do this, it must emulate the 'real' comicrack environment in a
number of important ways.

This module is a development tool; it is NOT part of the regular 
ComicVineScraper distributable.
'''

import sys
import os
import cPickle
from resources import Resources

import clr
clr.AddReferenceByPartialName("System.Windows.Forms")
from System.Windows.Forms import Form


# add a reference to a directory containing mockups of key comic rack dlls 
sys.path.append( os.path.dirname(os.path.dirname(__file__))+r"\comicrack")

#==============================================================================
class ComicRack(object):
   ''' A static class that emulates the real ComicRack object. '''
   class AppImpl:
      ProductVersion = '999.999.99999'
      def GetComicPage(self, arg1, arg2):
            return None
      def SetCustomBookThumbnail(self, book, bitmap):
         return True
   
   class MainForm(Form):
      pass
   
   @classmethod
   def Localize(cls, resource, key, backuptext):
      return backuptext    
   
   App = AppImpl()
   MainWindow = MainForm()
   MainWindow.Show()
   MainWindow.CenterToScreen()

#==============================================================================


# 1. add our 'fake' ComicRack into ComicVineScraper, in the same spot where it 
#    would be if we were running inside the real ComicRack app.
import ComicVineScraper
ComicVineScraper.ComicRack = ComicRack


# 2. change the location of key resources so that we run out of a profile 
#    directory in our project on the IDE, rather than the real profile dir.
Resources.enable_ide_mode( os.path.dirname(
   os.path.dirname( os.path.dirname(__file__))) )


# 3. now go ahead and start the ComicVineScraper plugin.
if len(sys.argv) == 2:
      # note that this doesn't work (for highly mysterious reasons) if you
      # change the project source character encoding to anything other 
      # than US-ASCII 
      f = open(sys.argv[1], "r")
      books = cPickle.load(f)
      ComicVineScraper.ComicVineScraper(books)  
else:
      print "Usage: this script takes a single file as an argument."
      
      