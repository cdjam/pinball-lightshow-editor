# python imports
import os
import random
import time
import wx
import wx.lib.scrolledpanel

# local imports
import constants
import event_handler
import combo_segment_panel
import utility


# constants
MILLISECONDS_TO_RUN_LABEL = "Ms To Run: "

DEFAULT_SEGMENT_PANEL_COLOR = (216, 216, 216)
SELECTED_SEGMENT_PANEL_COLOR = (175, 216, 189)


class ComboEditorPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._milliseconds_to_run = 1000

        self._selected = False

        self._event_handler = event_handler.event_handler
        self._event_handler.add_listener(self, self.handle_event)

        self._playing = False
        self._playing_segment = False

        # keep track of active panels
        self._segment_panels = []
        self._current_segment_panel_id = None

        self._setup()


    def get_current_values(self):
        lightshow_filepaths = []

        for combo_segment_panel in self._segment_panels:
            filepath = combo_segment_panel.get_loaded_file()

            if filepath not in lightshow_filepaths:
                lightshow_filepaths.append(filepath)

        return self._milliseconds_to_run, lightshow_filepaths


    def clear(self):
        self._playing = False
        self._playing_segment = False

        for segment in self._segment_panels:
            segment.destroy()

        self._segment_panels = []
        self._combo_editor_panel.DestroyChildren()


    def get_type(self):
        return constants.COMBO_EDITOR_TYPE


    def handle_event(self, event):
        # notebook page active
        if event.event_type == event_handler.EVENT_TYPE_NOTEBOOK_PAGE_ACTIVE:
            if event.data["active_page"] == self:
                self._selected = True
                self._refresh_selection()
            else:
                self._selected = False

        # from combo editor
        elif event.event_type == event_handler.EVENT_TYPE_COMBO_EDITOR_REMOVE:
            self._remove_combo_segment(event.data["id"])
            self._refresh_selection()
        elif not self._playing and event.event_type == event_handler.EVENT_TYPE_COMBO_EDITOR_SEGMENT_SELECTED:
            self._change_segment_selected(int(event.data["id"]))

        # from any
        elif event.event_type == event_handler.EVENT_TYPE_STOP_ALL:
            self._stop()
        elif event.event_type == event_handler.EVENT_TYPE_COMBO_EDITOR_LOAD_DATA:
            self.clear()

            combo_load_data = event.data["combo_load_data"]
            
            self._milliseconds_to_run = combo_load_data["milliseconds_to_run"]
            self._milliseconds_to_run_text.SetValue(str(self._milliseconds_to_run))

            lightshow_files = combo_load_data["lightshow_files"]

            for lightshow_filepath in lightshow_files:
                self._add_default_panel(lightshow_filepath)

    
    def update(self):
        current_micros = time.time_ns() / 1000

        if self._playing and self._segment_panels:
            if self._playing_segment:
                obj = self._segment_panels[self._current_segment_panel_id - 1]
                obj.get_logic().update()

                enabled_leds = obj.get_logic().get_enabled_leds()

                my_event = event_handler.Event(event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_CLEAR_AND_SET, {"led_names":enabled_leds})
                self._event_handler.send_event(self, my_event)
            elif current_micros >= self._run_started_micros + (self._milliseconds_to_run * 1000):
                self._stop()
            else:
                for obj in self._segment_panels:
                    obj.get_logic().update()

                enabled_leds = []

                for obj in self._segment_panels:
                    leds = obj.get_logic().get_enabled_leds()

                    for led in leds:
                        if led not in enabled_leds:
                            enabled_leds.append(led)

                my_event = event_handler.Event(event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_CLEAR_AND_SET, {"led_names":enabled_leds})
                self._event_handler.send_event(self, my_event)


    def _setup(self):
        # toolbar
        toolbar = self._create_combo_editor_toolbar(self)

        # time to run
        time_panel = wx.Panel(self, style=wx.SIMPLE_BORDER)

        milliseconds_to_run_label = wx.StaticText(time_panel, wx.ID_ANY, MILLISECONDS_TO_RUN_LABEL)

        self._milliseconds_to_run_text = wx.TextCtrl(time_panel, wx.ID_ANY)
        self._milliseconds_to_run_text.SetValue(str(self._milliseconds_to_run))
        self._milliseconds_to_run_text.Bind(wx.EVT_TEXT, self._on_milliseconds_to_run_changed)

        ms_to_run_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ms_to_run_sizer.Add(milliseconds_to_run_label, 0, wx.TOP | wx.LEFT, 4)
        ms_to_run_sizer.Add(self._milliseconds_to_run_text, 1, wx.EXPAND)

        time_panel.SetSizer(ms_to_run_sizer)

        # main editor panel
        self._combo_editor_panel = self._create_combo_editor_panel(self)

        # setup page sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(toolbar, 0, wx.EXPAND)
        sizer.AddSpacer(10)
        sizer.Add(time_panel, 0, wx.EXPAND)
        sizer.AddSpacer(5)
        sizer.Add(self._combo_editor_panel, 1, wx.EXPAND)
        self.SetSizer(sizer)


    def _create_combo_editor_toolbar(self, parent):
        icon_size = (40, 40)

        toolbar_panel = wx.Panel(parent, style=wx.SIMPLE_BORDER)

        play_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_play.png", "data/icon_play_pressed.png", self._on_play_pressed)
        stop_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_stop.png", "data/icon_stop_pressed.png", self._on_stop_pressed)
        play_segment_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_play_segment.png", "data/icon_play_segment_pressed.png", self._on_play_segment_pressed)
        
        add_default_segment_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_plus.png", "data/icon_plus_pressed.png", self._on_add_default_segment_pressed)
        refresh_button = utility.create_toolbar_button(toolbar_panel, icon_size, "data/icon_refresh_segment.png", "data/icon_refresh_pressed.png", self._on_refresh_pressed)

        # add sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(play_button, 1)
        sizer.Add(stop_button, 1)
        sizer.Add(play_segment_button, 1)
        sizer.Add((0,0), 1) # separator
        sizer.Add(add_default_segment_button, 1)
        sizer.Add(refresh_button, 1)
        toolbar_panel.SetSizer(sizer)

        return toolbar_panel


    def _create_combo_editor_panel(self, parent):
        panel = wx.lib.scrolledpanel.ScrolledPanel(parent, wx.ID_ANY)
        panel.SetupScrolling(scrollToTop=False)

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        return panel


    def _create_combo_default_panel(self, parent, id, filepath):
        return combo_segment_panel.ComboSegment(parent, id, filepath)


    def _refresh_scrolling(self):
        self._combo_editor_panel.SetupScrolling(scrollToTop=False)


    def _remove_combo_segment(self, id):
        sizer = self._combo_editor_panel.GetSizer()

        if id >= self._current_segment_panel_id:
            self._current_segment_panel_id -= 1

        # need to change to 0 index id for array
        panel = self._segment_panels[id - 1]
        panel.set_id(0) # set id to 0 to ensure it doesn"t pick up events until its garbage collected

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


    def _stop(self):
        self._playing = False
        self._playing_segment = False

        for obj in self._segment_panels:
            obj.get_logic().stop()

        self._refresh_selection()


    def _refresh_selection(self):
        if self._segment_panels and self._current_segment_panel_id:
            current_panel = self._segment_panels[self._current_segment_panel_id - 1]
            panel_logic = current_panel.get_logic()
            panel_logic.stop()

            self._change_segment_selected(self._current_segment_panel_id)
        else:
            my_event = event_handler.Event(event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_CLEAR_AND_SET, {"led_names":[]})
            self._event_handler.send_event(self, my_event)
            

    def _add_default_panel(self, filepath):
        for loaded_panels in self._segment_panels:
            if loaded_panels.get_loaded_file() == os.path.basename(filepath):
                # already loaded
                return True
            
        try:
            with open(filepath, "r") as file:
                # create panel
                panel = self._create_combo_default_panel(self._combo_editor_panel, len(self._segment_panels)+1, filepath)
                panel.SetBackgroundColour(DEFAULT_SEGMENT_PANEL_COLOR)

                success = panel.load_file_data()

                self._segment_panels.append(panel)

                sizer = self._combo_editor_panel.GetSizer()
                sizer.Add(panel, 0, wx.EXPAND | wx.ALL, border = 5)

                sizer.Layout()
                self._refresh_scrolling()

            return True
        except IOError:
            return False

        return True

    # event methods

    def _on_play_pressed(self, event):
        if self._playing == False:
            self._playing = True
            self._run_started_micros = time.time_ns() / 1000
            
            for obj in self._segment_panels:
                obj.get_logic().run()


    def _on_stop_pressed(self, event):
        if self._playing:
            self._stop()

    
    def _on_play_segment_pressed(self, event):
        if self._playing_segment == False:
            self._playing = True
            self._playing_segment = True

            if self._segment_panels and self._current_segment_panel_id:
                obj = self._segment_panels[self._current_segment_panel_id - 1]
                obj.get_logic().run()


    def _on_add_default_segment_pressed(self, event):
        with wx.FileDialog(self, "Load light show", wildcard="Lightshow files (*.ls)|*.ls", 
            style=wx.FD_OPEN  | wx.FD_FILE_MUST_EXIST) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return True

            return self._add_default_panel(fileDialog.GetPath())

    
    def _on_refresh_pressed(self, event):
        for loaded_panels in self._segment_panels:
            # reload data
            loaded_panels.load_file_data()


    def _on_milliseconds_to_run_changed(self, event):
        try:
            self._milliseconds_to_run = int(self._milliseconds_to_run_text.GetValue())
        except:
            self._milliseconds_to_run_text.SetValue(str(self._milliseconds_to_run))

        # pass on event for more handling
        event.Skip()