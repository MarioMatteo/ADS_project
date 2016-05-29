from file_handler import *
from config import *

from copy import deepcopy
import re

def generate_bad_twin(automaton, level=1):
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
                    transition.set_crossed()
                    triplets = find(dst, level - transition.get_event_cardinality(), fault, transition.get_event())
                    transition.set_crossed(False)
                    for event, dst2, fault2 in triplets:
                        if level == 1 or not event.is_composed_by_all_same_events():
                            dst2_name = dst2.get_name()
                            states[src_name].add_transition(states[dst2_name], Transition(event=event, fault=fault2))
    bad_twin = Automaton(automaton.get_initial_state(), states)
    if level == 1:
        bad_twin.remove_unreachable_states()
    return bad_twin

def generate_good_twin(bad_twin):
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

def first_synchronize(bad_twin, good_twin):
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
        for gt_src_name in gt_states:
            src_name = ','.join([gt_src_name] * 2)
            bt_src = bt_states[gt_src_name]
            for bt_dst, bt_transitions in bt_src.get_neighbours().iteritems():
                for gt_dst, gt_transitions in bt_src.get_neighbours().iteritems():
                    for bt_transition in bt_transitions:
                        for gt_transition in gt_transitions:
                            if (bt_transition.get_event_name() == gt_transition.get_event_name()) and \
                                    not (bt_transition.is_fault() and gt_transition.is_fault()):
                                if not bt_dst.equals(gt_dst) or bt_transition.is_fault() != gt_transition.is_fault():
                                    dst_name = ','.join(natural_sort([bt_dst.get_name(), gt_dst.get_name()]))
                                    rev_dst_name = ','.join(reversed(dst_name.split(',')))
                                    if dst_name not in states and rev_dst_name not in states:
                                        states[dst_name] = State(dst_name)
                                    ambiguous = bt_transition.is_fault() != gt_transition.is_fault()
                                    if ambiguous:
                                        ambiguous_transitions.add((states[src_name], states[dst_name]))
                                    states[src_name].add_transition(states[dst_name], Transition(
                                        deepcopy(bt_transition.get_event()), ambiguous=ambiguous))
        while set(states.keys()) != prev_states:
            diff_states = set(states.keys()) - prev_states
            prev_states = set(states.keys())
            for src_name in diff_states:
                splitted_name = src_name.split(',')
                bt_src, gt_src = bt_states[splitted_name[0]], bt_states[splitted_name[1]]
                for bt_dst, bt_transitions in bt_src.get_neighbours().iteritems():
                    for gt_dst, gt_transitions in gt_src.get_neighbours().iteritems():
                        for bt_transition in bt_transitions:
                            for gt_transition in gt_transitions:
                                if (bt_transition.get_event_name() == gt_transition.get_event_name()) and \
                                        not (bt_transition.is_fault() and gt_transition.is_fault()):
                                    dst_name = ','.join(natural_sort([bt_dst.get_name(), gt_dst.get_name()]))
                                    rev_dst_name = ','.join(reversed(dst_name.split(',')))
                                    if dst_name not in states and rev_dst_name not in states:
                                        states[dst_name] = State(dst_name)
                                    ambiguous = bt_transition.is_fault() != gt_transition.is_fault()
                                    if ambiguous:
                                        ambiguous_transitions.add((states[src_name], states[dst_name]))
                                    states[src_name].add_transition(states[dst_name], Transition(
                                        deepcopy(bt_transition.get_event()), ambiguous=ambiguous))
    initial_state = ','.join([good_twin.get_initial_state()] * 2)
    return Automaton(initial_state, states), ambiguous_transitions

def second_synchronize(old_synchronized, ambiguous_transitions, bad_twin, level):
    states = deepcopy(old_synchronized.get_states())
    bt_states = bad_twin.get_states()
    prev_states = set(states.keys())
    for src_name in old_synchronized.get_states():
        splitted_name = src_name.split(',')
        bt_src, gt_src = bt_states[splitted_name[0]], bt_states[splitted_name[1]]
        bt_current_level_transitions = bt_src.get_current_level_transitions(level)
        gt_current_level_transitions = gt_src.get_current_level_transitions(level)
        for bt_dst, bt_transitions in bt_current_level_transitions.iteritems():
            for gt_dst, gt_transitions in gt_current_level_transitions.iteritems():
                for bt_transition in bt_transitions:
                    for gt_transition in gt_transitions:
                        if bt_transition.get_event_name() == gt_transition.get_event_name() and \
                                not (bt_transition.is_fault() and gt_transition.is_fault()):
                            dst_name = ','.join(natural_sort([bt_dst.get_name(), gt_dst.get_name()]))
                            rev_dst_name = ','.join(reversed(dst_name.split(',')))
                            if dst_name not in states and rev_dst_name not in states:
                                states[dst_name] = State(dst_name)
                            ambiguous = bt_transition.is_fault() != gt_transition.is_fault()
                            if ambiguous:
                                ambiguous_transitions.add((states[src_name], states[dst_name]))
                            states[src_name].add_transition(states[dst_name], Transition(
                                deepcopy(bt_transition.get_event()), ambiguous=ambiguous))
    while set(states.keys()) != prev_states:
        diff_states = set(states.keys()) - prev_states
        prev_states = set(states.keys())
        for src_name in diff_states:
            splitted_name = src_name.split(',')
            bt_src, gt_src = bt_states[splitted_name[0]], bt_states[splitted_name[1]]
            for bt_dst, bt_transitions in bt_src.get_neighbours().iteritems():
                for gt_dst, gt_transitions in gt_src.get_neighbours().iteritems():
                    for bt_transition in bt_transitions:
                        for gt_transition in gt_transitions:
                            if bt_transition.get_event_name() == gt_transition.get_event_name() and \
                                    not (bt_transition.is_fault() and gt_transition.is_fault()):
                                dst_name = ','.join(natural_sort([bt_dst.get_name(), gt_dst.get_name()]))
                                rev_dst_name = ','.join(reversed(dst_name.split(',')))
                                if dst_name not in states and rev_dst_name not in states:
                                    states[dst_name] = State(dst_name)
                                ambiguous = bt_transition.is_fault() != gt_transition.is_fault()
                                if ambiguous:
                                    ambiguous_transitions.add((states[src_name], states[dst_name]))
                                states[src_name].add_transition(states[dst_name], Transition(
                                    deepcopy(bt_transition.get_event()), ambiguous=ambiguous))
    initial_state = old_synchronized.get_initial_state()
    return Automaton(initial_state, states)

def find(dst, n, fault, event):
    triplets = list()
    for dst2, transitions in dst.get_neighbours().iteritems():
        for transition in transitions:
            if not transition.is_crossed():
                fault2 = fault
                if transition.is_fault():
                    fault2 = True
                event_cardinality = transition.get_event_cardinality()
                if transition.is_observable() and event_cardinality <= n:
                    composed_event = deepcopy(transition.get_event())
                    composed_event.add(deepcopy(event))
                    if n == event_cardinality:
                        triplets.append((composed_event, dst2, fault2))
                    else:
                        transition.set_crossed()
                        triplets += find(dst2, n - event_cardinality, fault2, composed_event)
                        transition.set_crossed(False)
                if not transition.is_observable():
                    transition.set_crossed()
                    triplets += find(dst2, n, fault2, event)
                    transition.set_crossed(False)
    return triplets

def first_condition(ambiguous_transitions):
    return len(ambiguous_transitions) == 0

def second_condition(bad_twin):
    return not bad_twin.is_non_deterministic()

def third_condition(bad_twin):
    return not bad_twin.has_ambiguous_events()

def initialize_states(automaton):
    states = dict()
    for name, state in automaton.get_states().iteritems():
        states[name] = State(name)
    return states

def find_loops(src, visited):
    for dst in src.get_neighbours():
        if dst in visited:
            return True
        # new_visited = deepcopy(visited)
        # new_visited.add(src)
        visited.add(src)
        # if find_loops(dst, new_visited):
        if find_loops(dst, visited):
            return True
    return False

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)
