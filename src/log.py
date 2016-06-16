"""
Contains log messages and constants
"""

MSG_BT = '[Method %s - Level %s] generating bad twin ...'
MSG_GT = '[Method %s - Level %s] generating good twin ...'
MSG_SYNC = '[Method %s - Level %s] synchronizing twins ...'
MSG_RES = '[Method %s - Level %s] saving intermediate results ...'
MSG_COND_VER = '[Method %s - Level %s] verifying condition C%s ...'
MSG_COND_SAT = '[Method %s - Level %s] condition C%s%ssatisfied ...'
MSG_LEV_SAT = '[Method %s - Level %s] diagnosability level%ssatisfied ...'
MSG_MAX_LEV = '[Method %s] maximum diagnosability level: %s'
MSG_TRUE_LEV = '[Method %s] checked diagnosability level: %s (true)'

LEV_SEP = '-' * 70
METH_SEP = '#' * 70
END_LEV_SEP = '\\n'

TYPE_METH_SEP = 0
TYPE_COLOR_CHANGE = 1
TYPE_MSG_TWIN = 2
TYPE_MSG_RES = 3
TYPE_LEV_SAT = 4
TYPE_PARAMS_ERROR = 5
TYPE_FINISH = 6
TYPE_END_LEV = 7