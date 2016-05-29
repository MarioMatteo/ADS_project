import ConfigParser

def read_params():
    config = ConfigParser.RawConfigParser()
    config.read('config.txt')
    params = dict()
    for section in config.sections():
        for param in config.options(section):
            try:
                value = config.getint(section, param)
            except ValueError:
                value = config.get(section, param)
                if value in ('yes', 'no'):
                    value = config.getboolean(section, param)
            params[param] = value
    return params
