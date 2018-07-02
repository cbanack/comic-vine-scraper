"""
This module installs a GLOBAL logging system into an application.  Any 
information that is written out using the debug(), debug_exc(), or
handle_error methods will get printed to stdout.

Once installed, this module also logs all text that is written to stderr or 
stdout (by this module, or any other mechanism).  This text can be written out 
to a file in its entirety at any time by the save() method.

USAGE

To make the methods in this class usable, call install().  Use a 
try-finally to GUARANTEE that uninstall() will be called when your program 
completes (with or without errors).  This is VITAL in order to ensurethat
all system resources are freed and returned to their original state!

THREAD SAFETY

This module is threadsafe while running, but is not during install() and 
uninstall(), so care should be taken not to call any other method in this 
module while either of those two methods are running.  

@author: Cory Banack
"""

import sys
import clr
import utils
import i18n
from dberrors import DatabaseConnectionError

clr.AddReference('System')
from System.Threading import Mutex
from System import DateTime

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import DialogResult, MessageBox, \
    MessageBoxButtons, MessageBoxIcon, SaveFileDialog
    
from System.IO import FileInfo, StreamWriter
from System.Text import UTF8Encoding 

# a module global variable; an instance of the Logger class that will only be
# available when this module has been "installed" ( with install() )
__logger = None

# a module global variable; an instance of the main application window that we 
# will attach any messageboxes that we spit out to.
__app_window = None

#==============================================================================
def install(app_window=None):
   """
   Installs this module. This must be called before any other method in 
   this module is called.  You must take steps to GUARANTEE that this module's
   uninstall() method is called once you have called this method.
   
   Takes a single parameter, which is the Form/Window object that all error 
   dialogs should be attached to.  This parameter may be None, but if it is the
   'handle_error' method will not show any visible dialogs.
   """

   global __logger, __app_window
   if __logger is not None or __app_window is not None:
      raise Exception("don't install '" + __name__+ "' module twice!")
   __app_window = app_window
   __logger = __Logger() 



#==============================================================================
def uninstall(): 
   """
   Uninstalls this module.
   
   It is important to make sure this method is called at the end of your 
   script, so you should use a try-finally section to ensure it.
   """
   
   global __logger, __app_window
   if __logger:
      __logger.free()
      __logger = None
   if __app_window:
      __app_window = None



#==============================================================================
def debug(*messages):
   """
   Writes the given single-line message to the debug log.
   
   Arguments to this method (any number of them, including none) will be 
   converted to a string, then concatenated together, and finally a newline will
   be appended on the end.   The result will be written out to the debug log.
   
   Arguments are usually strings or numbers, but can be anything with a working
   __str__ method, or even 'None'. 
   """
   
   global __logger
   if __logger:
      __logger.debug(*messages)
   
   
   
#==============================================================================
def debug_exc(message=''):
   """
   Writes the python error stack trace (i.e. from the current thread) to the
   debug log.  This method should be only be called when that trace is current;
   i.e from within the 'except' section of a try-except block.
   
   Unlike the handle_error() method, this method will NOT display any dialog 
   or other information to the user.  Its ONLY function is to write the 
   currently caught exception out to the debug log.
   """
    
   global __logger
   if __logger:
      __logger.debug_exc(message)




#==============================================================================
def handle_error(error):
   '''
   Handles the given error object (a python or .net exception) by formatting it
   nicely and then printing it to the debug log.   If the 'app_window' provided
   to the 'install' method was not None, an "unexpected error" message 
   will also be displayed for the user in a modal dialog owned by the
   app_window.
   
   This method should be an application's normal way to handle unexpected
   errors and exceptions.
   '''
   
    
   global __logger, __app_window
   if not __logger:
      return
   
   # if none, do current python exception.  else sstr() the given exception
   if isinstance(error, Exception):
      debug("------------------- PYTHON ERROR ------------------------")
      debug_exc() # a python exception
   else:
      debug("-------------------- .NET ERROR -------------------------")
      debug(utils.sstr(error).replace('\r','')) # a .NET exception 
   
   
   if __app_window:     
      handled = False
      if type(error) == DatabaseConnectionError:  
         # if this is a DatabaseConnectionError, then it is a semi-expected 
         # error that may get a special error message
         if error.get_error_code_s() == "100": # coryhigh: i18n
            MessageBox.Show(__app_window,  # invalid api key
               i18n.get("LogDBErrorApiKeyText").format(error.get_db_name_s()), 
               i18n.get("LogDBErrorTitle"), MessageBoxButtons.OK, 
               MessageBoxIcon.Warning)
            handled = True
         elif error.get_error_code_s() == "107":
            MessageBox.Show(__app_window,  # rate limit reached
               i18n.get("LogDBErrorRateText").format(error.get_db_name_s()), 
               i18n.get("LogDBErrorTitle"), MessageBoxButtons.OK, 
               MessageBoxIcon.Warning)
            handled = True
         elif error.get_error_code_s() == "0":
            MessageBox.Show(__app_window,  # generic 
               i18n.get("LogDBErrorText").format(error.get_db_name_s()), 
               i18n.get("LogDBErrorTitle"), MessageBoxButtons.OK, 
               MessageBoxIcon.Warning)
            handled = True
         
      if not handled:
         # all other errors are considered "unexpected", and handled generically
         result = MessageBox.Show(__app_window, i18n.get("LogErrorText"),
            i18n.get("LogErrorTitle"),  MessageBoxButtons.YesNo, 
            MessageBoxIcon.Error)
      
         if result == DialogResult.Yes:
            save(True)



#==============================================================================
def save(show_error_message=False):
   """
   Asks for the user to specify a file, and then writes the entire contents of 
   the debug log (since the install() method was called) to the given file.  
   This does not clear the log.
   """
   
   global __logger, __app_window
   if not __logger or not __app_window:
      return
   
   def dosave():
      dialog = SaveFileDialog()
      dialog.FileName="cvs-debug-log-" + \
         DateTime.Today.ToString("yyyy-MM-dd") + ".txt"
      dialog.Title = i18n.get("LogSaveTitle")
      dialog.Filter = i18n.get("LogSaveFilter")+'|*.*'
   
      try:
         if dialog.ShowDialog(__app_window) == DialogResult.OK:
            if dialog.FileName != None:
               debug("wrote debug logfile: ", FileInfo(dialog.FileName).Name)
               __logger.save(dialog.FileName)
               if show_error_message:
                  MessageBox.Show(__app_window, i18n.get("LogSavedText"),
                     i18n.get("LogSavedTitle"), MessageBoxButtons.OK, 
                     MessageBoxIcon.Information )
      except:
         debug_exc()
         MessageBox.Show( __app_window, i18n.get("LogSaveFailedText") )
   
   if __app_window.InvokeRequired:
      # fixes a bug where this doesn't work if you manually invoke from
      # the comciform.   
      utils.invoke(__app_window, dosave, False)
   else:
      dosave()


#==============================================================================
class __Logger(object):
   """ A hidden class that implements the public api of this module. """ 


   #==========================================================================
   def __init__(self):
      """ 
      Initializes this class.  Only one may be initialized at a time!
      """ 
   
      if ( sys.stdout != sys.__stdout__ or sys.stderr != sys.__stderr__):
         raise "do not instantiate two instances of this class!!"
      
      # the log of all debugged output that this class creates
      self._loglines = []
      
      # a mutex that protects all access to the logLines (above)
      self._mutex = Mutex()
      
      # co-op stdout and stderr so we can intercept everything going to them
      sys.stdout = self 
      sys.stderr = self
      


   
   #==========================================================================
   def free(self):
      """ Frees up all resources owned or co-opted by this class """
      
      # protect access to the logLines by using the mutex.
      self._mutex.WaitOne(-1)
      try:
         self._loglines = None
         self.__app_window = None
      
         # return stdout and stderr to their original state
         sys.stdout = sys.__stdout__
         sys.stderr = sys.__stderr__
      finally:
         self._mutex.ReleaseMutex()
         
      # not perfectly threadsafe, but close enough since this method is only
      # really called when the app is completely finished running anyhow
      self._mutex.Dispose() 
      

    
   #==========================================================================
   def debug(self, *messages):
      """ Implements the module-level debug() method """
      
      strings = map(utils.sstr,messages)
      strings.append('\n')
      self.__debug_raw( ''.join(strings) )
 
 
   #==========================================================================
   def debug_exc(self, message):
      """ Implements the module-level debug_exc() method. """
      
      if not (message is None) and len(message.strip()) > 0:
         self.debug(message)
         
      try:
         self.debug(''.join(['Caught ', sys.exc_info()[0].__name__, ': ',
            utils.sstr(sys.exc_info()[1])]))
      except:
         self.debug(": Exception name couldn't be formatted :")
      
      try:
         self.debug("Traceback (most recent call last):")
         for line in self.__get_trace():
            self.debug(self.__format_trace_line(line))
      except:
         self.debug(": Traceback couldn't be formatted :")
         
      self.debug()

  
   
   #==========================================================================
   def __debug_raw(self, message=''):
      """ Records the given message, and writes it out to the 'real' stdout. """
         
      # protect access to the logLines with a mutex (for multiple threads)
      self._mutex.WaitOne(-1)
      try:
         if self._loglines == None:
            raise Exception("you must install the __Logger before using it")
         
         try:
            output_line = utils.sstr(message)
         except:
            # shouldn't happen!
            output_line = "***** LOGGING ERROR *****"
             
         self._loglines.append( output_line )
         sys.__stdout__.write(output_line)
      finally:
         self._mutex.ReleaseMutex()



   #==========================================================================
   def __get_trace(self):
      """ 
      Retrieves the current thread's python stacktrace, as a list of triples: 
                (filename, lineno, codename) 
      """
      
      traceback = sys.exc_info()[2]
      stackTrace = []
      while traceback is not None:
         frame = traceback.tb_frame
         lineno = traceback.tb_lineno
         code = frame.f_code
         filename = code.co_filename
         name = code.co_name
         stackTrace.append((filename, lineno, name))
         traceback = traceback.tb_next
      return stackTrace



   #==========================================================================
   def __format_trace_line(self, lineInfo):
      """
      Formats the triples from __get_trace() into a nice line. 
      """  
      fileName, lineNo, name = lineInfo
      line = '  File "%s", line %s, in %s' % (fileName, lineNo, name)
      return line


   
   #==========================================================================
   def save(self, filename):
      """ Implements the module-level save() method by writing the 
          debug log information to the given file. """
      
      # protect access to the logLines with a mutex (for multiple threads)
      self._mutex.WaitOne(-1)
      try:
         if self._loglines == None:
            raise Exception("you must install the __Logger before using it")
         loglines_copy = list(self._loglines)
      finally:
         self._mutex.ReleaseMutex()
         
      try:
         writer = StreamWriter(filename, False, UTF8Encoding())
         for line in loglines_copy:
            writer.Write(line)
      finally:
         if writer: writer.Dispose()
      
      
            
   #==========================================================================
   def write (self, obj):
      """ 
      This method exists in order to make this class into a 'file-like'
      object, which can be used to directly co-opt stdout and stderr.
      """
      
      self.__debug_raw(obj)
