from utils import *
import Tkinter as tk
import tkFileDialog as fileDialog

root = tk.Tk()
root.withdraw()

try:
    automaton_file = fileDialog.askopenfilename(title="Scegli il file da cui caricare l'automa",
                                                filetypes=(("XML files", "*.xml"), ("All files", "*.*")))
    automaton = load_xml(automaton_file)
except IOError:
    exit()

level=4
old_bad_twin = automaton
save_img(automaton, "Automaton", "automaton", "png")

# print "First method: " + str(first_method(automaton, level))
print "Second method: " + str(second_method(automaton, level))
# print "Third method: " + str(third_method(automaton, level))
