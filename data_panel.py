# python imports
import wx
import wx.lib.scrolledpanel

# local imports
import combo_editor_page
import constants
import event_handler
import lightshow_editor_page


class DataPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._setup()

        # enable first notebook page
        my_event = event_handler.Event(event_handler.EVENT_TYPE_NOTEBOOK_PAGE_ACTIVE, {"active_page":self._lightshow_editor_page})
        self._event_handler.send_event(self, my_event)
        

    def get_lightshow_editor_segment_logic_objs(self):
        segments = self._lightshow_editor_page.get_current_segments()

        logic_objs = []

        for segment in segments:
            logic_objs.append(segment.get_logic())

        return logic_objs


    def get_combo_editor_segment(self):
        return self._combo_editor_page


    def get_current_type(self):
        return self._selected_page_type


    def clear_current(self):
        if self._selected_page_type == constants.LIGHTSHOW_EDITOR_TYPE:
            self._lightshow_editor_page.clear()
        elif self._selected_page_type == constants.COMBO_EDITOR_TYPE:
            self._combo_editor_page.clear()


    def update(self):
        self._lightshow_editor_page.update()
        self._combo_editor_page.update()


    def _setup(self):
        self._event_handler = event_handler.event_handler

        self._notebook = wx.Notebook(self)
        self._notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_notebook_page_changed)

        # pages of notebook
        self._lightshow_editor_page = lightshow_editor_page.LightshowEditorPage(self._notebook)
        self._notebook.AddPage(self._lightshow_editor_page, "Lightshow Editor")

        self._combo_editor_page = combo_editor_page.ComboEditorPage(self._notebook)   
        self._notebook.AddPage(self._combo_editor_page, "Combo Editor")

        self._selected_page_type = constants.LIGHTSHOW_EDITOR_TYPE

        # add notebook to panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)


    # event methods

    def _on_notebook_page_changed(self, event):
        selected_page = self._notebook.GetPage(event.GetSelection())

        if selected_page == self._combo_editor_page:
            self._selected_page_type = constants.COMBO_EDITOR_TYPE
        elif selected_page == self._lightshow_editor_page:
            self._selected_page_type = constants.LIGHTSHOW_EDITOR_TYPE

        # stop all playing on switch
        my_event = event_handler.Event(event_handler.EVENT_TYPE_STOP_ALL, {})
        self._event_handler.send_event(self, my_event)

        my_event = event_handler.Event(event_handler.EVENT_TYPE_NOTEBOOK_PAGE_ACTIVE, {"active_page":selected_page})
        self._event_handler.send_event(self, my_event)
