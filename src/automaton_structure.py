from collections import Counter

class State:

    def __init__(self, name):
        self.name = name
        self.neighbours = dict()
        self.visited = False

    def get_name(self):
        return self.name

    def get_neighbours(self):
        return self.neighbours

    def is_visited(self):
        return self.visited

    def set_visited(self):
        self.visited = True

    def add_transition(self, neighbour, transition):
        if neighbour not in self.neighbours:
            self.neighbours[neighbour] = [transition]
        elif not self.transition_already_present(neighbour, transition):
            self.neighbours[neighbour].append(transition)

    def transition_already_present(self, _neighbour, _transition):
        for neighbour, transitions in self.get_neighbours().iteritems():
            for transition in transitions:
                if neighbour.get_name() == _neighbour.get_name()\
                        and transition.get_event().get_name() == _transition.get_event().get_name()\
                        and transition.is_fault() == _transition.is_fault():
                    return True
        return False


class Transition:

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

    def get_event_cardinality(self):
        if self.event is None:
            return 0
        return self.event.get_cardinality()


class Event:

    def __init__(self, name=None):
        self.multiset = Counter(name)

    def get_name(self):
        return "//".join(sorted(self.multiset.elements()))

    def get_multiset(self):
        return self.multiset

    def add(self, event):
        if event is not None:
            self.multiset |= event.get_multiset()

    def get_cardinality(self):
        return sum(self.multiset.values())

    def is_composed_by_all_same_events(self):
        return len(self.multiset) == 1


class Automaton:

    def __init__(self, initial_state, states):
        self.initial_state = initial_state
        self.states = states

    def get_initial_state(self):
        return self.initial_state

    def get_states(self):
        return self.states

    def __str__(self):
        res = ""
        for state in self.states:
            for destination, transitions in state.get_neighbours().iteritems():
                for transition in transitions:
                    res += state.get_name() + " -> " + destination.get_name()
                    if transition.is_observable():
                        res += " | " + transition.get_event().get_name()
                    if transition.is_fault():
                        res += " (fault)"
                    res += "\n"
        return res

    def find_reachable_states(self, initial_state):
        initial_state.set_visited()
        for state in initial_state.get_neighbours():
            if not state.is_visited():
                self.find_reachable_states(state)

    def remove_unreachable_states(self):
        self.find_reachable_states(self.initial_state)
        for state in self.states:
            if not state.is_visited():
                self.states.remove(state)
