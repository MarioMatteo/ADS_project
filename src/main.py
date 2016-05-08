from xml_parser import *
from utils import *
import Tkinter as tk
import tkFileDialog as fileDialog


def read_diagnosability_level():
    diagnosability_level = -1
    while diagnosability_level < 1:
        try:
            diagnosability_level = int(raw_input("Inserisci il livello di diagnosticabilita' da verificare: "))
        except ValueError:
            print "Valore errato! Reinserisci"
    return diagnosability_level

root = tk.Tk()
root.withdraw()

try:
    automaton_file = fileDialog.askopenfilename(title="Scegli il file da cui caricare l'automa",
                                                filetypes=(("XML files", "*.xml"), ("All files", "*.*")))
except IOError:
    exit(-1)

automaton = load(automaton_file)

# try:
#     save_file = fileDialog.asksaveasfilename(title="Scegli il file in cui salvare l'automa",
#                                                 filetypes=(("XML files", "*.xml"), ("All files", "*.*")))
# except IOError:
#     exit(-1)

level=3
old_bad_twin = automaton
for i in range(1, level+1):
    new_bad_twin = generate_bad_twin(old_bad_twin, i)
    save(new_bad_twin, "b"+str(i)+".xml")
    new_good_twin = generate_good_twin(new_bad_twin)
    save(new_good_twin, "g"+str(i)+".xml")
    old_bad_twin = new_bad_twin

# print str(bad_twin3)

# diagnosability_level = read_diagnosability_level()

# save(automaton, "trial.xml")
