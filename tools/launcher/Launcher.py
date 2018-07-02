'''
This module's purpose is to launch the ComicVineScraper plugin from within the 
Eclipse IDE.  To do this, it must emulate the 'real' comicrack environment.

This module is a development tool; it is NOT part of the regular 
ComicVineScraper distributable and will not be run by regular users.
'''

import sys
import os
import cPickle

import clr
clr.AddReferenceByPartialName("System.Windows.Forms")
from System.Windows.Forms import Form


# add a reference to a directory containing mockups of key comic rack dlls 
sys.path.append( os.path.dirname(os.path.dirname(__file__))+r"\comicrack")

# pylint:disable=W0232,C1001
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
   
   # the existence of the attribute tells identifies this as our "fake" version
   # of ComicRack, not the real application.  it's how we know we're standalone  
   StandAloneFlag = None 

#==============================================================================


# 1. add our 'fake' ComicRack into ComicVineScraper, in the same spot where it 
#    would be if we were running inside the real ComicRack app.
import ComicVineScraper
ComicVineScraper.ComicRack = ComicRack

# 2. now go ahead and start the ComicVineScraper plugin.
if len(sys.argv) == 2:
   # note that this doesn't work (for highly mysterious reasons) if you
   # change the project source character encoding to anything other 
   # than US-ASCII 
   f = open(sys.argv[1], "r")
   books = cPickle.load(f)
   ComicVineScraper.cvs_scrape(books)  
else:
   print "Usage: this script takes a single file as an argument."
      
      