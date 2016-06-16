"""
Contains the methods to parse and validate the configuration file in order to read the parameters.
"""

import ConfigParser

CONFIG_FILE_PATH = 'config\params.ini'
PARAMS_ERROR = 'Error(s) found in configuration file'
PARAMS = {
    #   [DIAGNOSABILITY ANALYSIS]
    'level': {'type': int, 'domain': lambda x: x > 0},
    'method': {'values': ('1', '2', '3v1', '3v2', 'all')},
    #   [INTERMEDIATE RESULTS]
    'save': {'values': ('yes', 'no')},
    'compact': {'values': ('yes', 'no')},
    #   [RANDOM AUTOMATON GENERATION]
    'ns': {'type': int, 'domain': lambda x: x > 1},
    'nt': {'type': int, 'domain': lambda x: x > 1},
    'ne': {'type': int, 'domain': lambda x: x > 0},
    'no': {'type': int, 'domain': lambda x: x > 0},
    'nf': {'type': int, 'domain': lambda x: x > 0},
    'attempts': {'type': int, 'domain': lambda x: x > 0},
    #   [COMPLEXITY ANALYSIS]
    'var': {'values': ('lv', 'ns', 'nt', 'bf', 'pe', 'po', 'pf')},
    'n': {'type': int, 'domain': lambda x: x > 0},
    'bf': {'type': float, 'domain': lambda x: x > 0},
    'po': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pe': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pf': {'type': float, 'domain': lambda x: 0 < x < 1},
    'lvmin': {'type': int, 'domain': lambda x: x > 0},
    'lvmax': {'type': int, 'domain': lambda x: x > 0},
    'lvstep': {'type': int, 'domain': lambda x: x > 0},
    'nsmin': {'type': int, 'domain': lambda x: x > 1},
    'nsmax': {'type': int, 'domain': lambda x: x > 1},
    'nsstep': {'type': int, 'domain': lambda x: x > 0},
    'ntmin': {'type': int, 'domain': lambda x: x > 1},
    'ntmax': {'type': int, 'domain': lambda x: x > 1},
    'ntstep': {'type': int, 'domain': lambda x: x > 0},
    'bfmin': {'type': float, 'domain': lambda x: x >= 1},
    'bfmax': {'type': float, 'domain': lambda x: x >= 1},
    'bfstep': {'type': float, 'domain': lambda x: x > 0},
    'pomin': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pomax': {'type': float, 'domain': lambda x: 0 < x < 1},
    'postep': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pemin': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pemax': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pestep': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pfmin': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pfmax': {'type': float, 'domain': lambda x: 0 < x < 1},
    'pfstep': {'type': float, 'domain': lambda x: 0 < x < 1},
}

INT_PARAMS = [p for p, v in PARAMS.iteritems() if 'type' in v and v['type'] is int]
FLOAT_PARAMS = [p for p, v in PARAMS.iteritems() if 'type' in v and v['type'] is float]

def read_params():

    """
    Reads the parameters from the configuration file.

    :return: a name-value map representing the parameters or the message error
    :rtype: dict(str: int or str) or str
    """

    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE_PATH)
    params = dict()
    for section in config.sections():
        for param in config.options(section):
            if param in INT_PARAMS:
                value = config.getint(section, param)
            elif param in FLOAT_PARAMS:
                value = config.getfloat(section, param)
            else:
                value = config.get(section, param)
            params[param] = value
    return validate_params(params)

def validate_params(params):

    """
    Validates the parameters read from the configuration file.

    :param params: the parameters to be validated
    :type params: dict(str: int or str)
    :return: the input parameters if the validation is successful, the message error otherwise
    :rtype: dict(str: int or str) or str
    """

    if len(params) != len(PARAMS):
        return False
    for param, value in params.iteritems():
        if param not in PARAMS:
            return PARAMS_ERROR
        v = PARAMS[param]
        if 'type' in v:
            if type(value) is not v['type'] or not v['domain'](value):
                return PARAMS_ERROR
        else:
            if value not in v['values']:
                return PARAMS_ERROR
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
