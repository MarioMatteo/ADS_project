"""
Contains the methods used by the solving algorithms.
"""

from file_handler import *
from copy import deepcopy

def generate_bad_twin(automaton, level=1):

    """
    Generates the next level bad twin starting from the current level one.

    Note that the 0-level bad twin is the input automaton.

    :param automaton: the current level bad twin
    :type automaton: Automaton
    :param level: the next level of the bad twin to be generated
    :type level: int
    :return: the next level bad twin
    :rtype: Automaton
    """

    states = initialize_states(automaton)
    for src_name, src in automaton.get_states().iteritems():
        for dst, transitions in src.get_neighbours().iteritems():
            dst_name = dst.get_name()
            for transition in transitions:
                if transition.is_observable():
                    states[src_name].add_transition(states[dst_name], deepcopy(transition))
                if level > 1 or not transition.is_observable():
                    fault = False
                    if transition.is_fault():
                        fault = True
                    triplets = find(dst, level - transition.get_event_level(), fault, transition.get_event())
                    for event, dst2, fault2 in triplets:
                        if level == 1 or not event.is_composed_by_all_identical_instances():
                            dst2_name = dst2.get_name()
                            states[src_name].add_transition(states[dst2_name], Transition(event=event, fault=fault2))
    bad_twin = Automaton(automaton.get_initial_state(), states)
    if level == 1:
        bad_twin.remove_unreachable_states()
    return bad_twin

def generate_good_twin(bad_twin):

    """
    Generates the good twin starting from the bad twin.

    :param bad_twin: the bad twin
    :type bad_twin: Automaton
    :return: the good twin
    :rtype: Automaton
    """

    states = initialize_states(bad_twin)
    for src_name, src in bad_twin.get_states().iteritems():
        for dst, transitions in src.get_neighbours().iteritems():
            dst_name = dst.get_name()
            for transition in transitions:
                if not transition.is_fault():
                    states[src_name].add_transition(states[dst_name], deepcopy(transition))
    good_twin = Automaton(bad_twin.get_initial_state(), states)
    good_twin.remove_unreachable_states()
    return good_twin

def synchronize_1(bad_twin, good_twin):

    """
    Generates the synchronized automaton starting from the bad twin and the good twin.

    It implements the first version of the synchronization method.
    It returns both the synchronized automaton and the set of representative ambiguous transitions.
    Each ambiguous transition is represented by a tuple in which the first element is the source state name and the
    second one is the destination state name.

    :param bad_twin: the bad twin
    :type bad_twin: Automaton
    :param good_twin: the good twin
    :type good_twin: Automaton
    :return: the synchronized automaton and the set of ambiguous transitions
    :rtype: tuple(Automaton, set(tuple(str, str)))
    """

    states = dict()
    ambiguous_transitions = set()
    for src_name in good_twin.get_states():
        couple_name = ','.join([src_name] * 2)
        states[couple_name] = State(couple_name)
    for src_name, src in good_twin.get_states().iteritems():
        couple_src_name = ','.join([src_name] * 2)
        for dst, transitions in src.get_neighbours().iteritems():
            dst_name = dst.get_name()
            couple_dst_name = ','.join([dst_name] * 2)
            for transition in transitions:
                states[couple_src_name].add_transition(states[couple_dst_name], deepcopy(transition))
    if bad_twin.is_non_deterministic():
        bt_states = bad_twin.get_states()
        gt_states = good_twin.get_states()
        prev_states = set(states.keys())
        for gt_src_name, gt_src in gt_states.iteritems():
            src_name = ','.join([gt_src_name] * 2)
            bt_src = bt_states[gt_src_name]
            for bt_dst, bt_transitions in bt_src.get_neighbours().iteritems():
                for gt_dst, gt_transitions in gt_src.get_neighbours().iteritems():
                    for bt_transition in bt_transitions:
                        for gt_transition in gt_transitions:
                            if bt_transition.get_event_name() == gt_transition.get_event_name():
                                if not bt_dst.equals(gt_dst) or bt_transition.is_fault():
                                    dst_name = ','.join([bt_dst.get_name(), gt_dst.get_name()])
                                    if dst_name not in states:
                                        states[dst_name] = State(dst_name)
                                    ambiguous = bt_transition.is_fault()
                                    states[src_name].add_transition(states[dst_name], Transition(
                                        deepcopy(bt_transition.get_event()), ambiguous=ambiguous))
                                    if ambiguous:
                                        ambiguous_transitions.add((src_name, dst_name))
        while set(states.keys()) != prev_states:
            diff_states = set(states.keys()) - prev_states
            prev_states = set(states.keys())
            for src_name in diff_states:
                splitted_name = src_name.split(',')
                bt_src, gt_src = bt_states[splitted_name[0]], gt_states[splitted_name[1]]
                for bt_dst, bt_transitions in bt_src.get_neighbours().iteritems():
                    for gt_dst, gt_transitions in gt_src.get_neighbours().iteritems():
                        for bt_transition in bt_transitions:
                            for gt_transition in gt_transitions:
                                if bt_transition.get_event_name() == gt_transition.get_event_name():
                                    dst_name = ','.join([bt_dst.get_name(), gt_dst.get_name()])
                                    if dst_name not in states:
                                        states[dst_name] = State(dst_name)
                                    ambiguous = bt_transition.is_fault()
                                    states[src_name].add_transition(states[dst_name], Transition(
                                        deepcopy(bt_transition.get_event()), ambiguous=ambiguous))
                                    if ambiguous:
                                        ambiguous_transitions.add((src_name, dst_name))
    initial_state = ','.join([good_twin.get_initial_state()] * 2)
    return Automaton(initial_state, states), ambiguous_transitions

def synchronize_2(old_synchronized, ambiguous_transitions, bad_twin, level):

    """
    Generates the synchronized automaton starting from the previous level synchronized one.

    It implements the second version of the synchronization method.
    It returns both the synchronized automaton and the set of representative ambiguous transitions.
    Each ambiguous transition is represented by a tuple in which the first element is the source state name and the
    second one is the destination state name.

    :param old_synchronized: the previous level synchronized automaton
    :type old_synchronized: Automaton
    :param ambiguous_transitions: the set of ambiguous transitions to be updated
    :type ambiguous_transitions: set(tuple(str, str))
    :param bad_twin: the current level bad twin
    :type bad_twin: Automaton
    :param level: the current level
    :type level: int
    :return: the synchronized automaton
    :rtype: Automaton
    """

    states = deepcopy(old_synchronized.get_states())
    bt_states = bad_twin.get_states()
    prev_states = set(states.keys())
    for src_name in old_synchronized.get_states():
        splitted_name = src_name.split(',')
        bt_src, gt_src = bt_states[splitted_name[0]], bt_states[splitted_name[1]]
        bt_current_level_transitions = bt_src.get_current_level_transitions(level)
        gt_current_level_transitions = gt_src.get_current_level_transitions(level, fault=False)
        for bt_dst, bt_transitions in bt_current_level_transitions.iteritems():
            for gt_dst, gt_transitions in gt_current_level_transitions.iteritems():
                for bt_transition in bt_transitions:
                    for gt_transition in gt_transitions:
                        if bt_transition.get_event_name() == gt_transition.get_event_name():
                            dst_name = ','.join([bt_dst.get_name(), gt_dst.get_name()])
                            if dst_name not in states:
                                states[dst_name] = State(dst_name)
                            ambiguous = bt_transition.is_fault()
                            states[src_name].add_transition(states[dst_name], Transition(
                                deepcopy(bt_transition.get_event()), ambiguous=ambiguous))
                            if ambiguous:
                                ambiguous_transitions.add((src_name, dst_name))
    while set(states.keys()) != prev_states:
        diff_states = set(states.keys()) - prev_states
        prev_states = set(states.keys())
        for src_name in diff_states:
            splitted_name = src_name.split(',')
            bt_src, gt_src = bt_states[splitted_name[0]], bt_states[splitted_name[1]]
            for bt_dst, bt_transitions in bt_src.get_neighbours().iteritems():
                for gt_dst, gt_transitions in gt_src.get_neighbours(fault=False).iteritems():
                    for bt_transition in bt_transitions:
                        for gt_transition in gt_transitions:
                            if bt_transition.get_event_name() == gt_transition.get_event_name():
                                dst_name = ','.join([bt_dst.get_name(), gt_dst.get_name()])
                                if dst_name not in states:
                                    states[dst_name] = State(dst_name)
                                ambiguous = bt_transition.is_fault()
                                states[src_name].add_transition(states[dst_name], Transition(
                                    deepcopy(bt_transition.get_event()), ambiguous=ambiguous))
                                if ambiguous:
                                    ambiguous_transitions.add((src_name, dst_name))
    initial_state = old_synchronized.get_initial_state()
    return Automaton(initial_state, states)

def find(src, n, fault, event):

    """
    Finds the triplets according to the provided pseudocode.

    :param src: the starting state
    :type src: State
    :param n: the target level
    :type n: int
    :param fault: a flag indicating whether the transition is fault or not
    :type fault: bool
    :param event: the composed n-level event to be associated with the transition
    :type event: Event
    :return: the triplets according to the provided pseudocode
    :rtype: list(tuple(Event, State, bool))
    """

    triplets = list()
    for dst, transitions in src.get_neighbours().iteritems():
        for transition in transitions:
            _fault = fault
            if transition.is_fault():
                _fault = True
            event_level = transition.get_event_level()
            if transition.is_observable() and event_level <= n:
                composed_event = deepcopy(transition.get_event())
                composed_event.add(deepcopy(event))
                if event_level == n:
                    triplets.append((composed_event, dst, _fault))
                else:
                    triplets += find(dst, n - event_level, _fault, composed_event)
            if not transition.is_observable():
                triplets += find(dst, n, _fault, event)
    return triplets

def condition_C1(ambiguous_transitions):

    """
    Checks if condition C1 is satisfied.

    Condition C1 is satisfied if the set of ambiguous transitions is empty.

    :param ambiguous_transitions: set of ambiguous transitions
    :type ambiguous_transitions: set(tuple(str, str))
    :return: whether condition C1 is satisfied or not
    :rtype: bool
    """

    return len(ambiguous_transitions) == 0

def condition_C2(bad_twin):

    """
    Checks if condition C2 is satisfied.

    Condition C2 is satisfied if the bad twin is not non-deterministic.

    :param bad_twin: the current level bad twin
    :type bad_twin: Automaton
    :return: whether condition C2 is satisfied or not
    :rtype: bool
    """

    return not bad_twin.is_non_deterministic()

def condition_C3(bad_twin):

    """
    Checks if condition C3 is satisfied.

    Condition C3 is satisfied if the bad twin has no events associated both to a fault transition and to an observable
    one.

    :param bad_twin: the current level bad twin
    :type bad_twin: Automaton
    :return: whether condition C3 is satisfied or not
    :rtype: bool
    """

    return not bad_twin.has_ambiguous_events()

def initialize_states(automaton):

    """
    Creates a name-state map of an automaton.

    :param automaton: the automaton
    :type automaton: Automaton
    :return: the name-state map the automaton
    :rtype: dict(str: State)
    """

    states = dict()
    for name, state in automaton.get_states().iteritems():
        states[name] = State(name)
    return states

def find_loops(src, visited):

    """
    Checks if there is some cyclic path starting from a state.

    :param src: the starting state
    :type src: State
    :param visited: set of names of already visited states
    :type visited: set(str)
    :return: whether there is some cyclic path starting from the input state
    :rtype: bool
    """

    for dst in src.get_neighbours():
        if dst.get_name() in visited:
            return True
        visited.add(src.get_name())
        if find_loops(dst, visited):
            return True
    return False
