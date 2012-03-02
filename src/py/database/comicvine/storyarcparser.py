'''
This module contains functions for extracting and parsing a story arc out of 
comic book titles. ("The God in the Bowl, Part 3" -> "The God in the Bowl").

Since finding story arcs requires comparing multiple issues, it is a two step
process.  First, call 'prime' with all of the IssueRefs for a series.  Then 
call 'extract' on any of the individual IssueRef titles to see if it has an
identifiable story arc. 

Created on Feb 2, 2012
@author: cbanack
'''

import log
import re
import utils

# the primed arcs; maps single characters (lower case) to sets of primed (known)
# arc names.  we try to match up issue titles with primed arc names. 
__arcmap = None
 
#==============================================================================
def initialize():
   '''  
   Initializes the storyarcparser.  Should be called once before it this module
   is used.   Call 'shutdown' when finished to free up resources.
   '''
   global __arcmap
   __arcmap = {"size":0}


#==============================================================================
def shutdown():
   '''
   Frees up resources held by this storyarcparser.   Call this just when the
   parser is no longer needed.  If it is needed again in the future, call
   'init' before using it again.
   '''
   global __arcmap
   __arcmap = None

 
#==============================================================================
def prime(issuerefs, return_arcs = False ):
   ''' 
   Primes the storyarcparseer module by having it find and store all of the 
   with all of the arcs in the given collection of issuerefs.  The collection 
   of arcs will be retained (also returned, if 'return_arcs' is true) so that
   future calls to 'extract' can make use of them.
   
   Every time this method is called, all previously primed story arcs are lost.
   '''
   
   if __arcmap == None:
      raise Exception(__name__ + " module is not initialized!")
   
   # 1. strip out issuerefs with empty titles, as well as ones that have 
   #    the same title as one that already exists (i.e. remove duplicates)
   issuerefs = {x.title_s:x for x in issuerefs if x.title_s.strip()}.values()
   
   # 2. sort the issuerefs by ascending issue_num, then natural ordering
   def cmp_val(x,y):
      sx,sy = x.issue_num_s,y.issue_num_s
      if utils.is_number(sx) and utils.is_number(sy):
         diff = float(sx)-float(sy)
         return diff if diff != 0 else x.__cmp__(y)  
      else:
         return 1 if utils.is_number(sx) else 0 if utils.is_number(sy) \
         else x.__cmp__(y)
   issuerefs = sorted(issuerefs, cmp_val )
   
   # 3. create a map of list indexes to valid STRICT arc names
   strictmap = {}
   for i in xrange(len(issuerefs)):
      arc_s = _ex_strict(issuerefs[i].title_s)
      if arc_s:
         strictmap[i] = arc_s
   
   # 4. find at least one other nearby issue that starts with each arc name,
   #    otherwise it's not an arc name at all.
   def at_least_two(i, arcname_s):
      for j in xrange(max(0,i-25),min(i+25,len(issuerefs))):
         if i != j and __title_matches_arc_b(issuerefs[j].title_s, arcname_s): 
            return True
      return False
      
   arcs_sl = [strictmap[i] for i in strictmap 
        if at_least_two(i, strictmap[i])]
   log.debug()   
   log.debug("================= FOUND ARCS =================") # coryhigh:delete
   initialize() # this resets the __arcmap after each priming
   # add each found arc to the list; retain those that weren't already there
   arcs_sl = [ x for x in arcs_sl if __save_primed_arc(x) ]
   log.debug("============================================") # coryhigh:delete
   
   return arcs_sl if return_arcs else None

 
#==============================================================================
def __search_primed_arcs(title_s):
   '''
   This method searches through our current collection of primed arc names, to
   decide if the given candidate title matches one of them.  If it does, the 
   arc name (string) is returned, otherwise, and empty string is returned.
   '''
   global __arcmap
   
   matching_arc = ""  # return value
   title_s = title_s.lower().lstrip("'\" ").strip() if title_s else ""
   
   # see if the first letter of the candidate title is in the __arcmap.  if it
   # is, search the set that the letter maps to for an arcname that matches the
   # candidate title. the map contains no entries for first letters that don't
   # map to any arc names.
   if len(title_s) > 0 and title_s[0] in __arcmap:
      for arc_s in __arcmap[title_s[0]]:
         if __title_matches_arc_b(title_s, arc_s) \
               and len(matching_arc) < len(arc_s):
            matching_arc = arc_s
   return matching_arc      



#==============================================================================
def __save_primed_arc(arc_s):
   '''
   This adds the given arc name to our stored collection of primed arc names.
   This is temporary, eventually the cache of arc names is flushed.
   Returns false if the arc was already in this list, true if it was a new one.
   '''
   global __arcmap
   newarc = False
   arc_s = arc_s.strip("'\" ") if arc_s else ""
   if len(arc_s) > 0 and not __search_primed_arcs(arc_s):
      key = arc_s.lower()[0]
      if not key in __arcmap:
         __arcmap[key] = set()
      arcset = __arcmap[key]
      if not arc_s in arcset:
         arcset.add(arc_s)
         __arcmap["size"] = __arcmap["size"] + 1
         newarc = True
         log.debug(arc_s, ": ", __arcmap["size"]) # coryhigh: delete
   return newarc

 
#==============================================================================
def __title_matches_arc_b(title_s, arc_s):
   '''
   Checks to see if the given title matches the given arc name, which
   roughly means the title 'starts with' the arc name.
   '''

   # strip out punctuation and extra spaces that could confound our comparison 
   space = r"[-:;,.!]"
   nothing = r"[`'\"]"
   andd = r"\s\&\s"
   arc_s = re.sub(andd,' and ',arc_s, 99)
   arc_s = re.sub(space,' ',arc_s, 99)
   arc_s = re.sub(nothing,'',arc_s, 99)
   arc_s = re.sub(" {2,}",' ', arc_s, 99).lower().strip();   
   title_s = re.sub(andd,' and ', title_s, 99)
   title_s = re.sub(space,' ', title_s, 99)
   title_s = re.sub(nothing,'', title_s, 99)
   title_s = re.sub(" {2,}",' ', title_s, 99).lower().strip();   
   
   if title_s.startswith(arc_s):
      # looks like a match, but check the unmatched second part of the 
      # title (the ending) to be SURE that its a match.
      ending = title_s[len(arc_s):].lstrip("'\" ").strip()
      pattern = r'''                 
         (?xi)\#|(\b(part|pt|no|number|num|ep|episode|
         volume|vol|ch|chapter|book|bk|prelude|prolog|prologue|
         intro|introduction|begin|beginning|begins|end|ending|ends|
         final|finale|finally|conclusion|epilog|epilogue|start|after|
         last|first)s?\b)'''
      return len(ending.strip()) == 0 or re.search(pattern, ending);       

 
#==============================================================================
def extract( title_s ):
   '''
   Takes the title of a comic book, and extracts the storyarc name out of it
   if possible.  Returns the storyarc name (a string) or "" if one could not
   be found.  To use this method, you MUST first prime the list of story arc
   names by calling prime() with all the IssueRefs in the comic book's series.
   ''' 
   
   if __arcmap == None:
      raise Exception(__name__ + " module is not initialized!")
   
   return __search_primed_arcs(title_s)


#==============================================================================
def _ex_strict( title_s ):
   '''
   Takes the title of a comic book, and extracts the storyarc name out of it
   strictly, that is if (and ONLY IF) it is directly recognizable as "part one"
   of a story arc. Returns the storyarc name (a string) or "" if one could not
   be found.
   ''' 
   title_s = title_s.strip()  
   pattern = r'''                 
      (?xi)^                              # The Grey: Part 1 (of 3) "Alpha"   
      (.{3,}?)                            # [The Grey]: Part 1 (of 3) "Alpha"
      [-, :([]+                           # The Grey[: ]Part 1 (of 3) "Alpha"
      
      (part|pt|no|number|                 # The Grey: [Part ]1 (of 3) "Alpha"
      \#|num|episode|ep|vol|volume|
      ch|chapter|book|bk)s?\.?\s*
      
      (?P<num>1|2|i|ii|one|two)\s*        # The Grey: Part [1 ](of 3) "Alpha"
      [[(]?\s*                            # The Grey: Part 1 [(]of 3) "Alpha"
      ((of|\\|/)\s*(\d+|\w{3,}))?\s*      # The Grey: Part 1 ([of 3]) "Alpha"
      []) ]*\s*                           # The Grey: Part 1 (of 3[) ]"Alpha"
      ((and|[-[&:,;'"({])+\s*.{2,})?      # The Grey: Part 1 (of 3) ["Alpha"]
      $'''
      
      
   match = re.match(pattern, title_s)
   
   # remove surrounding quotes and spaces before returning the match
   return match.group(1).strip("\"' ") if match else ""
