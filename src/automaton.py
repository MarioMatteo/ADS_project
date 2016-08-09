"""
Contains the classes to represent a non-deterministic finite automaton.
"""

from collections import Counter
import networkx as nx

class State:

    """
    Represents a state of the automaton.

    A state has the following attributes:
        - name: a string representing its name
        - neighbours: a dict representing its neighbours that maps a state into a list of transitions
        - visited: a boolean flag used during depth-first search
    """

    def __init__(self, name):

        """
        Initializes the state.

        :param name: the name of the state
        :type name: str
        """

        self.name = name
        self.neighbours = dict()
        self.visited = False

    def get_name(self):

        """
        Gets the name of this state.

        :return: the name of this state
        :rtype: str
        """

        return self.name

    def get_neighbours(self, fault=True):

        """
        Gets the neighbour-transitions map of this state.

        If fault is False it returns only the non fault outgoing transitions from this state towards its neighbours,
        otherwise it returns all the outgoing transitions from this state to its neighbours.

        :param fault: a flag indicating whether to include fault transitions or not
        :type fault: bool
        :return: the neighbour-transitions map of this state according to fault flag
        :rtype: dict(State: list(Transition))
        """

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

        """
        Checks if this state has been already visited.

        :return: whether this state has been visited or not
        :rtype: bool
        """

        return self.visited

    def set_visited(self, visited=True):

        """
        Sets the boolean flag of this state.

        :param visited: the new flag
        :type visited: bool
        """

        self.visited = visited

    def get_neighbour(self, name):

        """
        Gets the neighbour of this state, according to its name.

        :param name: the neighbour's name
        :type name: str
        :return: the neighbour state if exists, None otherwise
        :rtype: State or None
        """

        for neighbour in self.neighbours:
            if neighbour.get_name() == name:
                return neighbour
        return None

    def set_transitions(self, neighbour, transitions):

        """
        Sets a list of outgoing transitions from this state towards a neighbour.

        :param neighbour: the neighbour state
        :type neighbour: State
        :param transitions: the list of transitions to be set
        :type transitions: list(Transition)
        """

        self.neighbours[neighbour] = transitions

    def add_transition(self, neighbour, transition):

        """
        Adds an outgoing transition from this state towards a neighbour.

        A transition is not added when:
            - it's a self loop fault transition
            - it creates a loop of fault transitions between this state and its neighbour
            - it's already present (see beelow)

        :param neighbour: the neighbour state
        :type neighbour: State
        :param transition: the transition to be added
        :type transition: Transition
        :return: whether the transition has been added or not
        :rtype: bool
        """

        if self.equals(neighbour) and transition.is_fault():
            return False
        if neighbour.has_fault_transitions(self) and transition.is_fault():
            return False
        if neighbour not in self.neighbours:
            self.neighbours[neighbour] = [transition]
        elif not self.transition_already_present(neighbour, transition):
            self.neighbours[neighbour].append(transition)
        else:
            return False
        return True

    def transition_already_present(self, neighbour, _transition):

        """
        Checks if an outgoing transition from this state towards a neighbour is already present.

        Between two states cannot exist a couple of transitions sharing the same event, unless one is fault and the
        other not.

        :param neighbour: the neighbour state
        :type neighbour: State
        :param _transition: the transition to check
        :type _transition: Transition
        :return: whether the transition is already present or not
        :rtype: bool
        """

        for transition in self.neighbours[neighbour]:
            if transition.get_event_name() == _transition.get_event_name() and transition.is_fault() == _transition.is_fault():
                return True
        return False

    def has_observable_transitions(self, neighbour):

        """
        Checks if this state has at least an observable transition towards a neighbour.

        :param neighbour: the neighbour state
        :type neighbour: State
        :return: whether this state has at least an observable transition towards a neighbour
        :rtype: bool
        """

        if neighbour not in self.neighbours:
            return False
        for transition in self.neighbours[neighbour]:
            if transition.is_observable():
                return True
        return False

    def has_fault_transitions(self, neighbour):

        """
        Checks if this state has at least a fault transition towards a neighbour.

        :param neighbour: the neighbour state
        :type neighbour: State
        :return: whether this state has at least a fault transition towards a neighbour
        :rtype: bool
        """

        if neighbour not in self.neighbours:
            return False
        for transition in self.neighbours[neighbour]:
            if transition.is_fault():
                return True
        return False

    def has_unobservable_transitions(self, neighbour):

        """
        Checks if this state has at least an unobservable transition towards a neighbour.

        :param neighbour: the neighbour state
        :type neighbour: State
        :return: whether this state has at least an unobservable transition towards a neighbour
        :rtype: bool
        """

        if neighbour not in self.neighbours:
            return False
        for transition in self.neighbours[neighbour]:
            if not transition.is_observable():
                return True
        return False

    def get_current_level_transitions(self, level, fault=True):

        """
        Gets the transitions whose (composed) event is of a certain level.

        If fault is False it returns only the non fault outgoing transitions from this state towards its neighbours,
        otherwise it returns all the outgoing transitions from this state towards its neighbour (according to level).

        :param level: the level through which filter which transitions to get
        :type level: int
        :param fault: a flag indicating whether to include fault transitions or not
        :type fault: bool
        :return: the neighbour-transitions map according to level and fault flag
        :rtype: dict(State: list(Transition))
        """

        current_level_transitions = dict()
        for neighbour, transitions in self.neighbours.iteritems():
            _transitions = list()
            for transition in transitions:
                if transition.get_event_level() == level and (fault or not transition.is_fault()):
                    _transitions.append(transition)
            current_level_transitions[neighbour] = _transitions
        return current_level_transitions

    def equals(self, state):

        """
        Checks if this state is equal to another.

        Two states are equal if they have the same name.

        :param state: the state with which the comparison is performed
        :type state: State
        :return: whether this state is equal to another or not
        :rtype: bool
        """

        return self.name == state.get_name()

class Transition:

    """
    Represents a transition of the automaton.

    A transition has the following attributes:
        - event: the event associated with the transition
        - fault: a boolean flag marking it as fault
        - ambiguous: a boolean flag marking it as ambiguous
    """

    def __init__(self, event=None, fault=False, ambiguous=False):

        """
        Initializes the transition.

        :param event: the event to be associated with the transition
        :type event: Event
        :param fault: a flag indicating whether the transition is fault or not
        :type fault: bool
        :param ambiguous: a flag indicating whether the transition is ambiguous or not
        :type ambiguous: bool
        """

        self.event = event
        self.fault = fault
        self.ambiguous = ambiguous

    def get_event(self):

        """
        Gets the event associated with this transition.

        :return: the event associated with the transition
        :rtype: Event
        """

        return self.event

    def is_fault(self):

        """
        Checks if this transition is fault.

        :return: whether this transition is fault or not
        :rtype: bool
        """

        return self.fault

    def is_ambiguous(self):

        """
        Checks if this transition is ambiguous.

        :return: whether this transition is ambiguous or not
        :rtype: bool
        """

        return self.ambiguous

    def is_observable(self):


        """
        Checks if this transition is observable.

        A transition is observable if there is a not null event associated with it

        :return: whether the transition is observable or not
        :rtype: bool
        """

        return self.event is not None

    def set_event(self, event):

        """
        Associates an event with this transition.

        :param event: the event to be associated with this transition
        :type event: Event
        """

        self.event = event

    def set_fault(self):

        """
        Marks this transition as fault.
        """

        self.fault = True

    def get_event_name(self):

        """
        Gets the name of the event associated with this transition.

        If no event is associated with this transition it returns None.

        :return: the name of the event associated with this transition if exists, None otherwise
        :rtype: str or None
        """

        if self.event is None:
            return None
        return self.event.get_name()

    def get_event_level(self):

        """
        Gets the level of the event associated with this transition.

        If no event is associated with this transition it returns 0.

        :return: the level of the event associated with this transition
        :rtype: int
        """

        if self.event is None:
            return 0
        return self.event.get_level()


class Event:

    """
    Represents a (composed) event associated with a transition.

    An event has the following attributes:
        - multiset: a Counter representing the multiset of its components

    """

    def __init__(self, name=None):

        """
        Initializes the event.

        :param name: the name of the event
        :type name: str or list(str)
        """

        if type(name) is str:
            name = [name]
        self.multiset = Counter(name)

    def get_name(self):

        """
        Gets the name of this event.

        If its level is greater than 1, the name is obtained concatenating the names of its components using '//' as
        separator.

        :return: the name of this event
        :rtype: str
        """

        return '//'.join(sorted(self.multiset.elements()))

    def add(self, event):

        """
        Adds the components of an event to this event.

        :param event: the event to be added
        :type event: Event
        """

        if event is not None:
            for _event in event.multiset.elements():
                if type(_event) is str:
                    _event = [_event]
                self.multiset.update(_event)

    def get_level(self):

        """
        Gets the level of this event.

        The level of a composed event is its components multiset's cardinality.

        :return: the level of this event
        :rtype: int
        """

        return sum(self.multiset.values())

    def is_composed_by_all_identical_instances(self):

        """
        Checks if this event is composed by all identical instances of events.

        :return: whether this event is composed by all identical instances of events or not
        :rtype: bool
        """

        return len(self.multiset) == 1


class Automaton:

    """
    Represents a non-deterministic finite automaton.

    An automaton has the following attributes:
        - initial_state: the name of the initial state
        - states: a dict representing its states that maps a name into the corresponding state
    """

    def __init__(self, initial_state, states):

        """
        Initializes the automaton.

        :param initial_state: the name of the initial state
        :type initial_state: str
        :param states: the name-state map
        :type states: dict(str: State)
        """

        self.initial_state = initial_state
        self.states = states

    def get_initial_state(self):

        """
        Gets the initial state's name of this automaton.

        :return: the name of its initial state
        :rtype: str
        """

        return self.initial_state

    def get_states(self):

        """
        Gets the name-state map of this automaton.

        :return: its name-state map
        :rtype: dict(str: State)
        """

        return self.states

    def set_states(self, states):

        """
        Sets the name-state map.

        :param states: the name-state map to be set
        :type states: dict(str: State)
        """

        self.states = states

    def find_reachable_states(self, initial_state):

        """
        Performs a depth-first search, starting from its initial state.

        The states that are involved in this search are marked as visited.

        :param initial_state: the name of its initial state
        :type initial_state: str
        """

        initial_state.set_visited()
        for state in initial_state.get_neighbours():
            if not state.is_visited():
                self.find_reachable_states(state)

    def remove_unreachable_states(self):

        """
        Removes the states that are unreachable from the initial state.

        To perform this task, a depth-first search is used.
        """

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

        """
        Checks if this automaton is non-deterministic.

        An automaton is non-deterministic if there is at least a couple of outgoing transitions from the same state and
        sharing the same event.

        :return: whether this automaton is non-deterministic or not
        :rtype: bool
        """

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

    def is_language_alive(self):

        """
        Checks if the language generated by this automaton over its events alphabet is alive.

        The language is alive if:
            - every state has at least one outgoing transition
            - every cyclic path starting from the initial state contains at least an observable transition

        :return: whether the language generated by this automaton over its events alphabet is alive or not
        :rtype: bool
        """

        for state in self.states.values():
            if len(state.get_neighbours()) == 0:
                return False
        loops = self.get_loops()
        for loop in loops:
            if len(loops) == 1:
                src_name = loop[0]
                if not self.states[src_name].has_observable_transitions(self.states[src_name]):
                    return False
            else:
                _continue = True
                src_index = 0
                while src_index < len(loop) and _continue:
                    src_name = loop[src_index]
                    dst_index = (src_index + 1) % len(loop)
                    dst_name = loop[dst_index]
                    if self.states[src_name].has_observable_transitions(self.states[dst_name]):
                        _continue = False
                    src_index += 1
                if _continue:
                    return False
        return True

    def has_ambiguous_events(self):

        """
        Checks if this automaton has at least an ambiguous event.

        In our definition, an event is ambiguous if it is associated both to a fault transition and to an observable
        one.

        :return: whether this automaton has at least an ambiguous event
        :rtype: bool
        """

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

        """
        Gets the transitions of this automaton.

        The transitions are returned as a list of tuples in which the first element is the source name and the second
        one is the destination name.
        If unobservable is True it returns only the unobservable transitions of this automaton, otherwise it returns
        all its transitions.

        :param unobservable: a flag indicating whether to include only unobservable transitions
        :type unobservable: bool
        :return: the transitions of this automaton according to unobservable flag
        :rtype: list(tuple(str, str))
        """

        transitions = list()
        for state in self.states.values():
            for neighbour in state.get_neighbours():
                if not unobservable or state.has_unobservable_transitions(neighbour):
                    transitions.append((state.get_name(), neighbour.get_name()))
        return transitions

    def set_transition_event(self, src_name, dst_name, event):

        """
        Sets an event to a transition.

        This function is invoked during the first phase of the random generation of an automaton. In this phase
        there is only one outgoing transition from one state to a neighbour, so a transition can be identified by its
        source state's name and its destination state's name.
        An event is not added when the transition has an event already associated.

        :param src_name: the source state's name of the transition
        :type src_name: str
        :param dst_name: the destination state's name of the transition
        :type dst_name: str
        :param event: the event to be set
        :type event: Event
        :return: whether the event has been set or not
        :rtype: bool
        """

        src = self.states[src_name]
        dst = src.get_neighbour(dst_name)
        transition = src.get_neighbours()[dst][0]
        if not transition.is_observable():
            transition.set_event(event)
            return True
        return False

    def get_unobservable_transitions(self):

        """
        Gets the unobservable transitions of this automaton.

        :return: the unobservable transitions of this automaton
        :rtype: list(Transition)
        """

        unobservable_transitions = list()
        for state in self.states.values():
            for transitions in state.get_neighbours().values():
                for transition in transitions:
                    if not transition.is_observable() and not transition.is_fault():
                        unobservable_transitions.append(transition)
        return unobservable_transitions

    def get_loops(self):

        """
        Gets all the simple cycles of this automaton.

        The cycles are returned as a list of tuples, sorted by their length. Each tuple represents a cycle and
        it is composed by the sequence of the names of the states taking part to that cycle.

        :return: all the simple cycles of this automaton
        :rtype: list(tuple(str))
        """

        return sorted(list(nx.simple_cycles(nx.DiGraph(self.get_transitions()))), key=len)

    def has_fault_loops(self):

        """
        Checks if this automaton has at least a cycle composed only of fault transitions.

        :return: whether this automaton has at least a cycle composed only of fault transitions or not
        :rtype: bool
        """

        return len(list(nx.simple_cycles(nx.DiGraph(self.get_transitions(unobservable=True))))) > 0
