from xml_parser import *
from utils import *
import Tkinter as tk
import tkFileDialog as fileDialog

root = tk.Tk()
root.withdraw()

try:
    automaton_file = fileDialog.askopenfilename(title="Scegli il file da cui caricare l'automa",
                                                filetypes=(("XML files", "*.xml"), ("All files", "*.*")))
    automaton = load(automaton_file)
except IOError:
    exit()

level=3
old_bad_twin = automaton
for i in range(1, level+1):
    new_bad_twin = generate_bad_twin(old_bad_twin, i)
    save(new_bad_twin, "b"+str(i)+".xml")
    new_good_twin = generate_good_twin(new_bad_twin)
    save(new_good_twin, "g"+str(i)+".xml")
    old_bad_twin = new_bad_twin
    synchronized = synchronize(new_bad_twin, new_good_twin)
    save(synchronized, "s"+str(i)+".xml")
