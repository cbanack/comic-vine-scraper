''' 
This module is home to the IssueCoverPanel class.
 
@author: Cory Banack
'''

import clr
from dbpicturebox import DBPictureBox 
from utils import sstr
import db
import utils
import i18n
from scheduler import Scheduler 

clr.AddReference('System.Drawing')
from System.Drawing import ContentAlignment, Font, FontStyle, Point, Size 

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import Button, Label, Panel 


#==============================================================================
class IssueCoverPanel(Panel): 
   '''
   This panel is a compound gui compoent for displaying a comic book's issue 
   cover art (in a DBPictureBox), along with a few extra decorations.  
   
   Namely, there is a label displaying the current IssueRef's issue number
   just below the DBPictureBox, and on either side of that there are two buttons
   that allow you to navigate forward and backward through the list of alternate
   cover art for the currently displayed issue.
   
   You can set the issue that is currently being displayed by calling the 
   'set_issue' method.   After that, background threads will take care of 
   loading the cover art (and alternate covers) for that issue. 
   
   Do not forget to 'free' this panel when it is not longer in use!
   '''
   
   #===========================================================================
   def __init__(self, config):
      ''' 
      Initializes this panel.
      
      'config' -> the shared global Configuration object
      '''
      
      # the shared global configuration
      self.__config = config
      
      # a PictureBox that displays the cover art for the current selected issue
      self.__cover_image = None
      
      # a label describing the currently displayed cover image
      self.__label = None
      
      # the "next" button for seeing an issue's next available cover
      self.__nextbutton = None
      
      # the "prev" button for seeing an issue's previous cover
      self.__prevbutton = None
      
      # the IssueRef of the issue that we are currently displaying
      self.__issueref = None
      
      # a mapping of IssueRefs to _ButtonModels.  Basically caches the 
      # next/prev button state for each issue.
      self.__button_cache = {}
      
      # a simple "last-in-and-ignore-everything-else" scheduler
      self.__scheduler = Scheduler()
      
      # the user's alternate cover art choice, if she made one
      # this url is None until this panel is disposed (i.e. 'free' is called)
      self.__alt_cover_url = None
      
      Panel.__init__(self)
      self.__build_gui()
      
      
   # ==========================================================================
   def __build_gui(self):
      ''' Constructs and initializes the gui for this panel. '''
      
      # 1. --- build each gui component
      self.__cover_image = self.__build_coverimage()
      self.__label = self.__build_label()
      self.__nextbutton = self.__build_nextbutton()
      self.__prevbutton = self.__build_prevbutton()
      
      # 2. --- configure this form, and add all the gui components to it      
      self.Size = Size(195, 360)
      self.Controls.Add(self.__cover_image)
      self.Controls.Add(self.__prevbutton)
      self.Controls.Add(self.__label)
      self.Controls.Add(self.__nextbutton)

      #4. --- make sure the UI goes into a good initial state and the callback
      #       function gets its initial call.
      self.set_issue(None)


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
      Builds and return the label for toggling cover image display.
      '''
      
      label = Label()
      label.Visible = self.__config.show_covers_b
      label.Location = Point(18, 326)
      label.Size = Size(155,36)
      label.TextAlign = ContentAlignment.MiddleCenter

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
      
      # sets the alternate cover image that the user may have chosen
      # see get_alt_cover_image_url for more details
      if self.__issueref:
         button_model = self.__button_cache[self.__issueref]
         if button_model:
            if button_model.can_decrement():
               ref = button_model.get_current_ref()
               if utils.is_string(ref):
                  self.__alt_cover_url = ref
      
      self.__scheduler.shutdown(False)
      self.set_issue(None)
      self.__cover_image.free()
      self.__prevbutton = None
      self.__nextbutton = None
      self.__label = None
      self.Dispose()


   # ==========================================================================
   def set_issue(self, issue_ref):
      '''
      Sets the comic issue that this panel is displaying.
      'issue_ref'-> the IssueRef for the issue that we are displaying, or None.
      '''
      
      self.__issueref = issue_ref
      self.__update()

   # ==========================================================================
   def get_alt_cover_image_url(self):
      '''
      If the comic issue that this panel was displaying when it was closed was
      set to display an alternate cover image (i.e. anything other than the 
      default image) then this method will return the string URL for that image.  
      
      Otherwise, or if the panel hasn't been shutdown yet, we return None.
      '''
      return self.__alt_cover_url

   # ==========================================================================
   def __update(self):
      '''
      Updates all elements of this controls GUI.  Should be called anytime 
      anything has changed that might require a change to the data displayed
      by one of this controls child controls.  
      
      Note that this method call may initiate a background thread to update a 
      newly created _ButtonModel at some point in the future.
      '''
      
      # 1. grab copies of all the member variables that we might want to use; 
      # keep in mind that any of the following code can be running AFTER this 
      # panel and it's form has been closed/disposed, so we don't want to 
      # directly rely on any 'self.' members.
      issueref = self.__issueref
      cache = self.__button_cache
      cover_image = self.__cover_image
      nextbutton = self.__nextbutton
      prevbutton = self.__prevbutton
      label = self.__label
      scheduler = self.__scheduler
      
      
      if issueref is None or cache is None:
         # 2. do nothing, we're in a wierd/border state
         cover_image.set_image_ref(None)
         nextbutton.Visible = False
         prevbutton.Visible = False
         label.Enabled = True
         label.Text = ''
      else:
         # 3a. make sure the cache has a _ButtonModel for the current issue
         #    also, if that _ButtonModel is not fully updated, update it.
         if not cache.has_key(issueref) or \
               not cache[issueref].is_fully_updated():
            
            label.Enabled = False
            if not cache.has_key(issueref):
               cache[issueref] = _ButtonModel(issueref)
            bmodel = cache[issueref]
            
            def update_cache(): #runs on scheduler thread
               issue = db.query_issue(issueref)
               def add_refs():  # runs on application thread
                  bmodel.set_fully_updated()
                  if issue and len(issue.image_urls_sl) > 1:
                     for i in range(1, len(issue.image_urls_sl)):
                        bmodel.add_new_ref(issue.image_urls_sl[i])
                  self.__update(); # recurse!
                  
               utils.invoke(self, add_refs, False)
               
            scheduler.submit(update_cache)
            
         
         # 3b. now that we have a bmodel for the current issue, adjust our 
         #     various gui widgets according to its state.  remember, if this
         #     bmodel was freshly created, it's going to contain a single 
         #     image reference for now, but at some point in the future (~1 sec)
         #     this method will be automatically called again, and the bmodel
         #     will be fully updated, and may contain more images.
         bmodel = cache[issueref]
         cover_image.set_image_ref( bmodel.get_current_ref() )
         nextbutton.Visible = cover_image.Visible and bmodel.can_increment()
         prevbutton.Visible = cover_image.Visible and bmodel.can_decrement()
         
         # 3c. update the text for the label.
         issue_num_s = self.__issueref.issue_num_s if self.__issueref else ''
         label.Enabled = bmodel.is_fully_updated()
         if bmodel.is_fully_updated():
            if issue_num_s:
               if len(bmodel) > 1:
                  self.__label.Text = i18n.get("IssueCoverPanelPlural").\
                     format(sstr(issue_num_s), sstr(bmodel.get_ref_id()+1),\
                     sstr(len(bmodel)))
               else:
                  self.__label.Text = i18n.get("IssueCoverPanelSingle").\
                     format(sstr(issue_num_s))

            else:
               self.__label.Text = ""
         else:
            self.__label.Text = i18n.get("IssueCoverPanelSearching")
       
         
   # ==========================================================================
   def __button_click_fired(self, sender, args):
      ''' This method is called when the next/prev buttons are clicked '''
      
      # should never happen when the button cache is empty or issueref is None
      bmodel = self.__button_cache[self.__issueref]
      if sender == self.__nextbutton:
         bmodel.increment()
      else:
         bmodel.decrement()
        
      self.__update()         
         
         
         
# =============================================================================     
class _ButtonModel(object):
   ''' 
   Contains state for the next/prev buttons for a single comic issue. 
   In particular, contains 1 or more 'image references' for that issue. 
   Each image reference is a url (or IssueRef object) that maps to one of 
   the cover art images for that issue.
   '''
   
   #===========================================================================
   def __init__(self, issue_ref):
      ''' 
      Initializes this _ButtonModel with the given issue_ref as its sole
      image reference.  More references can be added.
            
      'issue_ref' -> an IssueRef that will be our sole image reference (so far).
      '''
      
      # a list of all of this buttons image references.  will always have at 
      # least one element, though that element may be a null image reference.
      self.__image_refs = []

      # the position of the 'current' element in the list of image references.
      # this value can be changed by the 'increment' or 'decrement' methods.
      self.__pos_n = 0
      
      # true iff this _ButtonModel has been fully updated with all image refs
      self.__is_fully_updated = False
      
      self.add_new_ref(issue_ref)
      
      
   #===========================================================================
   def add_new_ref(self, image_ref):
      '''
      Adds a new image reference to this button model.  The given ref should be
      either an IssueRef (which can be used indirectly to obtain a cover image)
      or the direct string url of the image. 
      '''  
      if image_ref:
         if not image_ref in self.__image_refs:
            self.__image_refs.append(image_ref)
            
         
   #===========================================================================
   def get_current_ref(self):
      ''' 
      Gets the current image reference for this _ButtonModel.  This value will
      be an IssueRef or an url string. 
      '''
      return self.__image_refs[self.__pos_n]

   
   #===========================================================================
   def increment(self):
      '''
      Increments the current image reference (see 'get_current_ref') to the next
      one in this _ButtonModel, unless we are already at the last one
      (see 'can_increment').
      '''
      self.__pos_n = min(len(self.__image_refs)-1, self.__pos_n + 1)
      
      
   #===========================================================================
   def can_increment(self):
      ''' Returns whether we can increment this _ButtonModel any further. '''
      return self.__pos_n < len(self.__image_refs)-1

         
   #===========================================================================
   def decrement(self):
      '''
      Decrements the current image reference (see 'get_current_ref') to the 
      previous one in this _ButtonModel, unless we are already at the first one
      (see 'can_decrement').
      '''
      self.__pos_n = max(0, self.__pos_n - 1)

      
   #===========================================================================
   def can_decrement(self):
      ''' Returns whether we can decrement this _ButtonModel any further. '''
      return self.__pos_n > 0
      
      
   #===========================================================================
   def set_fully_updated(self):
      ''' Marks this _ButtonModel as having a complete set of image refs.'''
      self.__is_fully_updated = True

      
   #===========================================================================
   def is_fully_updated(self):
      ''' Returns whether this _ButtonModel is flagged as 'fully updated'.'''
      return self.__is_fully_updated
   
   #===========================================================================
   def get_ref_id(self):
      ''' Returns the index of the current image reference.'''
      return self.__pos_n
   
   #===========================================================================
   def __len__(self):
      ''' Allows the 'len' operation to work on _ButtonModels. '''
      return len(self.__image_refs)