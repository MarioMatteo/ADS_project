from utils import *
from config import *
import string, random

def validate_params(ns, nt, no, ne, nf):

    """
    Validates the input parameters of the random automata generator.

    The parameters are considered valid if they satisfy the following constraints:
        - nt >= ns
        - no != 0
        - ne <= no
        - nf != 0
        - nt >= no + nf

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
    :return: true if the parameters are valid, the error message otherwise
    :rtype: bool or str
    """

    if nt < ns:
        return log.STATES_TRANSITIONS_NUMBER_ERROR
    if no == 0:
        return log.ZERO_OBSERVABLE_TRANSITIONS_ERROR
    if ne > no:
        return log.OBSERVABLE_EVENTS_TRANSITIONS_NUMBER_ERROR
    if nf == 0:
        return log.ZERO_FAULT_TRANSITIONS_ERROR
    if nt < no + nf:
        return log.TOTAL_TRANSITIONS_NUMBER_ERROR
    return True

def generate_random_automaton(ns, nt, no, ne, nf):

    """
    Generates a random non-deterministic finite automaton.

    The generation logic is the following:
        - ns random states are generated
        - ne random events are generated
        - a random state is marked as initial
        - some random unobservable transitions are added in order to guarantee that each state has at least one outgoing transition
        - some random observable transitions are added in order to guarantee that the events alphabet is alive
        - other random observable transitions are added till the total number of observable transitions is no
        - some random fault transitions are added
    
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
    :return: true if the parameters are valid and maximum number of attempts is not reached, the error message otherwise
    :rtype: bool or str
    """

    check = validate_params(ns, nt, no, ne, nf)
    if type(check) is not bool:
        return check
    params = read_params()
    if type(params) is str:
        return params
    max_attempts = read_params()['attempts']
    states = dict()
    if ns <= len(string.ascii_uppercase):
        states_names = string.ascii_uppercase[:ns]
    else:
        states_names = ['S' + str(i) for i in range(1, ns + 1)]
    if ne <= len(string.ascii_lowercase):
        events_names = string.ascii_lowercase[:ne]
    else:
        events_names = ['e' + str(i) for i in range(1, ne + 1)]
    for name in states_names:
        states[name] = State(name)
    events_names = initialize_events_names(events_names, no)
    initial_state = random.choice(states_names)
    added_nt = add_minimal_transitions(states[initial_state], states, ns, nt - ns)
    automaton = Automaton(initial_state, states)
    loops = automaton.get_loops()
    attempts = 1
    while len(loops) > no:
        if attempts > max_attempts:
            return log.MAX_ATTEMPTS_ERROR
        states = initialize_states(automaton)
        added_nt = add_minimal_transitions(states[initial_state], states, ns, nt - ns)
        automaton.set_states(states)
        loops = automaton.get_loops()
        attempts += 1
    nt -= added_nt
    added_no = add_minimal_observable_transitions(automaton, events_names, loops)
    no -= added_no
    while no > 0:
        if nt > nf:
            src = states[random.choice(states_names)]
            dst = states[random.choice(states_names)]
            event_name = events_names[-1]
            attempts = 1
            while not src.add_transition(dst, Transition(Event(event_name))):
                if attempts == max_attempts:
                    return log.MAX_ATTEMPTS_ERROR
                src = states[random.choice(states_names)]
                dst = states[random.choice(states_names)]
                attempts += 1
            events_names.pop()
            nt -= 1
        else:
            unobservable_transitions = automaton.get_unobservable_transitions()
            transition = random.choice(unobservable_transitions)
            transition.set_event(Event(events_names.pop()))
        no -= 1
    prev_nt = nt
    prev_nf = nf
    prev_automaton = automaton
    attempts1 = 0
    while True:
        if attempts1 == max_attempts:
            return log.MAX_ATTEMPTS_ERROR
        nt = prev_nt
        nf = prev_nf
        automaton = deepcopy(prev_automaton)
        states = automaton.get_states()
        while nf > 0:
            if nt > 0:
                src = states[random.choice(states_names)]
                dst = states[random.choice(states_names)]
                attempts2 = 1
                while not src.add_transition(dst, Transition(fault=True)):
                    if attempts2 == max_attempts:
                        return log.MAX_ATTEMPTS_ERROR
                    src = states[random.choice(states_names)]
                    dst = states[random.choice(states_names)]
                    attempts2 += 1
                nt -= 1
                automaton.set_states(states)
            else:
                unobservable_transitions = automaton.get_unobservable_transitions()
                transition = random.choice(unobservable_transitions)
                transition.set_fault()
            nf -= 1
        if not automaton.has_fault_loops():
            break
        attempts1 += 1
    for state in automaton.get_states().values():
        state.set_visited(False)
    return automaton

def initialize_events_names(events_names, no):

    """
    Initializes the list of the events names.

    It starts from a list of ne events names and generates a shuffled list of no events names, using a sampling with
    replacement and ensuring that all the input events names appears in the output list.

    :param events_names: the list of the events names
    :type events_names: list(str)
    :param no: the number of observable transitions
    :type no: int
    :return: the shuffled list of no sampled events names
    :rtype: list(str)
    """

    events = dict()
    for name in events_names:
        events[name] = 1
    for i in range(no - len(events_names)):
        name = random.choice(events_names)
        events[name] += 1
    result = list()
    for name, count in events.iteritems():
        for i in range(count):
            result.append(name)
    random.shuffle(result)
    return result

def add_minimal_transitions(src, states, ns, nl):

    """
    Recursively adds random unobservable transitions.

    It adds some random unobservable transitions in order to guarantee that each state has at least one outgoing
    transition.

    :param src: the transition source state
    :type src: State
    :param states: the name-state map of the automaton
    :type states: dict(str: State)
    :param ns: the number of states to be processed
    :type ns: int
    :param nl: the number of available loops
    :type nl: int
    :return: the number of unobservable transitions that have been added
    :rtype: int
    """

    state_names = states.keys()
    src.set_visited()
    dst_name = random.choice(state_names)
    dst = states[dst_name]
    if ns == 1:
        src.add_transition(dst, Transition())
        return 1
    if dst.is_visited() and nl > 0:
        while not src.add_transition(dst, Transition()) and len(state_names) > 1:
            state_names.remove(dst_name)
            dst_name = random.choice(state_names)
            dst = states[dst_name]
        if dst.is_visited():
            state_names = states.keys()
            next_name = random.choice(state_names)
            next_state = states[next_name]
            while not next_state.is_visited() and len(state_names) > 1:
                state_names.remove(next_name)
                next_name = random.choice(state_names)
                next_state = states[next_name]
            return 1 + add_minimal_transitions(next_state, states, ns, nl - 1)
        return 1 + add_minimal_transitions(dst, states, ns - 1, nl)
    while dst.is_visited() and len(state_names) > 1:
        state_names.remove(dst_name)
        dst_name = random.choice(state_names)
        dst = states[dst_name]
    src.add_transition(dst, Transition())
    return 1 + add_minimal_transitions(dst, states, ns - 1, nl)

def add_minimal_observable_transitions(automaton, events_names, loops):

    """
    Adds random observable transitions.

    It adds some random observable transitions in order to guarantee that the events alphabet is alive.

    :param automaton: the automaton to be updated
    :type automaton: Automaton
    :param events_names: the list of the names of the events to be associated with observable transitions
    :type events_names: list(str)
    :param loops: the loops to be covered by at least one observable transition
    :type loops: list(tuple(str))
    :return: the number of observable transitions that have been added
    :rtype: int
    """

    count = 0
    while len(loops) > 0:
        loop = loops.pop(0)
        if len(loop) == 1:
            src_name = loop[0]
            dst_name = src_name
        else:
            src_name = random.choice(loop)
            dst_index = (loop.index(src_name) + 1) % len(loop)
            dst_name = loop[dst_index]
        event_name = events_names[-1]
        if automaton.set_transition_event(src_name, dst_name, Event(event_name)):
            events_names.pop()
            count += 1
    return count

def search_automaton(ns, nt, no, ne, nf, level, method):

    """
    Searches an automaton whose diagnosability level is at least level.

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
    :param level: the diagnosability level
    :type level: int
    :param method: the method used to check the diagnosability level
    :type method: func
    :return: the automaton found
    :rtype: Automaton
    """

    automaton = generate_random_automaton(ns, nt, no, ne, nf)
    while type(automaton) is not str and type(method(automaton, level)) is not bool:
    # while type(automaton) is not str and method(automaton, level + 1) != level:
        automaton = generate_random_automaton(ns, nt, no, ne, nf)
    return automaton
