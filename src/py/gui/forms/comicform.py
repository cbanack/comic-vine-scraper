'''
The module is the home of the ComicForm class.

@author: Cory Banack
'''

import clr
import log
import utils
from utils import sstr
import i18n
from resources import Resources
from cvform import CVForm

clr.AddReference('IronPython')

clr.AddReference('System')
from System import GC, Array
from System.IO import Path

clr.AddReference('System.Drawing')
from System.Drawing import Color, GraphicsUnit, Point, Rectangle, Size
from System.Drawing.Imaging import ColorMap, ImageAttributes

from System.Threading import Monitor, Thread, ThreadStart, \
   ThreadExceptionEventHandler

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import AnchorStyles, Application, AutoScaleMode, \
   Button, Cursors, FormBorderStyle, Label, MouseButtons, PaintEventHandler, \
   Panel, PictureBox, PictureBoxSizeMode, ProgressBar

# =============================================================================
class ComicForm(CVForm):
   '''
   This class is a standalone dialog that displays the current status of 
   a ScrapeEngine.  The dialog displays an image of the ComicBook that's 
   currently being scraped, along with a few other details, and a 'cancel' 
   button that the user can use at any time to cancel the entire scraping
   operation.  It is visible at all times while scraping.
   
   This class runs its own Application message loop, so that it can be 
   responsive at all times, even when the main application's message loop is
   busy with network IO.  Since most of the rest of the scraper application is 
   running on a different thread than this Form, it is important to remember 
   to properly 'invoke' any code that makes calls between this Form and any
   other Forms (or vice versa.) 
   '''
   
   # ==========================================================================
   def __init__(self, scraper):
      '''
      Initializes this form.
      'scraper' -> the currently running ScrapeEngine
      '''
      CVForm.__init__(self, scraper.comicrack.MainWindow, \
         "comicformLocation", "comicformSize")
      
      # whether or not this form should call cancel when it is closed.
      # this is mainly to fix a difficult bug caused by calling cancel twice 
      self.__cancel_on_close = True
      
      # stops us from calling close twice.  also fixes a tricky bug.
      self.__already_closed = False
      
      # an internal reference to the main scrapeengine object
      self.__scraper = scraper
      
      # the book that is currently being scraped
      self.__current_book = None
      
      # the page from the currently scraped book that is currently displayed
      self.__current_page = 0 
      
      # the number of pages in the currently scraped book
      self.__current_page_count = 0
      
      self.__build_gui()
   
   
   # ==========================================================================          
   def __build_gui(self):
      ''' Constructs and initializes the gui for this form. '''
      
      # 1. --- build each gui component
      self.__progbar = self.__build_progbar()
      self.__label = self.__build_label()
      self.__pbox_panel = self.__build_pboxpanel()
      self.__cancel_button = self.__build_cancelbutton()
         
      # 2. -- configure this form, and add all the gui components to it
      self.Text = self.Text = Resources.SCRIPT_FULLNAME
      self.AutoScaleMode = AutoScaleMode.Font
      self.ClientSize = Size(346, 604)  
      self.MinimumSize = Size(166,275)
      self.FormBorderStyle = FormBorderStyle.Sizable
      self.Icon = None
   
      self.Controls.Add(self.__progbar)
      self.Controls.Add(self.__label)
      self.Controls.Add(self.__pbox_panel)
      self.Controls.Add(self.__cancel_button)
      
      # 3. -- set up some listeners
      self.__scraper.start_scrape_listeners.append(self.__start_scrape)
      self.__scraper.cancel_listeners.append(self.close_threadsafe)
      self.FormClosing += self.__form_closing_fired
      self.FormClosed += self.__form_closed_fired
      
      # 4. -- define the keyboard focus tab traversal ordering
      self.__cancel_button.TabIndex = 0                                        

      
   # ==========================================================================
   def __build_progbar(self):
      ''' Builds and returns the progress bar for this form. '''
      
      pb = ProgressBar()
      pb.Minimum = 0
      pb.Maximum = 0
      pb.Step = 1
      pb.Value = 0
      pb.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right
      pb.Width = 320
      pb.Height = 20
      pb.Location = Point(13, 15)
      return pb
   
   
   # ==========================================================================
   def __build_label(self):
      ''' Builds and returns the label for this form. '''
      
      label = Label()
      label.UseMnemonic = False
      label.Text = '' # updated everytime we start scraping a new comic
      label.Location = Point(13, 45)
      label.Size = Size(320, 15)
      label.Anchor = AnchorStyles.Top | AnchorStyles.Left |AnchorStyles.Right
      label.AutoSize = False
      return label
   
   
   # ==========================================================================
   def __build_pboxpanel(self):
      ''' Builds and returns the picturebox panel for this form. '''
      
      pbox = _PictureBoxPanel()
      pbox.Location = Point (13, 65)
      pbox.Size = Size(320, 496)
      pbox.Anchor = AnchorStyles.Top | \
         AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
       
      # register listeners on the panel  
      pbox.MouseClick += self.__picture_box_clicked
      pbox.MouseDoubleClick += self.__picture_box_clicked
      
      return pbox
   
   
   # ==========================================================================
   def __build_cancelbutton(self):
      ''' Builds and returns the cancel button for this form. '''
      
      button = Button()
      button.Text=""  # gets updated by the 'update' method
      def cancel(sender, args):
         button.Enabled = False
         self.Close()
      button.Click+=cancel
      button.Location = Point(78, 572)
      button.Size = Size(190, 23)
      button.Anchor = AnchorStyles.Bottom
      return button
   
   
   # ==========================================================================
   def __start_scrape(self, book, num_remaining):
      '''
      This method gets called once for each comic that the ScrapeEngine is 
      scraping; the call happens just before the scrape begins.  The method 
      updates all necessary graphical components to reflect the current scrape.
      
      'book' -> the comic book object that is about to be scraped
      'num_remaining' -> the # of books left to scrape (including current one) 
      '''

      # 1. obtain a nice filename string to put into out Label    
      book_name = Path.GetFileName(book.path_s.strip()) # path_s is never None
      fileless = book_name == ""
      if fileless:
         # 1a. this is a fileless book, so build up a nice, detailed name
         book_name = book.series_s 
         if not book_name:
            book_name = "<" + i18n.get("ComicFormUnknown") + ">"
         book_name += (' #' + book.issue_num_s) if book.issue_num_s else ''
         book_name += (' ({0} {1})'.format(
            i18n.get("ComicFormVolume"), sstr(book.volume_year_n) ) ) \
            if book.volume_year_n >= 0 else (' ('+sstr(book.pub_year_n) +')') \
            if book.pub_year_n >= 0 else ''
        
      # 2. obtain a copy of the first (cover) page of the book to install
      page_image = book.create_image_of_page(0)
      page_count = book.page_count_n
       
      # 3. install those values into the ComicForm.  update progressbar.        
      def delegate():
         # NOTE: now we're on the ComicForm Application Thread
         self.__current_book = book
         self.__current_page = 0
         self.__current_page_count = page_count
         self.__label.Text = i18n.get("ComicFormScrapingLabel") + book_name
         self.__pbox_panel.set_image(page_image) # cover image may be None
         self.__progbar.PerformStep()
         self.__progbar.Maximum = self.__progbar.Value + num_remaining
         self.__cancel_button.Text=\
            i18n.get("ComicFormCancelButton").format(sstr(num_remaining))
         self.Update()
      utils.invoke(self, delegate, False)
 
   
   #===========================================================================
   @classmethod 
   def show_threadsafe(cls, *args):
      '''
      A threadsafe method for instantiating a new ComicForm on a NEW 
      Application thread, and then displaying it to the user.  The Application
      thread will shutdown and dispose automatically when the ComicForm is
      closed.  
      
      All given arguments will be passed to the new ComicForm's constructor.
      '''
      
      cls.newform = None
      def shower():                                                           
         with cls(*args) as form:
            Monitor.Enter(cls)
            try:
               cls.newform = form
               Monitor.Pulse(cls)
            finally:
               Monitor.Exit(cls)
            def exception_handler(sender, event):
               log.handle_error(event.Exception)  
            Application.ThreadException +=\
               ThreadExceptionEventHandler(exception_handler)
            Application.Run(form) # start form on new App thread; blocks
      
      Monitor.Enter(cls)
      try:
         # starts a new thread, which will become the Application thread/ event
         # pump for the newly created ComicForm,
         Thread(ThreadStart(shower)).Start()
         Monitor.Wait(cls)
      finally:
         Monitor.Exit(cls)
      newform = cls.newform
      del cls.newform
       
      # make sure this method does not return until the newly created ComicForm
      # has actually been made visible and active.  see bug 139.
      def activate_form():
         # this call is probably not needed; the real trick here is that 
         # invoking this method synchronously delays us until the form has
         # a nice, visible handle on-screen
         newform.Activate()
      utils.invoke(newform, activate_form, True)
      
      return newform
   

   # ==========================================================================      
   def close_threadsafe(self):
      '''
      A threadsafe method for closing this ComicForm and disposing of it's
      Application thread.   Note that closing the form with this method will
      NOT flag the ScraperEngine as cancelled.  Any other method of closing
      (user clicks on red x, the Close() method, etc) will flag cancel.
      '''
      
      def delegate():
         self.__cancel_on_close = False
         self.Close()
         self.Dispose()
      if not self.__already_closed:
         utils.invoke(self, delegate, True)
          
   # ==========================================================================           
   def _can_change_page(self, forward):
      '''
      Returns whether or not the user can change the currently displayed comic
      book page forward (or backward if 'foward==False').  This value is 
      computed based on the current page and the number of available pages.
      ''' 
      if forward:
         return self.__current_page < self.__current_page_count-1
      else: 
         return self.__current_page > 0
                
              
   # ==========================================================================           
   def __form_closing_fired(self, sender, args):
      ''' This method is called just before this form closes. '''
      
      # Flag this form as 'already closed', so that the close_threadsafe 
      # method can be called multiple times reliably.
      self.__already_closed = True
      
      
      
   # ==========================================================================
   def __form_closed_fired(self, sender, args):
      ''' This method is called just after this form closes. '''
      
      # deregister listers; prevents infinite loop! 
      self.__scraper.start_scrape_listeners.remove(self.__start_scrape)
      self.__scraper.cancel_listeners.remove(self.close_threadsafe)
      
      # in some cases, we should interpret the closing of this form as 
      # a request by the user to cancel the entire scrape operation...
      if self.__cancel_on_close:
         self.__scraper.cancel()
         
      # clean up and disposal
      self.__current_book = None
      self.__current_page = 0
      self.__pbox_panel.Dispose(True)
      del self.__pbox_panel
      GC.Collect()
      
      
   # ==========================================================================
   def __picture_box_clicked(self, sender, args):
      ''' This method is called whenever the user clicks on the pboxpanel. '''
      
      # this method causes the currently displayed page to change, either
      # forward or backward, as a result of the user left-clicking on the pbox
      mouse_hovered_state = self.__pbox_panel.get_mouse_hovered_state()
      if self.__current_book and args.Button == MouseButtons.Left \
            and mouse_hovered_state:
         
         # 1. calculate a new current page index, based on where use clicked
         if mouse_hovered_state == 'FL':
            self.__current_page = 0
         elif mouse_hovered_state == 'L':
            self.__current_page -= 1
         elif mouse_hovered_state == 'R':
            self.__current_page += 1
         elif mouse_hovered_state == 'FR':
            self.__current_page = self.__current_page_count-1
            
         self.__current_page = \
            min( self.__current_page_count-1, max(0, self.__current_page) )
         
         # grab the new page_image on the main ComicRack thread, because doing 
         # so accesses ComicRack's data.  then set it our own thread, because
         # doing so accesses our own data!  thread safety is fun.
         page_index = self.__current_page # a thread safety copy
         current_book = self.__current_book # a thread safety copy
         page_image = [None]
         def get_page():
            page_image[0] = current_book.create_image_of_page(page_index)
            def set_page():
               self.__pbox_panel.set_image(page_image[0]) # image may be None
               self.__pbox_panel.Refresh() # just in case nothing changed
            utils.invoke(self, set_page, False)
         utils.invoke( self.__scraper.comicrack.MainWindow, get_page, False )
      

   # ==========================================================================
   def CenterToParent(self):
      # Overridden  to  makes the initial position of this form a little nicer
      # users will quickly set their own form positions anyway.
      super(ComicForm, self).CenterToParent()
      self.Location = Point(self.Location.X - self.Width, self.Location.Y)
      
      

# =============================================================================    
class _PictureBoxPanel(Panel):
   '''
   A custom panel that contains a centered PictureBox.  You can set the image 
   in that PictureBox, and whenever the panel is resized, the PictureBox will be 
   automatically resized to be as big as possible while still maintaining that 
   image's original aspect ratio (i.e. blank space added to the images sides 
   or top/bottom, as needed.
   '''    
   
   #===========================================================================
   def __init__(self):
      ''' Creates a _PictureBoxPanel.  Call set_image after initialization. '''
      
      # the left and right arrow Image objects
      self.__left_arrow = Resources.createArrowIcon(True, False)
      self.__full_left_arrow = Resources.createArrowIcon(True, True)
      self.__right_arrow = Resources.createArrowIcon(False, False)
      self.__full_right_arrow = Resources.createArrowIcon(False, True)
      
      # the vertical line boundary between the full_left and left arrow's
      # 'clickable columns' and the full_right and right arrow's.
      self.__left_bound = 0;
      self.__right_bound = 0;

      # the image attributes to use for drawing non-alpha blended images      
      self.__hovered_image_atts = None
      
      # the image attributes to use for drawing alpha blended images      
      self.__normal_image_atts = None
      
      # a string indicating whether the mouse is hovered over the full 
      # left ('FL'), left ('L'), right ('R'), or full right ('FR') side of 
      # this panel, or None if the mouse isn't over the panel at all.  
      self.__mouse_hovered_state = None
      
      # our PictureBox object, which we center and stretch as needed 
      self._picbox = None
      
      Panel.__init__(self)
      self.__build_gui()
      


   #===========================================================================
   def __build_gui(self):
      '''  Builds and initializes the gui for this panel '''      

      # configure our image attribute objects      
      cmap = ColorMap()
      cmap.OldColor = Color.White
      cmap.NewColor = Color.Gainsboro
      self.__normal_image_atts = ImageAttributes()
      self.__normal_image_atts.SetRemapTable( Array[ColorMap]([cmap]) )
      self.__hovered_image_atts = ImageAttributes()
      
      # build our PictureBox
      self._picbox = PictureBox()
      self._picbox.SizeMode = PictureBoxSizeMode.StretchImage
      self._picbox.Location = Point(0,0)
      self._picbox.Enabled = False
      self.Controls.Add(self._picbox)
      
      # set up our listeners
      self.Disposed += self.__disposed_fired
      self.Resize += self.__resize_fired
      self.MouseMove += self.__mouse_moved
      self.MouseLeave += self.__mouse_exited
      self._picbox.Paint += PaintEventHandler(self.__pbox_painted)
      
      # initialize ourself with a non-existent image
      self.set_image(None)
 
 
   # ==========================================================================     
   def set_image(self, image):
      '''
      Sets a new image for this _PictureBoxPanel to display.   If this image is
      None, a default logo will be displayed.  Any previous image that was set
      will have its Dispose() method called before it is discarded.
      '''
      
      if not image:
         image = Resources.createComicVineLogo()
      
      self._ratio = 0;
      if image and float(image.Height):
         self._ratio = float(image.Width) / float(image.Height)
      if not self._ratio:
         self._ratio =1.55
         
      # dispose the old image, if need be
      if self._picbox.Image:
         self._picbox.Image.Dispose()
         
      self._picbox.Image = image
      self.OnResize(None)
      
      # update our mouse cursor
      comicform = self.Parent
      if comicform != None:
         self.Cursor = Cursors.Hand if comicform._can_change_page(True) or \
           comicform._can_change_page(False) else None

   
   
   # ==========================================================================
   def get_mouse_hovered_state(self):
      ''' 
      Returns where the mouse is currently hovered over on this panel.  Returns
      'FL' if it's hovered over the full_left arrow, 'L' if hovered over the 
      left arrow, 'R' if over the right arrow, 'FR' if over the full_right
      arrow, and None if the mouse isn't hovered over this panel at all.
      '''
      return self.__mouse_hovered_state;
   
   
   # ==========================================================================      
   def __disposed_fired(self, sender, args):
      ''' This method is called when this panel is disposed '''
      
      # force the PictureBox and arrow icons to dispose in a timely manner 
      if self._picbox.Image:                                               
         self._picbox.Image.Dispose()                                      
      self._picbox.Image = None              
      self.__left_arrow.Dispose()
      self.__full_left_arrow.Dispose()
      self.__right_arrow.Dispose()
      self.__full_right_arrow.Dispose()
      self.__left_arrow = None
      self.__full_left_arrow = None
      self.__right_arrow = None
      self.__full_right_arrow = None
      
      
   # ==========================================================================      
   def __resize_fired(self, sender, args):
      ''' This method is called whenever this panel is resized. '''
      
      # adjust the size of our PictureBox as needed to fulfill our contract 
      panel_bds = self.Bounds
      a = Rectangle(panel_bds.X, panel_bds.Y,\
         self.Size.Width, self.Size.Width / self._ratio)
      b = Rectangle(panel_bds.X, panel_bds.Y,\
         self.Size.Height * self._ratio, self.Size.Height)
      
      if panel_bds.Contains(a):
         self._picbox.Size = a.Size
         self._picbox.Location = Point( 0, (self.Size.Height-a.Height)/2 )
      else:   
         self._picbox.Size = b.Size
         self._picbox.Location = Point( (self.Size.Width-b.Width)/2, 0 )
      
      
   # ==========================================================================
   def __mouse_moved(self, picbox, args):
      ''' This method is called whenever the mouse enters this panel. '''
      
      # update 'mouse hovered state'
      x = args.X - (self.Width - self._picbox.Width)/2
      mouse_hov_left = args.X < self.Width/2
      mouse_hov_full = x < self.__left_bound if mouse_hov_left \
         else x > self.__right_bound
         
      if mouse_hov_left:
         mouse_hovered_state = 'FL' if mouse_hov_full else 'L'
      else:
         mouse_hovered_state = 'FR' if mouse_hov_full else 'R'
         
      if self.__mouse_hovered_state != mouse_hovered_state:
         self.__mouse_hovered_state = mouse_hovered_state
         self.Refresh() # force repaint
         
   # ==========================================================================
   def __mouse_exited(self, picbox, args):
      ''' This method is called whenever the mouse leaves this panel. '''
      
      # update 'mouse hovered state'
      if self.__mouse_hovered_state:
         self.__mouse_hovered_state = None
         self.Refresh() # force repaint
          
      
   # ==========================================================================
   def __pbox_painted(self, picbox, args):
      ''' Called after the picturebox paints itself. '''

      # this method adds two arrows (left and right) to the PictureBox, 
      # painted on top of it's regular graphcis.
         
      left_arrow = self.__left_arrow
      full_left_arrow = self.__full_left_arrow
      right_arrow = self.__right_arrow
      full_right_arrow = self.__full_right_arrow
      
      if left_arrow.Width != right_arrow.Width or \
            full_left_arrow.Width != right_arrow.Width or \
            full_right_arrow.Width != right_arrow.Width or \
            left_arrow.Height != right_arrow.Height or \
            full_left_arrow.Height != right_arrow.Height or \
            full_right_arrow.Height != right_arrow.Height:
         raise Exception("arrows must be identical dimensions")
      
      # 1. compute scaled widths and heights for the arrow images
      old_width = float(right_arrow.Width)
      scaled_width = min(picbox.Width*0.15, old_width)
      old_height = float(right_arrow.Height)
      scaled_height = old_height * scaled_width / old_width
       
      # 2. compute the proper location for the full arrow images
      y = picbox.Height/2-scaled_height/2
      xoffset = picbox.Width * 0.01
      f_leftx = xoffset
      f_rightx = picbox.Width-xoffset-scaled_width
      
      # 3. compute the proper location for the arrow images
      leftx = f_leftx + scaled_width
      rightx = f_rightx - scaled_width
      
      # 4. keep track of the right edges of the left and right clickable 
      #    column, so we'll be able to tell which icon the user clicks on. 
      self.__left_bound = leftx
      self.__right_bound = f_rightx
      
      if self.Parent != None:
         
         # 5. paint each arrow if it is possible to "turn the page" in that
         #    direction.   alpha-blend the inactive arrow (the one on the half
         #    of the pbox that the mouse ISN'T hovering over.)
         g = args.Graphics
         mouse_hovered = self.__mouse_hovered_state
         can_go_left = self.Parent._can_change_page(False)
         can_go_right = self.Parent._can_change_page(True)
         
         # 5a. draw the full left and left arrows if they are active
         if mouse_hovered and can_go_left:
            image_atts = self.__hovered_image_atts if mouse_hovered == 'FL' \
               else self.__normal_image_atts 
            dest_rect = Rectangle(f_leftx, y, scaled_width, scaled_height)
            g.DrawImage(full_left_arrow, dest_rect, 0, 0, old_width, 
               old_height, GraphicsUnit.Pixel, image_atts);
               
            image_atts = self.__hovered_image_atts if mouse_hovered == 'L' \
               else self.__normal_image_atts 
            dest_rect = Rectangle(leftx, y, scaled_width, scaled_height)
            g.DrawImage(left_arrow, dest_rect, 0, 0, old_width, old_height,
                GraphicsUnit.Pixel, image_atts);
               
         # 5b. draw the right and full right arrows if they are active
         if mouse_hovered and can_go_right:
            image_atts = self.__hovered_image_atts if mouse_hovered == 'R' \
               else self.__normal_image_atts 
            dest_rect = Rectangle(rightx, y, scaled_width, scaled_height)  
            g.DrawImage(right_arrow, dest_rect, 0, 0, old_width, old_height,
                GraphicsUnit.Pixel, image_atts);
                
            image_atts = self.__hovered_image_atts if mouse_hovered == 'FR' \
               else self.__normal_image_atts 
            dest_rect = Rectangle(f_rightx, y, scaled_width, scaled_height)  
            g.DrawImage(full_right_arrow, dest_rect, 0, 0, old_width, 
               old_height, GraphicsUnit.Pixel, image_atts);
      

