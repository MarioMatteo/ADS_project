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

bad_twin1 = generate_bad_twin(automaton)
save(bad_twin1, "b1.xml")
bad_twin1 = load("b1.xml")

bad_twin2 = generate_bad_twin(bad_twin1, 2)
save(bad_twin2, "b2.xml")
bad_twin2 = load("b2.xml")

bad_twin3 = generate_bad_twin(bad_twin2, 3)
save(bad_twin3, "b3.xml")

# print str(bad_twin3)

# diagnosability_level = read_diagnosability_level()

# save(automaton, "trial.xml")
