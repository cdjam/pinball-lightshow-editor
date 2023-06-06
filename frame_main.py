# python imports
import time
import wx
import wx.aui

# local imports
import __init__
import combo_data
import constants
import data_panel
import event_handler
import lightshow_data
import playfield_panel

# constants
TITLE = "Pinball Lightshow Editor: v{} | ".format(__init__.__version__)
TITLE_SUFFIX_NEW_FILE = "New File"


class FrameMain(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, size=(768, 750))
        self.SetMinSize((768,750))

        self._event_handler = event_handler.event_handler
        self._event_handler.add_listener(self, self.handle_event)

        # instance variables
        self._current_save_filepath_map = {} # save location from save as/load per notebook page
        self._playfield_panel = None # hold panel for updating
        self._update_timer = None # timer for update
        
        # set wx title
        self.SetTitle(TITLE + TITLE_SUFFIX_NEW_FILE)
        
        self._setup()
        
        # bind close event to our own handler
        self.Bind(wx.EVT_CLOSE, self._on_close_window)
        
        # start update timer
        self._update_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_update_timer, self._update_timer)
        self._update_timer.Start(1)
        

    def handle_event(self, event):
        # notebook page active
        if event.event_type == event_handler.EVENT_TYPE_NOTEBOOK_PAGE_ACTIVE:
            if event.data["active_page"].get_type() in self._current_save_filepath_map:
                self.SetTitle(TITLE + self._current_save_filepath_map[event.data["active_page"].get_type()])
            else:
                self.SetTitle(TITLE + TITLE_SUFFIX_NEW_FILE)

    
    def _setup(self):
        menu_bar = self._create_menu_bar()
        self.SetMenuBar(menu_bar)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # data_panel holds editor data
        self._editor_panel = data_panel.DataPanel(self)

        # playfield panel holds playfield image and clickables
        self._playfield_panel = playfield_panel.PlayfieldPanel(self)
        
        sizer.Add(self._editor_panel, 1, wx.EXPAND)
        sizer.Add(self._playfield_panel, 0, wx.EXPAND)
        self.SetSizer(sizer)

        # create accelerator for menu bar bindings
        accelerator_table = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("O"), self._menu_load.GetId() ),
                                                      (wx.ACCEL_CTRL, ord("S"), self._menu_save.GetId()),
                                                      (wx.ACCEL_CTRL + wx.ACCEL_SHIFT, ord("S"), self._menu_save_as.GetId())
                                                      ])

        self.SetAcceleratorTable(accelerator_table)
        
    
    def _create_menu_bar(self):
        # create the menu bar
        menu_bar = wx.MenuBar()
        
        menu_bar.Append(self._create_menu_file(), "File")

        return menu_bar
        
        
    def _create_menu_file(self):
        menu = wx.Menu()

        menu_new = menu.Append(wx.ID_ANY, "New", "New")
        self.Bind(wx.EVT_MENU, self._on_new, menu_new)

        menu.AppendSeparator()
        
        self._menu_load = menu.Append(wx.ID_ANY, "Load (Ctrl+O)", "Load")
        self.Bind(wx.EVT_MENU, self._on_load, self._menu_load)
        
        self._menu_save = menu.Append(wx.ID_ANY, "Save (Ctrl+S)", "Save")
        self.Bind(wx.EVT_MENU, self._on_save, self._menu_save)
        
        self._menu_save_as = menu.Append(wx.ID_ANY, "Save As (Shift+Ctrl+S)", "Save As")
        self.Bind(wx.EVT_MENU, self._on_save_as, self._menu_save_as)
        
        menu.AppendSeparator()
        
        exit = menu.Append(wx.ID_ANY, "Exit", "Exit")
        self.Bind(wx.EVT_MENU, self._on_close_window, exit)

        return menu
        

    def _save_file(self, filepath):
        if self._editor_panel.get_current_type() == constants.LIGHTSHOW_EDITOR_TYPE:
            try:
                with open(filepath, "w") as file:
                    # save data
                    ls_middleware = lightshow_data.LightshowDataMiddleware()

                    segments = self._editor_panel.get_lightshow_editor_segment_logic_objs()

                    ls_middleware.from_lightshow_logic_list(segments)

                    if not ls_middleware.save(filepath):
                        return False
                    
                self._current_save_filepath_map[self._editor_panel.get_current_type()] = filepath
                self.SetTitle(TITLE + filepath)

                return True
            except IOError:
                return False
        elif self._editor_panel.get_current_type() == constants.COMBO_EDITOR_TYPE:
            try:
                with open(filepath, "w") as file:
                    # save data
                    combo_middleware = combo_data.ComboDataMiddleware()

                    milliseconds_to_run, lightshow_filepaths = self._editor_panel.get_combo_editor_segment().get_current_values()
                    combo_middleware.load_from_values(milliseconds_to_run, lightshow_filepaths)

                    if not combo_middleware.save(filepath):
                        return False
                    
                self._current_save_filepath_map[self._editor_panel.get_current_type()] = filepath
                self.SetTitle(TITLE + filepath)

                return True
            except IOError:
                return False

        return True

    
    # event methods

    def _on_new(self, event):
        self._editor_panel.clear_current()


    def _on_load(self, event):
        # load depends on current editor panel selection
        if self._editor_panel.get_current_type() == constants.LIGHTSHOW_EDITOR_TYPE:
            with wx.FileDialog(self, "Load lightshow", wildcard="Lightshow files (*.ls)|*.ls", 
                style=wx.FD_OPEN  | wx.FD_FILE_MUST_EXIST) as fileDialog:
                
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return True
                
                try:
                    with open(fileDialog.GetPath(), "r") as file:
                        # load data
                        ls_middleware = lightshow_data.LightshowDataMiddleware()

                        if not ls_middleware.load(fileDialog.GetPath()):
                            return False

                        lightshow_logic_list = ls_middleware.to_lightshow_logic_list()

                        event = event_handler.Event(event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_LOAD_DATA, {"lightshow_logic_list": lightshow_logic_list})
                        self._event_handler.send_event(self, event)
                    
                    self._current_save_filepath_map[self._editor_panel.get_current_type()] = fileDialog.GetPath()
                    self.SetTitle(TITLE + fileDialog.GetPath())
                    
                    return True
                except IOError:
                    return False
        elif self._editor_panel.get_current_type() == constants.COMBO_EDITOR_TYPE:
            with wx.FileDialog(self, "Load lightshow combo", wildcard="Lightshow combo files (*.lc)|*.lc", 
                style=wx.FD_OPEN  | wx.FD_FILE_MUST_EXIST) as fileDialog:
                
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return True

                try:
                    with open(fileDialog.GetPath(), "r") as file:
                        # load data
                        combo_middleware = combo_data.ComboDataMiddleware()

                        if not combo_middleware.load(fileDialog.GetPath()):
                            return False

                        event_data = {}
                        event_data["milliseconds_to_run"] = combo_middleware.combo_data.milliseconds_to_run
                        event_data["lightshow_files"] = combo_middleware.combo_data.lightshow_files

                        event = event_handler.Event(event_handler.EVENT_TYPE_COMBO_EDITOR_LOAD_DATA, {"combo_load_data": event_data})
                        self._event_handler.send_event(self, event)
                    
                    self._current_save_filepath_map[self._editor_panel.get_current_type()] = fileDialog.GetPath()
                    self.SetTitle(TITLE + fileDialog.GetPath())
                    
                    return True
                except IOError:
                    return False
                
                
    def _on_save(self, event):
        # save depends on current editor panel selection
        if self._editor_panel.get_current_type() == constants.LIGHTSHOW_EDITOR_TYPE or \
           self._editor_panel.get_current_type() == constants.COMBO_EDITOR_TYPE:
            if self._editor_panel.get_current_type() not in self._current_save_filepath_map:
                return self._on_save_as(event)
            else:
                return self._save_file(self._current_save_filepath_map[self._editor_panel.get_current_type()])
        
        return False

        
    def _on_save_as(self, event):
        # save depends on current editor panel selection
        if self._editor_panel.get_current_type() == constants.LIGHTSHOW_EDITOR_TYPE:
            with wx.FileDialog(self, "Save lightshow", wildcard="Lightshow files (*.ls)|*.ls", 
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return True
                    
                return self._save_file(fileDialog.GetPath())
        elif self._editor_panel.get_current_type() == constants.COMBO_EDITOR_TYPE:
            with wx.FileDialog(self, "Save lightshow combo", wildcard="Lightshow combo files (*.lc)|*.lc", 
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return True
                    
                return self._save_file(fileDialog.GetPath())

        return False
                
       
    def _on_close_window(self, event):
        self._update_timer.Stop()
        self.DestroyChildren()
        self.Destroy()
        
        
    def _on_update_timer(self, event):
        self._editor_panel.update()
        self._playfield_panel.update()