'''
The module is the home of the ComicForm class.

@author: Cory Banack
'''

import clr
import log
import resources
import utils
import i18n
from utils import sstr
from cvform import CVForm

clr.AddReference('IronPython')

clr.AddReference('System')
from System import GC

clr.AddReference('System.Drawing')
from System.Drawing import Point, Rectangle, Size

from System.Threading import Monitor, Thread, ThreadStart, \
   ThreadExceptionEventHandler

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import AnchorStyles, Application, AutoScaleMode, \
   Button, FormBorderStyle, Label, Panel, PictureBox, ProgressBar, \
   PictureBoxSizeMode

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
      
      self.__cancel_on_close = True
      
      self.__scraper = scraper
      
      self.__already_closed = False
      
      self.__last_scraped_book = None 
      
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
      self.Text = self.Text = resources.SCRIPT_FULLNAME
      self.AutoScaleMode = AutoScaleMode.Font
      self.ClientSize = Size(346, 604)  
      self.MinimumSize = Size(166,275)
      self.FormBorderStyle = FormBorderStyle.SizableToolWindow
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
      button.Location = Point(98, 572)
      button.Size = Size(150, 23)
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
      book_name = book.filename_ext_s
      fileless = False if book_name else True
      if fileless:
         # 1a. this is a fileless book, so build up a nice, detailed name
         book_name = book.series_s 
         if not book_name:
            book_name = "<" + i18n.get("ComicFormUnknown") + ">"
         book_name += (' #' + book.issue_num_s) if book.issue_num_s else ''
         book_name += (' ({0} {1})'.format(
            i18n.get("ComicFormVolume"), sstr(book.volume_n) ) ) \
            if book.volume_n >= 0 else (' (' + sstr(book.year_n) +')') \
            if book.year_n >= 0 else ''
        
      # 2. obtain a copy of the cover page of the book
      cover_image = book.get_cover_image()
       
      # 3. install those values into the ComicForm.  update progressbar.        
      def delegate():
         # NOTE: now we're on the ComicForm Application Thread
         self.__label.Text = i18n.get("ComicFormScrapingLabel") + book_name
         self.__pbox_panel.set_image(cover_image) # cover image may be None
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
      self.__pbox_panel.Dispose(True)
      del self.__pbox_panel
      GC.Collect()
      
      
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
      
      Panel.__init__(self)
      self._picbox = PictureBox()
      self._picbox.SizeMode = PictureBoxSizeMode.StretchImage
      self._picbox.Location = Point(0,0)
      self.Controls.Add(self._picbox)
      self.set_image(None)
      
      self.Disposed += self.__disposed_fired
      self.Resize += self.__resize_fired
 
   # ==========================================================================     
   def set_image(self, image):
      '''
      Sets a new image for this _PictureBoxPanel to display.   If this image is
      None, a default logo will be displayed.  Any previous image that was set
      will have its Dispose() method called before it is discarded.
      '''
      
      if not image:
         image = resources.createComicVineLogo()
      
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
   def __disposed_fired(self, sender, args):
      ''' This method is called when this panel is disposed '''
      
      # force the PictureBox to dispose in a timely manner 
      if self._picbox.Image:                                               
         self._picbox.Image.Dispose()                                      
      self._picbox.Image = None                           
