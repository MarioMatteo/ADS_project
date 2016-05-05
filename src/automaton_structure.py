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


class Event:

    def __init__(self, name):
        self.multiset = Counter(name)

    def __str__(self):
        return "//".join(sorted(self.multiset.elements()))

    def get_multiset(self):
        return self.multiset

    def add(self, name):
        self.multiset.update(name)


class Automaton:

    def __init__(self, diagnosability_level, states):
        self.diagnosability_level = diagnosability_level
        self.states = states

    def get_states(self):
        return self.states

    def get_transitions(self):
        return [transition for state in self.states for transition in state.get_neighbours().values()]
