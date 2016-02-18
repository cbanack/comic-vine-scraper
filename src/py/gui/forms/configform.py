'''
This module contains the ConfigForm class (a popup dialog).

@author: Cory Banack
'''
import clr
import log
from cvform import CVForm 
from configuration import Configuration
import i18n
import System

clr.AddReference('System.Windows.Forms') 
from System.Windows.Forms import AutoScaleMode, Button, CheckBox, ContextMenu, \
    CheckedListBox, DialogResult, FlatStyle, Label, MenuItem, \
    RichTextBox, SelectionMode, TabControl, TabPage, TextBox, LinkLabel

clr.AddReference('System.Drawing')
from System.Drawing import Point, Size, ContentAlignment

# =============================================================================
class ConfigForm(CVForm):
   '''
   This class is a popup, modal dialog that displays all of the configurable
   options available to the user.   The user can change any of the options, 
   and then click OK or Cancel to quit the dialog and contine the normal 
   execution of the program.   Clicking Cancel will discard any configuration
   changes that were made; clicking OK will save them permanently.
   '''
   
   # ==========================================================================
   def __init__(self, owner):
      ''' 
      Initializes this form.
      owner -> this form's owner window/dialog
      '''
      
      # these are the strings that the user sees for each checkbox; they can 
      # also be used to reference each checkbox inside the checkboxlist
      ConfigForm.__SERIES_CB = i18n.get("ConfigFormSeriesCB")
      ConfigForm.__NUMBER_CB = i18n.get("ConfigFormNumberCB")
      ConfigForm.__PUBLISHED_CB = i18n.get("ConfigFormPublishedCB")
      ConfigForm.__RELEASED_CB = i18n.get("ConfigFormReleasedCB")
      ConfigForm.__TITLE_CB = i18n.get("ConfigFormTitleCB")
      ConfigForm.__CROSSOVERS_CB = i18n.get("ConfigFormCrossoversCB")
      ConfigForm.__WRITER_CB = i18n.get("ConfigFormWriterCB")
      ConfigForm.__PENCILLER_CB = i18n.get("ConfigFormPencillerCB")
      ConfigForm.__INKER_CB = i18n.get("ConfigFormInkerCB")
      ConfigForm.__COVER_ARTIST_CB = i18n.get("ConfigFormCoverCB")
      ConfigForm.__COLORIST_CB = i18n.get("ConfigFormColoristCB")
      ConfigForm.__LETTERER_CB = i18n.get("ConfigFormLettererCB")
      ConfigForm.__EDITOR_CB = i18n.get("ConfigFormEditorCB")
      ConfigForm.__SUMMARY_CB = i18n.get("ConfigFormSummaryCB")
      ConfigForm.__IMPRINT_CB = i18n.get("ConfigFormImprintCB")
      ConfigForm.__PUBLISHER_CB = i18n.get("ConfigFormPublisherCB")
      ConfigForm.__VOLUME_CB = i18n.get("ConfigFormVolumeCB")
      ConfigForm.__CHARACTERS_CB = i18n.get("ConfigFormCharactersCB")
      ConfigForm.__TEAMS_CB = i18n.get("ConfigFormTeamsCB")
      ConfigForm.__LOCATIONS_CB = i18n.get("ConfigFormLocationsCB")
      ConfigForm.__WEBPAGE_CB = i18n.get("ConfigFormWebCB")
      
      # the TabControl that contains all our TabPages
      self.__tabcontrol = None
      
      # the ok button for this dialog
      self.__ok_button = None
      
      # the cancel button for this dialog
      self.__cancel_button = None
      
      # the restore defaults button for this dialog
      self.__restore_button = None
      
      # "options" checkboxes
      self.__ow_existing_cb = None 
      self.__ignore_blanks_cb = None                                          
      self.__autochoose_series_cb = None
      self.__confirm_issue_cb = None
      self.__convert_imprints_cb = None
      self.__summary_dialog_cb = None
      self.__download_thumbs_cb = None
      self.__preserve_thumbs_cb = None
      self.__fast_rescrape_cb = None
      self.__rescrape_tags_cb = None
      self.__rescrape_notes_cb = None
      
      # "api key" textbox
      self.__api_key_tbox = None
      
      # "advanced settings" textbox
      self.__advanced_tbox = None
      
      # "data" checkbox list
      self.__update_checklist = None
      
      CVForm.__init__(self, owner, "configformLocation")
      self.__build_gui()
          
         
          
   # ==========================================================================          
   def __build_gui(self):
      ''' Constructs and initializes the gui for this form. '''
      
      # 1. --- build each gui component
      self.__ok_button = self.__build_okbutton()
      self.__cancel_button = self.__build_cancel_button()
      self.__restore_button = self.__build_restore_button()
      self.__tabcontrol = self.__build_tabcontrol()
         
      # 2. -- configure this form, and add all the gui components to it
      self.AutoScaleMode = AutoScaleMode.Font
      self.ClientSize = Size(416, 375)
      self.Text = i18n.get("ConfigFormTitle")
   
      self.Controls.Add(self.__ok_button)                                     
      self.Controls.Add(self.__cancel_button)                                 
      self.Controls.Add(self.__restore_button)                                
      self.Controls.Add(self.__tabcontrol)                             
      
      # 3. -- define the keyboard focus tab traversal ordering
      self.__ok_button.TabIndex = 0                                        
      self.__cancel_button.TabIndex = 1                                    
      self.__restore_button.TabIndex = 2
      self.__tabcontrol.TabIndex = 3                                 

      self.__fired_update_gui()  

      
      
   # ==========================================================================
   def __build_okbutton(self):
      ''' builds and returns the ok button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.OK
      button.Location = Point(228, 343)
      button.Size = Size(80, 23)
      button.Text = i18n.get("ConfigFormOK")
      return button


   
   # ==========================================================================
   def __build_restore_button(self):
      ''' builds and returns the restore button for this form '''
      
      button = Button()
      button.Click += self.__fired_restore_defaults
      button.Location = Point(10, 343)
      button.Size = Size(170, 23)
      button.Text = i18n.get("ConfigFormRestore")
      return button


   
   # ==========================================================================
   def __build_cancel_button(self):
      ''' builds and returns the cancel button for this form '''
      
      button = Button()
      button.DialogResult = DialogResult.Cancel
      button.Location = Point(315, 343)
      button.Size = Size(90, 23)
      button.Text = i18n.get("ConfigFormCancel")
      return button


      
   # ==========================================================================
   def __build_tabcontrol(self):
      ''' builds and returns the TabControl for this dialog '''
      
      tabcontrol = TabControl()
      tabcontrol.Location = Point(10, 15)
      tabcontrol.Size = Size(395, 302)
      
      tabcontrol.Controls.Add( self.__build_comicvinetab() )
      tabcontrol.Controls.Add( self.__build_detailstab() )
      tabcontrol.Controls.Add( self.__build_behaviourtab() )
      tabcontrol.Controls.Add( self.__build_datatab() )
      tabcontrol.Controls.Add( self.__build_advancedtab() )
      
      return tabcontrol

   
   # ==========================================================================
   def __build_comicvinetab(self):
      ''' builds and returns the "ComicVine" Tab for the TabControl '''
      
      tabpage = TabPage()
      tabpage.Text = i18n.get("ConfigFormComicVineTab")
      tabpage.Name = "comicvine"
      
      # 1. --- a description label for this tabpage
      label = Label()
      label.UseMnemonic = False
      label.AutoSize = False
      label.Location = Point(34, 80)
      label.Size = Size(315, 54)
      label.Text = i18n.get("ConfigFormComicVineText")
      
      # 2. --- the API key text box 
      fired_update_gui = self.__fired_update_gui
      class ApiKeyTextBox(TextBox):
         def OnTextChanged(self, args):
            fired_update_gui()
            
      self.__api_key_tbox = ApiKeyTextBox()
      tbox = self.__api_key_tbox
      tbox.Location = Point(34, 135)
      tbox.Size = Size(315, 1)
      
      menu = ContextMenu()
      items = menu.MenuItems
      items.Add( MenuItem(i18n.get("TextCut"), lambda s, ea : tbox.Cut() ) )
      items.Add( MenuItem(i18n.get("TextCopy"), lambda s, ea : tbox.Copy() ) )
      items.Add( MenuItem(i18n.get("TextPaste"), lambda s, ea : tbox.Paste() ) )
      tbox.ContextMenu = menu
      
      # 3. --- add a clickable link to send the user to ComicVine
      linklabel = LinkLabel()
      linklabel.UseMnemonic = False
      linklabel.AutoSize = False
      linklabel.Location = Point(34, 170) 
      linklabel.Size = Size(315, 34)
      linklabel.Text = i18n.get("ConfigFormComicVineClickHere")
      linklabel.LinkClicked += self.__fired_linkclicked
      
      # 4. --- add 'em all to this tabpage
      tabpage.Controls.Add(label)
      tabpage.Controls.Add(tbox)
      tabpage.Controls.Add(linklabel)
      
      return tabpage
   
   
   # ==========================================================================
   def __build_detailstab(self):
      ''' builds and returns the "Details" Tab for the TabControl '''
      
      tabpage = TabPage()
      tabpage.Text = i18n.get("ConfigFormDetailsTab")
      tabpage.Name = "details"
      
      # 1. --- a description label for this tabpage
      label = Label()
      label.UseMnemonic = False
      label.AutoSize = True
      label.Location = Point(14, 35)
      label.Size = Size(299, 17)
      label.Text = i18n.get("ConfigFormDetailsText")
      
      # 2. --- the 'select all' button
      checkall_button = Button()
      checkall_button.Click += self.__fired_checkall
      checkall_button.Location = Point(280, 107)
      checkall_button.Size = Size(100, 23)
      checkall_button.Text = i18n.get("ConfigFormDetailsAll")
      
      # 3. --- the 'deselect all' button
      uncheckall_button = Button()
      uncheckall_button.Click += self.__fired_uncheckall
      uncheckall_button.Location = Point(280, 138)
      uncheckall_button.Size = Size(100, 23)
      uncheckall_button.Text = i18n.get("ConfigFormDetailsNone")
      
      # 4. --- build the update checklist (contains all the 'data' checkboxes)
      self.__update_checklist = CheckedListBox()
      self.__update_checklist.CheckOnClick = True
      self.__update_checklist.ColumnWidth = 125
      self.__update_checklist.ThreeDCheckBoxes = True
      self.__update_checklist.Location = Point(15, 65)
      self.__update_checklist.MultiColumn = True
      self.__update_checklist.SelectionMode = SelectionMode.One
      self.__update_checklist.Size = Size(260, 170)
      self.__update_checklist.ItemCheck += self.__fired_update_gui
      
      self.__update_checklist.Items.Add(ConfigForm.__SERIES_CB)
      self.__update_checklist.Items.Add(ConfigForm.__VOLUME_CB)
      self.__update_checklist.Items.Add(ConfigForm.__NUMBER_CB)
      self.__update_checklist.Items.Add(ConfigForm.__TITLE_CB)
      self.__update_checklist.Items.Add(ConfigForm.__PUBLISHED_CB)
      self.__update_checklist.Items.Add(ConfigForm.__RELEASED_CB)
      self.__update_checklist.Items.Add(ConfigForm.__CROSSOVERS_CB)
      self.__update_checklist.Items.Add(ConfigForm.__PUBLISHER_CB)
      self.__update_checklist.Items.Add(ConfigForm.__IMPRINT_CB)
      self.__update_checklist.Items.Add(ConfigForm.__WRITER_CB)
      self.__update_checklist.Items.Add(ConfigForm.__PENCILLER_CB)
      self.__update_checklist.Items.Add(ConfigForm.__INKER_CB)
      self.__update_checklist.Items.Add(ConfigForm.__COLORIST_CB)
      self.__update_checklist.Items.Add(ConfigForm.__LETTERER_CB)
      self.__update_checklist.Items.Add(ConfigForm.__COVER_ARTIST_CB)
      self.__update_checklist.Items.Add(ConfigForm.__EDITOR_CB)
      self.__update_checklist.Items.Add(ConfigForm.__SUMMARY_CB)
      self.__update_checklist.Items.Add(ConfigForm.__CHARACTERS_CB)
      self.__update_checklist.Items.Add(ConfigForm.__TEAMS_CB)
      self.__update_checklist.Items.Add(ConfigForm.__LOCATIONS_CB)     
      self.__update_checklist.Items.Add(ConfigForm.__WEBPAGE_CB)
   
      # 5. --- add 'em all to this tabpage
      tabpage.Controls.Add(label)
      tabpage.Controls.Add(checkall_button)
      tabpage.Controls.Add(uncheckall_button)
      tabpage.Controls.Add(self.__update_checklist)
      
      return tabpage

   
   
   # ==========================================================================
   def __build_behaviourtab(self):
      ''' builds and returns the "Behaviour" Tab for the TabControl '''
      
      tabpage = TabPage()
      tabpage.Text = i18n.get("ConfigFormBehaviourTab")
      
      # 1. --- build the 'When scraping for the first time' label
      first_scrape_label = Label()
      first_scrape_label.AutoSize = False
      first_scrape_label.FlatStyle = FlatStyle.System
      first_scrape_label.Location = Point(52, 27)
      first_scrape_label.Text = i18n.get("ConfigFormFirstScrapeLabel")
      first_scrape_label.Size = Size(300, 17)
      
      # 1. --- build the 'autochoose series' checkbox
      self.__autochoose_series_cb = CheckBox()
      self.__autochoose_series_cb.AutoSize = False
      self.__autochoose_series_cb.FlatStyle = FlatStyle.System
      self.__autochoose_series_cb.Location = Point(82, 45)
      self.__autochoose_series_cb.Size = Size(300, 34)
      self.__autochoose_series_cb.Text =i18n.get("ConfigFormAutochooseSeriesCB")
      self.__autochoose_series_cb.CheckedChanged += self.__fired_update_gui
       
      # 2. --- build the 'confirm issue' checkbox
      self.__confirm_issue_cb = CheckBox()
      self.__confirm_issue_cb.AutoSize = False
      self.__confirm_issue_cb.FlatStyle = FlatStyle.System
      self.__confirm_issue_cb.Location = Point(82, 75)
      self.__confirm_issue_cb.Size = Size(300, 34)
      self.__confirm_issue_cb.Text = i18n.get("ConfigFormConfirmIssueCB")
      self.__confirm_issue_cb.CheckedChanged += self.__fired_update_gui
      
      # 3. -- build the 'use fast rescrape' checkbox
      self.__fast_rescrape_cb = CheckBox()
      self.__fast_rescrape_cb.AutoSize = False
      self.__fast_rescrape_cb.FlatStyle = FlatStyle.System
      self.__fast_rescrape_cb.Location = Point(52, 116)
      self.__fast_rescrape_cb.Size = Size(300, 34)
      self.__fast_rescrape_cb.Text = i18n.get("ConfigFormRescrapeCB")
      self.__fast_rescrape_cb.CheckedChanged += self.__fired_update_gui
      
      # 4. -- build the 'add rescrape hints to notes' checkbox
      self.__rescrape_notes_cb = CheckBox()
      self.__rescrape_notes_cb.AutoSize = False
      self.__rescrape_notes_cb.FlatStyle = FlatStyle.System
      self.__rescrape_notes_cb.Location = Point(82, 151)
      self.__rescrape_notes_cb.Size = Size(270, 17)
      self.__rescrape_notes_cb.Text = i18n.get("ConfigFormRescrapeNotesCB")
      self.__rescrape_notes_cb.CheckedChanged += self.__fired_update_gui
      
      # 5. -- build the 'add rescrape hints to tags' checkbox
      self.__rescrape_tags_cb = CheckBox()
      self.__rescrape_tags_cb.AutoSize = False
      self.__rescrape_tags_cb.FlatStyle = FlatStyle.System
      self.__rescrape_tags_cb.Location = Point(82, 181)
      self.__rescrape_tags_cb.Size = Size(270, 17)
      self.__rescrape_tags_cb.Text = i18n.get("ConfigFormRescrapeTagsCB")
      self.__rescrape_tags_cb.CheckedChanged += self.__fired_update_gui 
   
      # 6. --- build the 'specify series name' checkbox
      self.__summary_dialog_cb = CheckBox()
      self.__summary_dialog_cb.AutoSize = False
      self.__summary_dialog_cb.FlatStyle = FlatStyle.System
      self.__summary_dialog_cb.Location = Point(52, 214)
      self.__summary_dialog_cb.Size = Size(300, 34)
      self.__summary_dialog_cb.Text = i18n.get("ConfigFormShowSummaryCB")
      self.__summary_dialog_cb.CheckedChanged += self.__fired_update_gui 
            
      # 7. --- add 'em all to the tabpage 
      tabpage.Controls.Add(first_scrape_label)
      tabpage.Controls.Add(self.__autochoose_series_cb)
      tabpage.Controls.Add(self.__confirm_issue_cb)
      tabpage.Controls.Add(self.__fast_rescrape_cb)
      tabpage.Controls.Add(self.__rescrape_tags_cb)
      tabpage.Controls.Add(self.__rescrape_notes_cb)
      tabpage.Controls.Add(self.__summary_dialog_cb)
      
      return tabpage
   
   
   
   # ==========================================================================
   def __build_datatab(self):
      ''' builds and returns the "Data" Tab for the TabControl '''
      
      tabpage = TabPage()
      tabpage.Text = i18n.get("ConfigFormDataTab")
      
      # 1. --- build the 'convert imprints checkbox'
      self.__convert_imprints_cb = CheckBox()
      self.__convert_imprints_cb.AutoSize = False
      self.__convert_imprints_cb.FlatStyle = FlatStyle.System
      self.__convert_imprints_cb.Location = Point(52, 35)
      self.__convert_imprints_cb.Size = Size(300, 34)
      self.__convert_imprints_cb.Text = i18n.get("ConfigFormImprintsCB")
      self.__convert_imprints_cb.CheckedChanged += self.__fired_update_gui
       
      # 2. -- build the 'overwrite existing' checkbox
      self.__ow_existing_cb = CheckBox()
      self.__ow_existing_cb.AutoSize = False
      self.__ow_existing_cb.FlatStyle = FlatStyle.System
      self.__ow_existing_cb.Location = Point(52, 85)
      self.__ow_existing_cb.Size = Size(310, 34)
      self.__ow_existing_cb.Text = i18n.get("ConfigFormOverwriteCB")
      self.__ow_existing_cb.CheckedChanged += self.__fired_update_gui 
   
      # 3. --- build the 'ignore blanks' checkbox
      self.__ignore_blanks_cb = CheckBox()                                          
      self.__ignore_blanks_cb.AutoSize = False                                       
      self.__ignore_blanks_cb.FlatStyle = FlatStyle.System                          
      self.__ignore_blanks_cb.Location = Point(82, 125)                             
      self.__ignore_blanks_cb.Size = Size(270, 34)                                  
      self.__ignore_blanks_cb.TextAlign = ContentAlignment.TopLeft                                  
      self.__ignore_blanks_cb.Text = i18n.get("ConfigFormOverwriteEmptyCB")                  
      self.__ignore_blanks_cb.CheckedChanged += self.__fired_update_gui 
   
      # 4. --- build the 'download thumbnails' checkbox
      self.__download_thumbs_cb = CheckBox()
      self.__download_thumbs_cb.AutoSize = False
      self.__download_thumbs_cb.FlatStyle = FlatStyle.System
      self.__download_thumbs_cb.Location = Point(52, 165)
      self.__download_thumbs_cb.Size = Size(300, 34)
      self.__download_thumbs_cb.Text = i18n.get("ConfigFormFilelessCB")
      self.__download_thumbs_cb.CheckedChanged += self.__fired_update_gui
      
      # 5. --- build the 'preserve thumbnails' checkbox
      self.__preserve_thumbs_cb = CheckBox()
      self.__preserve_thumbs_cb.AutoSize = False
      self.__preserve_thumbs_cb.FlatStyle = FlatStyle.System
      self.__preserve_thumbs_cb.Location = Point(82, 205)
      self.__preserve_thumbs_cb.Size = Size(270, 34)
      self.__preserve_thumbs_cb.TextAlign = ContentAlignment.TopLeft
      self.__preserve_thumbs_cb.Text = i18n.get("ConfigFormFilelessOverwriteCB")
      self.__preserve_thumbs_cb.CheckedChanged += self.__fired_update_gui
            
      # 6. --- add 'em all to the tabpage 
      tabpage.Controls.Add(self.__ow_existing_cb)
      tabpage.Controls.Add(self.__ignore_blanks_cb)
      tabpage.Controls.Add(self.__convert_imprints_cb)
      tabpage.Controls.Add(self.__download_thumbs_cb)
      tabpage.Controls.Add(self.__preserve_thumbs_cb)
      
      return tabpage
  
  
   # ==========================================================================
   def __build_advancedtab(self):
      ''' builds and returns the "Advanced" Tab for the TabControl '''
      
      tabpage = TabPage()
      tabpage.Text = i18n.get("ConfigFormAdvancedTab")
      
      
      # 1. --- a description label for this tabpage
      label = Label()
      label.UseMnemonic = False
      label.AutoSize = True
      label.Location = Point(14, 25)
      label.Size = Size(299, 17)
      label.Text = i18n.get("ConfigFormAdvancedText")
      
      
      # 2. --- build the update checklist (contains all the 'data' checkboxes)
      tbox = RichTextBox()
      tbox.Multiline=True
      tbox.MaxLength=65536
      tbox.WordWrap = True
      tbox.Location = Point(15, 50)
      tbox.Size = Size(355, 200)
      
      menu = ContextMenu()
      items = menu.MenuItems
      items.Add( MenuItem(i18n.get("TextCut"), lambda s, ea : tbox.Cut() ) )
      items.Add( MenuItem(i18n.get("TextCopy"), lambda s, ea : tbox.Copy() ) )
      items.Add( MenuItem(i18n.get("TextPaste"), lambda s, ea : tbox.Paste() ) )
      tbox.ContextMenu = menu
      self.__advanced_tbox = tbox
      
      # 3. --- add 'em all to the tabpage 
      tabpage.Controls.Add(label)
      tabpage.Controls.Add(self.__advanced_tbox)
      
      return tabpage
         
   # ==========================================================================
   def show_form(self):
      '''
      Displays this form, blocking until the user closes it.  When it is closed,
      this method will return a Configuration object containing the settings 
      that this dialog was displaying when it was closed (these settings were
      also just saved on the filesystem, so they are also the settings that 
      this dialog will display the next time it is opened.)
      
      If the user clicks 'Cancel' then this method will simply return null. 
      '''
      
      log.debug("opened the settings dialog.")
      defaults = Configuration()
      defaults.load_defaults()
      self.__set_configuration(defaults) 
      self.__switch_to_best_tab()
      dialogAnswer = self.ShowDialog() # blocks
      if dialogAnswer == DialogResult.OK:
         config = self.__get_configuration()
         config.save_defaults()
         log.debug("closed the settings dialog.")
      else:
         config = None
         log.debug("cancelled the settings dialog.")
      return config

  
   # ==========================================================================
   def __switch_to_best_tab(self):
      ''' Chooses the best tab to be displayed, and switch to it. '''
      have_api_key = self.__api_key_tbox.Text.strip()
      if have_api_key:
         for tab in self.__tabcontrol.Controls.Find("details", False):
            self.__tabcontrol.SelectedTab = tab
      else:
         for tab in self.__tabcontrol.Controls.Find("comicvine", False):
            self.__tabcontrol.SelectedTab = tab
      
      
   # ==========================================================================
   def __get_configuration(self):
      '''
      Returns a Configuration object the describes the current state of all the
      gui components on this ConfigForm.
      '''
      
      def is_checked( checkbox ):
         return self.__update_checklist.GetItemChecked( \
            self.__update_checklist.Items.IndexOf(checkbox) )
      
      config = Configuration()
      
      # 1. --- first get the parts from the checklist box (data tab)
      config.update_series_b = is_checked(ConfigForm.__SERIES_CB)
      config.update_number_b = is_checked(ConfigForm.__NUMBER_CB)
      config.update_published_b = is_checked(ConfigForm.__PUBLISHED_CB)
      config.update_released_b = is_checked(ConfigForm.__RELEASED_CB)
      config.update_title_b = is_checked(ConfigForm.__TITLE_CB)
      config.update_crossovers_b = is_checked(ConfigForm.__CROSSOVERS_CB)
      config.update_writer_b = is_checked(ConfigForm.__WRITER_CB)
      config.update_penciller_b = is_checked(ConfigForm.__PENCILLER_CB)
      config.update_inker_b = is_checked(ConfigForm.__INKER_CB)
      config.update_cover_artist_b = is_checked(ConfigForm.__COVER_ARTIST_CB)
      config.update_colorist_b = is_checked(ConfigForm.__COLORIST_CB)
      config.update_letterer_b = is_checked(ConfigForm.__LETTERER_CB)
      config.update_editor_b = is_checked(ConfigForm.__EDITOR_CB)
      config.update_summary_b = is_checked(ConfigForm.__SUMMARY_CB)
      config.update_imprint_b = is_checked(ConfigForm.__IMPRINT_CB)
      config.update_publisher_b = is_checked(ConfigForm.__PUBLISHER_CB)
      config.update_volume_b = is_checked(ConfigForm.__VOLUME_CB)
      config.update_characters_b = is_checked(ConfigForm.__CHARACTERS_CB)
      config.update_teams_b = is_checked(ConfigForm.__TEAMS_CB)
      config.update_locations_b = is_checked(ConfigForm.__LOCATIONS_CB)
      config.update_webpage_b = is_checked(ConfigForm.__WEBPAGE_CB)

      
      # 2. --- then get the parts from the other checkboxes (options tab)
      config.ow_existing_b = self.__ow_existing_cb.Checked
      config.convert_imprints_b = self.__convert_imprints_cb.Checked
      config.autochoose_series_b = self.__autochoose_series_cb.Checked
      config.confirm_issue_b = self.__confirm_issue_cb.Checked
      config.ignore_blanks_b = self.__ignore_blanks_cb.Checked
      config.download_thumbs_b = self.__download_thumbs_cb.Checked
      config.preserve_thumbs_b = self.__preserve_thumbs_cb.Checked
      config.fast_rescrape_b = self.__fast_rescrape_cb.Checked
      config.rescrape_notes_b = self.__rescrape_notes_cb.Checked
      config.rescrape_tags_b = self.__rescrape_tags_cb.Checked
      config.summary_dialog_b = self.__summary_dialog_cb.Checked
      
      # 3. --- then get the string out of the advanced settings textbox
      config.advanced_settings_s = self.__advanced_tbox.Text
      config.api_key_s = self.__api_key_tbox.Text.strip()
      
      return config
 
 
   
   # ==========================================================================
   def __set_configuration(self, config):
      '''
      Sets the state of all the gui components on this ConfigForm to match the 
      contents of the given Configuration object.
      '''
      
      def set_checked( checkbox, checked ):
         self.__update_checklist.SetItemChecked( \
            self.__update_checklist.Items.IndexOf(checkbox), checked )
      
      # 1. --- set get the parts in the checklist box (data tab)
      set_checked(ConfigForm.__SERIES_CB, config.update_series_b)
      set_checked(ConfigForm.__NUMBER_CB, config.update_number_b)
      set_checked(ConfigForm.__PUBLISHED_CB, config.update_published_b)
      set_checked(ConfigForm.__RELEASED_CB, config.update_released_b)
      set_checked(ConfigForm.__TITLE_CB, config.update_title_b)
      set_checked(ConfigForm.__CROSSOVERS_CB, config.update_crossovers_b)
      set_checked(ConfigForm.__WRITER_CB, config.update_writer_b)
      set_checked(ConfigForm.__PENCILLER_CB, config.update_penciller_b)
      set_checked(ConfigForm.__INKER_CB, config.update_inker_b)
      set_checked(ConfigForm.__COVER_ARTIST_CB,config.update_cover_artist_b)
      set_checked(ConfigForm.__COLORIST_CB, config.update_colorist_b)
      set_checked(ConfigForm.__LETTERER_CB, config.update_letterer_b)
      set_checked(ConfigForm.__EDITOR_CB, config.update_editor_b)
      set_checked(ConfigForm.__SUMMARY_CB, config.update_summary_b)
      set_checked(ConfigForm.__IMPRINT_CB, config.update_imprint_b)
      set_checked(ConfigForm.__PUBLISHER_CB, config.update_publisher_b)
      set_checked(ConfigForm.__VOLUME_CB, config.update_volume_b)
      set_checked(ConfigForm.__CHARACTERS_CB, config.update_characters_b)
      set_checked(ConfigForm.__TEAMS_CB, config.update_teams_b)
      set_checked(ConfigForm.__LOCATIONS_CB, config.update_locations_b)
      set_checked(ConfigForm.__WEBPAGE_CB, config.update_webpage_b)
      
      # 2. --- then get the parts in the other checkboxes (options tab)
      self.__ow_existing_cb.Checked = config.ow_existing_b
      self.__convert_imprints_cb.Checked = config.convert_imprints_b
      self.__autochoose_series_cb.Checked = config.autochoose_series_b
      self.__confirm_issue_cb.Checked = config.confirm_issue_b
      self.__ignore_blanks_cb.Checked = config.ignore_blanks_b
      self.__download_thumbs_cb.Checked = config.download_thumbs_b
      self.__preserve_thumbs_cb.Checked = config.preserve_thumbs_b
      self.__fast_rescrape_cb.Checked = config.fast_rescrape_b
      self.__rescrape_notes_cb.Checked = config.rescrape_notes_b
      self.__rescrape_tags_cb.Checked = config.rescrape_tags_b
      self.__summary_dialog_cb.Checked = config.summary_dialog_b
      
      # 3. --- finally, set the contents in the textboxes
      self.__advanced_tbox.Text = config.advanced_settings_s
      self.__api_key_tbox.Text = config.api_key_s.strip()
      
      self.__fired_update_gui()
      
      
      
   # ==========================================================================
   def __fired_restore_defaults(self, sender, args):
      ''' called when the user clicks the "restore defaults"  button '''
      
      api_key_s = self.__api_key_tbox.Text # preserve API key
      self.__set_configuration(Configuration())
      self.__api_key_tbox.Text = api_key_s
      log.debug("all settings were restored to their default values")
      self.__fired_update_gui()
      
      
      
   # ==========================================================================
   def __fired_update_gui(self, sender = None, args = None):
      ''' called anytime the gui for this form should be updated '''
      self.__ignore_blanks_cb.Enabled = self.__ow_existing_cb.Checked
      self.__preserve_thumbs_cb.Enabled = self.__download_thumbs_cb.Checked
      if self.__confirm_issue_cb.Checked:
         self.__autochoose_series_cb.Checked = False
      if self.__autochoose_series_cb.Checked:
         self.__confirm_issue_cb.Checked = False
      self.__confirm_issue_cb.Enabled = not self.__autochoose_series_cb.Checked
      self.__autochoose_series_cb.Enabled = not self.__confirm_issue_cb.Checked
      
      # ok button is disabled if we have no API key
      self.__ok_button.Enabled = self.__api_key_tbox.Text.strip()      
       
              
   # ==========================================================================
   def __fired_linkclicked(self, sender, args):
      ''' called when the user clicks the api key linklabel '''
      System.Diagnostics.Process.Start("http://www.comicvine.gamespot.com/api");
   
   # ==========================================================================
   def __fired_checkall(self, sender, args):
      ''' called when the user clicks the "select all" button '''
      for i in range(self.__update_checklist.Items.Count):
      
         self.__update_checklist.SetItemChecked(i, True)
   
   
   # ==========================================================================
   def __fired_uncheckall(self, sender, args):
      ''' called when the user clicks the "select none" button '''
      for i in range(self.__update_checklist.Items.Count):
         self.__update_checklist.SetItemChecked(i, False)
