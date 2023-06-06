# python imports
import random
import time

# local imports
import constants
import event_handler


class IndependentPlayingLed:
    def __init__(self):
        self.led_name = ""
        self.led_micros_to_run = 0
        self.led_start_micros = 0
        self.led_enabled = False


class LightshowLogic:
    def __init__(self):
        self.milliseconds_to_run = 1000
        self.type = None
        self.leds = []

        self._event_handler = event_handler.event_handler


    def run(self):
        raise Exception("Must be overwritten in sub-class!")


    def stop(self):
        raise Exception("Must be overwritten in sub-class!")


    def is_done(self):
        raise Exception("Must be overwritten in sub-class!")


    def is_running(self):
        raise Exception("Must be overwritten in sub-class!")


    def get_enabled_leds(self):
        raise Exception("Must be overwritten in sub-class!")

    
    def update(self):
        raise Exception("Must be overwritten in sub-class!")


class LightshowLogicEnable(LightshowLogic):
    def __init__(self):
        LightshowLogic.__init__(self)

        self.type = constants.LIGHTSHOW_TYPE_ENABLE

        self._to_run = False
        self._running = False
        self._done = False

        self._current_enabled_leds = []


    def run(self):
        self._to_run = True
        self._running = False
        self._done = False


    def stop(self):
        self._running = False
        self._to_run = False
        self._done = True


    def is_done(self):
        return self._done


    def is_running(self):
        return self._running


    def get_enabled_leds(self):
        return self._current_enabled_leds


    def update(self):
        current_micros = time.time_ns() / 1000

        # start a new run?
        if self._to_run:
            self._to_run = False
            self._run_started_micros = current_micros
            self._running = True

            # enable leds for duration
            self._current_enabled_leds = self.leds.copy()

        if self._running:
            if current_micros >= self._run_started_micros + (self.milliseconds_to_run * 1000):
                # done with this run
                self._done = True


class LightshowLogicRandom(LightshowLogic):
    def __init__(self):
        LightshowLogic.__init__(self)

        self.type = constants.LIGHTSHOW_TYPE_RANDOM
        
        self._independent_playing_leds = []
        self._current_enabled_leds = []
        self._to_run = False
        self._running = False
        self._done = False

        self._enabled_leds = []

        self.milliseconds_flash_min = 500
        self.milliseconds_flash_max = 1000
        self.number_of_leds_to_pick_min = 1
        self.number_of_leds_to_pick_max = 1


    def run(self):
        self._to_run = True
        self._running = False
        self._done = False


    def stop(self):
        self._running = False
        self._to_run = False
        self._done = True


    def is_done(self):
        return self._done


    def is_running(self):
        return self._running


    def get_enabled_leds(self):
        return self._current_enabled_leds


    def update(self):
        current_micros = time.time_ns() / 1000

        # start a new run?
        if self._to_run:
            self._to_run = False

            # pick our random data
            self._setup_random_leds()
            self._current_enabled_leds = []
            self._run_started_micros = current_micros
            self._running = True

        if self._running and not self._done:
            # track if any led changed state
            updated = False

            if current_micros >= self._run_started_micros + (self.milliseconds_to_run * 1000):
                # done with this run
                self._done = True
            else:
                for independent_playing_led in self._independent_playing_leds:
                    if current_micros >= independent_playing_led.led_start_micros + independent_playing_led.led_micros_to_run:
                        updated = True

                        # flip enabled/disabled
                        independent_playing_led.led_enabled = not independent_playing_led.led_enabled

                        if independent_playing_led.led_enabled:
                            self._current_enabled_leds.append(independent_playing_led.led_name)
                        else:
                            self._current_enabled_leds.remove(independent_playing_led.led_name)

                        # reset timer
                        independent_playing_led.led_start_micros = current_micros


    def _setup_random_leds(self):
        self._independent_playing_leds = []

        available_led_options = self.leds.copy()
        leds_to_pick = random.randint(self.number_of_leds_to_pick_min, self.number_of_leds_to_pick_max)

        for i in range(leds_to_pick):
            # if we are out, stop now
            if len(available_led_options) < 1:
                break

            random_index = random.randint(0, len(available_led_options)-1)

            led_info = IndependentPlayingLed()
            led_info.led_name = available_led_options[random_index]
            led_info.led_micros_to_run = random.randint(self.milliseconds_flash_min, self.milliseconds_flash_max) * 1000

            del available_led_options[random_index]

            self._independent_playing_leds.append(led_info)