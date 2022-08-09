import configparser


def read_config():
    config = configparser.ConfigParser()
    config.read('config/cfg.ini')
    return config
