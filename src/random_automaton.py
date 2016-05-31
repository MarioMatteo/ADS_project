from utils import *
import string, random
import networkx as nx

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
    automaton = Automaton(initial_state, states)
    loops = get_loops(automaton)
    while len(loops) > no:
        states = initialize_states(automaton)
        added_nt = add_minimal_transitions(states[initial_state], states, ns, nt - ns)
        automaton = Automaton(initial_state, states)
        loops = get_loops(automaton)
    nt -= added_nt
    added_no = add_minimal_observable_transitions(automaton, event_names, loops)
    no -= added_no
    while no > 0:
        if nt > nf:
            src = states[random.choice(state_names)]
            dst = states[random.choice(state_names)]
            event_name = event_names[-1]
            while not src.add_transition(dst, Transition(Event(event_name))):
                src = states[random.choice(state_names)]
                dst = states[random.choice(state_names)]
            event_names.pop()
            nt -= 1
        else:
            unobservable_transitions = automaton.get_unobservable_transitions()
            transition = random.choice(unobservable_transitions)
            transition.set_event(Event(event_names.pop()))
        no -= 1
    prev_nt = nt
    prev_nf = nf
    prev_automaton = automaton
    while True:
        nt = prev_nt
        nf = prev_nf
        automaton = deepcopy(prev_automaton)
        states = automaton.get_states()
        while nf > 0:
            if nt > 0:
                src = states[random.choice(state_names)]
                dst = states[random.choice(state_names)]
                while not src.add_transition(dst, Transition(fault=True)):
                    src = states[random.choice(state_names)]
                    dst = states[random.choice(state_names)]
                nt -= 1
                automaton.set_states(states)
            else:
                unobservable_transitions = automaton.get_unobservable_transitions()
                transition = random.choice(unobservable_transitions)
                transition.set_fault()
            nf -= 1
        if not has_fault_loops(automaton):
            break
    for state in automaton.get_states().values():
        state.set_visited(False)
    return automaton

def initialize_event_names(event_names, no):
    events = dict()
    for name in event_names:
        events[name] = 1
    for i in range(no - len(event_names)):
        name = random.choice(event_names)
        events[name] += 1
    result = list()
    for name, count in events.iteritems():
        for i in range(count):
            result.append(name)
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

def add_minimal_observable_transitions(automaton, event_names, loops):
    count = 0
    while len(loops) > 0:
        cycle = loops.pop(0)
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

def get_loops(automaton):
    return sorted(list(nx.simple_cycles(nx.DiGraph(automaton.get_transitions()))), key=len)

def has_fault_loops(automaton):
    return len(list(nx.simple_cycles(nx.DiGraph(automaton.get_transitions(unobservable=True))))) > 0
