from random_automaton import *
import log
from Tkinter import *
from PIL import ImageTk, Image
import tkFileDialog as fileDialog
import inspect, multiprocessing, thread
from multiprocessing import Queue
import datetime

def send_message(process_message, _type, msg=None):
    if _type == log.TYPE_METH_SEP:
        process_message.put('report.append(\'' + log.METH_SEP + '\')')
    if _type == log.TYPE_COLOR_CHANGE:
        process_message.put('status_bar.config(fg=\'' + msg + '\')')
        process_message.put('root.update_idletasks()')
    if _type == log.TYPE_MSG_TWIN:
        process_message.put('report.append(\'' + msg + '\')')
        process_message.put('status_text.set(\'' + msg + '\')')
        process_message.put('root.update_idletasks()')
    if _type == log.TYPE_MSG_RES:
        process_message.put('status_text.set(\'' + msg + '\')')
        process_message.put('root.update_idletasks()')
    if _type == log.TYPE_LEV_SAT:
        process_message.put('report.append(\'' + msg + '\')')
        process_message.put('report.append(\'' + log.LEV_SEP + '\')')
    if _type == log.TYPE_PARAMS_ERROR:
        process_message.put('run_menu.entryconfig(0, state=NORMAL)')
        process_message.put('run_menu.entryconfig(1, state=DISABLED)')
        process_message.put('status_bar.config(fg=\'red\')')
        process_message.put('status_text.set(params)')
        process_message.put('root.update_idletasks()')
    if _type == log.TYPE_FINISH:
        process_message.put('result_label[\'text\'] = \'' + msg + '\'')
        process_message.put('status_bar.config(fg=\'blue\')')
        process_message.put('status_text.set(\'Done!\')')
        process_message.put('automaton_menu.entryconfig(0, state=NORMAL)')
        process_message.put('automaton_menu.entryconfig(1, state=NORMAL)')
        process_message.put('automaton_menu.entryconfig(2, state=NORMAL)')
        process_message.put('run_menu.entryconfig(0, state=NORMAL)')
        process_message.put('run_menu.entryconfig(1, state=DISABLED)')
    if _type == log.TYPE_END_LEV:
        process_message.put('report.append(\'' + msg[0] + '\')')
        process_message.put('report.append(\'' + log.END_LEV_SEP + '\')')
        process_message.put('report.append(\'' + msg[1] + '\')')
        process_message.put('report.append(\'' + log.END_LEV_SEP + '\')')

def method1(automaton, params, process_message):
    send_message(process_message, log.TYPE_METH_SEP)
    level = params['level']
    save = to_bool(params['save'])
    compact = to_bool(params['compact'])
    old_bad_twin = automaton
    i = 1
    send_message(process_message, log.TYPE_COLOR_CHANGE, 'blue')
    while i <= level:
        msg_bt = log.MSG_BT %('1', i)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_bt)
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        msg_gt = log.MSG_GT % ('1', i)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_gt)
        good_twin = generate_good_twin(new_bad_twin)
        msg_sync = log.MSG_SYNC % ('1', i)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_sync)
        synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
        if save:
            msg_res = log.MSG_RES % ('1', i)
            send_message(process_message, log.TYPE_MSG_RES, msg_res)
            save_automata_files(i, compact, new_bad_twin, good_twin, synchronized)
        for src_name, dst_name in ambiguous_transitions:
            states = synchronized.get_states()
            if find_loops(states[dst_name], {src_name}):
                msg_lev_sat = log.MSG_LEV_SAT %('1', i, ' not ')
                msg_max_lev = log.MSG_MAX_LEV %('1', i - 1)
                send_message(process_message, log.TYPE_END_LEV, (msg_lev_sat, msg_max_lev))
                return i - 1
        old_bad_twin = new_bad_twin
        msg_lev_sat = log.MSG_LEV_SAT % ('1', i, ' ')
        send_message(process_message, log.TYPE_LEV_SAT, msg_lev_sat)
        i += 1
    msg_true_lev = log.MSG_TRUE_LEV %('1', level)
    send_message(process_message, log.TYPE_LEV_SAT, msg_true_lev)
    return True

def method2(automaton, params, process_message):
    send_message(process_message, log.TYPE_METH_SEP)
    level = params['level']
    save = to_bool(params['save'])
    compact = to_bool(params['compact'])
    old_bad_twin = automaton
    i = 1
    send_message(process_message, log.TYPE_COLOR_CHANGE, 'blue')
    while i <= level:
        msg_bt = log.MSG_BT % ('2', i)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_bt)
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            msg_res = log.MSG_RES % ('2', i)
            send_message(process_message, log.TYPE_MSG_RES, msg_res)
            save_automata_files(i, compact, bad_twin=new_bad_twin)
        msg_cond_ver = log.MSG_COND_VER % ('2', i, 2)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
        c2 = condition_C2(new_bad_twin)
        msg_cond_sat = log.MSG_COND_SAT % ('2', i, 2, ' not ' if not c2 else ' ')
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
        msg_cond_ver = log.MSG_COND_VER % ('2', 3, i)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
        c3 = condition_C3(new_bad_twin)
        msg_cond_sat = log.MSG_COND_SAT % ('2', i, 3, ' not ' if not c3 else ' ')
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
        if not(c2 or c3):
            msg_gt = log.MSG_GT % ('2', i)
            send_message(process_message, log.TYPE_MSG_TWIN, msg_gt)
            good_twin = generate_good_twin(new_bad_twin)
            msg_sync = log.MSG_SYNC % ('2', i)
            send_message(process_message, log.TYPE_MSG_TWIN, msg_sync)
            synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
            if save:
                msg_res = log.MSG_RES % ('2', i)
                send_message(process_message, log.TYPE_MSG_TWIN, msg_res)
                save_automata_files(i, compact, good_twin=good_twin, synchronized=synchronized)
            msg_cond_ver = log.MSG_COND_VER % ('2', i, 1)
            send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
            c1 = condition_C1(ambiguous_transitions)
            msg_cond_sat = log.MSG_COND_SAT % ('2', i, 1, ' not ' if not c1 else ' ')
            send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
            if not c1:
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], {src_name}):
                        msg_lev_sat = log.MSG_LEV_SAT % ('2', i, ' not ')
                        msg_max_lev = log.MSG_MAX_LEV % ('2', i - 1)
                        send_message(process_message, log.TYPE_END_LEV, (msg_lev_sat, msg_max_lev))
                        return i - 1
        old_bad_twin = new_bad_twin
        msg_lev_sat = log.MSG_LEV_SAT % ('2', i, ' ')
        send_message(process_message, log.TYPE_LEV_SAT, msg_lev_sat)
        i += 1
    msg_true_lev = log.MSG_TRUE_LEV % ('2', level)
    send_message(process_message, log.TYPE_LEV_SAT, msg_true_lev)
    return True

def method3_1(automaton, params, process_message):
    send_message(process_message, log.TYPE_METH_SEP)
    level = params['level']
    save = to_bool(params['save'])
    compact = to_bool(params['compact'])
    old_bad_twin = automaton
    i = 1
    send_message(process_message, log.TYPE_COLOR_CHANGE, 'blue')
    first_sync = True
    synchronized = None
    ambiguous_transitions = None
    last_sync_level = 1
    while i <= level:
        msg_bt = log.MSG_BT % ('3v1', i)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_bt)
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            msg_res = log.MSG_RES % ('3v1', i)
            send_message(process_message, log.TYPE_MSG_RES, msg_res)
            save_automata_files(i, compact, bad_twin=new_bad_twin)
        msg_cond_ver = log.MSG_COND_VER % ('3v1', i, 2)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
        c2 = condition_C2(new_bad_twin)
        msg_cond_sat = log.MSG_COND_SAT % ('3v1', i, 2, ' not ' if not c2 else ' ')
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
        msg_cond_ver = log.MSG_COND_VER % ('3v1', i, 3)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
        c3 = condition_C3(new_bad_twin)
        msg_cond_sat = log.MSG_COND_SAT % ('3v1', i, 3, ' not ' if not c3 else ' ')
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
        if not(c2 or c3):
            if first_sync:
                msg_gt = log.MSG_GT % ('3v1', i)
                send_message(process_message, log.TYPE_MSG_TWIN, msg_gt)
                good_twin = generate_good_twin(new_bad_twin)
                msg_sync = log.MSG_SYNC % ('3v1', i)
                send_message(process_message, log.TYPE_MSG_TWIN, msg_sync)
                synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
                first_sync = False
                if save:
                    msg_res = log.MSG_RES % ('3v1', i)
                    send_message(process_message, log.TYPE_MSG_RES, msg_res)
                    save_automata_files(i, compact, good_twin=good_twin, synchronized=synchronized)
            else:
                if last_sync_level < i - 1:
                    msg_gt = log.MSG_GT % ('3v1', i - 1)
                    send_message(process_message, log.TYPE_MSG_TWIN, msg_gt)
                    old_good_twin = generate_good_twin(old_bad_twin)
                    msg_sync = log.MSG_SYNC % ('3v1', i - 1)
                    send_message(process_message, log.TYPE_MSG_TWIN, msg_sync)
                    synchronized, ambiguous_transitions = synchronize_1(old_bad_twin, old_good_twin)
                    if save:
                        msg_res = log.MSG_RES % ('3v1', i)
                        send_message(process_message, log.TYPE_MSG_RES, msg_res)
                        save_automata_files(i - 1, compact, synchronized=synchronized)
                msg_sync = log.MSG_SYNC % ('3v1', i)
                send_message(process_message, log.TYPE_MSG_TWIN, msg_sync)
                synchronized = synchronize_2(synchronized, ambiguous_transitions, new_bad_twin, i)
                if save:
                    msg_res = log.MSG_RES % ('3v1', i)
                    send_message(process_message, log.TYPE_MSG_RES, msg_res)
                    save_automata_files(i, compact, synchronized=synchronized)
            last_sync_level = i
            msg_cond_ver = log.MSG_COND_VER % ('3v1', i, 1)
            send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
            c1 = condition_C1(ambiguous_transitions)
            msg_cond_sat = log.MSG_COND_SAT % ('3v1', i, 1, ' not ' if not c1 else ' ')
            send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
            if not c1:
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], {src_name}):
                        msg_lev_sat = log.MSG_LEV_SAT % ('3v1', i, ' not ')
                        msg_max_lev = log.MSG_MAX_LEV % ('3v1', i - 1)
                        send_message(process_message, log.TYPE_END_LEV, (msg_lev_sat, msg_max_lev))
                        return i - 1
        old_bad_twin = new_bad_twin
        msg_lev_sat = log.MSG_LEV_SAT % ('3v1', i, ' ')
        send_message(process_message, log.TYPE_LEV_SAT, msg_lev_sat)
        i += 1
    msg_true_lev = log.MSG_TRUE_LEV % ('3v1', level)
    send_message(process_message, log.TYPE_LEV_SAT, msg_true_lev)
    return True

def method3_2(automaton, params, process_message):
    send_message(process_message, log.TYPE_METH_SEP)
    level = params['level']
    save = to_bool(params['save'])
    compact = to_bool(params['compact'])
    old_bad_twin = automaton
    i = 1
    send_message(process_message, log.TYPE_COLOR_CHANGE, 'blue')
    synchronized = None
    ambiguous_transitions = None
    while i <= level:
        msg_bt = log.MSG_BT % ('3v2', i)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_bt)
        new_bad_twin = generate_bad_twin(old_bad_twin, i)
        if save:
            msg_res = log.MSG_RES % ('3v2', i)
            send_message(process_message, log.TYPE_MSG_RES, msg_res)
            save_automata_files(i, compact, bad_twin=new_bad_twin)
        if i == 1:
            msg_gt = log.MSG_GT % ('3v2', i)
            send_message(process_message, log.TYPE_MSG_TWIN, msg_gt)
            good_twin = generate_good_twin(new_bad_twin)
            msg_sync = log.MSG_SYNC % ('3v2', i)
            send_message(process_message, log.TYPE_MSG_TWIN, msg_sync)
            synchronized, ambiguous_transitions = synchronize_1(new_bad_twin, good_twin)
            if save:
                msg_res = log.MSG_RES % ('3v2', i)
                send_message(process_message, log.TYPE_MSG_RES, msg_res)
                save_automata_files(i, compact, good_twin=good_twin, synchronized=synchronized)
        else:
            msg_sync = log.MSG_SYNC % ('3v2', i)
            send_message(process_message, log.TYPE_MSG_TWIN, msg_sync)
            synchronized = synchronize_2(synchronized, ambiguous_transitions, new_bad_twin, i)
            if save:
                msg_res = log.MSG_RES % ('3v2', i)
                send_message(process_message, log.TYPE_MSG_RES, msg_res)
                save_automata_files(i, compact, synchronized=synchronized)
        msg_cond_ver = log.MSG_COND_VER % ('3v2', i, 2)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
        c2 = condition_C2(new_bad_twin)
        msg_cond_sat = log.MSG_COND_SAT % ('3v2', i, 2, ' not ' if not c2 else ' ')
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
        msg_cond_ver = log.MSG_COND_VER % ('3v2', i, 3)
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
        c3 = condition_C3(new_bad_twin)
        msg_cond_sat = log.MSG_COND_SAT % ('3v2', i, 3, ' not ' if not c3 else ' ')
        send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
        if not(c2 or c3):
            msg_cond_ver = log.MSG_COND_VER % ('3v2', i, 1)
            send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_ver)
            c1 = condition_C1(ambiguous_transitions)
            msg_cond_sat = log.MSG_COND_SAT % ('3v2', i, 1, ' not ' if not c1 else ' ')
            send_message(process_message, log.TYPE_MSG_TWIN, msg_cond_sat)
            if not c1:
                for src_name, dst_name in ambiguous_transitions:
                    states = synchronized.get_states()
                    if find_loops(states[dst_name], {src_name}):
                        msg_lev_sat = log.MSG_LEV_SAT % ('3v2', i, ' not ')
                        msg_max_lev = log.MSG_MAX_LEV % ('3v2', i - 1)
                        send_message(process_message, log.TYPE_END_LEV, (msg_lev_sat, msg_max_lev))
                        return i - 1
        old_bad_twin = new_bad_twin
        msg_lev_sat = log.MSG_LEV_SAT % ('3v2', i, ' ')
        send_message(process_message, log.TYPE_LEV_SAT, msg_lev_sat)
        i += 1
    msg_true_lev = log.MSG_TRUE_LEV % ('3v2', level)
    send_message(process_message, log.TYPE_LEV_SAT, msg_true_lev)
    return True

def load():
    automaton_file = fileDialog.askopenfilename(title='Choose a file that describes an automaton',
                                                filetypes=(('XML files', '*.xml'), ('All files', '*.*')))
    if len(automaton_file) == 0:
        return
    global automaton, canvas, button, automaton_menu, run_menu, status_bar, status_text, result_label
    params = read_params()
    automaton_menu.entryconfig(2, state=DISABLED)
    if type(params) is str:
        automaton_menu.entryconfig(0, state=NORMAL)
        automaton_menu.entryconfig(1, state=NORMAL)
        run_menu.entryconfig(0, state=DISABLED)
        status_bar.config(fg='red')
        status_text.set(params)
        root.update_idletasks()
        result_label['text'] = ''
        return
    compact = to_bool(params['compact'])
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
    save_img(automaton, 'automaton', compact)
    image = ImageTk.PhotoImage(Image.open('temp/imgs/automaton.png'))
    if image.width() < root.winfo_width() and image.height() < 0.75 * root.winfo_height():
        canvas = Canvas(root)
        canvas.configure(background='white')
        canvas.pack(expand=YES, fill=BOTH)
        canvas.img = image
        canvas.create_image((root.winfo_width() - image.width()) / 2, 0, image=image, anchor=NW)
    else:
        button = Button(root, text='Display automaton', command=lambda: display_image('automaton.png'))
        button.place(relx=.5, rely=.5, anchor=CENTER)

def generate():
    global automaton, canvas, button, automaton_menu, run_menu, status_text, result_label, root
    params = read_params()
    automaton_menu.entryconfig(2, state=DISABLED)
    if type(params) is str:
        automaton_menu.entryconfig(0, state=DISABLED)
        automaton_menu.entryconfig(1, state=DISABLED)
        run_menu.entryconfig(0, state=DISABLED)
        status_bar.config(fg='red')
        status_text.set(params)
        root.update_idletasks()
        result_label['text'] = ''
        return
    ns = params['ns']
    nt = params['nt']
    no = params['no']
    ne = params['ne']
    nf = params['nf']
    compact = to_bool(params['compact'])
    if canvas is not None:
        canvas.destroy()
    if button is not None:
        button.destroy()
    status_bar.config(fg='blue')
    status_text.set('Generating a random automaton...')
    root.update_idletasks()
    automaton = generate_random_automaton(ns, nt, no, ne, nf)
    if type(automaton) is str:
        run_menu.entryconfig(0, state=DISABLED)
        status_bar.config(fg='red')
        status_text.set(automaton)
        root.update_idletasks()
        result_label['text'] = ''
        return
    run_menu.entryconfig(0, state=NORMAL)
    status_text.set('Automaton generated')
    root.update_idletasks()
    result_label['text'] = ''
    save_img(automaton, 'random', compact)
    save_xml(automaton, 'random')
    image = ImageTk.PhotoImage(Image.open('temp/imgs/random.png'))
    if image.width() < root.winfo_width() and image.height() < 0.75 * root.winfo_height():
        canvas = Canvas(root)
        canvas.configure(background='white')
        canvas.pack(expand=YES, fill=BOTH)
        canvas.img = image
        canvas.create_image((root.winfo_width() - image.width()) / 2, 0, image=image, anchor=NW)
    else:
        button = Button(root, text='Display automaton', command=lambda: display_image('random.png'), font=('', 16))
        button.place(relx=.5, rely=.5, anchor=CENTER)

def save_report():
    global report, automaton_menu, status_text
    filename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
    save_file('reports/' + filename, '\n'.join(report))
    status_text.set('Report successfully saved!')
    automaton_menu.entryconfig(2, state=DISABLED)

def check_diagnosability_level(automaton, process_message):
    params = read_params()
    if type(params) is str:
        send_message(process_message, log.TYPE_PARAMS_ERROR)
        return
    level = params['level']
    method = params['method']
    def get_text_result(method, result):
        if type(result) is bool:
            result = 'true (' + str(level) + ')'
        return log.MSG_MAX_LEV %(method, result)
    methods = method
    if method == '1':
        invoke_methods = [method1]
    elif method == '2':
        invoke_methods = [method2]
    elif method == '3v1':
        invoke_methods = [method3_1]
    elif method == '3v2':
        invoke_methods = [method3_2]
    else:
        methods = [m for m in PARAMS['method']['values'] if m != 'all']
        invoke_methods = [method1, method2, method3_1, method3_2]
    results = [m(automaton, params, process_message) for m in invoke_methods]
    text_results = list()
    for method, result in zip(methods, results):
        text_results.append(get_text_result(method, result))
    send_message(process_message, log.TYPE_FINISH, '\\n'.join(text_results))

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
    os.startfile(get_script_dir() + '\\temp\\imgs\\' + name, 'open')

def run_command():
    global automaton, p, result_label, process_message, automaton_menu, run_menu, report
    result_label['text'] = ''
    report = list()
    p = multiprocessing.Process(target=check_diagnosability_level, args=(automaton, process_message))
    automaton_menu.entryconfig(0, state=DISABLED)
    automaton_menu.entryconfig(1, state=DISABLED)
    run_menu.entryconfig(0, state=DISABLED)
    run_menu.entryconfig(1, state=NORMAL)
    p.start()

def stop_command():
    global p, automaton_menu, run_menu, status_text, root
    if p:
        p.terminate()
        p.join()
        automaton_menu.entryconfig(0, state=NORMAL)
        automaton_menu.entryconfig(1, state=NORMAL)
        run_menu.entryconfig(0, state=NORMAL)
        run_menu.entryconfig(1, state=DISABLED)
        status_text.set('Stopped!')
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

if __name__ == '__main__':
    automaton = None
    canvas = None
    button = None
    report = list()
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
    automaton_menu.add_command(label='Save report...', command=save_report)
    automaton_menu.entryconfig(2, state=DISABLED)
    automaton_menu.add_separator()
    automaton_menu.add_command(label='Quit', command=terminate_and_quit)
    menu_bar.add_cascade(label='Automaton', menu=automaton_menu)
    config_menu = Menu(menu_bar, tearoff=0)
    config_menu.add_command(label='Parameters', command=edit)
    menu_bar.add_cascade(label='Edit', menu=config_menu)
    run_menu = Menu(menu_bar, tearoff=0)
    run_menu.add_command(label='Check diagnosability level', command=run_command)
    run_menu.add_command(label='Stop computation', command=stop_command)
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
