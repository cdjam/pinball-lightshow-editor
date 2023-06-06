# python imports
import json

# local imports
import constants
import lightshow_logic


class LightshowData:
    def __init__(self):
        self.type = constants.LIGHTSHOW_TYPE_UNDEFINED
        self.milliseconds_to_run = 1000

    
    def to_dict(self):
        raise Exception("Must be overwritten in child class!")


    def load_from_dict(self, dict_to_load_from):
        raise Exception("Must be overwritten in child class!")


class LightshowEnabledData(LightshowData):
    def __init__(self):
        LightshowData.__init__(self)

        self.type = constants.LIGHTSHOW_TYPE_ENABLE
        self.leds_to_enable = []


    def to_dict(self):
        ret = {}
        ret["type"] = self.type
        ret["milliseconds_to_run"] = self.milliseconds_to_run
        ret["leds_to_enable"] = self.leds_to_enable

        return ret

    
    def load_from_dict(self, dict_to_load_from):
        self.milliseconds_to_run = dict_to_load_from["milliseconds_to_run"]
        self.leds_to_enable = dict_to_load_from["leds_to_enable"]


class LightshowRandomData(LightshowData):
    def __init__(self):
        LightshowData.__init__(self)

        self.type = constants.LIGHTSHOW_TYPE_RANDOM
        self.available_leds = []
        self.milliseconds_to_run_flash_min = 1000
        self.milliseconds_to_run_flash_max = 1000
        self.number_of_leds_to_pick_min = 1
        self.number_of_leds_to_pick_max = 1


    def to_dict(self):
        ret = {}
        ret["type"] = self.type
        ret["milliseconds_to_run"] = self.milliseconds_to_run
        ret["available_leds"] = self.available_leds
        ret["milliseconds_to_run_flash_min"] = self.milliseconds_to_run_flash_min
        ret["milliseconds_to_run_flash_max"] = self.milliseconds_to_run_flash_max
        ret["number_of_leds_to_pick_min"] = self.number_of_leds_to_pick_min
        ret["number_of_leds_to_pick_max"] = self.number_of_leds_to_pick_max

        return ret


    def load_from_dict(self, dict_to_load_from):
        self.milliseconds_to_run = dict_to_load_from["milliseconds_to_run"]
        self.available_leds = dict_to_load_from["available_leds"]
        self.milliseconds_to_run_flash_min = dict_to_load_from["milliseconds_to_run_flash_min"]
        self.milliseconds_to_run_flash_max = dict_to_load_from["milliseconds_to_run_flash_max"]
        self.number_of_leds_to_pick_min = dict_to_load_from["number_of_leds_to_pick_min"]
        self.number_of_leds_to_pick_max = dict_to_load_from["number_of_leds_to_pick_max"]


class LightshowDataMiddleware:
    def __init__(self):
        self.lightshow_datas = []


    def to_lightshow_logic_list(self):
        lightshow_logic_list = []
        
        for lightshow_data in self.lightshow_datas:
            ll = None

            if lightshow_data.type == constants.LIGHTSHOW_TYPE_ENABLE:
                ll = lightshow_logic.LightshowLogicEnable()

                ll.milliseconds_to_run = lightshow_data.milliseconds_to_run
                ll.leds = lightshow_data.leds_to_enable
            elif lightshow_data.type == constants.LIGHTSHOW_TYPE_RANDOM:
                ll = lightshow_logic.LightshowLogicRandom()

                ll.milliseconds_to_run = lightshow_data.milliseconds_to_run
                ll.leds = lightshow_data.available_leds
                ll.milliseconds_flash_min = lightshow_data.milliseconds_to_run_flash_min
                ll.milliseconds_flash_max = lightshow_data.milliseconds_to_run_flash_max
                ll.number_of_leds_to_pick_min = lightshow_data.number_of_leds_to_pick_min
                ll.number_of_leds_to_pick_max = lightshow_data.number_of_leds_to_pick_max

            if ll:
                lightshow_logic_list.append(ll)

        return lightshow_logic_list


    def from_lightshow_logic_list(self, lightshow_logic_list):
        self.lightshow_datas = []

        if not lightshow_logic_list:
            return False

        for lightshow_logic_obj in lightshow_logic_list:
            ld = None

            if lightshow_logic_obj.type == constants.LIGHTSHOW_TYPE_ENABLE:
                ld = LightshowEnabledData()

                ld.milliseconds_to_run = lightshow_logic_obj.milliseconds_to_run
                ld.leds_to_enable = lightshow_logic_obj.leds
            elif lightshow_logic_obj.type == constants.LIGHTSHOW_TYPE_RANDOM:
                ld = LightshowRandomData()

                ld.milliseconds_to_run = lightshow_logic_obj.milliseconds_to_run
                ld.available_leds = lightshow_logic_obj.leds
                ld.milliseconds_to_run_flash_min = lightshow_logic_obj.milliseconds_flash_min
                ld.milliseconds_to_run_flash_max = lightshow_logic_obj.milliseconds_flash_max
                ld.number_of_leds_to_pick_min = lightshow_logic_obj.number_of_leds_to_pick_min
                ld.number_of_leds_to_pick_max = lightshow_logic_obj.number_of_leds_to_pick_max

            if ld:
                self.lightshow_datas.append(ld)

        return True

    
    def load(self, filepath):
        try:
            with open(filepath, "r") as fp:
                data_to_load = fp.read()
        except:
            return False

        try:
            json_data = json.loads(data_to_load)

            segment_json_data = json_data["lightshow_segments"]

            self.lightshow_datas = []

            for segment in segment_json_data:
                if segment["type"] == constants.LIGHTSHOW_TYPE_ENABLE:
                    segment_obj = LightshowEnabledData()
                    segment_obj.load_from_dict(segment)
                elif segment["type"] == constants.LIGHTSHOW_TYPE_RANDOM:
                    segment_obj = LightshowRandomData()
                    segment_obj.load_from_dict(segment)

                self.lightshow_datas.append(segment_obj)
        except:
            return False

        return True


    def save(self, filepath):
        json_data = {}
        
        json_data["lightshow_segments"] = []

        for data in self.lightshow_datas:
            json_data["lightshow_segments"].append(data.to_dict())

        try:
            data_to_save = json.dumps(json_data, indent=4)
        except:
            return False

        try:
            with open(filepath, "w") as fp:
                fp.write(data_to_save)
        except:
            return False

        return True
