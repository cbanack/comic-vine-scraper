"""
This module installs a GLOBAL logging system into an application.  Any 
information that is written out using the debug(), debug_exc(), or
handle_error methods will get printed to stdout.

All information that is written to stderr or stdout (by this class, or any other
mechanism) is also saved in memory, so that it can be written out to a file in 
its entirety at any time by the dump() method.

USAGE

To make the methods in this class usable, call install().  Use a 
try-finally to GUARANTEE that uninstall() will be called when your program 
completes (with or without errors).  This is VITAL in order to ensurethat
all system resources are freed and returned to their original state!

THREAD SAFETY

This module is threadsafe while running, but is not when during install() and 
uninstall(), so care should be taken not to call any other method in this 
module while either of those two methods are running.  

Created on Feb 10, 2010
@author: cbanack
"""
#corylow: comment and cleanup this file
import sys, clr
import utils
from dbmodels import DatabaseConnectionError

clr.AddReference('System')
from System.Threading import Mutex

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import DialogResult, MessageBox, \
    MessageBoxButtons, MessageBoxIcon, SaveFileDialog

# a global variable, an instance of the Logger class that will only be
# available when this module has been "installed" ( with install() )
_logger = None

# a global variable, an instance of the main application window that we will
# attach any messageboxes that we spit out to.
_comicrack_window = None

#==============================================================================
def install(comicrack_window):
   """
   Installs this module. This must be called before any other method in 
   this module is called.
   
   Takes a single optional parameter, which is the minimum line width of the 
   code identifier tag that is prepended onto debug lines.
   """

   global _logger, _comicrack_window
   if _logger is not None or _comicrack_window is not None:
      raise Exception("don't install '" + __name__+ "' module twice")
   _comicrack_window = comicrack_window
   _logger = _Logger(comicrack_window) 



#==============================================================================
def uninstall(): 
   """
   Uninstalls this module.
   
   It is so important to make sure this method is called at the end of your 
   script, you should probably use a try-finally section to ensure it.
   """
   
   global _logger, _comicrack_window
   if _logger:
      _logger.free()
      _logger = None
   if _comicrack_window:
      _comicrack_window = None



#==============================================================================
def debug(*messages):
   """
   Writes the given single-line message to the debug log.
   
   Arguments to this method (any number of them, including none) will be 
   converted to a string, then concatenated together, and finally a newline will
   be appended on the end.   The result wil be written out to the debug log.
   
   Arguments are usually strings or numbers, but can be anything with a working
   __str__ method, or even 'None'. 
   """
   
   global _logger
   if _logger:
      _logger.debug(*messages)
   
   
   
#==============================================================================
def debug_exc(message=''):
   """
   Writes the current error stack trace (i.e. from the current thread) to the
   debug log.  This method should be only be called when that trace is current;
   i.e from within the 'except' section of a try-except block.
   
   Unlike the handle_error() method, this method will NOT display any dialog 
   or other information to the user.  Its ONLY function is to write the 
   currently caught exception out to the debug log.
   """
    
   global _logger
   if _logger:
      _logger.debug_exc(message)


   
#==============================================================================
def dump(filename):
   """
   Writes the entire contents of the debug log (since the install() method was
   called) to the given file.  This does not clear the log.
   """
   
   global _logger
   if _logger:
      _logger.dump(filename)



#==============================================================================
def handle_error(error):
   '''
   Handles the given error object (a python or .net exception) by formatting it
   nicely and then printing it to the debug log.   Then an "unexpected error"
   message is displayed for the user in a modal dialog (owned by the main
   comicrack app window that was passed into the log.install() method. )
   
   This method should be the application's normal way to handle unexpected
   errors and exceptions.
   '''
   
    
   global _logger, _comicrack_window
   if not _logger or not _comicrack_window:
      return
   
   # if none, do current python exception.  else sstr() the given exception
   if isinstance(error, Exception):
      debug("------------------- PYTHON ERROR ------------------------")
      debug_exc() # a python exception
   else:
      debug("-------------------- .NET ERROR -------------------------")
      debug(utils.sstr(error).replace('\r','')) # a .NET exception 
        
   if type(error) == DatabaseConnectionError:  
      # if this is a DatabaseConnectionError, then it is a semi-expected 
      # error that usually occurs when the database website goes down.  
      # Thus, it gets a special error message.
      MessageBox.Show(_comicrack_window,
         'The ' + error.db_name_s() + ' website could not be reached.  It is\n'+
         'possible that the website is not responding, or that\n' +
         'you are not connected to the internet.\n\n' +
         'Please try again later.', "Cannot Access Comic Database",
         MessageBoxButtons.OK, MessageBoxIcon.Warning)
      
   else:
      # all other errors are considered "unexpected", and handled generically
      result = MessageBox.Show(_comicrack_window, 
         'An unexpected error occurred.  Would you like to save\n' +
         'a log file with more details about this problem?', 
         "Unexpected Error",  MessageBoxButtons.YesNo, MessageBoxIcon.Error)
   
      if result == DialogResult.Yes:
         dialog = SaveFileDialog()
         dialog.Title = 'Save Log File'
         dialog.Filter = 'All Files (*.*)|*.*'
   
         try:
            if dialog.ShowDialog() == DialogResult.OK:
               dump(dialog.FileName)
               MessageBox.Show(_comicrack_window,\
              'A log file for this error has been saved.  Please consider\n'+
              "reporting this incident (and submitting the log) to the\n" + 
              "issue tracker on the main Comic Vine Scraper website.",
              'Saved Log File',\
              MessageBoxButtons.OK, MessageBoxIcon.Information)
         except:
            debug_exc()
            MessageBox.Show(_comicrack_window, "Error saving debug log.")



#==============================================================================
class _Logger(object):
   """ A hidden class that implements the public api of this module. """ 


   #==========================================================================
   def __init__(self, comicrack_window):
      """ 
      Initializes this class.  Only one may be initialized at a time!
      
      comicrack_window => All writing to stdout will occur on the comicrack
         windows event pump thread (i.e. invoked via a delegate).
         This is needed because comicrack has a gui implementation of stdout
         that we want to be properly in sync with.   
      """ 
   
      if ( sys.stdout != sys.__stdout__ or sys.stderr != sys.__stderr__):
         raise "do not instantiate two instances of this class!!"
      
      # the comicrack window whose gui stdout we will write debug messages to
      self._comicrack_window = comicrack_window
      
      # the log of all debugged output that this class creates
      self._logLines = []
      
      # a mutex that protects all access to the logLines (above)
      self._mutex = Mutex()
      
      sys.stdout = self 
      sys.stderr = self
      


   
   #==========================================================================
   def free(self):
      """ Frees up all resources owned or co-opted by this class """
      
      # protect access to the logLines by using the mutex.
      self._mutex.WaitOne(0)
      try:
         self._logLines = None
         self._comicrack_window = None
      
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
      self._debugRaw( ''.join(strings) )
   
   
   #==========================================================================
   def _debugRaw(self, message=''):
      """ Records the given message, and writes it out to the -real- stdout. """
         
      # protect access to the logLines with a mutex (for multiple threads)
      self._mutex.WaitOne(0)
      try:
         if self._logLines == None:
            raise Exception("you must install the _Logger before using it")
         
         try:
            output_line = utils.sstr(message)
         except:
            # shouldn't happen!
            output_line = "***** LOGGING ERROR *****"
             
         self._logLines.append( output_line )
         
         # invoking this on the application thread for the comicrack window
         # can help prevent deadlock when running comicrack's debug window...
         # but it might also be causing other deadlocking problems...
         def delegate():
            sys.__stdout__.write(output_line)
         utils.invoke(self._comicrack_window, delegate, False)
      finally:
         self._mutex.ReleaseMutex()


    
   #==========================================================================
   def debug_exc(self, message):
      if not (message is None) and len(message.strip()) > 0:
         self.debug(message)
         
      """ Implements the module-level debug_exc() method. """
      try:
         self.debug(''.join(['Caught ', sys.exc_info()[0].__name__, ': ',
            utils.sstr(sys.exc_info()[1])]))
      except:
         self.debug(": Exception name couldn't be formatted :")
      
      try:
         self.debug("Traceback (most recent call last):")
         for line in self._getCurrentStackTrace():
            self.debug(self._formatTraceLine(line))
      except:
         self.debug(": Traceback couldn't be formatted :")


   #==========================================================================
   def _getCurrentStackTrace(self):
      """ 
      Retrieves the current stacktrace, as a list of triples: 
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
   def _formatTraceLine(self, lineInfo):
      """ Formats the triples from _getCurrentStackTrace() into a nice line. """  
      fileName, lineNo, name = lineInfo
      line = '  File "%s", line %s, in %s' % (fileName, lineNo, name)
      return line


   
   #==========================================================================
   def dump(self, filename):
      """ Implements the module-level dump() method. """
      
      # protect access to the logLines with a mutex (for multiple threads)
      self._mutex.WaitOne(0)
      try:
         if self._logLines == None:
            raise Exception("you must install the _Logger before using it")
         
         # corylow: switch this to use .NET and utf8
         with file(filename, "w") as f:
            for line in self._logLines:
               f.write(line)
      finally:
         self._mutex.ReleaseMutex()
      
      
            
   #==========================================================================
   def write (self, obj):
      """ 
      This method exists in order to make this class into a 'file-like'
      object, which can be used to directly co-opt stdout and stderr.
      """
      
      self._debugRaw(obj)
