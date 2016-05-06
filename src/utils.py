from automaton_structure import *

from copy import deepcopy

def generate_bad_twin(automaton, level=1):
    initial_state, states = initialize_states(automaton)
    for state in automaton.get_states():
        for destination, transitions in state.get_neighbours().iteritems():
            for transition in transitions:
                if transition.is_observable():
                    states[state.get_name()].add_transition(states[destination.get_name()], deepcopy(transition))
                if level > 1 or not transition.is_observable():
                    fault = False
                    if transition.is_fault():
                        fault = True
                    # print "source " + state.get_name() + ", destination " + destination.get_name()
                    triplets = find(destination, level - transition.get_event_cardinality(), fault, transition.get_event())
                    for event, destination2, fault2 in triplets:
                        states[state.get_name()].add_transition(states[destination2.get_name()],
                                                                Transition(event=event, fault=fault2))
    bad_twin = Automaton(initial_state, states.values())
    if level == 1:
        bad_twin.remove_unreachable_states()
    return bad_twin

def generate_good_twin(automaton):
    good_twin = deepcopy(automaton)
    for state in good_twin.get_states():
        for transitions in state.get_neighbours().values():
            for transition in transitions:
                if transition.is_fault():
                    transitions.remove(transition)
    good_twin.remove_unreachable_states()
    return good_twin

def find(destination, n, fault, event):
    triplets = list()
    for destination2, transitions in destination.get_neighbours().iteritems():
        for transition in transitions:
            fault2 = fault
            if transition.is_fault():
                fault2 = True
            # print "destination2 " + destination2.get_name() + " observable " + str(transition.is_observable())
            event_cardinality = transition.get_event_cardinality()
            if transition.is_observable() and event_cardinality <= n:
                composed_event = deepcopy(transition.get_event())
                composed_event.add(deepcopy(event))
                if n == event_cardinality:
                    triplets.append((composed_event, destination2, fault2))
                else:
                    triplets += find(destination2, n - event_cardinality, fault2, composed_event)
            if not transition.is_observable():
                triplets += find(destination2, n, fault2, event)
    return triplets

def initialize_states(automaton):
    states = dict()
    for state in automaton.get_states():
            states[state.get_name()] = State(state.get_name())
    initial_state = states[automaton.get_initial_state().get_name()]
    return initial_state, states

