from collections import Counter

class State:

    def __init__(self, name):
        self.name = name
        self.neighbours = dict()
        self.visited = False

    def get_name(self):
        return self.name

    def get_neighbours(self, fault=True):
        if fault:
            return self.neighbours
        neighbours = dict()
        for neighbour, transitions in self.neighbours.iteritems():
            _transitions = list()
            for transition in transitions:
                if not transition.is_fault():
                    _transitions.append(transition)
            neighbours[neighbour] = _transitions
        return neighbours

    def is_visited(self):
        return self.visited

    def set_visited(self, visited=True):
        self.visited = visited

    def get_neighbour(self, name):
        for neighbour in self.neighbours:
            if neighbour.get_name() == name:
                return neighbour
        return None

    def set_transitions(self, neighbour, transitions):
        self.neighbours[neighbour] = transitions

    def add_transition(self, neighbour, transition):
        if self.equals(neighbour) and transition.is_fault() and not transition.is_observable():
            return False
        if (self.has_unobservable_transitions(neighbour) or neighbour.has_unobservable_transitions(self)) and \
                transition.is_fault() and not transition.is_observable():
            return False
        if neighbour not in self.neighbours:
            self.neighbours[neighbour] = [transition]
        elif not self.transition_already_present(neighbour, transition):
            self.neighbours[neighbour].append(transition)
        else:
            return False
        return True

    def transition_already_present(self, neighbour, _transition):
        for transition in self.neighbours[neighbour]:
            if transition.get_event_name() == _transition.get_event_name() and transition.is_fault() == _transition.is_fault():
                return True
        return False

    def has_unobservable_transitions(self, neighbour):
        if neighbour not in self.neighbours:
            return False
        for transition in self.neighbours[neighbour]:
            if not transition.is_observable():
                return True
        return False

    def get_current_level_transitions(self, level, fault=True):
        current_level_transitions = dict()
        for neighbour, transitions in self.neighbours.iteritems():
            _transitions = list()
            for transition in transitions:
                if transition.get_event_cardinality() == level and (fault or not transition.is_fault()):
                    _transitions.append(transition)
            current_level_transitions[neighbour] = _transitions
        return current_level_transitions

    def equals(self, state):
        return self.name == state.get_name()

class Transition:

    def __init__(self, event=None, fault=False, ambiguous=False):
        self.event = event
        self.fault = fault
        self.ambiguous = ambiguous
        self.crossed = False

    def get_event(self):
        return self.event

    def is_fault(self):
        return self.fault

    def is_ambiguous(self):
        return self.ambiguous

    def is_observable(self):
        return self.event is not None

    def is_crossed(self):
        return self.crossed

    def set_event(self, event):
        self.event = event

    def set_fault(self):
        self.fault = True

    def set_crossed(self, crossed=True):
        self.crossed = crossed

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
        if type(name) is str:
            name = [name]
        self.multiset = Counter(name)

    def get_name(self):
        return '//'.join(sorted(self.multiset.elements()))

    def get_multiset(self):
        return self.multiset

    def add(self, event):
        if event is not None:
            for _event in event.multiset.elements():
                if type(_event) is str:
                    _event = [_event]
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

    def set_states(self, states):
        self.states = states

    def find_reachable_states(self, initial_state):
        initial_state.set_visited()
        for state in initial_state.get_neighbours():
            if not state.is_visited():
                self.find_reachable_states(state)

    def remove_unreachable_states(self):
        for state in self.states.values():
            state.set_visited(False)
        self.find_reachable_states(self.states[self.initial_state])
        states = dict()
        for name, state in self.states.iteritems():
            if state.is_visited():
                state.set_visited(False)
                states[name] = state
        self.states = states

    def is_non_deterministic(self):
        for state in self.states.values():
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
        for state in self.states.values():
            for transitions in state.get_neighbours().values():
                for transition in transitions:
                    try:
                        if events[transition.get_event_name()] != transition.is_fault():
                            return True
                    except KeyError:
                        events[transition.get_event_name()] = transition.is_fault()
        return False

    def get_transitions(self, unobservable=False):
        transitions = list()
        for state in self.states.values():
            for neighbour in state.get_neighbours():
                if not unobservable or state.has_unobservable_transitions(neighbour):
                    transitions.append((state.get_name(), neighbour.get_name()))
        return transitions

    def set_transition_event(self, src_name, dst_name, event):
        src = self.states[src_name]
        dst = src.get_neighbour(dst_name)
        transition = src.get_neighbours()[dst][0]
        if not transition.is_observable():
            transition.set_event(event)
            return True
        return False

    def get_unobservable_transitions(self):
        unobservable_transitions = list()
        for state in self.states.values():
            for transitions in state.get_neighbours().values():
                for transition in transitions:
                    if not transition.is_observable() and not transition.is_fault():
                        unobservable_transitions.append(transition)
        return unobservable_transitions
