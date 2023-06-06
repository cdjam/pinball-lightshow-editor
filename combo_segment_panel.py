# python imports
import os
import string
import wx

# local imports
import combo_logic
import constants
import event_handler
import lightshow_data
import utility

# constants
SEGMENT_COUNT_LABEL = "Segments: "


class ComboSegment(wx.Panel):
    def __init__(self, parent, id, filepath):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.SetMinSize((200, 50))

        self._filepath = filepath
        self._combo_logic = combo_logic.ComboLogic()

        self._id = id
        self._previous_order_id = None

        self._event_handler = event_handler.event_handler

        toolbar = self._create_toolbar(self, id)

        # events for our panel
        self.Bind(wx.EVT_LEFT_UP, self._on_focus)

        # create sizer
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._main_sizer.Add(toolbar, 1)
        self.SetSizer(self._main_sizer)

        self._setup()

        # set on focus binding for all children in key elements
        for child in self.GetChildren():
            child.Bind(wx.EVT_LEFT_UP, self._on_focus)

        for child in toolbar.GetChildren():
            child.Bind(wx.EVT_LEFT_UP, self._on_focus)

        for child in self._main_panel.GetChildren():
            child.Bind(wx.EVT_LEFT_UP, self._on_focus)


    def destroy(self):
        self._event_handler.remove_listener(self)


    def get_loaded_file(self):
        return os.path.basename(self._filepath)


    def load_file_data(self):
        ls_middleware = lightshow_data.LightshowDataMiddleware()

        if ls_middleware.load(self._filepath):
            self._reset()

            self._combo_logic.set_lightshow_logic_list(ls_middleware.to_lightshow_logic_list())

            self._segment_count_label.SetLabel(SEGMENT_COUNT_LABEL + str(len(self._combo_logic.lightshow_logic_list)))
        else:
            return False

        return True


    def get_logic(self):
        return self._combo_logic


    def set_id(self, id):
        self._id = id
        self._previous_order_id = id


    def get_id(self):
        return self._id


    def _setup(self):
        self._main_panel = wx.Panel(self)
        self._main_panel.Bind(wx.EVT_LEFT_UP, self._on_focus)

        # panel sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        #sub-data here if needed
        self._main_panel.SetSizer(sizer)

        self._main_sizer.Add(self._main_panel, 1, wx.EXPAND)
        self._main_sizer.Layout()
        

    def _reset(self):
        self._playing = False
        self._combo_logic.lightshow_logic_list = []
        self._main_panel.DestroyChildren()


    def _create_toolbar(self, parent, id):
        icon_size = (20, 20)
        button_size = (26, 26)

        toolbar_panel = wx.Panel(parent, style=wx.BORDER_THEME)
        toolbar_panel.SetMaxSize((-1, 40))
        toolbar_panel.SetMinSize((5000, 40))

        file_to_run_text = wx.StaticText(toolbar_panel, wx.ID_ANY, os.path.basename(self._filepath))

        x_button = utility.create_toolbar_button_sized(toolbar_panel, icon_size, button_size, "data/icon_x.png", "data/icon_x_pressed.png", self._on_x_button_pressed)

        self._segment_count_label = wx.StaticText(toolbar_panel, wx.ID_ANY, SEGMENT_COUNT_LABEL + "0")

        # create sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(file_to_run_text, 0, wx.TOP | wx.LEFT, 7)
        sizer.Add(x_button, 1, wx.TOP | wx.LEFT, 5)
        sizer.Add(self._segment_count_label, 1, wx.TOP | wx.LEFT, 7)
        toolbar_panel.SetSizer(sizer)

        return toolbar_panel


    def _send_focus_msg(self):
        my_event = event_handler.Event(event_handler.EVENT_TYPE_COMBO_EDITOR_SEGMENT_SELECTED, {"id":self._id})
        self._event_handler.send_event(self, my_event)
        

    # event methods

    def _on_focus(self, event):
        self._previous_order_id = self._id
        self._send_focus_msg()
        event.Skip()


    def _on_x_button_pressed(self, event):
        my_event = event_handler.Event(event_handler.EVENT_TYPE_COMBO_EDITOR_REMOVE, {"id":self._id})
        self._event_handler.send_event(self, my_event)

        self._event_handler.remove_listener(self)