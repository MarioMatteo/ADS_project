from collections import Counter

class State:

    def __init__(self, name):
        self.name = name
        self.neighbours = dict()

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def get_neighbours(self):
        return self.neighbours

    def add_transition(self, neighbour, transition):
        if neighbour not in self.neighbours:
            self.neighbours[neighbour] = [transition]
        else:
            self.neighbours[neighbour].append(transition)

    def get_unobservable_neighbours(self):
        unobservable_neighbours = dict()
        for state, transitions in self.neighbours:
            unobservable_transitions = list()
            for transition in transitions:
                if not transition.is_observable():
                    unobservable_transitions.append(transition)
            unobservable_neighbours[state] = unobservable_transitions
        return unobservable_neighbours


class Transition:

    TYPE_OBSERVABLE = "observable"
    TYPE_FAULT = "fault"

    def __init__(self, event=None, fault=False, ambiguous=False):
        self.event = event
        self.fault = fault
        self.ambiguous = ambiguous

    def get_event(self):
        return self.event

    def is_fault(self):
        return self.fault

    def is_ambiguous(self):
        return self.ambiguous

    def is_observable(self):
        return self.event is not None


class Event:

    def __init__(self, name):
        self.multiset = Counter(name)

    def get_name(self):
        return "//".join(sorted(self.multiset.elements()))

    def get_multiset(self):
        return self.multiset

    def add(self, event):
        if event is not None:
            self.multiset.update(event.get_name())

    def get_cardinality(self):
        return sum(self.multiset.values())


class Automaton:

    def __init__(self, diagnosability_level, initial_state, states):
        self.diagnosability_level = diagnosability_level
        self.initial_state = initial_state
        self.states = states

    def get_diagnosability_level(self):
        return self.diagnosability_level

    def get_initial_state(self):
        return self.initial_state

    def get_states(self):
        return self.states

    def get_transitions(self):
        return [transition for state in self.states for transition in state.get_neighbours().values()]
