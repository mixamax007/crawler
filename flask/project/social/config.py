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
    def setup_main_config(path_config=None):

        key_handle = os.environ.get('HANDLE', 'test')

        if not path_config:
            path = os.path.join(os.path.dirname(__file__), 'config', 'rabbitmq.yml')
        else:
            path = path_config

        if os.path.exists(path):
            with open(path, 'rt') as f:
                config_variable = yaml.safe_load(f.read())
                handle_config = config_variable.get(key_handle)
                return Config(handle_config)
        else:
            print("No existing config file in flask config")
            exit(0)