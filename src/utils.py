from automaton_structure import *

from copy import copy

def generate_bad_twin(automaton, level=1):
    if level == 1:
        return generate_first_level_bad_twin(automaton)
    return generate_nth_level_bad_twin(automaton, level)

def generate_good_twin(automaton):
    pass

def generate_first_level_bad_twin(automaton):
    initial_state, states = initialize_states(automaton)
    for state in automaton.get_states():
        for destination, transitions in state.get_neighbours().iteritems():
            for transition in transitions:
                if transition.is_observable():
                    states[state.get_name()].add_transition(destination, transition)
                else:
                    fault = False
                    if transition.is_fault():
                        fault = True
                    print "source " + state.get_name() + ", destination " + destination.get_name()
                    triplets = find(destination, 1, fault, None)
                    for event, destination2, fault2 in triplets:
                        states[state.get_name()].add_transition(destination2, Transition(event=event, fault=fault2))
    return Automaton(initial_state, states.values())


def find(destination, n, fault, event):
    triplets = list()
    for destination2, transitions in destination.get_neighbours().iteritems():
        for transition in transitions:
            fault2 = fault
            if transition.is_fault():
                fault2 = True
            print "destination2 " + destination2.get_name() + " observable " + str(transition.is_observable())
            event_cardinality = transition.get_event().get_cardinality()
            if transition.is_observable() and event_cardinality <= n:
                composed_event = copy(transition.get_event())
                composed_event.add(event)
                if n == event_cardinality:
                    triplets_union(triplets, [(composed_event, destination2, fault2)])
                else:
                    triplets_union(triplets, find(destination2, n - event_cardinality, fault2, composed_event))
            if not transition.is_observable():
                triplets_union(triplets, find(destination2, n, fault2, event))
    return triplets

def generate_nth_level_bad_twin(automaton, level):
    initial_state, states = initialize_states(automaton)
    for state in automaton.get_states():
        for destination, transitions in state.get_neighbours().iteritems():
            for transition in transitions:
                states[state.get_name()].add_transition(destination, transition)
                fault = False
                if transition.is_fault():
                    fault = True
                event_cardinality = transition.get_event().get_cardinality()
                print "source " + state.get_name() + ", destination " + destination.get_name()
                triplets = find(destination, level - event_cardinality, fault, transition.get_event())
                for event, destination2, fault2 in triplets:
                    if not event.is_composed_by_all_same_events():
                        states[state.get_name()].add_transition(destination2, Transition(event=event, fault=fault2))
    return Automaton(initial_state, states.values())

def initialize_states(automaton):
    states = dict()
    for state in automaton.get_states():
            states[state.get_name()] = State(state.get_name())
    initial_state = states[automaton.get_initial_state().get_name()]
    return initial_state, states

def triplet_already_present(triplet, triplet_list):
    event, destination, fault = triplet
    for _event, _destination, _fault in triplet_list:
        if event.get_name() == _event.get_name() and destination.get_name() == _destination.get_name() and fault == _fault:
            return True
    return False

def triplets_union(triplets1, triplets2):
    for triplet in triplets2:
        if not triplet_already_present(triplet, triplets1):
            triplets1.append(triplet)
