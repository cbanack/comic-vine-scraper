'''
This module contains the DBPictureBox class, which can be used to display 
remotely loaded images using an asyncrhonous off-loading thread manner.

@author: Cory Banack
'''
#import clr
#import resources
#import utils


# a global variable, an instance of the I18n class that will only be 
# available to our module's methods when this module has been "installed"
__i18n = None

def install(comicrack):
   """
   Installs this module.  This must be called before any other method in this
   module is called.  You must take steps to GUARANTEE that this module's
   uninstall() method is called once you have called this method.
   
   Takes a single parameter, which is the ComicRack object that we are 
   running as part of.
   """
   
   global __i18n
   if __i18n is not None:
      raise Exception("don't install '" + __name__ + "' module twice!")
   __i18n = __I18n(comicrack)
   
#==============================================================================
def uninstall(): 
   """
   Uninstalls this module.
   
   It is so important to make sure this method is called at the end of your 
   script, you should probably use a try-finally section to ensure it!
   """
   
   global __i18n
   if __i18n:
      __i18n = None
         

#==============================================================================
def get(key_s):
   """
   Retrieves the internationalized (i18n) string for the given string key,
   which should not be empty or None.
   
   The value returned by this method will be locale dependent--that is, if the
   user's ComicRack instance is running in a specific locale mode,
   then the returned string will match that locale's language, if possible.  
   
   If the given key is invalid, this method will throw an exception.  If there
   is simply no translated string for the current locale, however, then this
   method will return the string in the default locale--english (en).
   
   This method only words while this module is installed.
   """
   
   if not __i18n:
      raise Exception("this module is not currently installed!")
   
   return __i18n.get(key_s)
      
      
   
    

#==============================================================================
class __I18n(object):
   '''
   A hidden class that implements the public API of this module
   '''

   #===========================================================================
   def __init__(self, comicrack):
      ''' 
      Initializes this class. Takes the currently running ComicRack
      object as it's only argument (this must not be None.)
      '''
      
      if not comicrack:
         raise Exception("comicrack cannot be null!")
      
      self.__comicrack = comicrack
   
      # coryhigh: this will have to be fixed up!
      # make sure NONE of the defaults are empty/none
      self.__default_strings = {"Test":"Default answer to 'test'"}
      
   
   
   #===========================================================================
   def get(self, key_s):
      ''' Implements the module-level get() method '''
      
      if not key_s:
         raise Exception("cannot retrieve string for empty key")
      if key_s in self.__default_strings:
         return self.__comicrack.Localize(
            "Script.ComicVineScraper", key_s, self.__default_strings[key_s] )
      else:
         raise Exception("unrecognized i18n key: " + key_s)