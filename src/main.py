from random_automaton import *
from config import *
from Tkinter import *
from PIL import ImageTk, Image
import tkFileDialog as fileDialog
import inspect, multiprocessing, thread
from multiprocessing import Queue


def method1(automaton, level, process_message):
    params = read_params()
    save = params['save']
    compact = params['compact']
    save_source = params['save_source']
    old_bad_twin = automaton
    i = 1
    # global status_bar, status_text, root
    # status_bar.config(fg='blue')
    process_message.put('status_bar.config(fg=\'blue\')')
    while i <= level:
        # status_text.set('Method 1: generating bad twin of level ' + str(i) + '...')
        process_message.put('status_text.set(\'Method 1: generating bad twin of level '+str(i)+'...\')')
        process_message.put('root.update_idletasks()')
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        process_message.put('status_text.set(\'Method 1: generating good twin of level '+str(i)+'...\')')
        process_message.put('root.update_idletasks()')
        good_twin = generate_good_twin(new_bad_twin)
        process_message.put('status_text.set(\'Method 1: synchronizing twins of level '+str(i)+'...\')')
        process_message.put('root.update_idletasks()')
        synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
        if save:
            process_message.put('status_text.set(\'Method 1: saving intermediate results of level '+str(i)+'...\')')
            process_message.put('root.update_idletasks()')
            save_automata_files(i, compact, save_source, new_bad_twin, good_twin, synchronized)
        for src_name, dst_name in ambiguous_transitions:
            states = synchronized.get_states()
            if find_loops(states[dst_name], set([src_name])):
                return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True


def method2(automaton, level, process_message):
    params = read_params()
    save = params['save']
    compact = params['compact']
    save_source = params['save_source']
    old_bad_twin = automaton
    i = 1
    # global status_bar, status_text, root
    # status_bar.config(fg='blue')
    process_message.put('status_bar.config(fg=\'blue\')')
    while i <= level:
        # status_text.set('Method 2: generating bad twin of level ' + str(i) + '...')
        # root.update_idletasks()
        process_message.put('status_text.set(\'Method 2: generating bad twin of level '+str(i)+'...\')')
        process_message.put('root.update_idletasks()')

        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            # status_text.set('Method 2: saving intermediate results of level ' + str(i) + '...')
            # root.update_idletasks()
            process_message.put('status_text.set(\'Method 2: saving intermediate results of level ' + str(i) + '...\')')
            process_message.put('root.update_idletasks()')
            save_automata_files(i, compact, save_source, bad_twin=new_bad_twin)
        if not(condition_C2(new_bad_twin) or condition_C3(new_bad_twin)):
            # status_text.set('Method 2: generating good twin of level ' + str(i) + '...')
            # root.update_idletasks()
            process_message.put('status_text.set(\'Method 2: generating good twin of level ' + str(i) + '...\')')
            process_message.put('root.update_idletasks()')
            good_twin = generate_good_twin(new_bad_twin)
            # status_text.set('Method 2: synchronizing twins of level ' + str(i) + '...')
            # root.update_idletasks()
            process_message.put('status_text.set(\'Method 2: synchronizing twins of level ' + str(i) + '...\')')
            process_message.put('root.update_idletasks()')
            synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
            if save:
                # status_text.set('Method 2: saving intermediate results of level ' + str(i) + '...')
                # root.update_idletasks()
                process_message.put('status_text.set(\'Method 2: saving intermediate results of level ' + str(i) + '...\')')
                process_message.put('root.update_idletasks()')
                save_automata_files(i, compact, save_source, good_twin=good_twin, synchronized=synchronized)
            if not condition_C1(ambiguous_transitions):
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], set([src_name])):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True


def method3_1(automaton, level, process_message):
    params = read_params()
    save = params['save']
    compact = params['compact']
    save_source = params['save_source']
    old_bad_twin = automaton
    i = 1
    global status_bar, status_text, root
    # status_bar.config(fg='blue')
    process_message.put('status_bar.config(fg=\'blue\')')
    first_sync = True
    synchronized = None
    ambiguous_transitions = None
    last_sync_level = 1
    while i <= level:
        # status_text.set('Method 3v1: generating bad twin of level ' + str(i) + '...')
        # root.update_idletasks()
        process_message.put('status_text.set(\'Method 3v1: generating bad twin of level ' + str(i) + '...\')')
        process_message.put('root.update_idletasks()')

        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            # status_text.set('Method 3v1: saving intermediate results of level ' + str(i) + '...')
            # root.update_idletasks()
            process_message.put('status_text.set(\'Method 3v1: saving intermediate results of level ' + str(i) + '...\')')
            process_message.put('root.update_idletasks()')

            save_automata_files(i, compact, save_source, bad_twin=new_bad_twin)
        if not (condition_C2(new_bad_twin) or condition_C3(new_bad_twin)):
            if first_sync:
                # status_text.set('Method 3v1: generating good twin of level ' + str(i) + '...')
                # root.update_idletasks()
                process_message.put(
                    'status_text.set(\'Method 3v1: generating good twin of level ' + str(i) + '...\')')
                process_message.put('root.update_idletasks()')

                good_twin = generate_good_twin(new_bad_twin)
                # status_text.set('Method 3v1: synchronizing twins of level ' + str(i) + '...')
                # root.update_idletasks()
                process_message.put('status_text.set(\'Method 3v1: synchronizing twins of level ' + str(i) + '...\')')
                process_message.put('root.update_idletasks()')

                synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
                first_sync = False
                if save:
                    # status_text.set('Method 3v1: saving intermediate results of level ' + str(i) + '...')
                    # root.update_idletasks()
                    process_message.put('status_text.set(\'Method 3v1: saving intermediate results of level ' + str(i) + '...\')')
                    process_message.put('root.update_idletasks()')

                    save_automata_files(i, compact, save_source, good_twin=good_twin, synchronized=synchronized)
            else:
                if last_sync_level < i - 1:
                    # status_text.set('Method 3v1: generating good twin of level ' + str(i - 1) + '...')
                    # root.update_idletasks()
                    process_message.put('status_text.set(\'Method 3v1: generating good twin of level ' + str(i - 1) + '...\')')
                    process_message.put('root.update_idletasks()')

                    old_good_twin = generate_good_twin(old_bad_twin)
                    # status_text.set('Method 3v1: synchronizing twins of level ' + str(i - 1) + '...')
                    # root.update_idletasks()
                    process_message.put('status_text.set(\'Method 3v1: synchronizing twins of level ' + str(i - 1) + '...\')')
                    process_message.put('root.update_idletasks()')

                    synchronized, ambiguous_transitions = synchronize_1(old_bad_twin, old_good_twin)
                    if save:
                        # status_text.set('Method 3v1: saving intermediate results of level ' + str(i - 1) + '...')
                        # root.update_idletasks()
                        process_message.put(
                            'status_text.set(\'Method 3v1: saving intermediate results of level ' + str(i - 1) + '...\')')
                        process_message.put('root.update_idletasks()')

                        save_automata_files(i - 1, compact, save_source, synchronized=synchronized)
                # status_text.set('Method 3v1: synchronizing twins of level ' + str(i) + '...')
                # root.update_idletasks()
                process_message.put('status_text.set(\'Method 3v1: synchronizing twins of level ' + str(i) + '...\')')
                process_message.put('root.update_idletasks()')

                synchronized = synchronize_2(synchronized, ambiguous_transitions, new_bad_twin, i)
                if save:
                    # status_text.set('Method 3v1: saving intermediate results of level ' + str(i) + '...')
                    # root.update_idletasks()
                    process_message.put('status_text.set(\'Method 3v1: saving intermediate results of level ' + str(i) + '...\')')
                    process_message.put('root.update_idletasks()')

                    save_automata_files(i, compact, save_source, synchronized=synchronized)
            last_sync_level = i
            if not condition_C1(ambiguous_transitions):
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], set([src_name])):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def method3_2(automaton, level, process_message):
    params = read_params()
    save = params['save']
    compact = params['compact']
    save_source = params['save_source']
    old_bad_twin = automaton
    i = 1
    global status_bar, status_text, root
    # status_bar.config(fg='blue')
    process_message.put('status_bar.config(fg=\'blue\')')

    synchronized = None
    ambiguous_transitions = None
    while i <= level:
        # status_text.set('Method 3v2: generating bad twin of level ' + str(i) + '...')
        # root.update_idletasks()
        process_message.put('status_text.set(\'Method 3v2: generating bad twin of level ' + str(i) + '...\')')
        process_message.put('root.update_idletasks()')

        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            # status_text.set('Method 3v2: saving intermediate results of level ' + str(i) + '...')
            # root.update_idletasks()
            process_message.put('status_text.set(\'Method 3v2: saving intermediate results of level ' + str(i) + '...\')')
            process_message.put('root.update_idletasks()')

            save_automata_files(i, compact, save_source, bad_twin=new_bad_twin)
        if i == 1:
            # status_text.set('Method 3v2: generating good twin of level ' + str(i) + '...')
            # root.update_idletasks()
            process_message.put(
                'status_text.set(\'Method 3v2: generating good twin of level ' + str(i) + '...\')')
            process_message.put('root.update_idletasks()')

            good_twin = generate_good_twin(new_bad_twin)
            # status_text.set('Method 3v2: synchronizing twins of level ' + str(i) + '...')
            # root.update_idletasks()
            process_message.put(
                'status_text.set(\'Method 3v2: synchronizing twins of level ' + str(i) + '...\')')
            process_message.put('root.update_idletasks()')

            synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
            if save:
                # status_text.set('Method 3v2: saving intermediate results of level ' + str(i) + '...')
                # root.update_idletasks()
                process_message.put(
                    'status_text.set(\'Method 3v2: saving intermediate results of level ' + str(i) + '...\')')
                process_message.put('root.update_idletasks()')

                save_automata_files(i, compact, save_source, good_twin=good_twin, synchronized=synchronized)
        else:
            # status_text.set('Method 3v2: synchronizing twins of level ' + str(i) + '...')
            # root.update_idletasks()
            process_message.put(
                'status_text.set(\'Method 3v2: synchronizing twins of level ' + str(i) + '...\')')
            process_message.put('root.update_idletasks()')

            synchronized = synchronize_2(synchronized, ambiguous_transitions, new_bad_twin, i)
            if save:
                # status_text.set('Method 3v2: saving intermediate results of level ' + str(i) + '...')
                # root.update_idletasks()
                process_message.put(
                    'status_text.set(\'Method 3v2: saving intermediate results of level ' + str(i) + '...\')')
                process_message.put('root.update_idletasks()')

                save_automata_files(i, compact, save_source, synchronized=synchronized)
        if not (condition_C2(new_bad_twin) or condition_C3(new_bad_twin)):
            if not condition_C1(ambiguous_transitions):
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], set([src_name])):
                        return i - 1
        old_bad_twin = new_bad_twin
        i += 1
    return True

def load():
    automaton_file = fileDialog.askopenfilename(title='Choose a file that describes an automaton',
                                                    filetypes=(('XML files', '*.xml'), ('All files', '*.*')),
                                                    initialdir='automata')
    if len(automaton_file) == 0:
        return
    params = read_params()
    compact = params['compact']
    save_source = params['save_source']
    global automaton, canvas, button, run_menu, status_bar, status_text, result_label
    if canvas is not None:
        canvas.destroy()
    if button is not None:
        button.destroy()
    status_bar.config(fg='blue')
    status_text.set('Loading automaton from file...')
    root.update_idletasks()
    automaton = load_xml(automaton_file)
    if type(automaton) is str:
        run_menu.entryconfig(0, state=DISABLED)
        status_bar.config(fg='red')
        status_text.set(automaton)
        root.update_idletasks()
        result_label['text'] = ''
        return
    run_menu.entryconfig(0, state=NORMAL)
    status_text.set('Automaton loaded')
    result_label['text'] = ''
    root.update_idletasks()
    save_img(automaton, 'Automaton', 'automaton', compact, save_source)
    image = ImageTk.PhotoImage(Image.open('imgs/automaton.png'))
    if image.width() < root.winfo_width() and image.height() < 0.75 * root.winfo_height():
        canvas = Canvas(root)
        canvas.pack(expand=YES, fill=BOTH)
        canvas.img = image
        canvas.create_image((root.winfo_width() - image.width()) / 2, 0, image=image, anchor=NW)
    else:
        button = Button(root, text='Display automaton', command=lambda: display_image('automaton.png'))
        button.place(relx=.5, rely=.5, anchor=CENTER)

def generate():
    params = read_params()
    ns = params['ns']
    nt = params['nt']
    ne = params['ne']
    no = params['no']
    nf = params['nf']
    compact = params['compact']
    save_source = params['save_source']
    global automaton, canvas, button, run_menu, status_text, result_label, root
    if canvas is not None:
        canvas.destroy()
    if button is not None:
        button.destroy()
    status_bar.config(fg='blue')
    status_text.set('Generating a random automaton...')
    root.update_idletasks()
    automaton = generate_random_automaton(ns, nt, ne, no, nf)
    run_menu.entryconfig(0, state=NORMAL)
    status_text.set('Automaton generated')
    root.update_idletasks()
    result_label['text'] = ''
    save_img(automaton, 'Random automaton', 'random', compact, save_source)
    save_xml(automaton, 'random')
    image = ImageTk.PhotoImage(Image.open('imgs/random.png'))
    if image.width() < root.winfo_width() and image.height() < 0.75 * root.winfo_height():
        canvas = Canvas(root)
        canvas.pack(expand=YES, fill=BOTH)
        canvas.img = image
        canvas.create_image((root.winfo_width() - image.width()) / 2, 0, image=image, anchor=NW)
    else:
        button = Button(root, text='Display automaton', command=lambda: display_image('random.png'), font=('', 16))
        button.place(relx=.5, rely=.5, anchor=CENTER)

def check_diagnosability_level(automaton, process_message):
    process_message.put('run_menu.entryconfig(0, state=DISABLED)')
    process_message.put('run_menu.entryconfig(1, state=NORMAL)')
    params = read_params()
    level = params['level']
    method = params['method']
    #global automaton, status_bar, status_text, result_label
    # result_label['text'] = ''
    # process_message.put('result_label[\'text\'] = \'\'')
    def get_text_result(method, result):
        if type(result) is bool:
            result = 'true (' + str(level) + ')'
        return 'Diagnosability level (method ' + str(method) +'): ' + str(result)
    if method == 1:
        result = method1(automaton, level, process_message)
        #result_label['text'] = get_text_result(method, result)
        process_message.put('result_label[\'text\']=\'' + get_text_result(method, result) + '\'')
    elif method == 2:
        result = method2(automaton, level, process_message)
        #result_label['text'] = get_text_result(method, result)
        process_message.put('result_label[\'text\']=\'' + get_text_result(method, result) + '\'')
    elif method == '3v1':
        result = method3_1(automaton, level, process_message)
        #result_label['text'] = get_text_result(method, result)
        process_message.put('result_label[\'text\']=\'' + get_text_result(method, result) + '\'')
    elif method == '3v2':
        result = method3_2(automaton, level, process_message)
        #result_label['text'] = get_text_result(method, result)
        process_message.put('result_label[\'text\']=\'' + get_text_result(method, result) + '\'')
    else:
        result1 = method1(automaton, level, process_message)
        result2 = method2(automaton, level, process_message)
        result3_1 = method3_1(automaton, level, process_message)
        result3_2 = method3_2(automaton, level, process_message)
        text_results = list()
        for method, result in zip([1, 2, '3v1', '3v2'], [result1, result2, result3_1, result3_2]):
            text_results.append(get_text_result(method, result))
        #result_label['text'] = '\n'.join(text_results)
        process_message.put('result_label[\'text\'] = \'' + '\\n'.join(text_results) + '\'')
    #status_bar.config(fg='blue')
    process_message.put('status_bar.config(fg=\'blue\')')
    #status_text.set('Done!')
    process_message.put('status_text.set(\'Done!\')')
    process_message.put('run_menu.entryconfig(0, state=NORMAL)')
    process_message.put('run_menu.entryconfig(1, state=DISABLED)')


def edit():
    os.startfile(CONFIG_FILE_PATH, 'open')

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


def run_command():
    global automaton, p, result_label, process_message
    result_label['text'] = ''
    p = multiprocessing.Process(target=check_diagnosability_level, args=(automaton, process_message))
    p.start()


def stop_command():
    global p, run_menu, status_text, root
    if p:
        p.terminate()
        p.join()
        run_menu.entryconfig(1,state=DISABLED)
        status_text.set('Process stopped by user')
        root.update_idletasks()


def terminate_and_quit():
    global p, root
    if p:
        p.terminate()
        p.join()
    root.quit()


def process_queue(message_queue):
    global status_bar, status_text, result_label
    while True:
        exec message_queue.get()


if __name__ == "__main__":
    automaton = None
    canvas = None
    button = None
    ###
    process_message = Queue()
    p = None
    ###
    root = Tk()
    root.attributes('-fullscreen', True)
    menu_bar = Menu(root)
    automaton_menu = Menu(menu_bar, tearoff=0)
    automaton_menu.add_command(label='Load', command=load)
    automaton_menu.add_command(label='Generate', command=generate)
    automaton_menu.add_separator()
    automaton_menu.add_command(label='Quit', command=lambda: terminate_and_quit())
    menu_bar.add_cascade(label='Automaton', menu=automaton_menu)
    config_menu = Menu(menu_bar, tearoff=0)
    config_menu.add_command(label='Parameters', command=edit)
    menu_bar.add_cascade(label='Edit', menu=config_menu)
    run_menu = Menu(menu_bar, tearoff=0)
    run_menu.add_command(label='Check diagnosability level', command=lambda: run_command())
    run_menu.add_command(label='Stop computation', command=lambda: stop_command())
    run_menu.entryconfig(0, state=DISABLED)
    run_menu.entryconfig(1, state=DISABLED)
    menu_bar.add_cascade(label='Run', menu=run_menu)
    root.config(menu=menu_bar)
    status_text = StringVar(value='Ready')
    status_bar = Label(root, textvariable=status_text, bd=1, relief=SUNKEN, anchor=W, font=('', 16), fg='blue')
    status_bar.pack(side=BOTTOM, fill=X)
    result_label = Label(root, justify=LEFT, anchor=W, font=('', 16))
    result_label.pack(side=BOTTOM, fill=X)
    ###
    thread.start_new_thread(process_queue, (process_message,))
    ###
    root.mainloop()
