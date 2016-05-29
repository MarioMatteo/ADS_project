from automaton import *

import xml.etree.ElementTree as ET
from xml.dom import minidom
from graphviz import Digraph
import os

def load_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    states = dict()
    for state in root.findall('states/state'):
        states[state.text] = State(state.text)
    for transition in root.findall('transitions/transition'):
        src = states[transition.find('source').text]
        dst = states[transition.find('destination').text]
        event = None
        fault = False
        if 'observable' in transition.attrib:
            event = Event()
            for name in transition.find('event').text.strip().split('//'):
                event.add(Event(name))
        if 'fault' in transition.attrib:
            fault = True
        src.add_transition(dst, Transition(event=event, fault=fault))
    initial_state = root.find('states/state[@initial="true"]').text
    return Automaton(initial_state, states)

def save_xml(automaton, filename):
    root = ET.Element('automaton')
    states = ET.SubElement(root, 'states')
    for name in automaton.get_states():
        if name == automaton.get_initial_state():
            ET.SubElement(states, 'state', {'initial': 'true'}).text = name
        else:
            ET.SubElement(states, 'state').text = name
    transitions = ET.SubElement(root, 'transitions')
    for src_name, src in automaton.get_states().iteritems():
        for dst, _transitions in src.get_neighbours().iteritems():
            dst_name = dst.get_name()
            for _transition in _transitions:
                event = None
                if _transition.is_observable():
                    transition = ET.SubElement(transitions, 'transition', {'observable': 'true'})
                    event = _transition.get_event()
                else:
                    transition = ET.SubElement(transitions, 'transition')
                if _transition.is_fault():
                    transition.set('fault', 'true')
                if _transition.is_ambiguous():
                    transition.set('ambiguous', 'true')
                ET.SubElement(transition, 'source').text = src_name
                if event is not None:
                    ET.SubElement(transition, 'event').text = event.get_name()
                ET.SubElement(transition, 'destination').text = dst_name
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(encoding='utf-8')
    save_file('xmls/' + filename + '.xml', xmlstr)

def save_img(automaton, title, file_name, _format, compact=False, save_source=False):
    dot = Digraph(name=file_name, format=_format, graph_attr={'rankdir': 'LR'})
    dot.body.append('graph [fontname="verdana", labelloc="t", label="'+title+'"]')
    dot.body.append('node [fontname="verdana", fillcolor="#4f81bd", fontcolor="white", '
                    'style="filled, solid", color="#385d8a", penwidth="2"]')
    dot.body.append('edge [fontname="verdana", fontcolor="orange", color="#385d8a"]')
    dot.node('start', _attributes={'style': 'invisible'})
    for name in automaton.get_states():
        node_name = name.replace(',', '')
        dot.node(node_name, label=name)
    dot.edge('start', automaton.get_initial_state().replace(',', ''))
    for state in automaton.get_states().values():
        src = state.get_name().replace(',', '')
        for neighbour, transitions in state.get_neighbours().iteritems():
            dst = neighbour.get_name().replace(',', '')
            if not compact:
                for transition in transitions:
                    if transition.is_fault():
                        if transition.is_observable():
                            dot.edge(src, dst, label=transition.get_event_name(), _attributes={'color': 'red'})
                        else:
                            dot.edge(src, dst, _attributes={'color': 'red'})
                    elif transition.is_ambiguous():
                        dot.edge(src, dst, label=transition.get_event_name(), _attributes={'color': 'purple'})
                    elif transition.is_observable():
                        dot.edge(src, dst, label=transition.get_event_name())
                    else:
                        dot.edge(src, dst, _attributes={'color': 'gray65'})
            else:
                observable = False
                fault = False
                ambiguous = False
                count = 1
                events = '<'
                for i in range(len(transitions)):
                    transition = transitions[i]
                    if transition.is_fault():
                        fault = True
                        if transition.is_observable():
                            observable = True
                            events += '<font color="red">' + transition.get_event_name() + '</font>' + \
                                      ('<br/>+' if count % 2 == 0 and i < len(transitions) - 1 else '+')
                            count += 1
                    elif transition.is_ambiguous():
                        ambiguous = True
                        observable = True
                        events += '<font color="purple">' + transition.get_event_name() + '</font>' + \
                                  ('<br/>+' if count % 2 == 0 and i < len(transitions) - 1 else '+')
                        count += 1
                    elif transition.is_observable():
                        observable = True
                        events += transition.get_event_name() + ('<br/>+' if count % 2 == 0 and i < len(transitions) - 1 else '+')
                        count += 1
                if '+' in events:
                    events = ''.join(events.rsplit('+', 1))
                events += '>'
                if fault:
                    dot.edge(src, dst, label=events, _attributes={'color': 'red'})
                elif ambiguous:
                    dot.edge(src, dst, label=events, _attributes={'color': 'purple'})
                elif not observable:
                    dot.edge(src, dst, _attributes={'color': 'gray65'})
                else:
                    dot.edge(src, dst, label=events)
    dot.render('imgs/' + file_name, cleanup=not save_source, view=False)

def save_file(filename, content):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, 'w') as f:
        f.write(content)

def save_automata_files(level, bad_twin=None, good_twin=None, synchronized=None, verbose=False):
    if bad_twin is not None:
        save_xml(bad_twin, "b" + str(level))
        save_img(bad_twin, "Bad twin - Level " + str(level), "b" + str(level), "png", verbose)
    if good_twin is not None:
        save_xml(good_twin, "g" + str(level))
        save_img(good_twin, "Good twin - Level " + str(level), "g" + str(level), "png", verbose)
    if synchronized is not None:
        save_xml(synchronized, "s" + str(level))
        save_img(synchronized, "Synchronized - Level " + str(level), "s" + str(level), "png", verbose)
