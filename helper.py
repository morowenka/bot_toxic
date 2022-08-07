import configparser

def read_config():
    config = configparser.ConfigParser()
    config.read('cfg.ini')
    return config