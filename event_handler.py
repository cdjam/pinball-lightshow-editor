# listeners must have handle_event function that takes 1 argument, event (of type Event)
EVENT_TYPE_LIGHTSHOW_EDITOR_REMOVE = 100
EVENT_TYPE_LIGHTSHOW_EDITOR_MOVE_UP = 101
EVENT_TYPE_LIGHTSHOW_EDITOR_MOVE_DOWN = 102
EVENT_TYPE_LIGHTSHOW_EDITOR_CHANGE_POSITION = 103
EVENT_TYPE_LIGHTSHOW_EDITOR_SEGMENT_SELECTED = 104
EVENT_TYPE_LIGHTSHOW_EDITOR_ADD_LED = 105
EVENT_TYPE_LIGHTSHOW_EDITOR_REMOVE_LED = 106
EVENT_TYPE_LIGHTSHOW_EDITOR_LOAD_DATA = 107

EVENT_TYPE_COMBO_EDITOR_REMOVE = 200
EVENT_TYPE_COMBO_EDITOR_MOVE_UP = 201
EVENT_TYPE_COMBO_EDITOR_MOVE_DOWN = 202
EVENT_TYPE_COMBO_EDITOR_CHANGE_POSITION = 203
EVENT_TYPE_COMBO_EDITOR_SEGMENT_SELECTED = 204
EVENT_TYPE_COMBO_EDITOR_LOAD_DATA = 205

EVENT_TYPE_PLAYFIELD_LED_ENABLE = 1000
EVENT_TYPE_PLAYFIELD_LED_DISABLE = 1001

EVENT_TYPE_TO_PLAYFIELD_LED_CLEAR_AND_SET = 1100
EVENT_TYPE_TO_PLAYFIELD_LED_ENABLE_OK = 1101
EVENT_TYPE_TO_PLAYFIELD_LED_DISABLE_OK = 1102

EVENT_TYPE_NOTEBOOK_PAGE_ACTIVE = 1200

EVENT_TYPE_STOP_ALL = 1300
EVENT_TYPE_SAVE_NOTEBOOK_PAGE = 1301


class Event:
    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data


class EventHandler:
    def __init__(self):
        self._listener_function_map = {}

    
    def add_listener(self, listener, function):
        self._listener_function_map[listener] = function


    def remove_listener(self, listener):
        if listener in self._listener_function_map:
            del self._listener_function_map[listener]


    def send_event(self, sender, event):
        cur_map = self._listener_function_map.copy()

        for key in cur_map:
            # dont send to self
            if key is not sender:
                cur_map[key](event)


# singleton
event_handler = EventHandler()