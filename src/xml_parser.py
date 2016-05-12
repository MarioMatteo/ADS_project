from automaton_structure import *

import xml.etree.ElementTree as ET
from xml.dom import minidom
from graphviz import Digraph
import os

def load_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    states = dict()
    for state in root.findall("states/state"):
        states[state.text] = State(state.text)
    for transition in root.findall("transitions/transition"):
        source = states[transition.find("source").text]
        destination = states[transition.find("destination").text]
        event = None
        fault = False
        if "observable" in transition.attrib:
            event = Event()
            for name in transition.find("event").text.strip().split("//"):
                event.add(Event(name))
        if "fault" in transition.attrib:
            fault = True
        source.add_transition(destination, Transition(event=event, fault=fault))
    initial_state_name = root.find("states/state[@initial='true']").text
    return Automaton(states[initial_state_name], states.values())

def save_xml(automaton, filename):
    root = ET.Element("automaton")
    states = ET.SubElement(root, "states")
    for state in automaton.get_states():
        if state == automaton.get_initial_state():
            ET.SubElement(states, "state", {"initial": "true"}).text = state.get_name()
        else:
            ET.SubElement(states, "state").text = state.get_name()
    transitions = ET.SubElement(root, "transitions")
    for state in automaton.get_states():
        for destination, _transitions in state.get_neighbours().iteritems():
            for _transition in _transitions:
                event = None
                if _transition.is_observable():
                    transition = ET.SubElement(transitions, "transition", {"observable": "true"})
                    event = _transition.get_event()
                else:
                    transition = ET.SubElement(transitions, "transition")
                if _transition.is_fault():
                    transition.set("fault", "true")
                if _transition.is_ambiguous():
                    transition.set("ambiguous", "true")
                ET.SubElement(transition, "source").text = state.get_name()
                if event is not None:
                    ET.SubElement(transition, "event").text = event.get_name()
                ET.SubElement(transition, "destination").text = destination.get_name()
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(encoding="utf-8")
    save_file("xmls/" + filename + ".xml", xmlstr)

def save_img(automaton, title, file_name, _format, verbose=False):
    dot = Digraph(name=file_name, format=_format, graph_attr={'rankdir': 'LR'})
    dot.body.append('labelloc="t"')
    dot.body.append('label="'+title+'"')
    for state in automaton.get_states():
        src = state.get_name().replace(",", "")
        if state.equals(automaton.get_initial_state()):
            dot.node(src, label=state.get_name(), _attributes={'shape': 'doublecircle'})
        else:
            dot.node(src, label=state.get_name())
    for state in automaton.get_states():
        src = state.get_name().replace(",", "")
        for neighbour, transitions in state.get_neighbours().iteritems():
            dst = neighbour.get_name().replace(",", "")
            if verbose:
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
                        dot.edge(src, dst, _attributes={'color': 'blue'})
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
                events = ''.join(events.rsplit('+', 1)) + '>'
                if fault:
                    dot.edge(src, dst, label=events, _attributes={'color': 'red'})
                elif ambiguous:
                    dot.edge(src, dst, label=events, _attributes={'color': 'purple'})
                elif not observable:
                    dot.edge(src, dst, _attributes={'color': 'blue'})
                else:
                    dot.edge(src, dst, label=events)
    dot.render('imgs/' + file_name, cleanup=not verbose, view=False)

def save_file(filename, content):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, "w") as f:
        f.write(content)