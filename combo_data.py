# python imports
import json

# local imports
import constants
import combo_logic
import lightshow_data


class ComboData:
    def __init__(self):
        self.milliseconds_to_run = 0
        self.lightshow_files = []


    def to_dict(self):
        ret = {}
        ret["milliseconds_to_run"] = self.milliseconds_to_run
        ret["lightshow_files"] = self.lightshow_files

        return ret

    
    def load_from_dict(self, dict_to_load_from):
        self.milliseconds_to_run = dict_to_load_from["milliseconds_to_run"]
        self.lightshow_files = dict_to_load_from["lightshow_files"]


class ComboDataMiddleware:
    def __init__(self):
        self.combo_data = None


    def load_from_values(self, milliseconds_to_run, lightshow_filepaths):
        self.combo_data = ComboData()
        self.combo_data.milliseconds_to_run = milliseconds_to_run

        for lightshow_filepath in lightshow_filepaths:
            self.combo_data.lightshow_files.append(lightshow_filepath)

    
    def load(self, filepath):
        try:
            with open(filepath, "r") as fp:
                data_to_load = fp.read()
        except:
            return False

        try:
            json_data = json.loads(data_to_load)

            combo_json_data = json_data["combo"]

            self.combo_data = ComboData()
            self.combo_data.milliseconds_to_run = int(combo_json_data["milliseconds_to_run"])

            lightshow_files = combo_json_data["lightshow_files"]

            for lightshow_file in lightshow_files:
                self.combo_data.lightshow_files.append(lightshow_file)
        except:
            return False

        return True


    def save(self, filepath):
        json_data = {}
        
        json_data["combo"] = self.combo_data.to_dict()

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
