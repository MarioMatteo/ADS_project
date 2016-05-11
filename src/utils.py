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
                    triplets = find(destination, level - transition.get_event_cardinality(), fault, transition.get_event())
                    for event, destination2, fault2 in triplets:
                        if level == 1 or not event.is_composed_by_all_same_events():
                            states[state.get_name()].add_transition(states[destination2.get_name()],
                                                                    Transition(event=event, fault=fault2))
    bad_twin = Automaton(initial_state, states.values())
    if level == 1:
        bad_twin.remove_unreachable_states()
    return bad_twin

def generate_good_twin(bad_twin):
    initial_state, states = initialize_states(bad_twin)
    for state in bad_twin.get_states():
        for destination, transitions in state.get_neighbours().iteritems():
            for transition in transitions:
                if not transition.is_fault():
                    states[state.get_name()].add_transition(states[destination.get_name()],
                                                            deepcopy(transition))
    good_twin = Automaton(initial_state, states.values())
    good_twin.remove_unreachable_states()
    return good_twin

def synchronize(bad_twin, good_twin):
    states = dict()
    for state in good_twin.get_states():
        states[",".join(state.get_name()*2)] = State(",".join(state.get_name()*2))
    for state in good_twin.get_states():
        for neighbour, transitions in state.get_neighbours().iteritems():
            for transition in transitions:
                states[",".join(state.get_name()*2)].add_transition(states[",".join(neighbour.get_name()*2)],
                                                                    deepcopy(transition))
    if bad_twin.is_non_deterministic():
        bt_states = initialize_states_with_transitions(bad_twin)
        gt_states = initialize_states_with_transitions(good_twin)
        old_diff_states = list()
        rev_flags = set()
        for gt_state in gt_states.values():
            src_name = ",".join(gt_state.get_name()*2)
            for bt_neighbour, bt_transitions in bt_states[gt_state.get_name()].get_neighbours().iteritems():
                for bt_transition in bt_transitions:
                    for gt_neighbour, gt_transitions in gt_state.get_neighbours().iteritems():
                        for gt_transition in gt_transitions:
                            if gt_transition.get_event_name() == bt_transition.get_event_name():
                                if (not bt_neighbour.equals(gt_neighbour)) or (bt_neighbour.equals(gt_neighbour)\
                                                             and gt_transition.is_fault() != bt_transition.is_fault()):
                                    dst_name = bt_neighbour.get_name() + "," + gt_neighbour.get_name()
                                    rev_dst_name = ",".join(sorted(dst_name.replace(",", "")))
                                    if dst_name != rev_dst_name:
                                        dst_name = rev_dst_name
                                        rev_flags.add(dst_name)
                                    if dst_name not in states:
                                        states[dst_name] = State(dst_name)
                                        old_diff_states.append(dst_name)
                                    ambiguous = bt_transition.is_fault()
                                    states[src_name].add_transition(states[dst_name], Transition(
                                        deepcopy(gt_transition.get_event()), ambiguous=ambiguous))
        while len(old_diff_states) > 0:
            new_diff_states = list()
            for name in old_diff_states:
                bt_state, gt_state = bt_states[name.split(",")[0]], gt_states[name.split(",")[1]]
                if name in rev_flags:
                    bt_state, gt_state = bt_states[name.split(",")[1]], gt_states[name.split(",")[0]]
                for bt_neighbour, bt_transitions in bt_state.get_neighbours().iteritems():
                    for bt_transition in bt_transitions:
                        for gt_neighbour, gt_transitions in gt_state.get_neighbours().iteritems():
                            for gt_transition in gt_transitions:
                                if gt_transition.get_event_name() == bt_transition.get_event_name():
                                    dst_name = bt_neighbour.get_name() + "," + gt_neighbour.get_name()
                                    dst_name = ",".join(sorted(dst_name.replace(",", "")))
                                    if dst_name not in states:
                                        states[dst_name] = State(dst_name)
                                        new_diff_states.append(dst_name)
                                    ambiguous = bt_transition.is_fault()
                                    states[name].add_transition(states[dst_name], Transition(
                                        deepcopy(gt_transition.get_event()), ambiguous=ambiguous))
            old_diff_states = new_diff_states
    initial_state = states[",".join(good_twin.get_initial_state().get_name()*2)]
    return Automaton(initial_state, states.values())

def find(destination, n, fault, event):
    triplets = list()
    for destination2, transitions in destination.get_neighbours().iteritems():
        for transition in transitions:
            fault2 = fault
            if transition.is_fault():
                fault2 = True
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

def initialize_states_with_transitions(automaton):
    states = dict()
    for state in automaton.get_states():
        states[state.get_name()] = deepcopy(state)
    return states
