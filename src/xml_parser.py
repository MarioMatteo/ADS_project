from automaton_structure import *

import xml.etree.ElementTree as ET
from xml.dom import minidom

def load(file_path):
    tree = ET.parse(file_path)
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

def save(automaton, file_path):
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
                ET.SubElement(transition, "source").text = state.get_name()
                if event is not None:
                    ET.SubElement(transition, "event").text = event.get_name()
                ET.SubElement(transition, "destination").text = destination.get_name()
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml()
    with open(file_path, "w") as f:
        f.write(xmlstr.encode('utf-8'))
