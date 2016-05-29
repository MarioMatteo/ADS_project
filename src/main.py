from random_automaton import *
from config import *

from Tkinter import *
from PIL import ImageTk, Image
import tkFileDialog as fileDialog
import inspect

automaton = None
canvas = None

def first_method(automaton, level):
    params = read_params()
    save = params['save']
    old_bad_twin = automaton
    i = 1
    global status_text, root
    while i <= level:
        status_text.set('Method 1: generating bad twin of level ' + str(i) + '...')
        root.update_idletasks()
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        status_text.set('Method 1: generating good twin of level ' + str(i) + '...')
        root.update_idletasks()
        good_twin = generate_good_twin(new_bad_twin)
        status_text.set('Method 1: synchronizing twins of level ' + str(i) + '...')
        root.update_idletasks()
        synchronized, ambiguous_transitions = first_synchronize(new_bad_twin, good_twin)
        if save:
            status_text.set('Method 1: saving intermediate results of level ' + str(i) + '...')
            root.update_idletasks()
            save_automata_files(i, new_bad_twin, good_twin, synchronized)
        for src, dst in ambiguous_transitions:
            if find_loops(dst, set([src])):
                return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def second_method(automaton, level):
    params = read_params()
    save = params['save']
    old_bad_twin = automaton
    i = 1
    while i <= level:
        status_text.set('Method 2: generating bad twin of level ' + str(i) + '...')
        root.update_idletasks()
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            status_text.set('Method 2: saving intermediate results of level ' + str(i) + '...')
            root.update_idletasks()
            save_automata_files(i, bad_twin=new_bad_twin)
        if not(second_condition(new_bad_twin) or third_condition(new_bad_twin)):
            status_text.set('Method 2: generating good twin of level ' + str(i) + '...')
            root.update_idletasks()
            good_twin = generate_good_twin(new_bad_twin)
            status_text.set('Method 2: synchronizing twins of level ' + str(i) + '...')
            root.update_idletasks()
            synchronized, ambiguous_transitions = first_synchronize(new_bad_twin, good_twin)
            if save:
                status_text.set('Method 2: saving intermediate results of level ' + str(i) + '...')
                root.update_idletasks()
                save_automata_files(i, good_twin=good_twin, synchronized=synchronized)
            if not first_condition(ambiguous_transitions):
                for src, dst in ambiguous_transitions:
                    if find_loops(dst, set([src])):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def third_method_v1(automaton, level):
    params = read_params()
    save = params['save']
    old_bad_twin = automaton
    i = 1
    first_sync = True
    synchronized = None
    ambiguous_transitions = None
    last_sync_level = 1
    while i <= level:
        status_text.set('Method 3v1: generating bad twin of level ' + str(i) + '...')
        root.update_idletasks()
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            status_text.set('Method 3v1: saving intermediate results of level ' + str(i) + '...')
            root.update_idletasks()
            save_automata_files(i, bad_twin=new_bad_twin)
        if not (second_condition(new_bad_twin) or third_condition(new_bad_twin)):
            if first_sync:
                status_text.set('Method 3v1: generating good twin of level ' + str(i) + '...')
                root.update_idletasks()
                good_twin = generate_good_twin(new_bad_twin)
                status_text.set('Method 3v1: synchronizing twins of level ' + str(i) + '...')
                root.update_idletasks()
                synchronized, ambiguous_transitions = first_synchronize(new_bad_twin, good_twin)
                first_sync = False
                if save:
                    status_text.set('Method 3v1: saving intermediate results of level ' + str(i) + '...')
                    root.update_idletasks()
                    save_automata_files(i, good_twin=good_twin, synchronized=synchronized)
            else:
                if last_sync_level < i - 1:
                    status_text.set('Method 3v1: generating good twin of level ' + str(i - 1) + '...')
                    root.update_idletasks()
                    old_good_twin = generate_good_twin(old_bad_twin)
                    status_text.set('Method 3v1: synchronizing twins of level ' + str(i - 1) + '...')
                    root.update_idletasks()
                    synchronized, ambiguous_transitions = first_synchronize(old_bad_twin, old_good_twin)
                    if save:
                        status_text.set('Method 3v1: saving intermediate results of level ' + str(i - 1) + '...')
                        root.update_idletasks()
                        save_automata_files(i - 1, synchronized=synchronized)
                status_text.set('Method 3v1: synchronizing twins of level ' + str(i) + '...')
                root.update_idletasks()
                synchronized = second_synchronize(synchronized, ambiguous_transitions, new_bad_twin, i)
                if save:
                    status_text.set('Method 3v1: saving intermediate results of level ' + str(i) + '...')
                    root.update_idletasks()
                    save_automata_files(i, synchronized=synchronized)
            last_sync_level = i
            if not first_condition(ambiguous_transitions):
                for src, dst in ambiguous_transitions:
                    if find_loops(dst, set([src])):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def third_method_v2(automaton, level):
    params = read_params()
    save = params['save']
    old_bad_twin = automaton
    i = 1
    synchronized = None
    ambiguous_transitions = None
    while i <= level:
        status_text.set('Method 3v2: generating bad twin of level ' + str(i) + '...')
        root.update_idletasks()
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            status_text.set('Method 3v2: saving intermediate results of level ' + str(i) + '...')
            root.update_idletasks()
            save_automata_files(i, bad_twin=new_bad_twin)
        if i == 1:
            status_text.set('Method 3v2: generating good twin of level ' + str(i) + '...')
            root.update_idletasks()
            good_twin = generate_good_twin(new_bad_twin)
            status_text.set('Method 3v2: synchronizing twins of level ' + str(i) + '...')
            root.update_idletasks()
            synchronized, ambiguous_transitions = first_synchronize(new_bad_twin, good_twin)
            if save:
                status_text.set('Method 3v2: saving intermediate results of level ' + str(i) + '...')
                root.update_idletasks()
                save_automata_files(i, good_twin=good_twin, synchronized=synchronized)
        else:
            status_text.set('Method 3v2: synchronizing twins of level ' + str(i) + '...')
            root.update_idletasks()
            synchronized = second_synchronize(synchronized, ambiguous_transitions, new_bad_twin, i)
            if save:
                status_text.set('Method 3v2: saving intermediate results of level ' + str(i) + '...')
                root.update_idletasks()
                save_automata_files(i, synchronized=synchronized)
        if not (second_condition(new_bad_twin) or third_condition(new_bad_twin) or first_condition(ambiguous_transitions)):
                for src, dst in ambiguous_transitions:
                    if find_loops(dst, set([src])):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def load():
        automaton_file = fileDialog.askopenfilename(title='Choose a file that describes an automaton',
                                                    filetypes=(('XML files', '*.xml'), ('All files', '*.*')),
                                                    initialdir='automata')
        if len(automaton_file) > 0:
            global automaton, canvas, run_menu, status_text, result_label
            if canvas is not None:
                canvas.destroy()
            status_text.set('Loading automaton from file...')
            root.update_idletasks()
            automaton = load_xml(automaton_file)
            run_menu.entryconfig(1, state=ACTIVE)
            status_text.set('Automaton loaded')
            root.update_idletasks()
            result_label['text'] = ''
            save_img(automaton, 'Automaton', 'automaton', 'png')
            image = ImageTk.PhotoImage(Image.open('imgs/automaton.png'))
            if image.width() < root.winfo_width():
                canvas = Canvas(root)
                canvas.pack(expand=YES, fill=BOTH)
                canvas.img = image
                canvas.create_image((root.winfo_width() - image.width()) / 2, 0, image=image, anchor=NW)
            else:
                button = Button(root, text='Display automaton', command=lambda: display_image('automaton.png'))
                button.place(relx=.5, rely=.5)

def generate():
    params = read_params()
    ns = params['ns']
    nt = params['nt']
    ne = params['ne']
    no = params['no']
    nf = params['nf']
    global automaton, canvas, run_menu, status_text, result_label, root
    if canvas is not None:
        canvas.destroy()
    status_text.set('Generating a random automaton...')
    root.update_idletasks()
    automaton = generate_random_automaton(ns, nt, ne, no, nf)
    run_menu.entryconfig(1, state=ACTIVE)
    status_text.set('Automaton generated')
    root.update_idletasks()
    result_label['text'] = ''
    save_img(automaton, 'Random automaton', 'random', 'png')
    save_xml(automaton, 'random')
    image = ImageTk.PhotoImage(Image.open('imgs/random.png'))
    if image.width() < root.winfo_width():
        canvas = Canvas(root)
        canvas.pack(expand=YES, fill=BOTH)
        canvas.img = image
        canvas.create_image((root.winfo_width() - image.width()) / 2, 0, image=image, anchor=NW)
    else:
        button = Button(root, text='Display automaton', command=lambda: display_image('random.png'))
        button.place(relx=.5, rely=.5)

def check_diagnosability_level():
    params = read_params()
    level = params['level']
    method = params['method']
    global status_text, result_label
    result_label['text'] = ''
    def get_text_result(method, result):
        if type(result) is bool:
            result = 'true (' + str(level) + ')'
        return 'Diagnosability level (method ' + str(method) +'): ' + str(result)
    if method == 1:
        result = first_method(automaton, level)
        result_label['text'] = get_text_result(method, result)
    elif method == 2:
        result = second_method(automaton, level)
        result_label['text'] = get_text_result(method, result)
    elif method == '3v1':
        result = third_method_v1(automaton, level)
        result_label['text'] = get_text_result(method, result)
    elif method == '3v2':
        result = third_method_v2(automaton, level)
        result_label['text'] = get_text_result(method, result)
    else:
        result1 = first_method(automaton, level)
        result2 = second_method(automaton, level)
        result3v1 = third_method_v1(automaton, level)
        result3v2 = third_method_v2(automaton, level)
        text_results = list()
        for method, result in zip([1, 2, '3v1', '3v2'], [result1, result2, result3v1, result3v2]):
            text_results.append(get_text_result(method, result))
        result_label['text'] = '\n'.join(text_results)
    status_text.set('Done!')

def edit():
    os.startfile('config.txt', 'open')

def display_image(name):
    def get_script_dir(follow_symlinks=True):
        if getattr(sys, 'frozen', False):
            path = os.path.abspath(sys.executable)
        else:
            path = inspect.getabsfile(get_script_dir)
        if follow_symlinks:
            path = os.path.realpath(path)
        return os.path.dirname(path)
    os.startfile(get_script_dir() + '\\imgs\\' + name, 'open')

root = Tk()
root.attributes('-fullscreen', True)
menu_bar = Menu(root)
automaton_menu = Menu(menu_bar, tearoff=0)
automaton_menu.add_command(label='Load', command=load)
automaton_menu.add_command(label='Generate', command=generate)
automaton_menu.add_separator()
automaton_menu.add_command(label='Quit', command=root.quit)
menu_bar.add_cascade(label='Automaton', menu=automaton_menu)
config_menu = Menu(menu_bar, tearoff=0)
config_menu.add_command(label='Parameters', command=edit)
menu_bar.add_cascade(label='Edit', menu=config_menu)
run_menu = Menu(menu_bar, tearoff=0)
run_menu.add_command(label='Check diagnosability level', command=check_diagnosability_level)
run_menu.entryconfig(1, state=DISABLED)
menu_bar.add_cascade(label='Run', menu=run_menu)
root.config(menu=menu_bar)
status_text = StringVar(value='Ready')
status_bar = Label(root, textvariable=status_text, bd=1, relief=SUNKEN, anchor=W, font=14)
status_bar.pack(side=BOTTOM, fill=X)
result_label = Label(root, anchor=W, font=14)
result_label.pack(side=BOTTOM, fill=X)
root.mainloop()