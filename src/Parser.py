from automaton_structure import *

import xml.etree.ElementTree as ET

class Parser:

    def __init__(self, file_path):
        tree = ET.parse(file_path)
        self.root = tree.getroot()

    def parse(self):
        diagnosability_level = self.root.attrib["diagnosability-level"]
        states = dict()
        for state in self.root.findall("states/state"):
            states[state.text] = State(state.text)
        for transition in self.root.findall("transitions/transition"):
            source = states[transition.find("source").text]
            destination = states[transition.find("destination").text]
            if not transition.attrib:
                source.add_transition(destination, Transition())
            elif transition.attrib["type"] == Transition.TYPE_OBSERVABLE:
                event = Event(transition.find("event").text)
                source.add_transition(destination, Transition(event=event))
            elif transition.attrib["type"] == Transition.TYPE_FAULT:
                source.add_transition(destination, Transition(fault=True))
        initial_state_name = self.root.find("states/state[@type='initial']").text
        return Automaton(diagnosability_level, states[initial_state_name], states.values())