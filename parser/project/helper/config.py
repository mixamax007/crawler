
import os
import yaml


class Config:
    def __init__(self, entries):
        for key, value in entries.items():
            if type(value) is dict:
                value_tmp = Config(value)
            else:
                value_tmp = value
            self.__dict__[key] = value_tmp

    @staticmethod
    def setup_main_config(path):
        if os.path.exists(path):
            with open(path, 'rt', encoding="utf-8") as f:
                config_variable = yaml.safe_load(f.read())
                return Config(config_variable)
        else:
            print("No existing config file")
            exit(0)