# python imports
import wx

# local imports
import constants
import event_handler
import sprite


class PlayfieldPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._event_handler = event_handler.event_handler
        self._event_handler.add_listener(self, self.handle_event)

        # instance variables
        self._sprite_light_map = {} # map of pinball-light-name to sprite
        self._sprite_playfield = None

        # events for our panel
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_UP, self._on_click)
        self.Bind(wx.EVT_RIGHT_UP, self._on_right_click)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_bg)

        self._setup()


    def handle_event(self, event):
        if event.event_type == event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_CLEAR_AND_SET:
            self._clearLeds()
            
            for led in event.data["led_names"]:
                sprite_obj = self._sprite_light_map[led]
                sprite_obj.enable()

            self.update()
        elif event.event_type == event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_ENABLE_OK:
            sprite_obj = self._sprite_light_map[event.data["led_name"]]

            sprite_obj.enable()
        elif event.event_type == event_handler.EVENT_TYPE_TO_PLAYFIELD_LED_DISABLE_OK:
            sprite_obj = self._sprite_light_map[event.data["led_name"]]

            sprite_obj.disable()

    
    def update(self):
        for key in self._sprite_light_map:
            sprite_obj = self._sprite_light_map[key]
            sprite_obj.update()
            
        if self:
            self.Refresh()


    def _clearLeds(self):
        for key in self._sprite_light_map:
            self._sprite_light_map[key].disable()


    def _setup(self):
        # playfield sprite dictates the size of the panel
        self._sprite_playfield = sprite.Sprite("data/playfield.png", 0, 0)
        wx.Panel.SetMinSize(self, self._sprite_playfield.bitmap.GetSize())

        # light sprites
        self._sprite_light_map[constants.LED_START_BUTTON] = sprite.Sprite("data/start_color.png", 9, 652)
        
        self._sprite_light_map[constants.LED_LANE_GUIDES] = sprite.Sprite("data/guides_color.png", 138, 113)  
        self._sprite_light_map[constants.LED_LANE_GUIDE_LEFT_INSERT] = sprite.Sprite("data/green_insert_color.png", 118, 95)
        self._sprite_light_map[constants.LED_LANE_GUIDE_MIDDLE_INSERT] = sprite.Sprite("data/blue_insert_color.png", 155, 90)
        self._sprite_light_map[constants.LED_LANE_GUIDE_RIGHT_INSERT] = sprite.Sprite("data/green_insert_color.png", 192, 95)
        
        self._sprite_light_map[constants.LED_OUTLANE_LEFT] = sprite.Sprite("data/red_insert_color.png", 4, 503)
        self._sprite_light_map[constants.LED_OUTLANE_RIGHT] = sprite.Sprite("data/red_insert_color.png", 279, 506)
        self._sprite_light_map[constants.LED_INLANE_LEFT] = sprite.Sprite("data/clear_insert_color.png", 32, 488)
        self._sprite_light_map[constants.LED_INLANE_RIGHT] = self._sprite_insert_right_inlane_clear = sprite.Sprite("data/clear_insert_color.png", 248, 491)
        
        self._sprite_light_map[constants.LED_LEFT_LANE_INSERT] = sprite.Sprite("data/blue_insert_color.png", 20, 199)
        self._sprite_light_map[constants.LED_MIDDLE_LANE_INSERT] = sprite.Sprite("data/purple_insert_color.png", 249, 183)
        self._sprite_light_map[constants.LED_RIGHT_LANE_INSERT] = sprite.Sprite("data/blue_insert_color.png", 310, 181)
        
        self._sprite_light_map[constants.LED_TARGET_BLUE_INSERT] = sprite.Sprite("data/blue_insert_color.png", 218, 351)
        self._sprite_light_map[constants.LED_TARGET_GREEN_INSERT] = sprite.Sprite("data/green_insert_color.png", 47, 310)
        self._sprite_light_map[constants.LED_TARGET_ORANGE_INSERT] = sprite.Sprite("data/orange_insert_color.png", 87, 175)
        self._sprite_light_map[constants.LED_TARGET_RED_LEFT_INSERT] = sprite.Sprite("data/red_insert_color.png", 115, 327)
        self._sprite_light_map[constants.LED_TARGET_RED_RIGHT_INSERT] = sprite.Sprite("data/red_insert_color.png", 167, 328)
        
        self._sprite_light_map[constants.LED_BUMPER_RED] = sprite.Sprite("data/red_pop_color.png", 132, 242)
        self._sprite_light_map[constants.LED_BUMPER_GREEN_LEFT] = sprite.Sprite("data/green_pop_color.png", 105, 190)
        self._sprite_light_map[constants.LED_BUMPER_GREEN_RIGHT] = sprite.Sprite("data/green_pop_color.png", 162, 190)
        
        self._sprite_light_map[constants.LED_AREA_TOP_LEFT] = sprite.Sprite("data/top_left_color.png", 0, 13)
        self._sprite_light_map[constants.LED_AREA_TOP_RIGHT] = sprite.Sprite("data/top_right_color.png", 218, 13)
        self._sprite_light_map[constants.LED_AREA_TOP_MIDDLE_LEFT] = sprite.Sprite("data/top_left_cloud_color.png", 52, 79)
        self._sprite_light_map[constants.LED_AREA_TOP_MIDDLE_RIGHT] = sprite.Sprite("data/top_right_cloud_color.png", 212, 79)
        self._sprite_light_map[constants.LED_AREA_MIDDLE] = sprite.Sprite("data/middle_cloud_color.png", 116, 287)
        self._sprite_light_map[constants.LED_AREA_MIDDLE_LEFT] = sprite.Sprite("data/left_cloud_color.png", 0, 239)
        self._sprite_light_map[constants.LED_AREA_MIDDLE_RIGHT] = sprite.Sprite("data/right_cloud_color.png", 244, 303)
        self._sprite_light_map[constants.LED_AREA_LOWER_LEFT] = sprite.Sprite("data/bottom_left_cloud_color.png", 20, 479)
        self._sprite_light_map[constants.LED_AREA_LOWER_RIGHT] = sprite.Sprite("data/bottom_right_cloud_color.png", 180, 479)


    # event methods

    def _on_erase_bg(self, event):
        # stop this from running to eliminate flicker on redraw
        pass


    def _on_click(self, event):
        for key in self._sprite_light_map:
            sprite_obj = self._sprite_light_map[key]
            
            if event.x >= sprite_obj.x and event.x <= sprite_obj.x + sprite_obj.width \
                and event.y >= sprite_obj.y and event.y <= sprite_obj.y + sprite_obj.height:
                if sprite_obj.is_enabled():
                    # send request to disable led
                    my_event = event_handler.Event(event_handler.EVENT_TYPE_PLAYFIELD_LED_DISABLE, {"led_name":key})
                    self._event_handler.send_event(self, my_event)
                else:
                    # send request to enable led
                    my_event = event_handler.Event(event_handler.EVENT_TYPE_PLAYFIELD_LED_ENABLE, {"led_name":key})
                    self._event_handler.send_event(self, my_event)
                
                # stop at first (highest priority)
                break


    def _on_right_click(self, event):
        enable = True

        # if we have any leds enabled, then we will disable all, otherwise enable all
        for key in self._sprite_light_map:
            sprite_obj = self._sprite_light_map[key]

            if sprite_obj.is_enabled():
                enable = False
                break

        for key in self._sprite_light_map:
            sprite_obj = self._sprite_light_map[key]

            if enable:
                sprite_obj.enable()

                my_event = event_handler.Event(event_handler.EVENT_TYPE_PLAYFIELD_LED_ENABLE, {"led_name":key})
                self._event_handler.send_event(self, my_event)
            else:
                sprite_obj.disable()

                my_event = event_handler.Event(event_handler.EVENT_TYPE_PLAYFIELD_LED_DISABLE, {"led_name":key})
                self._event_handler.send_event(self, my_event)
                

    def _on_paint(self, event):
        dc = wx.BufferedPaintDC(self)

        dc.DrawBitmap(self._sprite_playfield.bitmap, self._sprite_playfield.x, self._sprite_playfield.y, True)
        
        for key in self._sprite_light_map:
            sprite_obj = self._sprite_light_map[key]
            if sprite_obj.is_visible():
                dc.DrawBitmap(sprite_obj.bitmap, sprite_obj.x, sprite_obj.y, True)