"""
Contains the method to parse the configuration file in order to retrieve parameters.
"""

import ConfigParser

CONFIG_FILE_PATH = 'conf\params.ini'

def read_params():

    """
    Reads the parameters from the configuration file.

    :return: a name-value map representing the parameters
    :rtype: dict(str: int or bool or str)
    """

    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE_PATH)
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
