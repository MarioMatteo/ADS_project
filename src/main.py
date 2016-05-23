from random_automaton import *

import Tkinter as tk
import tkFileDialog as fileDialog

root = tk.Tk()
root.withdraw()

try:
    automaton_file = fileDialog.askopenfilename(title='Scegli il file da cui caricare l\'automa',
                                                filetypes=(('XML files', '*.xml'), ('All files', '*.*')))
    automaton = load_xml(automaton_file)
except IOError:
    exit()
#
level=6
save_img(automaton, 'Automaton', 'automaton', 'png')

i = 1
while i <= 1:
    print '--------------'+str(i)+'--------------'
    print 'First method: ' + str(first_method(automaton, level))
    # print 'Second method: ' + str(second_method(automaton, level))
    # print 'Third method: ' + str(third_method_v2(automaton, level))
    i += 1

# i = 1
# while i <= 1:
#     print '------------------'
#     print 'AUTOMATON '+str(i)
#     print '------------------'
#     automaton = generate_random_automaton(2, 8, 27, 3, 0)
#     if automaton is not None:
#         save_img(automaton, 'Random automaton ' + str(i), 'random' + str(i), 'png')
#         save_xml(automaton, 'random' + str(i))
#         print 'First method: ' + str(first_method(automaton, level))
#         # print 'Second method: ' + str(second_method(automaton, level))
#         # print 'Third method: ' + str(third_method(automaton, level))
#     print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
#     i += 1

# save_img(load_xml('generated_automaton.xml'), 'Generated automaton', 'generated_automaton', 'png')
