# python imports
import random
import time

# local imports
import event_handler


class ComboLogic:
    def __init__(self):
        self.lightshow_logic_list = []
        self.current_lightshow_id = 0

        self.leds = [] # all used leds across segments
        
        self._event_handler = event_handler.event_handler


    def set_lightshow_logic_list(self, logic_list):
        self.lightshow_logic_list = logic_list

        # reset and setup
        self.leds = []

        for logic_obj in self.lightshow_logic_list:
            for led in logic_obj.leds:
                if led not in self.leds:
                    self.leds.append(led)


    def run(self):
        self.current_lightshow_id = 0
        self.lightshow_logic_list[self.current_lightshow_id].run()


    def stop(self):
        self.lightshow_logic_list[self.current_lightshow_id].stop()


    def get_enabled_leds(self):
        return self.lightshow_logic_list[self.current_lightshow_id].get_enabled_leds()

    
    def update(self):
        self.lightshow_logic_list[self.current_lightshow_id].update()

        # go to next segment
        if self.lightshow_logic_list[self.current_lightshow_id].is_running() and self.lightshow_logic_list[self.current_lightshow_id].is_done():
            self.current_lightshow_id = (self.current_lightshow_id + 1) % len(self.lightshow_logic_list)
            self.lightshow_logic_list[self.current_lightshow_id].run()