"""
Contains the methods to parse and validate the configuration file in order to read the parameters.
"""

import ConfigParser

CONFIG_FILE_PATH = 'config\params.ini'
PARAMS = {
    'level': int,
    'method': ('1', '2', '3v1', '3v2'),
    'save': ('yes', 'no'),
    'save_source': ('yes', 'no'),
    'compact': ('yes', 'no'),
    'ns': int,
    'nt': int,
    'ne': int,
    'no': int,
    'nf': int
}

def read_params():

    """
    Reads the parameters from the configuration file.

    :return: a name-value map representing the parameters or False
    :rtype: dict(str: int or str) or bool
    """

    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE_PATH)
    params = dict()
    for section in config.sections():
        for param in config.options(section):
            try:
                if param != 'method':
                    value = config.getint(section, param)
                else:
                    value = config.get(section, param)
            except ValueError:
                value = config.get(section, param)
            params[param] = value
    return validate_params(params)

def validate_params(params):

    """
    Validates the parameters read from the configuration file.

    :param params: the parameters to be validated
    :type params: dict(str: int or str)
    :return: the input parameters if the validation is successful, False otherwise
    :rtype: dict(str: int or str) or bool
    """

    if len(params) != len(PARAMS):
        return False
    for param, value in params.iteritems():
        if param not in PARAMS:
            return False
        if type(PARAMS[param]) is type:
            if type(value) is not PARAMS[param]:
                return False
        else:
            if value not in PARAMS[param]:
                return False
    return params

def to_bool(value):

    """
    Converts a value into the corresponding boolean one.

    :param value: the value to be converted
    :type value: str
    :return: the corresponding boolean value
    :rtype: bool
    """

    if value == 'yes':
        return True
    return False
