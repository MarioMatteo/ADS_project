from utils import *
import string, random
import networkx as nx

"""
    ns: number of states
    nt: max number of transitions
    ne: cardinality of events alphabet
    no: number of observable transitions
    nf: number of fault transitions
"""
def generate_random_automaton(ns, nt, ne, no, nf):
    states = dict()
    if ns <= len(string.ascii_uppercase):
        state_names = string.ascii_uppercase[:ns]
    else:
        state_names = ['S' + str(i) for i in range(1, ns + 1)]
    if ne <= len(string.ascii_lowercase):
        event_names = string.ascii_lowercase[:ne]
    else:
        event_names = ['e' + str(i) for i in range(1, ne + 1)]
    for name in state_names:
        states[name] = State(name)
    event_names = initialize_event_names(event_names, no)
    initial_state = random.choice(state_names)
    added_nt = add_minimal_transitions(states[initial_state], states, ns, nt - ns)
    random_automaton = Automaton(initial_state, states)
    cycles = get_cycles(random_automaton)
    while len(cycles) > no:
        states = initialize_states(random_automaton)
        added_nt = add_minimal_transitions(states[initial_state], states, ns, nt - ns)
        random_automaton = Automaton(initial_state, states)
        cycles = get_cycles(random_automaton)
        # print 'a'
    nt -= added_nt
    added_no = add_minimal_observable_transitions(random_automaton, event_names, cycles)
    no -= added_no
    # print 'nt=',str(nt),' no=',str(no),' nf=',str(nf)
    while no > 0:
        if nt > nf:
            src = states[random.choice(state_names)]
            dst = states[random.choice(state_names)]
            event_name = event_names[-1]
            while not src.add_transition(dst, Transition(Event(event_name))):
                src = states[random.choice(state_names)]
                dst = states[random.choice(state_names)]
                # print 'b'
            event_names.pop()
            nt -= 1
        else:
            unobservable_transitions = random_automaton.get_unobservable_transitions()
            transition = random.choice(unobservable_transitions)
            transition.set_event(Event(event_names.pop()))
        no -= 1
    # print 'nt=', str(nt), ' no=', str(no), ' nf=', str(nf)
    while nf > 0:
        if nt > 0:
            src = states[random.choice(state_names)]
            dst = states[random.choice(state_names)]
            while not src.add_transition(dst, Transition(fault=True)):
                src = states[random.choice(state_names)]
                dst = states[random.choice(state_names)]
                # print src.get_name()+'->'+dst.get_name()
                # save_img(random_automaton, 'in loop', 'in loop', 'png', True)
            nt -= 1
        else:
            unobservable_transitions = random_automaton.get_unobservable_transitions()
            transition = random.choice(unobservable_transitions)
            transition.set_fault()
        nf -= 1
    for state in random_automaton.get_states().values():
        state.set_visited(False)
    return random_automaton

def initialize_event_names(event_names, no):
    events = dict()
    for name in event_names:
        events[name] = 1
    for i in range(no - len(event_names)):
        name = random.choice(event_names)
        events[name] += 1
    result = map(lambda (name, count): [name] * count, events.iteritems())
    random.shuffle(result)
    return result

def add_minimal_transitions(src, states, ns, nl):
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

def add_minimal_observable_transitions(automaton, event_names, cycles):
    count = 0
    while len(cycles) > 0:
        cycle = cycles.pop(0)
        if len(cycle) == 1:
            src_name = cycle[0]
            dst_name = src_name
        else:
            src_name = random.choice(cycle)
            dst_index = (cycle.index(src_name) + 1) % len(cycle)
            dst_name = cycle[dst_index]
        event_name = event_names[-1]
        if automaton.set_transition_event(src_name, dst_name, Event(event_name)):
            event_names.pop()
            count += 1
    return count

def get_cycles(automaton):
    return sorted(list(nx.simple_cycles(nx.DiGraph(automaton.get_transitions()))), key=len)
