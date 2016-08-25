from random_automaton import *
import time, datetime
import csv
import math

TIMES_PATH = 'output/times/'
DATE_FORMAT = '%Y-%m-%d_%H-%M-%S'

def method1(automaton, level):

    """
    Implements the first resolving method.

    :param automaton: the automaton to be checked
    :type automaton: Automaton
    :param level: the diagnosability level to be checked
    :type level: int
    :return: True if the automaton has the given diagnosability level, the maximum diagnosability level
    otherwise
    :rtype: bool or int
    """

    old_bad_twin = automaton
    i = 1
    while i <= level:
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        good_twin = generate_good_twin(new_bad_twin)
        synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
        for src_name, dst_name in ambiguous_transitions:
            states = synchronized.get_states()
            if find_loops(states[dst_name], {src_name}):
                return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def method2(automaton, level):

    """
    Implements the second resolving method.

    :param automaton: the automaton to be checked
    :type automaton: Automaton
    :param level: the diagnosability level to be checked
    :type level: int
    :return: True if the automaton has the diagnosability level specified in params, the maximum diagnosability level
    otherwise
    :rtype: bool or int
    """

    old_bad_twin = automaton
    i = 1
    while i <= level:
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        c2 = condition_C2(new_bad_twin)
        c3 = condition_C3(new_bad_twin)
        if not(c2 or c3):
            good_twin = generate_good_twin(new_bad_twin)
            synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
            c1 = condition_C1(ambiguous_transitions)
            if not c1:
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], {src_name}):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def method3_1(automaton, level):

    """
    Implements the first version of the third resolving method.

    In the first version the synchronized automaton is computed only when C2 and C3 conditions are not satisfied.
    If the previous level synchronized automaton is not available it is first computed through the first version
    of the synchronization method. Then it is used in the second version of the synchronization method in order to
    compute the current level synchronized automaton.

    :param automaton: the automaton to be checked
    :type automaton: Automaton
    :param level: the diagnosability level to be checked
    :type level: int
    :return: True if the automaton has the diagnosability level specified in params, the maximum diagnosability level
    otherwise
    :rtype: bool or int
    """

    old_bad_twin = automaton
    i = 1
    first_sync = True
    last_sync_level = 1
    while i <= level:
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        c2 = condition_C2(new_bad_twin)
        c3 = condition_C3(new_bad_twin)
        if not(c2 or c3):
            if first_sync:
                good_twin = generate_good_twin(new_bad_twin)
                synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
                first_sync = False
            else:
                if last_sync_level < i - 1:
                    old_good_twin = generate_good_twin(old_bad_twin)
                    synchronized, ambiguous_transitions = synchronize_1(old_bad_twin, old_good_twin)
                synchronized = synchronize_2(synchronized, ambiguous_transitions, new_bad_twin, i)
            last_sync_level = i
            c1 = condition_C1(ambiguous_transitions)
            if not c1:
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], {src_name}):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def method3_2(automaton, level):

    """
    Implements the second version of the third resolving method.

    Unlike the first version, the synchronized automaton is always computed; this guarantees its availability through
    the iterations. At level one the first version of the synchronization method is used; at next levels the second
    version is used.

    :param automaton: the automaton to be checked
    :type automaton: Automaton
    :param level: the diagnosability level to be checked
    :type level: int
    :return: True if the automaton has the diagnosability level specified in params, the maximum diagnosability level
    otherwise
    :rtype: bool or int
    """

    old_bad_twin = automaton
    i = 1
    while i <= level:
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if i == 1:
            good_twin = generate_good_twin(new_bad_twin)
            synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
        else:
            synchronized = synchronize_2(synchronized, ambiguous_transitions, new_bad_twin, i)
        c2 = condition_C2(new_bad_twin)
        c3 = condition_C3(new_bad_twin)
        if not(c2 or c3):
            c1 = condition_C1(ambiguous_transitions)
            if not c1:
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], {src_name}):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def get_times(level, ns, nt, no, ne, nf):

    """
    Measures the execution time of the resolving methods.

    The methods are performed on a random generated automaton that satisfies the input parameters.

    :param level: the diagnosability level
    :type level: int
    :param ns: the number of states
    :type ns: int
    :param nt: the maximum number of transitions
    :type nt: int
    :param no: the number of observable transitions
    :type no: int
    :param ne: the cardinality of the events alphabet
    :type ne: int
    :param nf: the number of fault transitions
    :type nf: int
    :return: the list of the measured times in seconds, one for each method
    :rtype: list(float)
    """

    automaton = search_automaton(ns, nt, no, ne, nf, level, method3_2)
    if type(automaton) is str:
        print automaton
        exit(-1)
    times = list()
    for method in (method1, method2, method3_1, method3_2):
        start = time.clock()
        method(automaton, level)
        stop = time.clock()
        times.append(stop - start)
    return times

def show_progress(varname, varvalue, varmin, varmax, varstep, i, n):

    """
    Shows the progress of the analysis.

    :param varname: the name of the variable under analysis
    :type varname: str
    :param varvalue: the current value of the variable under analysis
    :type varvalue: int or float
    :param varmin: the minimum value of the variable under analysis
    :type varmin: int or float
    :param varmax: the maximum value of the variable under analysis
    :type varmax: int or float
    :param varstep: the step value of the variable under analysis
    :type varstep: int or float
    :param i: the current automaton index, given a configuration of the parameters
    :type i: int
    :param n: the number of automaton to be generated, given a configuration of the parameters
    :type n: int
    """

    varnum = n * (varvalue - varmin) / float(varstep)
    varden = math.ceil((varmax - varmin) / float(varstep)) + 1
    num = int(varnum + i + 1)
    den = int(varden * n)
    progress = int(round(100 * float(num) / den))
    if type(varvalue) is float:
        varvalue = round(varvalue, 2)
        varmax = round(varmax, 2)
    os.system('cls')
    print varname + ': ' + str(varvalue) + '/' + str(varmax) + ', n: ' + str(i + 1) + '/' + str(n) + ', progress: ' + \
          str(progress) + '% (' + str(num) + '/' + str(den) + ')'

def lv_analysis():

    """
    Performs the analysis by varying the diagnosability level.
    """

    global params
    n = params['n']
    lvmin = params['lvmin']
    lvmax = params['lvmax']
    lvstep = params['lvstep']
    ns = params['ns']
    nt = params['nt']
    no = params['no']
    ne = params['ne']
    nf = params['nf']
    lv_dir = create_dir(TIMES_PATH + 'lv')
    filename = datetime.datetime.now().strftime(DATE_FORMAT) + '.csv'
    with open(lv_dir + filename, 'wb') as csvfile:
        fw = csv.writer(csvfile)
        fw.writerow(('lv', 'ns', 'nt', 'no', 'ne', 'nf',
                     'method1', 'method2', 'method3_1', 'method3_2'))
        lv = lvmin
        while lv <= lvmax:
            times = [0] * 4
            for i in range(n):
                times = map(sum, zip(times, get_times(lv, ns, nt, no, ne, nf)))
                show_progress('lv', lv, lvmin, lvmax, lvstep, i, n)
            times = map(lambda x : float(x) / n, times)
            fw.writerow((lv, ns, nt, no, ne, nf) + tuple(times))
            lv += lvstep
    csvfile.close()

def ns_analysis():

    """
    Performs the analysis by varying the number of states.
    """

    global params
    n = params['n']
    level = params['level']
    nsmin = params['nsmin']
    nsmax = params['nsmax']
    nsstep = params['nsstep']
    bf = params['bf']
    po = params['po']
    pe = params['pe']
    pf = params['pf']
    ns_dir = create_dir(TIMES_PATH + 'ns')
    filename = datetime.datetime.now().strftime(DATE_FORMAT) + '.csv'
    with open(ns_dir + filename, 'wb') as csvfile:
        fw = csv.writer(csvfile)
        fw.writerow(('lv', 'ns', 'nt', 'no', 'ne', 'nf',
                     'method1', 'method2', 'method3_1', 'method3_2'))
        ns = nsmin
        while ns <= nsmax:
            nt = int(round(bf * ns))
            no = max(int(round(po * nt)), 1)
            ne = max(int(round(pe * no)), 1)
            nf = max(int(round(pf * nt)), 1)
            times = [0] * 4
            for i in range(n):
                times = map(sum, zip(times, get_times(level, ns, nt, no, ne, nf)))
                show_progress('ns', ns, nsmin, nsmax, nsstep, i, n)
            times = map(lambda x: float(x) / n, times)
            fw.writerow((level, ns, nt, no, ne, nf) + tuple(times))
            ns += nsstep
    csvfile.close()

def bf_analysis():

    """
    Performs the analysis by varying the branching factor.
    """

    global params
    n = params['n']
    level = params['level']
    bfmin = params['bfmin']
    bfmax = params['bfmax']
    bfstep = params['bfstep']
    ns = params['ns']
    po = params['po']
    pe = params['pe']
    pf = params['pf']
    bf_dir = create_dir(TIMES_PATH + 'bf')
    filename = datetime.datetime.now().strftime(DATE_FORMAT) + '.csv'
    with open(bf_dir + filename, 'wb') as csvfile:
        fw = csv.writer(csvfile)
        fw.writerow(('lv', 'ns', 'bf', 'nt', 'no', 'ne', 'nf',
                     'method1', 'method2', 'method3_1', 'method3_2'))
        bf = bfmin
        while bf <= bfmax:
            nt = int(round(bf * ns))
            no = max(int(round(po * nt)), 1)
            ne = max(int(round(pe * no)), 1)
            nf = max(int(round(pf * nt)), 1)
            times = [0] * 4
            for i in range(n):
                times = map(sum, zip(times, get_times(level, ns, nt, no, ne, nf)))
                show_progress('bf', bf, bfmin, bfmax, bfstep, i, n)
            times = map(lambda x: float(x) / n, times)
            fw.writerow((level, ns, bf, nt, no, ne, nf) + tuple(times))
            bf += bfstep
    csvfile.close()

def pe_analysis():

    """
    Performs the analysis by varying the cardinality of events alphabet over the number of observable transitions.
    """

    global params
    n = params['n']
    level = params['level']
    pemin = params['pemin']
    pemax = params['pemax']
    pestep = params['pestep']
    ns = params['ns']
    nt = params['nt']
    po = params['po']
    pf = params['pf']
    pe_dir = create_dir(TIMES_PATH + 'pe')
    filename = datetime.datetime.now().strftime(DATE_FORMAT) + '.csv'
    with open(pe_dir + filename, 'wb') as csvfile:
        fw = csv.writer(csvfile)
        fw.writerow(('lv', 'ns', 'nt', 'no', 'pe', 'ne', 'nf',
                     'method1', 'method2', 'method3_1', 'method3_2'))
        pe = pemin
        while pe <= pemax:
            no = max(int(round(po * nt)), 1)
            ne = max(int(round(pe * no)), 1)
            nf = max(int(round(pf * nt)), 1)
            times = [0] * 4
            for i in range(n):
                times = map(sum, zip(times, get_times(level, ns, nt, no, ne, nf)))
                show_progress('pe', pe, pemin, pemax, pestep, i, n)
            times = map(lambda x: float(x) / n, times)
            fw.writerow((level, ns, nt, no, pe, ne, nf) + tuple(times))
            pe += pestep
    csvfile.close()

def po_analysis():

    """
    Performs the analysis by varying the percentage of observable transitions.
    """

    global params
    n = params['n']
    level = params['level']
    pomin = params['pomin']
    pomax = params['pomax']
    postep = params['postep']
    ns = params['ns']
    nt = params['nt']
    pe = params['pe']
    pf = params['pf']
    po_dir = create_dir(TIMES_PATH + 'po')
    filename = datetime.datetime.now().strftime(DATE_FORMAT) + '.csv'
    with open(po_dir + filename, 'wb') as csvfile:
        fw = csv.writer(csvfile)
        fw.writerow(('lv', 'ns', 'nt', 'po', 'no', 'ne', 'nf',
                     'method1', 'method2', 'method3_1', 'method3_2'))
        po = pomin
        while po <= pomax:
            no = max(int(round(po * nt)), 1)
            ne = max(int(round(pe * no)), 1)
            nf = max(int(round(pf * nt)), 1)
            times = [0] * 4
            for i in range(n):
                times = map(sum, zip(times, get_times(level, ns, nt, no, ne, nf)))
                show_progress('po', po, pomin, pomax, postep, i, n)
            times = map(lambda x: float(x) / n, times)
            fw.writerow((level, ns, nt, po, no, ne, nf) + tuple(times))
            po += postep
    csvfile.close()

def pf_analysis():

    """
    Performs the analysis by varying the percentage of fault transitions.
    """

    global params
    n = params['n']
    level = params['level']
    pfmin = params['pfmin']
    pfmax = params['pfmax']
    pfstep = params['pfstep']
    ns = params['ns']
    nt = params['nt']
    po = params['po']
    pe = params['pe']
    pf_dir = create_dir(TIMES_PATH + 'pf')
    filename = datetime.datetime.now().strftime(DATE_FORMAT) + '.csv'
    with open(pf_dir + filename, 'wb') as csvfile:
        fw = csv.writer(csvfile)
        fw.writerow(('lv', 'ns', 'nt', 'no', 'ne', 'pf', 'nf',
                     'method1', 'method2', 'method3_1', 'method3_2'))
        pf = pfmin
        while pf <= pfmax:
            no = max(int(round(po * nt)), 1)
            ne = max(int(round(pe * no)), 1)
            nf = max(int(round(pf * nt)), 1)
            times = [0] * 4
            for i in range(n):
                times = map(sum, zip(times, get_times(level, ns, nt, no, ne, nf)))
                show_progress('pf', pf, pfmin, pfmax, pfstep, i, n)
            times = map(lambda x: float(x) / n, times)
            fw.writerow((level, ns, nt, no, ne, pf, nf) + tuple(times))
            pf += pfstep
    csvfile.close()

def complexity_analysis(var):

    """
    Performs the analysis by varying the input variable.
    """

    {'lv': lv_analysis,
     'ns': ns_analysis,
     'bf': bf_analysis,
     'pe': pe_analysis,
     'po': po_analysis,
     'pf': pf_analysis
    }.get(var)()

if __name__ == '__main__':
    params = read_params()
    if type(params) is str:
        print params
        exit(-1)
    complexity_analysis(params['var'])