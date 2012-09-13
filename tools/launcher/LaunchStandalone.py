'''
This module's purpose is to launch the ComicVineScraper app in standalone mode.
This is the stand
'''

from FakeComicRack import FakeComicRack

# 1. set the ComicRack attribute on ComicVineScraper
import ComicVineScraper
ComicVineScraper.ComicRack = FakeComicRack

# 2. now go ahead and start the ComicVineScraper Standalone app.
ComicVineScraper.cvs_scrape([])    