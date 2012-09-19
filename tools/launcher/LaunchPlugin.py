'''
This module's purpose is to launch the ComicVineScraper app in plugin mode,
from within the Eclipse IDE.  
'''

import sys
import os
import cPickle
from FakeComicRack import FakeComicRack


if len(sys.argv) == 2:
   # 1. add a path reference to a directory containing copies of comic rack dlls 
   sys.path.append( os.path.dirname(os.path.dirname(__file__))+r"\comicrack" )
   
   # 2. set the ComicRack attribute on ComicVineScraper
   import ComicVineScraper
   ComicVineScraper.ComicRack = FakeComicRack
   
   # 3. now go ahead and start the ComicVineScraper plugin.
   # note that this doesn't work (for highly mysterious reasons) if you
   # change the project source character encoding to anything other 
   # than US-ASCII 
   f = open(sys.argv[1], "r")
   books = cPickle.load(f)
   ComicVineScraper.cvs_scrape(books, True)  
else:
      print "Usage: this script takes a single file as an argument."
      
      