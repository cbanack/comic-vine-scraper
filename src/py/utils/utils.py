'''
This module contains a variety of generally useful utility methods.

@author: Cory Banack
'''

import clr
import log
from time import strftime
import re
import sys

clr.AddReference('System')
from System.IO import File, StreamReader, StreamWriter, StringWriter
from System.Text import Encoding
from System.Net import WebRequest

clr.AddReference('System.Drawing')
from System.Drawing import Graphics, Bitmap

clr.AddReference('System.Web')
from System.Web import HttpUtility

clr.AddReference('IronPython')
from IronPython.Compiler import CallTarget0 


#==============================================================================
def is_string(object):
   ''' returns a boolean indicating whether the given object is a string '''
   
   if object is None:
      return False
   return isinstance(object, basestring)


#==============================================================================
def is_number(s):
   ''' returns a boolean indicating whether the given object is a number, or
       a string that can be converted to a number. '''
   try:
      float(s)
      return True
   except:
      return False


#==============================================================================
def sstr(object):
   ''' safely converts the given object into a string (sstr = safestr) '''
   if object is None:
      return '<None>'
   if is_string(object):
      # this is needed, because str() breaks on some strings that have unicode
      # characters, due to a python bug.  (all strings in python are unicode.)
      return object 
   return str(object)


# ==========================================================================
def invoke(control, delegate, synchronous = True): 
   '''
   Invokes the given delegate (method) on the given control/form's 
   GUI thread.  If the control doesn't have access to a working window 
   handle, usually because the Form it is in was disposed) then do nothing.
   
   The 'synchronous' parameter determines whether or not this method blocks 
   while the given delegate is run.  True means block, false means don't.
   '''
   if not control or not delegate:
      raise TypeError("null parameter not allowed!")
   
   if True or control.IsHandleCreated and \
         not control.IsDisposed and not control.Disposing:

      try:
         if synchronous:
            # allow thrown exceptions to bubble up
            if control.InvokeRequired:
               control.Invoke(CallTarget0(delegate))
            else:
               delegate()
         else:
            control.BeginInvoke(CallTarget0(delegate))
      except: 
         if sys.exc_info()[0].__name__ == "SystemError" and \
               sstr(sys.exc_info()[1]).find("handle") != -1:
            # deliberately ignore this exception, its unavoidably possible
            # since we might invoke on a control via a thread that doesn't
            # own that control's handle--the handle can dissappear at any time
            #
            # see issue 147 for an example of this happening:
            #
            # "SystemError: Invoke or BeginInvoke cannot be called on a control 
            #  until the window handle has been created."
            pass 
         else:
            # any other exceptions should be raised and reported as usual
            raise
            
            
#==============================================================================
def convert_roman_numerals(num_s):
   '''
   Converts the given string into an positive or negative integer value, 
   throwing an exception if it can't.  The given string can be a integer value
   in regular arabic form (1, 2, 3,...) or roman form (i, ii, iii, iv,...).
   The returned value will be an integer.
   
   Note that roman numerals outside the range [-20, 20] and 0 are not supported.
   '''
   
   roman_mapping = {'i':1, 'ii':2,'iii':3,'iv':4,'v':5,'vi':6,'vii':7,'viii':8,
                    'ix':9,'x':10,'xi':11,'xii':12,'xiii':13,'xiv':14,'xv':15,
                    'xvi':16,'xvii':17,'xviii':18,'xix':19,'xx':20}
   
   num_s = num_s.replace(' ', '').strip().lower();
   negative = num_s.startswith('-')
   if negative:
      num_s = num_s[1:]
   
   retval = None
   try:
      retval = int(num_s)
   except:
      retval = roman_mapping[num_s]
   
   return retval * -1 if negative else retval


#==============================================================================
def convert_number_words(phrase_s, expand_b):
   """
   Converts all of the number words (as defined by regular expression 'words')
   in the given phrase, either expanding or contracting them as specified.
   When expanding, words like '1' and '2nd' will be transformed into 'one'
   and 'second' in the returned string.   When contracting, the transformation
   goes in reverse.
   
   This method only works for numbers up to 20, and it only works properly
   on lower case strings. 
   """
   number_map = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three',\
      '4': 'four', '5': 'five', '6': 'six','7': 'seven', '8': 'eight',\
      '9': 'nine', '10': 'ten', '11': 'eleven', '12': 'twelve',\
      '13': 'thirteen', '14': 'fourteen', '15': 'fifteen',\
      '16': 'sixteen', '17': 'seventeen', '18': 'eighteen', '19': 'nineteen',\
      '20': 'twenty', '0th': 'zeroth', '1rst': 'first', '2nd': 'second',\
      '3rd': 'third', '4th': 'fourth', '5th': 'fifth', '6th': 'sixth',\
      '7th': 'seventh', '8th': 'eighth', '9th': 'ninth', '10th': 'tenth',\
      '11th': 'eleventh', '12th': 'twelveth', '13th': 'thirteenth',\
      '14th': 'fourteenth', '15th': 'fifteenth', '16th': 'sixteenth',\
      '17th': 'seventeenth', '18th': 'eighteenth', '19th': 'nineteenth',\
      '20th': 'twentieth'}

   b = r'\b'
   if expand_b:
      for (x,y) in number_map.iteritems():
         phrase_s = re.sub(b+x+b, y, phrase_s);
      phrase_s = re.sub(r'\b1st\b', 'first', phrase_s);
   else:
      for (x,y) in number_map.iteritems():
         phrase_s = re.sub(b+y+b, x, phrase_s);
      phrase_s = re.sub(r'\btwelfth\b', '12th', phrase_s);
      phrase_s = re.sub(r'\beightteenth\b', '18th', phrase_s);
   return phrase_s


#==============================================================================
def persist_map(map, file):
   """
   Writes the given map of strings-to-values into a file, by converting all of 
   its values into strings.  Any key value pair that contains the ':' 
   character will not be written out.  All other contents that were in the 
   given file will be destroyed. 
   """
   
   try:
      with StreamWriter(file, False, Encoding.UTF8) as sw:
         sw.Write(":: This file was generated on "\
            + strftime(r'%Y.%m.%d %X') + "\n\n")
         keys = map.keys()
         keys.sort()
         for key in keys:
            value = sstr(map[key]).strip()
            key = sstr(key).strip()
            if ':' in key or ':' in value:
               log.debug("WARNING: can't write map entry containing ':'; ",
                         key, " -> ", value)
            else:
               sw.Write(key + ' : ' + value + "\n")
   except:
      log.debug_exc("problem saving mapfile: " + sstr(file)) 
         
         
#==============================================================================
def load_map(file):
   """
   Reads a map out of the given file, which was created with the persist_map
   function.  All keys in the returned map will be strings, but the values will
   be converted to integers, booleans and floats where possible.
   
   If this given file doesn't exist, this method returns an empty map.
   """
   retval = {}
   try:
      if File.Exists(file): 
         with StreamReader(file, Encoding.UTF8, False) as sr:
            line = sr.ReadLine()
            while line is not None:
               pair = line.strip().split(':') 
               if len(pair) == 2:
                  key = pair[0].strip()
                  value = pair[1].strip()
                  if value.lower() == "false":
                     value = False
                  elif value.lower() == "true":
                     value = True 
                  else: 
                     try: 
                        if '.' in value: value = float(value)
                        else: value = int(value)
                     except:
                        pass
                  retval[key] = value
               line = sr.ReadLine()
   except:
      log.debug_exc("problem loading mapfile " + sstr(file))
      retval = {}
   return retval


#==============================================================================
def strip_back_cover(image):
   """
   Checks the given image to see if it has the pixel ratio of 2 comic book pages
   side by side.  If it does NOT, then this method does nothing and the given 
   image is returned without modification.
   
   But if it does have that magic pixel ratio, then we assume that the 2 pages
   are the front and back covers of a comic book (on the right and left halves 
   of the image, respectively) and we create and return a NEW image that 
   contains only the front cover (right half) of the original.
   
   If a new image is returned, this method will call Dispose on the original.
   """
   if image:
      pixel_ratio = float(image.Width)/float(image.Height)
      if pixel_ratio < 1.5 and pixel_ratio > 1.2:
         # create a new image with the back cover (left half) deleted
         new_image = Bitmap(image.Width/2, image.Height)
         graphics = Graphics.FromImage(new_image)
         graphics.DrawImage(image, -image.Width/2, 0)
         graphics.Dispose()
         image.Dispose();
         image = new_image
          
   return image


#==============================================================================
def get_html_string(url):
   '''
   This method takes a url (string) of a webpage, and connects to the URL,
   then downloads, htmldecodes, and returns the contents of that page as 
   an html string.
   
   This method will throw an exception if anything goes wrong.
   '''
   
   try:
      request = WebRequest.Create(url) 
      response = request.GetResponse()
      responseStream = response.GetResponseStream()
      reader = StreamReader(responseStream, Encoding.UTF8)
      page = reader.ReadToEnd()
      with StringWriter() as writer: 
         HttpUtility.HtmlDecode(page, writer)
         page = writer.ToString()
      return page
   finally:
      if 'reader' in vars(): reader.Close()
      if 'responseStream' in vars(): responseStream.Close()
      if 'response' in vars(): response.Close()
