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

    def set_visited(self, visited=True):
        self.visited = visited

    def add_transition(self, neighbour, transition):
        if neighbour not in self.neighbours:
            self.neighbours[neighbour] = [transition]
        elif not self.transition_already_present(neighbour, transition):
            self.neighbours[neighbour].append(transition)

    def transition_already_present(self, _neighbour, _transition):
        for transition in self.neighbours[_neighbour]:
            if transition.get_event_name() == _transition.get_event_name()\
                    and transition.is_fault() == _transition.is_fault():
                return True
        return False

    def get_current_level_transitions(self, level, get_faulty=True):
        current_level_transitions = dict()
        for neighbour, transitions in self.neighbours.iteritems():
            current_level_transitions[neighbour] = list()
            for transition in transitions:
                if transition.get_event_cardinality() == level and get_faulty:
                    current_level_transitions[neighbour].append(transition)
        return current_level_transitions

    def equals(self, state):
        return self.name == state.get_name()

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

    def get_event_name(self):
        if self.event is None:
            return None
        return self.event.get_name()

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
            for _event in event.multiset.elements():
                self.multiset.update(_event)

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

    def find_reachable_states(self, initial_state):
        initial_state.set_visited()
        for state in initial_state.get_neighbours():
            if not state.is_visited():
                self.find_reachable_states(state)

    def remove_unreachable_states(self):
        for state in self.states:
            state.set_visited(False)
        self.find_reachable_states(self.initial_state)
        for state in self.states:
            if not state.is_visited():
                self.states.remove(state)

    def is_non_deterministic(self):
        for state in self.states:
            events = dict()
            for transitions in state.get_neighbours().values():
                for transition in transitions:
                    if transition.is_observable():
                        try:
                            if events[transition.get_event_name()]:
                                return True
                        except KeyError:
                            events[transition.get_event_name()] = True
        return False

    def has_ambiguous_events(self):
        events = dict()
        for state in self.states:
            for transitions in state.get_neighbours().values():
                for transition in transitions:
                    try:
                        if events[transition.get_event_name()] != transition.is_fault():
                            return True
                    except KeyError:
                        events[transition.get_event_name()] = transition.is_fault()
        return False