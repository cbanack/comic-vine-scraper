'''
This module contains the I18n ( = "internationalization") class, which is 
used to obtain properly internationalized strings for display to the user. 

To use it, call i18n.install() to get things started.
Then, i18n.get("keystring") to obtain the internationalized string
When done, call i18n.uninstall() (this is very important)

To add new keystrings, edit the en.zip file.

@author: Cory Banack
'''
import clr
from resources import Resources

clr.AddReference("System")
from System.IO import StreamReader
from System.Text import UTF8Encoding

clr.AddReference("System.Xml.Linq")
from System.Xml.Linq import XElement

clr.AddReference("Ionic.Zip.dll") # a 3rd party dll
from Ionic.Zip import ZipFile #@UnresolvedImport

clr.AddReference('MessageBoxManager.dll') # a 3rd party dll
from System.Windows.Forms import MessageBoxManager #@UnresolvedImport


# a global variable; the singleton instance of the I18n class. will only be 
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
   if __i18n is None:
      __i18n = __I18n(comicrack)
   
      # the MessageBoxManager is a helpful little DLL that I downloaded from here:
      #    http://www.codeproject.com/KB/miscctrl/Localizing_MessageBox.aspx
      #
      # it allows me to define localized strings for the different button types in
      # a MessageBox.  it MUST be uninstalled afterwards, to change things back!
      MessageBoxManager.Register()
      MessageBoxManager.OK = get("MessageBoxOk")
      MessageBoxManager.Cancel = get("MessageBoxCancel");
      MessageBoxManager.Retry = get("MessageBoxRetry")
      MessageBoxManager.Ignore = get("MessageBoxIgnore");
      MessageBoxManager.Abort = get("MessageBoxAbort");
      MessageBoxManager.Yes = get("MessageBoxYes");
      MessageBoxManager.No = get("MessageBoxNo");
      
   
#==============================================================================
def uninstall(): 
   """
   Uninstalls this module.
   
   It is so important to make sure this method is called at the end of your 
   script, you should probably use a try-finally section to ensure it!
   """
   
   MessageBoxManager.Unregister()
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
      self.__default_strings = self.__read_defaults()
      
      
   #===========================================================================
   def __read_defaults(self):
      '''
      This method reads in the default i18n strings. It returns a dictionary 
      containing the name of each string, mapped to it's default (english) 
      value_s.  The set of all keys in the returned dictionary is the complete
      set of all valid i18n strings in this application.
      '''
           
      # parses in a file that looks like this:
      #
      # <?xml version="1.0" encoding="UTF-8"?>
      # <TR xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
      #        xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
      #        Name="Script.ComicVineScraper" CultureName="en">
      #    <Texts>
      #       <Text Key="Button1" Text="Ok" Comment="Ok"/>
      #       <Text Key="Button2" Text="Cancel" Comment="Cancel"/>
      #       ...
      #    </Texts>
      # </TR>
           
      default_strings = {}
      zip = Resources.I18N_DEFAULTS_FILE
      xml = Resources.I18N_XML_ENTRY 
      
      # grab the default (i.e. english) zip file, unzip it, and grab the
      # xml file from inside.  parse that to obtain default i18n strings.
      with ZipFile.Read(zip) as zipfile:
         entry = zipfile[xml]
         if not entry: raise Exception("can't find " + xml +" in " + zip)
         with StreamReader(entry.OpenReader(), UTF8Encoding) as stream:
            contents = stream.ReadToEnd()
         if not contents: raise Exception(xml + "is empty")

         # the following code throws all kind of exceptions if anything isn't
         # just perfect.  that's desired behaviour, so I don't catch anything.
         xelem = XElement.Parse(contents)
         entries = xelem.Element("Texts").Elements("Text") 
         for entry in entries:
            key_s = entry.Attribute("Key").Value
            key_s = key_s.strip() if key_s else key_s
            value_s = entry.Attribute("Text").Value
            value_s = value_s.strip() if value_s else value_s
            if key_s and value_s:
               default_strings[key_s] =\
                  value_s.replace("\\n", "\n").replace("\\t","\t")
               #log.debug(key_s, " ---> ", value_s)
      return default_strings   
   
   #===========================================================================
   def get(self, key_s):
      ''' Implements the module-level get() method '''
      
      if not key_s or not key_s.strip():
         raise Exception("cannot retrieve string for empty key")
      if key_s in self.__default_strings:
         return self.__comicrack.Localize(
            "Script.ComicVineScraper", key_s, self.__default_strings[key_s] )
      else:
         raise Exception("unrecognized i18n key: " + key_s)
