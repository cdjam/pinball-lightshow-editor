# python imports
import random
import time
import wx
import wx.lib.scrolledpanel

# local imports
import constants
import event_handler
import lightshow_logic
import lightshow_segment_panel
import utility


# constants
DEFAULT_SEGMENT_PANEL_COLOR = (216, 216, 216)
SELECTED_SEGMENT_PANEL_COLOR = (175, 216, 189)


class RandomPlayingLed:
    def __init__(self):
        self.led_name = ""
        self.led_micros_to_run = 0
        self.led_start_micros = 0
        self.led_enabled = False


class LightshowEditorPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._selected = False

        self._event_handler = event_handler.event_handler
        self._event_handler.add_listener(self, self.handle_event)

        self._playing = False
        self._playing_segment = False

        self._segment_started_micros = 0
        self._playing_current_segment_panel_id = None # while running play

        # keep track of active panels
        self._segment_panels = []
        self._current_segment_panel_id = None

        self._setup()


    def clear(self):
        for segment in self._segment_panels:
            segment.destroy()
            
        self._reset()


    def get_type(self):
        return constants.LIGHTSHOW_EDITOR_TYPE


    def get_current_segments(self):
        return self._segment_panels


    def handle_event(self, event):
        # notebook page active
        if event.event_type == event_handler.EVENT_TYPE_NOTEBOOK_PAGE_ACTIVE:
            if event.data["active_page"] == self:
                self._selected = True
                self._change_segment_selected(self._current_segment_panel_id)
            else:
                self._selected = False

        # from lightshow editor
        elif event.event_type == event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_REMOVE:
            self._remove_lightshow_segment(event.data["id"])
        elif event.event_type == event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_MOVE_UP:
            self._move_lightshow_segment(event.data["id"], event.data["id"]-1)
        elif event.event_type == event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_MOVE_DOWN:
            self._move_lightshow_segment(event.data["id"], event.data["id"]+1)
        elif event.event_type == event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_CHANGE_POSITION:
            self._move_lightshow_segment(event.data["id"], event.data["new_id"])
        elif not self._playing and event.event_type == event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_SEGMENT_SELECTED:
            self._change_segment_selected(int(event.data["id"]))
        elif event.event_type == event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_LOAD_DATA:
            self.clear()

            logic_list = event.data["lightshow_logic_list"]

            for logic_item in logic_list:
                if logic_item.type == constants.LIGHTSHOW_TYPE_ENABLE:
                    self._add_enabled_segment(logic_item)
                elif logic_item.type == constants.LIGHTSHOW_TYPE_RANDOM:
                    self._add_random_segment(logic_item)

        # playfield
        elif not self._playing and event.event_type == event_handler.EVENT_TYPE_PLAYFIELD_LED_DISABLE:
            if self._current_segment_panel_id is not None:
                my_event = event_handler.Event(event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_REMOVE_LED, {"recv_id":self._current_segment_panel_id, "led_name":event.data["led_name"]})
                self._event_handler.send_event(self, my_event)

                my_event = event_handler.Event(event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_DISABLE_OK, {"led_name":event.data["led_name"]})
                self._event_handler.send_event(self, my_event)
        elif not self._playing and self._selected and event.event_type == event_handler.EVENT_TYPE_PLAYFIELD_LED_ENABLE:
            if self._current_segment_panel_id is not None:
                my_event = event_handler.Event(event_handler.EVENT_TYPE_LIGHTSHOW_EDITOR_ADD_LED, {"recv_id":self._current_segment_panel_id, "led_name":event.data["led_name"]})
                self._event_handler.send_event(self, my_event)

                my_event = event_handler.Event(event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_ENABLE_OK, {"led_name":event.data["led_name"]})
                self._event_handler.send_event(self, my_event)

        # from any
        elif event.event_type == event_handler.EVENT_TYPE_STOP_ALL:
            self._stop()


    def update(self):
        current_micros = time.time_ns() / 1000

        if self._playing and self._segment_panels:
            panel = self._segment_panels[self._playing_current_segment_panel_id - 1]

            panel_logic = panel.get_logic()
            panel_logic.update()

            if not self._playing_segment and panel_logic.is_done() and panel_logic.is_running():
                # keep between 0-max
                self._playing_current_segment_panel_id = (self._playing_current_segment_panel_id) % len(self._segment_panels)
                
                # set back to 1-index
                self._playing_current_segment_panel_id += 1

                panel = self._segment_panels[self._playing_current_segment_panel_id - 1]
                panel_logic = panel.get_logic()
                panel_logic.run()
                panel_logic.update() # immediate update to enable leds immediately and avoid flickers

                self._change_segment_selected(self._playing_current_segment_panel_id)
        
            my_event = event_handler.Event(event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_CLEAR_AND_SET, {"led_names":panel_logic.get_enabled_leds()})
            self._event_handler.send_event(self, my_event)


    def _setup(self):
        # toolbar
        toolbar = self._create_lightshow_editor_toolbar(self)

        # panel
        self._lightshow_editor_panel = self._create_lightshow_editor_panel(self)

        # setup page sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(toolbar, 0, wx.EXPAND)
        sizer.AddSpacer(10)
        sizer.Add(self._lightshow_editor_panel, 1, wx.EXPAND)
        self.SetSizer(sizer)


    def _create_lightshow_editor_toolbar(self, parent):
        icon_size = (40, 40)

        toolbar_panel = wx.Panel(parent, style=wx.SIMPLE_BORDER)

        play_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_play.png", "data/icon_play_pressed.png", self._on_play_pressed)
        stop_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_stop.png", "data/icon_stop_pressed.png", self._on_stop_pressed)
        play_segment_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_play_segment.png", "data/icon_play_segment_pressed.png", self._on_play_segment_pressed)

        add_enable_segment_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_add_enable_segment.png", "data/icon_add_enable_segment_pressed.png", self._on_add_enable_segment_pressed)
        add_random_segment_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_add_random_segment.png", "data/icon_add_random_segment_pressed.png", self._on_add_random_segment_pressed)

        # add sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(play_button, 1)
        sizer.Add(stop_button, 1)
        sizer.Add(play_segment_button, 1)
        sizer.Add((0,0), 1) # separator
        sizer.Add(add_enable_segment_button, 1)
        sizer.Add(add_random_segment_button, 1)
        toolbar_panel.SetSizer(sizer)

        return toolbar_panel


    def _create_lightshow_editor_panel(self, parent):
        panel = wx.lib.scrolledpanel.ScrolledPanel(parent, wx.ID_ANY)
        panel.SetupScrolling(scrollToTop=False)

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        return panel


    def _create_lightshow_segment_enabled_panel(self, parent, id, logic_obj=None):
        return lightshow_segment_panel.LightShowSegmentEnable(parent, id, logic_obj)


    def _create_lightshow_segment_random_panel(self, parent, id, logic_obj=None):
        return lightshow_segment_panel.LightShowSegmentRandom(parent, id, logic_obj)
        

    def _refresh_scrolling(self):
        self._lightshow_editor_panel.SetupScrolling(scrollToTop=False)


    def _remove_lightshow_segment(self, id):
        sizer = self._lightshow_editor_panel.GetSizer()

        # need to change to 0 index id for array
        panel = self._segment_panels[id - 1]
        panel.set_id(0) # set id to 0 to ensure it doesn"t pick up events until its garbage collected
        
        panel.destroy()

        # remove from GUI
        sizer.Detach(panel)
        panel.Destroy()

        # free item from list
        del self._segment_panels[id - 1]

        # re-order items in list
        for i in range(len(self._segment_panels)):
            self._segment_panels[i].set_id(i + 1)

        # update scrolling
        self._refresh_scrolling()


    def _move_lightshow_segment(self, id, new_id):
        # normalize new_id to acceptable range
        if new_id <= 0:
            new_id = 1
        elif new_id >= len(self._segment_panels):
            new_id = len(self._segment_panels)

        # get panel and remove from current spot
        panel = self._segment_panels[id - 1]
        del self._segment_panels[id - 1]

        # inject panel into new_id spot
        self._segment_panels.insert(new_id - 1, panel)

        # re-draw sizer with new positions
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._lightshow_editor_panel.SetSizer(sizer)

        for index, segment_panel in enumerate(self._segment_panels):
            sizer.Add(segment_panel, 0, wx.EXPAND | wx.ALL, border = 5)

            # reset text for id, etc
            segment_panel.set_id(index + 1)

        sizer.Layout()
        self._refresh_scrolling()


    def _change_segment_selected(self, id):
        if id is None:
            return

        self._current_segment_panel_id = id
        panel = self._segment_panels[id - 1]

        for segment_panel in self._segment_panels:
            segment_panel.SetBackgroundColour(DEFAULT_SEGMENT_PANEL_COLOR)

        panel.SetBackgroundColour(SELECTED_SEGMENT_PANEL_COLOR)

        panel_logic = panel.get_logic()
        leds_to_enable = panel_logic.leds

        my_event = event_handler.Event(event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_CLEAR_AND_SET, {"led_names":leds_to_enable})
        self._event_handler.send_event(self, my_event)

        self.Refresh()


    def _setup_random_led_datas(self, random_panel):
        self._random_led_datas = []

        panel_logic = random_panel.get_logic()
        led_options = panel_logic.leds.copy()

        milliseconds_flash_min, milliseconds_flash_max, number_of_leds_to_pick_min, number_of_leds_to_pick_max  = random_panel.get_random_info()
        leds_to_pick = random.randint(number_of_leds_to_pick_min, number_of_leds_to_pick_max)

        for i in range(leds_to_pick):
            if len(led_options) < 1:
                continue

            random_index = random.randint(0, len(led_options)-1)

            led_info = RandomPlayingLed()
            led_info.led_name = led_options[random_index]
            led_info.led_micros_to_run = random.randint(milliseconds_flash_min, milliseconds_flash_max) * 1000

            del led_options[random_index]

            self._random_led_datas.append(led_info)


    def _reset(self):
        self._playing = False
        self._playing_segment = False
        self._segment_panels = []
        self._lightshow_editor_panel.DestroyChildren()


    def _add_enabled_segment(self, logic_obj=None):
        panel = self._create_lightshow_segment_enabled_panel(self._lightshow_editor_panel, len(self._segment_panels)+1, logic_obj)
        panel.SetBackgroundColour(DEFAULT_SEGMENT_PANEL_COLOR)

        self._segment_panels.append(panel)

        sizer = self._lightshow_editor_panel.GetSizer()
        sizer.Add(panel, 0, wx.EXPAND | wx.ALL, border = 5)

        sizer.Layout()
        self._refresh_scrolling()


    def _add_random_segment(self, logic_obj=None):
        panel = self._create_lightshow_segment_random_panel(self._lightshow_editor_panel, len(self._segment_panels)+1, logic_obj)
        panel.SetBackgroundColour(DEFAULT_SEGMENT_PANEL_COLOR)

        self._segment_panels.append(panel)

        sizer = self._lightshow_editor_panel.GetSizer()
        sizer.Add(panel, 0, wx.EXPAND | wx.ALL, border = 5)

        sizer.Layout()
        self._refresh_scrolling()


    def _stop(self):
        self._playing = False
        self._playing_segment = False

        if self._segment_panels and self._playing_current_segment_panel_id:
            current_panel = self._segment_panels[self._playing_current_segment_panel_id - 1]
            panel_logic = current_panel.get_logic()
            panel_logic.stop()

            self._change_segment_selected(self._playing_current_segment_panel_id)

            self._playing_current_segment_panel_id = None


    # event methods

    def _on_play_pressed(self, event):
        if self._playing:
            return

        if len(self._segment_panels) > 0:
            self._playing_current_segment_panel_id = self._current_segment_panel_id

            if not self._playing_current_segment_panel_id:
                self._playing_current_segment_panel_id = 1

            self._playing = True
            self._change_segment_selected(self._playing_current_segment_panel_id)

            current_panel = self._segment_panels[self._playing_current_segment_panel_id - 1]
            panel_logic = current_panel.get_logic()

            panel_logic.run()


    def _on_stop_pressed(self, event):
        if self._playing:
            self._stop()


    def _on_play_segment_pressed(self, event):
        if self._playing and not self._playing_segment:
            return

        if len(self._segment_panels) > 0 and len(self._segment_panels) >= self._current_segment_panel_id:
            panel = self._segment_panels[self._current_segment_panel_id - 1]
            self._playing_current_segment_panel_id = panel.get_id()

            self._playing = True
            self._playing_segment = True
            self._change_segment_selected(self._playing_current_segment_panel_id)

            panel_logic = panel.get_logic()
            panel_logic.run()
            

    def _on_add_enable_segment_pressed(self, event):
        self._add_enabled_segment()


    def _on_add_random_segment_pressed(self, event):
        self._add_random_segment()