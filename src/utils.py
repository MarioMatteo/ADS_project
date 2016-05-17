from file_handler import *

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

def first_synchronize(bad_twin, good_twin):
    states = dict()
    ambiguous_transitions = set()
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
                                    if ambiguous:
                                        ambiguous_transitions.add((states[src_name], states[dst_name]))
                                    states[src_name].add_transition(states[dst_name], Transition(
                                        deepcopy(gt_transition.get_event()), ambiguous=ambiguous))
        while len(old_diff_states) > 0:
            new_diff_states = list()
            for name in old_diff_states:
                if name in rev_flags:
                    bt_state, gt_state = bt_states[name.split(",")[1]], gt_states[name.split(",")[0]]
                else:
                    bt_state, gt_state = bt_states[name.split(",")[0]], gt_states[name.split(",")[1]]
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
                                    if ambiguous:
                                        ambiguous_transitions.add((states[name], states[dst_name]))
                                    states[name].add_transition(states[dst_name], Transition(
                                        deepcopy(gt_transition.get_event()), ambiguous=ambiguous))
            old_diff_states = new_diff_states
    initial_state = states[",".join(good_twin.get_initial_state().get_name()*2)]
    return Automaton(initial_state, states.values()), ambiguous_transitions

def second_synchronize(old_synchronized, ambiguous_transitions, bad_twin, level):
    states = initialize_states_with_transitions(old_synchronized)
    twins_states = initialize_states_with_transitions(bad_twin)
    old_diff_states = list()
    rev_flags = set()
    for state in states.values():
        src_name = state.get_name()
        for bt_neighbour, bt_transitions in twins_states[src_name.split(",")[0]].get_current_level_transitions(level).iteritems():
            for bt_transition in bt_transitions:
                for gt_neighbour, gt_transitions in twins_states[src_name.split(",")[1]].get_current_level_transitions(level).iteritems():
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
                                if ambiguous:
                                    ambiguous_transitions.add((states[src_name], states[dst_name]))
                                states[src_name].add_transition(states[dst_name], Transition(
                                    deepcopy(gt_transition.get_event()), ambiguous=ambiguous))
    while len(old_diff_states) > 0:
        new_diff_states = list()
        for name in old_diff_states:
            if name in rev_flags:
                bt_state, gt_state = twins_states[name.split(",")[1]], twins_states[name.split(",")[0]]
            else:
                bt_state, gt_state = twins_states[name.split(",")[0]], twins_states[name.split(",")[1]]
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
                                if ambiguous:
                                    ambiguous_transitions.add((states[name], states[dst_name]))
                                states[name].add_transition(states[dst_name], Transition(
                                    deepcopy(gt_transition.get_event()), ambiguous=ambiguous))
        old_diff_states = new_diff_states
    initial_state = states[old_synchronized.get_initial_state().get_name()]
    return Automaton(initial_state, states.values()), ambiguous_transitions

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

def first_condition(ambiguous_transitions):
    return len(ambiguous_transitions) == 0

def second_condition(bad_twin):
    return not bad_twin.is_non_deterministic()

def third_condition(bad_twin):
    return not bad_twin.has_ambiguous_events()

def first_method(automaton, level):
    old_bad_twin = automaton
    i = 1
    while i <= level:
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        good_twin = generate_good_twin(new_bad_twin)
        synchronized, ambiguous_transitions = first_synchronize(new_bad_twin, good_twin)
        save_automata_files(i, new_bad_twin, good_twin, synchronized)
        for src, dst in ambiguous_transitions:
            if find_loops(dst, set([src])):
                return i - 1
            # if not (src.is_visited() or dst.is_visited()):
            # src.set_visited()
            # result = find_loops(dst)
            # if result == True or src in result:
            #     return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def second_method(automaton, level):
    old_bad_twin = automaton
    i = 1
    while i <= level:
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        save_automata_files(i, bad_twin=new_bad_twin)
        if not(second_condition(new_bad_twin) or third_condition(new_bad_twin)):
            good_twin = generate_good_twin(new_bad_twin)
            synchronized, ambiguous_transitions = first_synchronize(new_bad_twin, good_twin)
            save_automata_files(i, good_twin=good_twin, synchronized=synchronized)
            if not first_condition(ambiguous_transitions):
                for src, dst in ambiguous_transitions:
                    if find_loops(dst, set([src])):
                        return i - 1
                    # if not (src.is_visited() or dst.is_visited()):
                        # src.set_visited()
                        # result = find_loops(dst)
                        # if result == True or src in result:
                        #     return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def third_method(automaton, level):
    old_bad_twin = automaton
    i = 1
    first_sync = True
    synchronized = None
    ambiguous_transitions = None
    while i <= level:
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        save_automata_files(i, bad_twin=new_bad_twin)
        if not (second_condition(new_bad_twin) or third_condition(new_bad_twin)):
            if not first_sync:
                synchronized, ambiguous_transitions = second_synchronize(synchronized, ambiguous_transitions, new_bad_twin, i)
                save_automata_files(i, synchronized=synchronized)
            else:
                good_twin = generate_good_twin(new_bad_twin)
                synchronized, ambiguous_transitions = first_synchronize(new_bad_twin, good_twin)
                first_sync = False
                save_automata_files(i, good_twin=good_twin, synchronized=synchronized)
            if not first_condition(ambiguous_transitions):
                for src, dst in ambiguous_transitions:
                    if find_loops(dst, set([src])):
                        return i - 1
                        # if not (src.is_visited() or dst.is_visited()):
                        # src.set_visited()
                        # result = find_loops(dst)
                        # if result == True or src in result:
                        #     return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

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

# def find_loops(src):
#     visited = set()
#     src.set_visited()
#     for dst in src.get_neighbours():
#         if dst.is_visited():
#             visited.add(dst)
#         else:
#             result = find_loops(dst)
#             if result == True:
#                 return True
#             visited.union(result)
#     if src in visited:
#         return True
#     return visited

def find_loops(src, visited):
    for dst in src.get_neighbours():
        if dst in visited:
            return True
        new_visited = deepcopy(visited)
        new_visited.add(src)
        if find_loops(dst, new_visited):
            return True
    return False

def save_automata_files(level, bad_twin=None, good_twin=None, synchronized=None):
    if bad_twin is not None:
        save_xml(bad_twin, "b" + str(level))
        save_img(bad_twin, "Bad twin - Level " + str(level), "b" + str(level), "png")
    if good_twin is not None:
        save_xml(good_twin, "g" + str(level))
        save_img(good_twin, "Good twin - Level " + str(level), "g" + str(level), "png")
    if synchronized is not None:
        save_xml(synchronized, "s" + str(level))
        save_img(synchronized, "Synchronized - Level " + str(level), "s" + str(level), "png")