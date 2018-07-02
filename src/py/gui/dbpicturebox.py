'''
This module contains the DBPictureBox class, which can be used to display 
remotely loaded images using an asyncrhonous off-loading thread.

@author: Cory Banack
'''

import clr
import utils
import db
from resources import Resources
from scheduler import Scheduler

clr.AddReference('System.Drawing')
from System.Drawing import Graphics, Bitmap
from System.Drawing import Rectangle, GraphicsUnit
from System.Drawing.Imaging import ColorMatrix, ImageAttributes

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import PictureBox, PictureBoxSizeMode

#==============================================================================
class DBPictureBox(PictureBox):
   '''
   This class extends a regular .NET PictureBox so that it's image can be set
   asynchronously by giving it a SeriesRef or IssueRef object (the 
   set_image_ref method).  This ref object is then used to query the 
   comic book database to find the appropriate image (if any) to set.   

   Because accessing a database can be slow and potentially prone to errors, 
   this class contains a number of features to automatically handle
   problems that may occur:

   1) All image retrieval happens asyncronously on an external thread.   The 
   final result is only loaded into this picturebox when the image retrieval is
   finished.  If many image retrievals are requested nearly simulataneously, 
   most of them will be ignored, and only the most recent one is guaranteed to 
   actually be performed (and update the displayed image.)

   2) All image retrieval is short-term cached, so if you switch the image ref 
   back to a previous one, it will automatically use the cached image instead of 
   reloading.
   
   '''


   #===========================================================================
   def __init__(self): 
      ''' Defines member variables for new instances of this class. '''
      # the ref of whatever image should currently be displayed, or None
      self.__current_image_ref = None
      
      # a simple "last-in-and-ignore-everything-else" scheduler
      self.__scheduler = Scheduler()
      
      # our cache of loaded image objects. {(imageref,issuehint)->Image}
      self.__image_cache = {}
      
      # the image that gets displayed if we have nothing else to display
      self.__unknown_image = Resources.createComicVineLogo()
      
      # the image that gets displayed while we are loading another image
      self.__loading_image = self.__copy_transparent(self.__unknown_image)
      
      self._initialize()


   #===========================================================================
   def _initialize(self):
      ''' Initial configuration for new instances of this class '''
      
      PictureBox.__init__(self)      
      def visibility_changed(sender, args):
         if self.Visible: self.__update_image()
         
      self.VisibleChanged += visibility_changed
      self.SizeMode = PictureBoxSizeMode.StretchImage
      self.set_image_ref(None)


   #===========================================================================
   def free(self):
      ''' Explicitly frees all resources held by this object. '''
      self.__scheduler.shutdown(True) # blocks; safer even if gui locks a little
      self.__unknown_image.Dispose()
      self.__loading_image.Dispose()
      for image in self.__image_cache.values():
         image.Dispose()
      self.__image_cache = {}
      PictureBox.Dispose(self, True)
      

   #===========================================================================
   def set_image_ref(self, ref):
      '''
      Sets the image displayed in this picturebox to whatever image
      corresponds to the given ref (a SeriesRef or IssueRef) in the database.
      If the given value is None, or unavailable, a placeholder image gets used.
      '''
      
      self.__current_image_ref = ref
      if self.Visible:
         self.__update_image()
     
    
   #===========================================================================
   def __copy_transparent(self, image):
      ''' Creates a semi-transparent copy of the given image ''' 
      
      b = Bitmap( image.Width, image.Height )
      g = Graphics.FromImage(b)
      cm = ColorMatrix()
      cm.Matrix33 = 0.3
      ia = ImageAttributes()
      ia.SetColorMatrix(cm)
      g.DrawImage(image, Rectangle(0,0, image.Width, image.Height), 0,0,\
         image.Width, image.Height, GraphicsUnit.Pixel, ia)
      return b

   #===========================================================================
   def __update_image(self):
      '''
      Update the currently displayed image on this picturebox to match
      whatever image __current_image_ref pulls out of the database or cache.
      
      If the image is coming from the database, loading is done on separate
      worker thread, so as not to lock up the UI.
      '''
       
      # simple image setter that uses a blank image if 'image' is None 
      def switchimage( image ):
         if image: self.Image = image
         else: self.Image = self.__unknown_image
             
      ref = self.__current_image_ref
      
      # 1. if the ref is empty, switch to display an empty image
      if not ref and ref != 0:
         switchimage(None)
         
      # 2. if the ref is cached, switch to display the cached image
      elif ref in self.__image_cache:
         switchimage( self.__image_cache[ref] )
         
      # 3. if the ref is unkown, the hard part begins.  create a download "task"
      #    that downloads, caches, and then switches display to the needed 
      #    image.  then invoke this task asyncrhonously on the off-thread.
      else:
         self.Image = self.__loading_image
         def download_task():
            
            # 3a. load the image. 
            new_image = db.query_image(ref) # disposed later
               
            # 3b. now that we've loaded a new image, the following method is
            #     passed back to the gui thread and run to update our gui 
            def update_image():
               
               # if somehow the image we just loaded is already in the cache,
               # take it out and dispose it.  this should be rare.    
               if ref in self.__image_cache:
                  old_image = self.__image_cache[ref]
                  del self.__image_cache[ref]
                  if old_image:
                     old_image.Dispose()
               
               # cache the new image, so we never have to load it again
               if new_image:
                  self.__image_cache[ref] = new_image
               
               # if the __current_image_ref hasn't changed, switch this 
               # PictureBox to display that image.  otherwise, we already 
               # loading a new one, so don't do a pointless visual update.
               if ref == self.__current_image_ref:
                  switchimage(new_image)
                  
            utils.invoke(self, update_image, False) 
         self.__scheduler.submit(download_task)
         