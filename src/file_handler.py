"""
Contains the methods to handle XML and png files representing the automata.
"""

from automaton import *
import log
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree
from graphviz import Digraph
import os, sys
import inspect

def validate_syntax(filepath):

    """
    Validates the XML syntax according the XML schema used to represent the automaton.

    An XML is considered syntactically valid if it contains:
        - <automaton> as root
        - <states> as first child of <automaton>
        - a list of <state> as child of <states>, containing #text and the optional attribute initial="true"
        - <transitions> as second child of <automaton>
        - a list of <transition> as child of <transitions>, containing the optional attributes observable="true"
          and fault="true"
        - <source> as child of <transition>, containing #text
        - <event> as optional child of <transition>, containing #text
        - <destination> as child of <transition>, containing #text

    :param filepath: the path of the XML file representing the automaton structure.
    :type filepath: str
    :return: true if the XML syntax is correct, the error message otherwise
    :rtype: bool or str
    """

    try:
        doc = etree.parse(filepath)
        xsd = etree.parse('schema/automaton.xsd')
        xmlschema = etree.XMLSchema(xsd)
        xmlschema.assertValid(doc)
    except (etree.XMLSyntaxError, etree.DocumentInvalid) as e:
        return log.XML_SYNTAX_ERROR % str(e)
    return True

def validate_xml_semantics(filepath):

    """
    Validates the XML semantics according to the definition of the automaton.

    An XML is considered semantically valid if:
        - it contains exactly one <state> with attribute initial="true"
        - none of its <state> contain the special character ',' in their #text
        - it contains at least a <transition> with attribute observable="true"
        - it contains at least a <transition> with attribute fault="true"
        - none of its <transition> have more than one attribute
        - only <transition> with attribute observable="true" must have the associated <event>
        - none of its <event> contain the special characters '//' and '+' in their #text

    :param filepath: the path of the XML file representing the automaton
    :type filepath: str
    :return: true if the XML semantics is correct, the error message otherwise
    :rtype: bool or str
    """

    tree = ET.parse(filepath)
    root = tree.getroot()
    states = root.findall('states/state')
    initial_states_count = 0
    for state in states:
        if ',' in state.text.strip():
            return log.STATE_NAME_ERROR % state.text.strip()
        if len(state.attrib) > 0:
            initial_states_count += 1
    if initial_states_count != 1:
        if initial_states_count == 0:
            return log.ZERO_INITIAL_STATES_ERROR
        else:
            return log.MULTIPLE_INITIAL_STATES_ERROR
    transitions = root.findall('transitions/transition')
    observable_transitions_count = 0
    fault_transitions_count = 0
    for transition in transitions:
        if len(transition.attrib) > 1:
            return log.MULTIPLE_ATTRIBUTES_TRANSITIONS_ERROR
        event = transition.find('event')
        if 'observable' in transition.attrib:
            observable_transitions_count += 1
            if event is None:
                return log.NO_EVENT_IN_OBSERVABLE_TRANSITION_ERROR
            if '//' in event.text.strip() or '+' in event.text.strip():
                return log.EVENT_NAME_ERROR % event.text.strip()
        if 'fault' in transition.attrib:
            fault_transitions_count += 1
        if 'observable' not in transition.attrib:
            if event is not None:
                return log.EVENT_IN_UNOBSERVABLE_TRANSITION_ERROR
    if observable_transitions_count == 0:
        return log.NO_OBSERVABLE_TRANSITIONS_ERROR
    if fault_transitions_count == 0:
        return log.NO_FAULT_TRANSITIONS_ERROR
    return True

def validate_language_semantics(automaton):

    """
    Validates the language semantics.

    It uses the automaton function that checks if the language is alive.

    :param automaton: the automaton to be checked
    :type automaton: Automaton
    :return: true if the XML semantics is correct, otherwise the error message
    :rtype: bool or str
    """

    if not automaton.is_language_alive():
        return log.LANGUAGE_NOT_ALIVE_ERROR
    return True

def load_xml(filepath):

    """
    Loads an automaton from an XML file.

    :param filepath: the path of the XML file representing the automaton
    :type filepath: str
    :return: the automaton represented by the XML file, or an error message if its validation fails
    :rtype: Automaton or str
    """

    check = validate_syntax(filepath)
    if type(check) is not bool:
        return check
    check = validate_xml_semantics(filepath)
    if type(check) is not bool:
        return check
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
            name = transition.find('event').text.strip()
            event = Event(name)
        if 'fault' in transition.attrib:
            fault = True
        src.add_transition(dst, Transition(event=event, fault=fault))
    initial_state = root.find('states/state[@initial="true"]').text
    automaton = Automaton(initial_state, states)
    check = validate_language_semantics(automaton)
    if type(check) is not bool:
        return check
    return automaton

def save_xml(automaton, filename):

    """
    Saves an automaton into an XML file.

    :param automaton: the automaton to be saved
    :type automaton: Automaton
    :param filename: the name of the XML file
    :rtype filename: str
    """

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
    save_file('temp/xmls/' + filename + '.XML', xmlstr)

def save_img(automaton, file_name, compact):

    """
    Saves the graphical representation of the automaton into a png file.

    :param automaton: the automaton to be saved
    :type automaton: Automaton
    :param file_name: the name of the file to be saved
    :type file_name: str
    :param compact: whether to render transitions in compact mode or in complete mode
    :type compact: bool
    """

    dot = Digraph(name=file_name, format='png', graph_attr={'rankdir': 'LR'})
    dot.body.append('graph [fontname="verdana"]')
    dot.body.append('node [fontname="verdana", fillcolor="#4f81bd", fontcolor="white", '
                    'style="filled, solid", color="#385d8a", penwidth="2"]')
    dot.body.append('edge [fontname="verdana", fontcolor="orange", color="#385d8a"]')
    dot.node('s', _attributes={'style': 'invisible'})
    for name in automaton.get_states():
        node_name = name.replace(',', '')
        dot.node(node_name, label=name)
    dot.edge('s', automaton.get_initial_state().replace(',', ''))
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
                        dot.edge(src, dst, label=transition.get_event_name(), _attributes={'color': 'deeppink'})
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
                        events += '<font color="deeppink">' + transition.get_event_name() + '</font>' + \
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
                    dot.edge(src, dst, label=events, _attributes={'color': 'deeppink'})
                elif not observable:
                    dot.edge(src, dst, _attributes={'color': 'gray65'})
                else:
                    dot.edge(src, dst, label=events)
    dot.render('temp/imgs/' + file_name, view=False, cleanup=True)

def save_file(filename, content):

    """
    Saves a text file.

    :param filename: the name of the file
    :type filename: str
    :param content: the text to save into the file
    :type content: str
    """

    create_dir(os.path.dirname(filename))
    with open(filename, 'w') as f:
        f.write(content)

def create_dir(dirname):
    """
    Creates a directory.

    :param dirname: the name of the directory
    :type dirname: str
    :return: the name of the directory followed by a separator
    :rtype: str
    """

    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return dirname + '/'


def get_script_dir():
    """
    Gets the name of the directory in which the script is located.

    :return: the name of the directory
    :rtype: str
    """

    if getattr(sys, 'frozen', False):
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    path = os.path.realpath(path)
    return os.path.dirname(path)

def save_automata_files(level, compact, bad_twin=None, good_twin=None, synchronized=None):

    """
    Saves XML and png files representing the automata.

    Only not None automata will be saved.

    :param level: the current automata level
    :type level: int
    :param compact: whether to render transitions in compact mode or in complete mode
    :type compact: bool
    :param bad_twin: the current level bad twin
    :type bad_twin: Automaton or None
    :param good_twin: the current level good twin
    :type good_twin: Automaton or None
    :param synchronized: the current level synchronized automaton
    :type synchronized: Automaton or None
    """

    if bad_twin is not None:
        save_xml(bad_twin, "b" + str(level))
        save_img(bad_twin, "b" + str(level), compact)
    if good_twin is not None:
        save_xml(good_twin, "g" + str(level))
        save_img(good_twin, "g" + str(level), compact)
    if synchronized is not None:
        save_xml(synchronized, "s" + str(level))
        save_img(synchronized, "s" + str(level), compact)
