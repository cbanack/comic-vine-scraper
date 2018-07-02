''' 
This module is home to the IssueCoverPanel class.
 
@author: Cory Banack
'''
import clr
from dbmodels import IssueRef, SeriesRef
from dbpicturebox import DBPictureBox
from scheduler import Scheduler
import utils
from utils import sstr
import db
import i18n

clr.AddReference('System.Drawing')
from System.Drawing import ContentAlignment, Font, FontStyle, Point, Size

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import Button, Panel, LinkLabel




#==============================================================================
class IssueCoverPanel(Panel): 
   '''
   This panel is a compound gui component for displaying a comic book's issue 
   or series cover art (in a DBPictureBox), along with a few extra decorations.  
   
   The panel is updated when we set a new "ref" object, which is either an
   IssueRef (comic issue) or SeriesRef (comic series).  If the ref is an 
   IssueRef, we display that issue's cover art.  If it is a SeriesRef, we 
   display the cover art for the entire series, OR the cover art for a 
   particular issue in the series (if issue_num_hint_s has be set, see below.)
   
   There is also label just below the DBPictureBox that displays the issue 
   number of the ref cover that is currently on display (if possible), and on 
   either side of that there are two buttons that allow you to navigate forward 
   and backward through any available alternate cover art for that ref.
   
   You can set the ref that is currently being displayed by calling the 
   'set_ref' method.   After that, background threads will take care of 
   loading the cover art (and alternate covers) for that issue. 
   
   Do not forget to 'free' this panel when it is not longer in use!
   '''
   
   #===========================================================================
   def __init__(self, config, issue_num_hint_s=None):
      ''' 
      Initializes this panel.
      
      'config' -> the shared global Configuration object
      'issue_num_hint_s' -> issue number to use for figuring out which cover
          art to display when the currently set ref is a SeriesRef.
      '''
      
      # the shared global configuration
      self.__config = config
      
      # the issue number to use when finding cover art for a SeriesRef
      self.__issue_num_hint_s = issue_num_hint_s
      
      # a PictureBox that displays the cover art for the current selected issue
      self.__coverpanel = None
      
      # a linklabel describing the currently displayed cover image
      self.__label = None
      
      # the function that gets called if a link on self.__label gets clicked
      self.__link_callback = None
      
      # the "next" button for seeing a ref's next available cover
      self.__nextbutton = None
      
      # the "prev" button for seeing a ref's previous cover
      self.__prevbutton = None
      
      # the IssueRef or SeriesRef whose cover we are currently displaying
      self.__ref = None
      
      # a mapping of refs to _ButtonModels.  Basically caches the 
      # next/prev button state for each ref.
      self.__button_cache = {}
      
      # a mapping of SeriesRefs to IssueRefs (or SeriesRefs).  this cache lets
      # us avoid querying the database twice for the same SeriesRef.
      self.__series_cache = {}
      
      # a scheduler (thread) for finding cover images...
      self.__finder_scheduler = Scheduler()
      
      # a scheduler (thread) for setting new refs...
      self.__setter_scheduler = Scheduler()
      
      # a tuple containing the user's alternate cover art choice (a url) for 
      # a specific IssueRef i.e. (IssuRef, url). none if no alt choice was made.
      self.__alt_cover_choice = None
      
      Panel.__init__(self)
      self.__build_gui()
      
      
   # ==========================================================================
   def __build_gui(self):
      ''' Constructs and initializes the gui for this panel. '''
      
      # 1. --- build each gui component
      self.__coverpanel = self.__build_coverimage()
      self.__label = self.__build_label()
      self.__nextbutton = self.__build_nextbutton()
      self.__prevbutton = self.__build_prevbutton()
      
      # 2. --- configure this form, and add all the gui components to it      
      self.Size = Size(195, 360)
      self.Controls.Add(self.__coverpanel)
      self.Controls.Add(self.__prevbutton)
      self.Controls.Add(self.__label)
      self.Controls.Add(self.__nextbutton)

      #4. --- make sure the UI goes into a good initial state and the callback
      #       function gets its initial call.
      self.set_ref(None)


   # ==========================================================================
   def __build_coverimage(self):
      ''' builds and returns the cover image DBPictureBox for this panel '''
      
      cover = DBPictureBox()
      cover.Location = Point(0, 0)
      cover.Size = Size(195, 320)
      cover.Visible = self.__config.show_covers_b
      return cover
   
   
   # ==========================================================================
   def __build_label(self):
      ''' 
      Builds and return the label for the cover image.
      '''
      
      label = LinkLabel()
      label.UseMnemonic = False
      label.Visible = self.__config.show_covers_b
      label.Location = Point(18, 326)
      label.Size = Size(155,36)
      label.TextAlign = ContentAlignment.MiddleCenter
      
      def link_clicked(sender, args):
         if self.__link_callback:
            self.__link_callback()
      label.LinkClicked += link_clicked

      return label
   
   
   # ==========================================================================
   def __build_nextbutton(self):
      ''' Builds and returns the 'next' button for this panel. '''

      button = Button()
      button.Location = Point(173, 332)
      button.Size = Size(20, 24)
      button.Text = '>'
      button.Font = Font(button.Font, FontStyle.Bold)
      button.UseVisualStyleBackColor = True
      button.Click += self.__button_click_fired
      # note: this button's visibility is manipulated by __update
      return button
   
   
   # ==========================================================================
   def __build_prevbutton(self):
      ''' Builds and returns the 'previous' button for this panel. '''

      button = Button()
      button.Location = Point(2, 332)
      button.Size = Size(20, 24)
      button.Text = '<'
      button.Font = Font(button.Font, FontStyle.Bold)
      button.UseVisualStyleBackColor = True
      button.Click += self.__button_click_fired
      # note: this button's visibility is manipulated by __update
      return button

      
   # ==========================================================================
   def free(self): 
      ''' 
      Free all resources allocated by this class when it is no longer needed.
      '''
      
      # sets the alternate issue cover that the user may have chosen
      # see get_alt_issue_cover_choice() for more details
      if type(self.__ref) == IssueRef:
         issue_ref = self.__ref
         button_model = self.__button_cache[issue_ref]
         if button_model:
            if button_model.can_decrement():
               image_ref = button_model.get_current_ref()
               if utils.is_string(image_ref):
                  self.__alt_cover_choice = (issue_ref, image_ref)
      
      self.__finder_scheduler.shutdown(False)
      self.__setter_scheduler.shutdown(False)
      self.set_ref(None)
      self.__coverpanel.free()
      self.__prevbutton = None
      self.__nextbutton = None
      self.__label = None
      self.Dispose()


   # ==========================================================================
   def set_ref(self, ref):
      '''
      Sets the comic IssueRef or SeriesRef that this panel is displaying.
      'ref'-> the IssueRef or SeriesRef that we are displaying, or None.
      '''

      run_in_background = type(ref) == SeriesRef and self.__issue_num_hint_s       
      if run_in_background:
         # 1a. our ref is a SeriesRef.  use our issue num hint to try to convert
         #     it into an IssueRef.  use a simple cache to avoid requerying
         def maybe_convert_seriesref_to_issue_ref(ref):
            if not ref in self.__series_cache:
               issue_ref = db.query_issue_ref(ref, self.__issue_num_hint_s)
               self.__series_cache[ref] = issue_ref if issue_ref else ref
                  
            # 1b. go back to the application thread to do the actual ref change
            def change_ref():  
               self.__ref = self.__series_cache[ref]
               self.__update()
            utils.invoke(self.__coverpanel, change_ref, True)
            
         def dummy(): # I don't know why this is needed 
            maybe_convert_seriesref_to_issue_ref(ref)
         self.__setter_scheduler.submit(dummy)
         
      else:
         # 2. our ref is an IssueRef
         # we're already on the application thread, so just do the ref change 
         self.__ref = ref
         self.__update()
            

   # ==========================================================================
   def get_alt_issue_cover_choice(self):
      '''
      If the comic cover that this panel was displaying when it was closed was
      an alternate cover image (i.e. anything other than the default image 
      choice for an issue or series) then this method will return a tuple, with 
      the first element being the IssueRef (never a SeriesRef) for the 
      alternate image choice, and the second element being a string URL for 
      the alternate image itself.  
      
      If the chosen image was the default image anyway, or if the panel hasn't 
      been shutdown yet, we return None.
      '''
      return self.__alt_cover_choice

   # ==========================================================================
   def __update(self):
      '''
      Updates all elements of this control's GUI.  Should be called anytime 
      anything has changed that might require us to update the data displayed
      by any of our child controls (text labels, buttons, DBPictureBox, etc).  
      
      Note that this method call may initiate a background thread to update a 
      a ref's _ButtonModel based on a db query.
      '''
      
      # 1. grab copies of all the member variables that we might want to use; 
      # keep in mind that any of the following code can be running AFTER this 
      # panel and it's form has been closed/disposed, so we don't want to 
      # directly rely on any 'self.' members.
      ref = self.__ref
      cache = self.__button_cache
      cover_image = self.__coverpanel
      nextbutton = self.__nextbutton
      prevbutton = self.__prevbutton
      label = self.__label
      scheduler = self.__finder_scheduler
      
      
      if ref is None or cache is None:
         # 2. do nothing, we're in a wierd/border state
         cover_image.set_image_ref(None)
         nextbutton.Visible = False
         prevbutton.Visible = False
         label.Text = ''
         
      else:
         # 3a. if we don't already have a cached _ButtonModel for the current 
         #     ref, create one and put it in the cache. 
         if not cache.has_key(ref):
            cache[ref] = _ButtonModel(ref, \
              'searched' if type(ref) == SeriesRef else 'not-searched')
            
         
         # 3b. now that we have a _ButtonModel for the current issue, adjust our 
         #     various gui widgets according to its state.  remember, if this
         #     model was freshly created, it's only going to contain a single 
         #     image reference for now, but at some point in the future (~2 sec)
         #     this method will be automatically called again, and the bmodel
         #     will be fully updated, and may then contain more images.
         bmodel = cache[ref]
         cover_image.set_image_ref( bmodel.get_current_ref() )
         nextbutton.Visible = cover_image.Visible and bmodel.can_increment()
         prevbutton.Visible = cover_image.Visible and bmodel.can_decrement()
         
         # 3c. update the text, hyperlinks, and link callback for the label.
         label.Links.Clear()
         self.__link_callback = None
         issue_num_s = ref.issue_num_s if type(ref) == IssueRef else ''
         if bmodel.get_status() == 'searched':
            if issue_num_s:
               if len(bmodel) > 1:
                  label.Text = i18n.get("IssueCoverPanelPlural").\
                     format(sstr(issue_num_s), sstr(bmodel.get_position()+1),\
                     sstr(len(bmodel)))
               else:
                  label.Text = i18n.get("IssueCoverPanelSingle").\
                     format(sstr(issue_num_s))
            else:
               label.Text = i18n.get("IssueCoverPanelSeries")
         elif bmodel.get_status() == 'searching': 
            label.Text = i18n.get("IssueCoverPanelSearching").\
               format(sstr(issue_num_s))
         elif bmodel.get_status() == 'not-searched':
            label.Text = i18n.get("IssueCoverPanelSearchable").\
               format(sstr(issue_num_s))
            # create a link in between the first set of brackets. if use clicks
            # on it, flip the current bmodel to "searching" status, and update
            start = label.Text.find('(')
            end = label.Text.find(')', start) if start > -1 else -1
            if start >= 0 and end >= start:
               label.Links.Add(start+1, end)
               def link_callback():
                  bmodel.set_status("searching")
                  self.__update()
               self.__link_callback = link_callback 
         else:
            raise Exception()
            
         # 4. search to see if there are any more covers to find
         search_for_more_covers = cache[ref].get_status()=='searching'
         if search_for_more_covers:
            def update_cache(): #runs on scheduler thread
               issue = db.query_issue(ref, True) \
                  if type(ref) == IssueRef else None 
                  
               def update_bmodel():  # runs on application thread
                  bmodel = cache[ref]
                  if issue and len(issue.image_urls_sl) > 1:
                     for i in range(1, len(issue.image_urls_sl)):
                        bmodel.add_new_ref(issue.image_urls_sl[i])
                  bmodel.set_status('searched')
                  self.__update() # recurse!
               utils.invoke(self, update_bmodel, True)
            scheduler.submit(update_cache)
       
         
   # ==========================================================================
   def __button_click_fired(self, sender, args):
      ''' This method is called when the next/prev buttons are clicked '''
      
      # should never happen when button cache is empty or current ref is None
      bmodel = self.__button_cache[self.__ref]
      if sender == self.__nextbutton:
         bmodel.increment()
      else:
         bmodel.decrement()
        
      self.__update()         
         
         
         
# =============================================================================     
class _ButtonModel(object):
   ''' 
   Contains state for a pair of next/prev buttons, including a list of 1 or 
   more 'image references', and a current position within that list.
   
   Each image reference is either a url string, an IssueRef, or a SeriesRef.  
   Any of these objects can be mapped back to a cover image.
   '''
   
   #===========================================================================
   def __init__(self, ref, status="not-searched"):
      ''' 
      Initializes this _ButtonModel with the given ref as its sole
      image reference.  More references can be added.
            
      'ref' -> an IssueRef, SeriesRef, or url string reference to an image.
         This will be our sole image reference (until more are added).
      'status' -> one of three values, see comment for 'set_status'
      '''
      
      # a list of all of our image references.  will always have at 
      # least one element, though that element may be a null image reference.
      self.__image_refs = []

      # one of 'not-searched', 'searching', or 'searched' 
      self.__status = None
      self.set_status(status)
      
      # the position of the 'current' element in the list of image references.
      # this value can be changed by the 'increment' or 'decrement' methods.
      self.__pos_n = 0
      
      self.add_new_ref(ref)
      
      
   #===========================================================================
   def add_new_ref(self, image_ref):
      '''
      Adds a new image reference to this _ButtonModel.  The given ref should be
      either an IssueRef or a SeriesRef (either which can be used indirectly to 
      obtain a cover image via the db) or a direct url string to the image. 
      '''  
      if image_ref:
         if not image_ref in self.__image_refs:
            self.__image_refs.append(image_ref)
            
         
   #===========================================================================
   def get_current_ref(self):
      ''' 
      Gets the current image reference for this _ButtonModel, based on the 
      underlying model's position in the list of image refs.  This value will
      be an IssueRef, SeriesRef or a direct url string to the image. 
      '''
      return self.__image_refs[self.__pos_n] if self.__image_refs else None

   
   #===========================================================================
   def increment(self):
      '''
      Increments the current image reference position (see 'get_current_ref') 
      to the next one in this _ButtonModel, unless we are already at the last 
      one (see 'can_increment').
      '''
      self.__pos_n = min(len(self.__image_refs)-1, self.__pos_n + 1)
      
      
   #===========================================================================
   def can_increment(self):
      ''' Returns whether we can increment this _ButtonModel any further. '''
      return self.__pos_n < len(self.__image_refs)-1

         
   #===========================================================================
   def decrement(self):
      '''
      Decrements the current image reference position (see 'get_current_ref') 
      to the previous one in this _ButtonModel, unless we are already at the 
      first one (see 'can_decrement').
      '''
      self.__pos_n = max(0, self.__pos_n - 1)

      
   #===========================================================================
   def can_decrement(self):
      ''' Returns whether we can decrement this _ButtonModel any further. '''
      return self.__pos_n > 0
      
      
   #===========================================================================
   def set_status(self, status):
      ''' 
      Changes the search status of this _ButtonModel. Must be one of:
         'not-searched' : user has not requested a search for more image refs
         'searching' : a background thread is currently search for image refs
         'searched' : the search for more image refs is now complete
      '''
      if status=='not-searched' or status=='searching' or status=='searched':
         self.__status = status
      else:
         raise Exception("bad status received: ", sstr(status))
      
   #===========================================================================
   def get_status(self):
      '''  Gets the search status of this _ButtonModel. See set_status.  '''
      return self.__status
   
   #===========================================================================
   def get_position(self):
      ''' Returns 0-indexed position of the current image reference.'''
      return self.__pos_n
   
   #===========================================================================
   def __len__(self):
      ''' Allows the 'len' operation to work on _ButtonModels. '''
      return len(self.__image_refs)
