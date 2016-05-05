from Parser import *
import Tkinter as tk
import tkFileDialog as fileDialog

root = tk.Tk()
root.withdraw()

automaton_file = fileDialog.askopenfilename(title="Select the automaton file",
                                            filetypes=(("XML files", "*.xml"), ("All files", "*.*")))
if not automaton_file:
    exit(0)

automaton = Parser(automaton_file).parse()
print "States:\n" + automaton.get_states()
print "Transitions:\n" + automaton.get_transitions()
