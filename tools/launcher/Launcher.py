# This Python file uses the following encoding: us-ascii

# corylow: comment and cleanup this file

import sys
import os
import cPickle
import resources

import clr
clr.AddReferenceByPartialName("System.Windows.Forms")
clr.AddReferenceByPartialName("System.Drawing")
from System.Windows.Forms import Form

# add a reference to a directory containing mockups of key comic rack dlls 
sys.path.append( os.path.dirname(os.path.dirname(__file__))+r"\comicrack")

# we have to add a few definitions to help the starting conditions when this 
# script is running as part of ComicRack

import ComicVineScraper

class ComicRack:
   class AppImpl:
      ProductVersion = '999.999.99999'
      def GetComicPage(self, arg1, arg2):
            return None
      def SetCustomBookThumbnail(self, book, bitmap):
         return True    
   class MainForm(Form):
      pass
   
   App = AppImpl()
   MainWindow = MainForm()
   MainWindow.Show()
   MainWindow.CenterToScreen()

ComicVineScraper.ComicRack = ComicRack

resources._SCRIPT_DIRECTORY = os.path.dirname( \
   os.path.dirname( os.path.dirname(__file__))) + r'/profile/' 
resources.LOCAL_CACHE_DIRECTORY = resources._SCRIPT_DIRECTORY + r'localCache/'
resources.SETTINGS_FILE = resources._SCRIPT_DIRECTORY + r'settings.dat'
resources.GEOMETRY_FILE = resources._SCRIPT_DIRECTORY + r'geometry.dat'

# now grab the
class Launcher(object):
   def __init__(self):
      if len(sys.argv) == 2:
            # note that this doesn't work (for highly mysterious reasons) if you
            # change the project source character encoding to anything other 
            # than US-ASCII 
            f = open(sys.argv[1], "r")
            books = cPickle.load(f)
            ComicVineScraper.ComicVineScraper(books)  
      else:
            print "Usage: this script takes a single file as an argument."
    
Launcher()