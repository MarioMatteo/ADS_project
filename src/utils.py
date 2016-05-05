from automaton_structure import *

def generate_bad_twin(automaton, level=1):
    if level == 1:
        return generate_first_level_bad_twin(automaton)
    else:
        return generate_nth_level_bad_twin(automaton, level)

def generate_first_level_bad_twin(automaton):
    initial_state, states = initialize_states(automaton)
    for state in automaton.get_states():
        for destination, unobservable_transitions in state.get_unobservable_neighbours():
            for transition in unobservable_transitions:
                fault = False
                if transition.is_fault():
                    fault = True


def find(automaton, destination, n, fault, event):
    triplets = list()
    for destination2, transitions in destination.get_neighbours():
            for transition in transitions:
                fault = False
                if transition.is_fault():
                    fault = True
                if transition.is_observable() and transition.get_event().get_cardinality() <= n:
                    if n == transition.get_event().get_cardinality():
                        composed_event = transition.get_event()
                        composed_event.add(event)
                        triplets.add((Event()))


def generate_nth_level_bad_twin(automaton, level):
    pass

def initialize_states(automaton):
    states = [State(state.get_name()) for state in automaton.get_states()
              if state.get_name() != automaton.get_initial_state().get_name()]
    initial_state = automaton.get_initial_state()
    states.append(initial_state)
    return initial_state, states