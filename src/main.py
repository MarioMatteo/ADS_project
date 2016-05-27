from random_automaton import *

import Tkinter as tk
import tkFileDialog as fileDialog

level = 12

root = tk.Tk()
root.withdraw()

try:
    automaton_file = fileDialog.askopenfilename(title='Scegli il file da cui caricare l\'automa',
                                                filetypes=(('XML files', '*.xml'), ('All files', '*.*')))
    automaton = load_xml(automaton_file)
except IOError:
    exit()

save_img(automaton, 'Automaton', 'automaton', 'png')

print 'First method: ' + str(first_method(automaton, level))
print 'Second method: ' + str(second_method(automaton, level))
print 'Third method (v1): ' + str(third_method_v1(automaton, level))
print 'Third method (v2): ' + str(third_method_v2(automaton, level))

# i = 1
# ns = 10
# nt = 20
# ne = 8
# no = 13
# nf = 1
# while i <= 10:
#     print '------------------'
#     print 'AUTOMATON '+str(i)
#     print '------------------'
#     automaton = generate_random_automaton(ns, nt, ne, no, nf)
#     save_img(automaton, 'Random automaton ' + str(i), 'random' + str(i), 'png')
#     save_xml(automaton, 'random' + str(i))
#     print 'First method: ' + str(first_method(automaton, level))
#     print 'Second method: ' + str(second_method(automaton, level))
#     print 'Third method (v1): ' + str(third_method_v1(automaton, level))
#     print 'Third method (v2): ' + str(third_method_v2(automaton, level))
#     print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
#     i += 1
