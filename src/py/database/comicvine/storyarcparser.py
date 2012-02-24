'''
This module contains functions for extracting and parsing a story arc out of 
comic book titles. ("The God in the Bowl, Part 3" -> "The God in the Bowl")

Created on Feb 2, 2012
@author: cbanack
'''

from distutils.log import Log
from utils import sstr
import log
import re
import utils
 
# coryhigh: init and shutdown must be called
# we need a mechanism to limit the size of arcmap (arcmap["size"]?)
# this class must be cleaned up
__arcmap = None
 
#==============================================================================
def init():
   '''  
   Initializes the storyarcparser.  Should be called once before it this module
   is used.   Call 'shutdown' when finished to free up resources.
   '''
   global __arcmap
   __arcmap = {}  # coryhigh: make methods blow up if not called
   pass


#==============================================================================
def shutdown():
   '''
   Frees up resources held by this storyarcparser.   Call this just when the
   parser is no longer needed.  If it is needed again in the future, call
   'init' before using it again.
   '''
   global __arcmap
   __arcmap = None
   pass

 
#==============================================================================
def prime(issuerefs, return_arcs = False ):
   ''' coryhigh: comment '''
   
   # 1. start by replacing the list of issue refs with a sorted list
   #    sort by issue num (then natural ordering), in ascending order
   def cmp_val(x,y):
      sx,sy = x.issue_num_s,y.issue_num_s
      if utils.is_number(sx) and utils.is_number(sy):
         diff = float(sx)-float(sy)
         return diff if diff != 0 else x.__cmp__(y)  
      else:
         return 1 if utils.is_number(sx) else 0 if utils.is_number(sy) \
         else x.__cmp__(y)
   issuerefs = sorted(issuerefs, cmp_val )
   
   # 2. create a map of list indexes to valid arc names
   arcmap = {}
   for i in xrange(len(issuerefs)):
      arc_s = _extract(issuerefs[i].title_s, i == len(issuerefs)-1)
      if arc_s:
         arcmap[i] = arc_s
   
   # 3. find at least one other nearby issue that starts with each arc name,
   #    otherwise it's not an arc name at all.
   def at_least_two(i, arcname):
      retval = False
      if i == len(issuerefs)-1:
         retval = True
      else:
         arcname = arcname.lower()
         for j in xrange(max(0,i-5),min(i+5,len(issuerefs))):
            title_s = issuerefs[j].title_s.lower().lstrip("'\" ")
            if title_s.startswith(arcname) and j != i: 
               # coryhigh: maybe a trick here where we check remainder size?
               retval = True
               break;
      return retval
      
   arcs_sl = sorted([arcmap[i] for i in arcmap if at_least_two(i, arcmap[i])])
   for arc_s in arcs_sl:
      __save_arc(arc_s)
      
   return arcs_sl if return_arcs else None

 
#==============================================================================
def __search_arcs(candidate_s):
   global __arcmap
   
   matching_arc = ""
   candidate_s = candidate_s.lower().strip()
   if len(candidate_s) > 0:
      key = candidate_s[0]
      if key in __arcmap:
         arcset = __arcmap[key]
         for arc in arcset:
            if candidate_s.startswith(arc.lower()) and \
                  len(matching_arc) < len(arc):
               matching_arc = arc
   return matching_arc      


#==============================================================================
def __save_arc(arc_s):
   global __arcmap
   arc_s = arc_s.strip()
   if len(arc_s) > 0 and not __search_arcs(arc_s):
      key = arc_s.lower()[0]
      if not key in __arcmap:
         __arcmap[key] = set()
      arcset = __arcmap[key]
      arcset.add(arc_s)
      

 
#==============================================================================
def extract( title_s ):
   '''
   Takes the title of a comic book, and extracts the storyarc name out of it
   if possible.  Returns the storyarc name (a string) or "" if one could not
   be found.
   ''' 
   global __arcmap
   return __search_arcs(title_s)

#==============================================================================
def _extract( title_s, strict = True ):
   '''
   Takes the title of a comic book, and extracts the storyarc name out of it
   if (and ONLY IF) it is recognizable as part one of a story arc.  
   Returns the storyarc name (a string) or "" if one could not
   be found.
   ''' 
   
   title_s = title_s.strip()  
   pattern = r'''                 
      (?xi)^                              # The Grey: Part 1 (of 3) "Alpha"   
      (.{3,}?)                            # [The Grey]: Part 1 (of 3) "Alpha"
      [-, :([]+                           # The Grey[: ]Part 1 (of 3) "Alpha"
      
      (part|pt|pt\.|no\.|number           # The Grey: [Part ]1 (of 3) "Alpha"
      |\#|num|num\.|episode|ep
      |ep\.|vol\.|vol|volume|ch
      |ch.|chapter|book|bk\.|bk)STRICT\s*
      
      (1|i|one)\s*                        # The Grey: Part [1 ](of 3) "Alpha"
      [[(]?\s*                            # The Grey: Part 1 [(]of 3) "Alpha"
      ((of|\\|/)\s*(\d+|\w{3,}))?\s*      # The Grey: Part 1 ([of 3]) "Alpha"
      []) ]*\s*                           # The Grey: Part 1 (of 3[) ]"Alpha"
      ([-[:,;'"({]+\s*.{2,})?             # The Grey: Part 1 (of 3) ["Alpha"]    
      $'''
   # allows or ban "The Grey 1", or "The Grey I", or "The Grey, One"
   pattern = re.sub("STRICT", "" if strict else "?", pattern)
      
      
   match = re.match(pattern, title_s )
   if match:
      arcname = match.group(1).strip()
      match = re.match("^['\"](.*?)['\"]$", arcname)
      if match:
         arcname = match.group(1).strip()
   else:
      arcname = ""
   return arcname
