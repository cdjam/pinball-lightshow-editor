# python imports
import random
import string
import wx

# local imports
import event_handler
import lightshow_logic
import utility

# constants
DEFAULT_MILLISECONDS_TO_RUN_ENABLE = 500
DEFAULT_MILLISECONDS_TO_RUN_RANDOM = 15000
LED_COUNT_LABEL = "LedCount: "
ENABLE_LABEL = "En"
RANDOM_LABEL = "Rd"
MILLISECONDS_TO_RUN_LABEL = "Ms To Run: "
MILLISECONDS_TO_FLASH_LABEL = "Flash Ms Range: "
LEDS_TO_CHOOSE_LABEL = "# Leds To Choose: "
MIN_MAX_SEPARATOR = " - "


def get_unique_id():
    global unique_id

    try:
        unique_id += 1
    except:
        unique_id = 1
    
    return unique_id


class LightshowSegment(wx.Panel):
    def __init__(self, parent, id, type_label, logic_obj=None):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.SetMinSize((200, 125))

        # must be set by child
        if logic_obj:
            self._lightshow_logic = logic_obj
        else:
            self._lightshow_logic = None

        self._id = id
        self._previous_order_id = None

        self._event_handler = event_handler.event_handler
        self._event_handler.add_listener(self, self.handle_event)

        toolbar = self._create_toolbar(self, id, type_label)

        # events for our panel
        self.Bind(wx.EVT_LEFT_UP, self._on_focus)
        toolbar.Bind(wx.EVT_LEFT_UP, self._on_focus)

        # create sizer
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._main_sizer.Add(toolbar, 1)
        self.SetSizer(self._main_sizer)


    def set_id(self, id):
        self._id = id
        self._previous_order_id = id
        self._order_text.SetValue(str(id))


    def destroy(self):
        self._event_handler.remove_listener(self)
        

    def get_id(self):
        return self._id


    def get_logic(self):
        raise Exception("Must overwrite in sub-class!")


    def handle_event(self, event):
        if event.event_type == event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_ADD_LED and event.data["recv_id"] == self._id:
            if event.data["led_name"] not in self._lightshow_logic.leds:
                self._lightshow_logic.leds.append(event.data["led_name"])
                self._led_count_label.SetLabel(LED_COUNT_LABEL + str(len(self._lightshow_logic.leds)))
        elif event.event_type == event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_REMOVE_LED and event.data["recv_id"] == self._id:
            if event.data["led_name"] in self._lightshow_logic.leds:
                self._lightshow_logic.leds.remove(event.data["led_name"])
                self._led_count_label.SetLabel(LED_COUNT_LABEL + str(len(self._lightshow_logic.leds)))


    def _create_toolbar(self, parent, id, type_label):
        icon_size = (20, 20)
        button_size = (26, 26)

        toolbar_panel = wx.Panel(parent, style=wx.BORDER_THEME)
        toolbar_panel.SetMaxSize((-1, 40))
        toolbar_panel.SetMinSize((5000, 40))

        # give global id to help identify panel when changing positions
        type_text = wx.StaticText(toolbar_panel, wx.ID_ANY, type_label + str(get_unique_id()))
        
        self._order_text = wx.TextCtrl(toolbar_panel, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self._order_text.SetMaxSize((100, 26))
        self._order_text.SetValue(str(id))
        self._order_text.Bind(wx.EVT_TEXT_ENTER, self._on_order_text_changed)
        self._order_text.Bind(wx.EVT_LEFT_UP, self._on_focus)

        up_button = utility.create_toolbar_button_sized(toolbar_panel, icon_size, button_size, "data/icon_up.png", "data/icon_up_pressed.png", self._on_up_button_pressed)
        down_button = utility.create_toolbar_button_sized(toolbar_panel, icon_size, button_size, "data/icon_down.png", "data/icon_down_pressed.png", self._on_down_button_pressed)
        x_button = utility.create_toolbar_button_sized(toolbar_panel, icon_size, button_size, "data/icon_x.png", "data/icon_x_pressed.png", self._on_x_button_pressed)

        led_count = 0

        if self._lightshow_logic:
            led_count = len(self._lightshow_logic.leds)

        self._led_count_label = wx.StaticText(toolbar_panel, wx.ID_ANY, LED_COUNT_LABEL + str(led_count))

        # create sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(type_text, 0, wx.TOP | wx.LEFT, 7)
        sizer.Add(self._order_text, 1, wx.TOP | wx.LEFT, 7)
        sizer.Add(up_button, 1, wx.TOP | wx.LEFT, 5)
        sizer.Add(down_button, 1, wx.TOP | wx.RIGHT, 5)
        sizer.Add(x_button, 1, wx.TOP | wx.LEFT, 5)
        sizer.Add(self._led_count_label, 1, wx.TOP | wx.LEFT, 7)
        toolbar_panel.SetSizer(sizer)

        return toolbar_panel


    def _send_focus_msg(self):
        my_event = event_handler.Event(event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_SEGMENT_SELECTED, {"id":self._id})
        self._event_handler.send_event(self, my_event)

    # event methods

    def _on_order_text_changed(self, event):
        new_order_id = self._order_text.GetValue()

        try:
            new_order_id = int(new_order_id)
        except:
            if self._previous_order_id:
                new_order_id = self._previous_order_id
            else:
                new_order_id = None

        if new_order_id is not None:
            my_event = event_handler.Event(event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_CHANGE_POSITION, {"id":self._id, "new_id":new_order_id})
            self._event_handler.send_event(self, my_event)

        self._send_focus_msg()


    def _on_focus(self, event):
        self._previous_order_id = self._id
        self._send_focus_msg()
        event.Skip()


    def _on_up_button_pressed(self, event):
        my_event = event_handler.Event(event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_MOVE_UP, {"id":self._id})
        self._event_handler.send_event(self, my_event)
        self._send_focus_msg()


    def _on_down_button_pressed(self, event):
        my_event = event_handler.Event(event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_MOVE_DOWN, {"id":self._id})
        self._event_handler.send_event(self, my_event)
        self._send_focus_msg()


    def _on_x_button_pressed(self, event):
        my_event = event_handler.Event(event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_REMOVE, {"id":self._id})
        self._event_handler.send_event(self, my_event)

        self._event_handler.remove_listener(self)


class LightShowSegmentEnable(LightshowSegment):
    def __init__(self, parent, id, logic_obj=None):
        LightshowSegment.__init__(self, parent, id, ENABLE_LABEL, logic_obj)

        if not logic_obj:
            self._lightshow_logic = lightshow_logic.LightshowLogicEnable()
            self._lightshow_logic.milliseconds_to_run = DEFAULT_MILLISECONDS_TO_RUN_ENABLE

        self._setup()


    def get_logic(self):
        return self._lightshow_logic


    def _setup(self):
        panel = wx.Panel(self)
        panel.Bind(wx.EVT_LEFT_UP, self._on_focus)

        milliseconds_to_run_label = wx.StaticText(panel, wx.ID_ANY, MILLISECONDS_TO_RUN_LABEL)

        self._milliseconds_to_run_text = wx.TextCtrl(panel, wx.ID_ANY)
        self._milliseconds_to_run_text.SetValue(str(self._lightshow_logic.milliseconds_to_run))
        self._milliseconds_to_run_text.Bind(wx.EVT_TEXT, self._on_milliseconds_changed)
        self._milliseconds_to_run_text.Bind(wx.EVT_LEFT_UP, self._on_focus)

        ms_to_run_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ms_to_run_sizer.Add(milliseconds_to_run_label, 0, wx.TOP, 4)
        ms_to_run_sizer.Add(self._milliseconds_to_run_text, 0)

        # panel sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(ms_to_run_sizer, 0, wx.TOP | wx.LEFT, 7)
        panel.SetSizer(sizer)

        self._main_sizer.Add(panel, 1, wx.EXPAND)
        self._main_sizer.Layout()


    def _on_milliseconds_changed(self, event):
        try:
            self._lightshow_logic.milliseconds_to_run = int(self._milliseconds_to_run_text.GetValue())
        except:
            self._milliseconds_to_run_text.SetValue(str(self._lightshow_logic.milliseconds_to_run))

        # pass on event for more handling
        event.Skip()


class LightShowSegmentRandom(LightshowSegment):
    def __init__(self, parent, id, logic_obj=None):
        LightshowSegment.__init__(self, parent, id, RANDOM_LABEL, logic_obj)

        if not logic_obj:
            self._lightshow_logic = lightshow_logic.LightshowLogicRandom()
            self._lightshow_logic.milliseconds_to_run = DEFAULT_MILLISECONDS_TO_RUN_RANDOM
            self._lightshow_logic.milliseconds_flash_min = 500
            self._lightshow_logic.milliseconds_flash_max = 1000
            self._lightshow_logic.number_of_leds_to_pick_min = 1
            self._lightshow_logic.number_of_leds_to_pick_max = 1

        self._setup()


    def get_random_info(self):
        return (self._lightshow_logic.milliseconds_flash_min, self._lightshow_logic.milliseconds_flash_max, 
                self._lightshow_logic.number_of_leds_to_pick_min, self._lightshow_logic.number_of_leds_to_pick_max)


    def get_logic(self):
        return self._lightshow_logic


    def _setup(self):
        panel = wx.Panel(self)
        panel.Bind(wx.EVT_LEFT_UP, self._on_focus)

        # ms to run
        milliseconds_to_run_label = wx.StaticText(panel, wx.ID_ANY, MILLISECONDS_TO_RUN_LABEL)

        self._milliseconds_to_run_text = wx.TextCtrl(panel, wx.ID_ANY)
        self._milliseconds_to_run_text.SetValue(str(self._lightshow_logic.milliseconds_to_run))
        self._milliseconds_to_run_text.Bind(wx.EVT_TEXT, self._on_milliseconds_changed)
        self._milliseconds_to_run_text.Bind(wx.EVT_LEFT_UP, self._on_focus)

        ms_to_run_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ms_to_run_sizer.Add(milliseconds_to_run_label, 0, wx.TOP, 4)
        ms_to_run_sizer.Add(self._milliseconds_to_run_text, 0)

        # flash min-max
        milliseconds_flash_label = wx.StaticText(panel, wx.ID_ANY, MILLISECONDS_TO_FLASH_LABEL)
        milliseconds_flash_separator_label = wx.StaticText(panel, wx.ID_ANY, MIN_MAX_SEPARATOR)

        self._milliseconds_flash_min_text = wx.TextCtrl(panel, wx.ID_ANY)
        self._milliseconds_flash_min_text.SetValue(str(self._lightshow_logic.milliseconds_flash_min))
        self._milliseconds_flash_min_text.Bind(wx.EVT_TEXT, self._on_milliseconds_flash_changed)
        self._milliseconds_flash_min_text.Bind(wx.EVT_LEFT_UP, self._on_focus)

        self._milliseconds_flash_max_text = wx.TextCtrl(panel, wx.ID_ANY)
        self._milliseconds_flash_max_text.SetValue(str(self._lightshow_logic.milliseconds_flash_max))
        self._milliseconds_flash_max_text.Bind(wx.EVT_TEXT, self._on_milliseconds_flash_changed)
        self._milliseconds_flash_max_text.Bind(wx.EVT_LEFT_UP, self._on_focus)

        ms_flash_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ms_flash_sizer.Add(milliseconds_flash_label, 0, wx.TOP, 4)
        ms_flash_sizer.Add(self._milliseconds_flash_min_text, 0, wx.LEFT, 4)
        ms_flash_sizer.Add(milliseconds_flash_separator_label, wx.LEFT, 4)
        ms_flash_sizer.Add(self._milliseconds_flash_max_text, 0, wx.LEFT, 4)

        # number of leds to choose
        leds_to_choose_label = wx.StaticText(panel, wx.ID_ANY, LEDS_TO_CHOOSE_LABEL)
        leds_to_choose_separator_label = wx.StaticText(panel, wx.ID_ANY, MIN_MAX_SEPARATOR)

        self._leds_to_choose_min_text = wx.TextCtrl(panel, wx.ID_ANY)
        self._leds_to_choose_min_text.SetValue(str(self._lightshow_logic.number_of_leds_to_pick_min))
        self._leds_to_choose_min_text.Bind(wx.EVT_TEXT, self._on_leds_to_choose_changed)
        self._leds_to_choose_min_text.Bind(wx.EVT_LEFT_UP, self._on_focus)

        self._leds_to_choose_max_text = wx.TextCtrl(panel, wx.ID_ANY)
        self._leds_to_choose_max_text.SetValue(str(self._lightshow_logic.number_of_leds_to_pick_max))
        self._leds_to_choose_max_text.Bind(wx.EVT_TEXT, self._on_leds_to_choose_changed)
        self._leds_to_choose_max_text.Bind(wx.EVT_LEFT_UP, self._on_focus)

        leds_to_choose_sizer = wx.BoxSizer(wx.HORIZONTAL)
        leds_to_choose_sizer.Add(leds_to_choose_label, 0, wx.TOP, 4)
        leds_to_choose_sizer.Add(self._leds_to_choose_min_text, 0, wx.LEFT, 4)
        leds_to_choose_sizer.Add(leds_to_choose_separator_label, wx.LEFT, 4)
        leds_to_choose_sizer.Add(self._leds_to_choose_max_text, 0, wx.LEFT, 4)

        # panel sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(ms_to_run_sizer, 0, wx.TOP | wx.LEFT, 7)
        sizer.Add(ms_flash_sizer, 0, wx.LEFT, 7)
        sizer.Add(leds_to_choose_sizer, 0, wx.LEFT, 7)
        panel.SetSizer(sizer)

        self._main_sizer.Add(panel, 1, wx.EXPAND)
        self._main_sizer.Layout()


    def _on_milliseconds_changed(self, event):
        try:
            self._lightshow_logic.milliseconds_to_run = int(self._milliseconds_to_run_text.GetValue())
        except:
            self._milliseconds_to_run_text.SetValue(str(self._lightshow_logic.milliseconds_to_run))

        # pass on event for more handling
        event.Skip()


    def _on_milliseconds_flash_changed(self, event):
        try:
            self._lightshow_logic.milliseconds_flash_min = int(self._milliseconds_flash_min_text.GetValue())
        except:
            self._milliseconds_flash_min_text.SetValue(str(sself._lightshow_logic.milliseconds_flash_min))

        try:
            self._lightshow_logic.milliseconds_flash_max = int(self._milliseconds_flash_max_text.GetValue())
        except:
            self._milliseconds_flash_max_text.SetValue(str(self._lightshow_logic.milliseconds_flash_max))

        # pass on event for more handling
        event.Skip()

    
    def _on_leds_to_choose_changed(self, event):
        try:
            self._lightshow_logic.number_of_leds_to_pick_min = int(self._leds_to_choose_min_text.GetValue())
        except:
            self._leds_to_choose_min_text.SetValue(str(self._lightshow_logic.number_of_leds_to_pick_min))

        try:
            self._lightshow_logic.number_of_leds_to_pick_max = int(self._leds_to_choose_max_text.GetValue())
        except:
            self._leds_to_choose_max_text.SetValue(str(self._lightshow_logic.number_of_leds_to_pick_max))

        # pass on event for more handling
        event.Skip()