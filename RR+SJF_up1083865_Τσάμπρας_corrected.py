# Κωνσταντίνος Τσάμπρας
# +Προσθήκη κώδικα για ενσωμάτωση αλγορίθμου SJF

# Εισαγωγή στους υπολογιστές με τη γλώσσα Python. εκδ.4
# Κεφάλαιο 14 - Παράδειγμα 4
# Το πρόγραμμα αυτό εξομοιώνει τη λειτουργία του αλγόριθμου χρονοπρογραμματισμού
# Round Robin (RR)
# περιγράφει τις μεταγωγές περιβάλλοντος, για πόσο χρόνο θα εκτελείται η κάθε D,
# τον μέσο χρόνο αναμονής και απόκρισης.
# NMA 5/2018 Έκδοση με γραφική διεπαφή (scrollable Canvas, grid geometry)


import tkinter as tk

# symbols
NO = '~'  # σύμβολο για κατάσταση εισόδου
W = 'W'  # σύμβολο για αναμονή (κατάσταση ετοιμότητας)
R = 'R'  # σύμβολο για κατάσταση εκτέλεσης
M = '>'  # σύμβολο για κατάσταση μεταγωγής
scheduler = "RR"
minifont = 'Arial 10'
DEBUG = False


class Process():
    '''κλάση που αναπαριστά τις διεργασίες, σημαντική παράμετρος είναι η self.active.get() που δείχνει ότι η διεργασία είναι ενεργή'''
    d_list = []

    @staticmethod
    def active_processes():
        # έλεγχος αν υπάρχουν ακόμη διεργασίες με end = False
        for d in Process.d_list:
            if not d.end: return True
        return False

    def __init__(self, i, panel):
        self.name = "D{}".format(i + 1)
        # γραφική αναπαράσταση της διεργασίας
        f = tk.LabelFrame(panel, width=100, height=80, text=self.name, padx=2, font=minifont)
        f.grid(row=0, column=i, sticky='w')
        self.active = tk.IntVar()
        self.check = tk.Checkbutton(f, text='ενεργή', variable=self.active, command=self.activate, width=8)
        self.check.grid(column=0, row=0, columnspan=2, sticky="w")
        self.check.deselect()
        tk.Label(f, text="CPU", font=minifont, width=5).grid(column=0, row=1, sticky="w")
        self.cpu_box = tk.IntVar()
        self.cpu_box.set(10)
        self.cpu_entry = tk.Entry(f, textvar=self.cpu_box, width=3, font=minifont, bg='grey60', state='disabled')
        self.cpu_entry.grid(column=1, row=1, sticky="w")
        tk.Label(f, text="Ready", font=minifont, width=5).grid(column=0, row=2, sticky="w")
        self.ready_box = tk.IntVar()
        self.ready_box.set(0)
        self.ready_entry = tk.Entry(f, textvar=self.ready_box, width=3, font=minifont, bg='grey60', state='disabled')
        self.ready_entry.grid(column=1, row=2, sticky="w")
        self.cpu = self.cpu_box.get()
        self.ready = self.ready_box.get()
        self.remain = self.cpu
        self.life = []
        self.end = True
        Process.d_list.append(self)
        self.ready_entry.bind("<KeyRelease>", self.ready_update)
        self.cpu_entry.bind("<KeyRelease>", self.cpu_update)

    def reset(self):
        self.remain = self.cpu
        self.life = []
        self.end = True

    def ready_update(self, event):
        if self.ready_box.get() > 0:
            self.ready = self.ready_box.get()
        else:
            self.ready_box.set(0)

    def cpu_update(self, event):
        if self.cpu_box.get() > 0:
            self.cpu = self.cpu_box.get()
            self.remain = self.cpu
        else:
            self.ready_box.set(0)

    def activate(self):
        if DEBUG: print(self.active.get())
        if self.active.get():  # είναι ενεργή
            self.cpu_entry.config(state='normal')
            self.cpu_entry.config(bg='yellow')
            self.ready_entry.config(state='normal')
            self.ready_entry.config(bg='yellow')
            self.end = False
        else:  # η διεργασία είναι ανενεργή
            self.cpu_entry.config(state='disabled')
            self.cpu_entry.config(bg='grey60')
            self.ready_entry.config(state='disabled')
            self.ready_entry.config(bg='grey60')
            self.end = True

    def new_state(self, state):
        self.life.append(state)
        if state == R: self.remain -= 1
        if self.remain == 0:
            self.end = True
        if DEBUG: print(self.name, self.remain, state, self.end)

    def waiting_time(self):
        waiting = 0
        for x in self.life:
            if x == W: waiting += 1
        return waiting

    def response_time(self):
        response = 0
        for x in self.life:
            if x == W or x == M or x == R: response += 1
        if self.life[-1] == M: response -= 1
        return response


class Waiting_Processes:
    '''βοηθητική κλάση που προσομοιώνει ουρά -χρησιμοποιείται για τις διεργασίες σε κατάσταση αναμονής'''

    def __init__(self):
        self.items = []

    def insert(self, item):
        self.items.insert(0, item)

    def pop(self, item=None):
        if scheduler == "RR":
            return self.items.pop()
        elif scheduler == "SJF":
            if item in self.items:
                self.items.remove(item)
                return item

    def queue(self):
        return self.items


class OS_Scheduler_RR(Process, Waiting_Processes):
    '''η κλάση που προσομοιώνει τη λειτουργία της εκτέλεσης διεργασιών'''

    def __init__(self, quantum, switching, process_list):
        self.quantum = quantum
        self.quantum_left = quantum
        self.switching = switching
        self.switching_left = switching
        self.cpu_process = None
        self.waiting_processes = Waiting_Processes()
        self.switching_processes = []
        self.clock = -1
        self.process_list = [x for x in process_list if x.active.get()]
        if DEBUG: print([(x.name, "life:", x.life, "end:", x.end, "cpu:", x.cpu, "ready:", x.ready, "\n") for x in
                         self.process_list])  # FOR DEBUGGING

    def do_context_switch(self, p_list):
        p = len(p_list)
        if p == 1:
            self.cpu_process = p_list[0]
        else:
            if p_list[0] and not p_list[0].end:
                self.waiting_processes.insert(p_list[0])
            if p_list[1]:
                self.cpu_process = p_list[1]
        self.quantum_left = self.quantum
        self.switching_processes = []

    def start_context_switch(self, p1, p2):
        self.switching_processes = []
        self.switching_processes.extend([p1, p2])

    def define_new_state(self):
        self.clock += 1
        for p in self.process_list:
            if self.clock < p.ready:  # η διεργασία όχι στον κύκλο χρονοπρογραμματισμού
                p.life.append(NO)
            elif self.clock == p.ready:  # η διεργασία μπαίνει στον κύκλο προγραμματισμού
                self.waiting_processes.insert(p)
                if len(self.switching_processes) == 0 and not self.cpu_process:
                    self.switching_processes.append(p)
                    self.waiting_processes.pop()
                    if self.switching == 0:
                        self.do_context_switch([self.cpu_process, p])
                        # η διεργασία είναι σε εκτέλεση
            if p == self.cpu_process:
                if p.end or self.quantum_left == 0:  # τερμάτισε ή τέλος κβάντου χρόνου
                    if len(self.waiting_processes.queue()) > 0:
                        if self.switching == 0:
                            self.do_context_switch([self.cpu_process, self.waiting_processes.pop()])
                        else:
                            self.cpu_process = None
                            self.start_context_switch(p, self.waiting_processes.pop())
                            self.switching_left = self.switching
                    elif not p.end:  # αν δεν έχει τερματίσει, έχει τελειώσει το κβάντο
                        self.quantum_left = self.quantum  # ανανέωση κβάντου χρονου
        # εαν εκετελείται διεργασία μειώνεται κατά 1 το κβάντο χρόνου
        if len(self.switching_processes) > 0:  # μεταγωγή
            if self.switching_left <= 0:
                self.do_context_switch(self.switching_processes)
            self.switching_left -= 1
        if self.cpu_process:
            self.quantum_left -= 1
        # ανανεώνουμε την κατάσταση σε όλες τις μη ολοκληρωμένες εργασίες
        if self.cpu_process and not self.cpu_process.end:
            self.cpu_process.new_state(R)
        for p in self.waiting_processes.queue():
            p.new_state(W)
        for p in self.switching_processes:
            p.new_state(M)


class OS_Scheduler_SJF(Process, Waiting_Processes):

    def __init__(self, quantum, switching, process_list):
        self.quantum = quantum
        self.quantum_left = quantum
        self.switching = switching
        self.switching_left = switching
        self.cpu_process = None
        self.waiting_processes = Waiting_Processes()
        self.switching_processes = []
        self.clock = -1
        self.process_list = [x for x in process_list if x.active.get()]
        if DEBUG: print([(x.name, "life:", x.life, "end:", x.end, "cpu:", x.cpu, "ready:", x.ready, "\n") for x in
                         self.process_list])  # FOR DEBUGGING

    def do_context_switch(self, p_list):
        p = len(p_list)
        if p == 1:
            self.cpu_process = p_list[0]
        else:
            if p_list[0] and not p_list[0].end:
                self.waiting_processes.insert(p_list[0])
            if p_list[1]:
                self.cpu_process = p_list[1]
        self.quantum_left = self.quantum
        self.switching_processes = []

    def start_context_switch(self, p1, p2):
        self.switching_processes = []
        self.switching_processes.extend([p1, p2])

    def define_new_state(self):
        self.clock += 1
        for p in self.process_list:
            if self.clock < p.ready:  # η διεργασία όχι στον κύκλο χρονοπρογραμματισμού
                p.life.append(NO)
            elif self.clock == p.ready:  # η διεργασία μπαίνει στον κύκλο προγραμματισμού
                self.waiting_processes.insert(p)
                if len(self.switching_processes) == 0 and not self.cpu_process:
                    self.min_time = p.remain
                    for x in self.waiting_processes.queue():  # από τις διεργασίες σε ετοιμότητα βρίσκουμε τον μικρότερο χρόνο
                        if x.remain < self.min_time:
                            self.min_time = x.remain
                    if p.remain == self.min_time and len(self.switching_processes) == 0:  # αν η συγκεκριμένη διεργασία
                        self.switching_processes.append(p)  # έχει τον μικρότερο χρόνο εκτελείται
                        self.waiting_processes.pop(p)
                        if self.switching == 0:
                            self.do_context_switch([self.cpu_process, p])
                        # η διεργασία είναι σε εκτέλεση
            if p == self.cpu_process:
                if p.end or self.quantum_left == 0:  # τερμάτισε ή τέλος κβάντου χρόνου
                    if len(self.waiting_processes.queue()) > 0:
                        self.min_time = self.waiting_processes.queue()[0].remain
                        for x in self.waiting_processes.queue():
                            if x.remain < self.min_time:
                                self.min_time = x.remain
                        p1 = None
                        for p1 in self.waiting_processes.queue():  # βρίσκουμε την διεργασία p1 η οποία απαιτεί τον λιγότερο
                            if p1.remain == self.min_time:  # χρόνο από τις διεργασίες που βρίσκονται σε ετοιμότητα
                                break
                        if p.remain > p1.remain or p.remain == 0: # αν η p1 είναι πιο γρήγορη απο την διεργασία η οποία
                            if self.switching == 0: # βρισκόταν σε επεξεργασία μέχρι τώρα, ή αυτή η διεργασία τελείωσε
                                self.do_context_switch([self.cpu_process, self.waiting_processes.pop(p1)])
                            else:                   # τότε η p1 μπαίνει για επεξεργασία
                                self.cpu_process = None
                                self.start_context_switch(p, self.waiting_processes.pop(p1))
                                self.switching_left = self.switching
                    elif not p.end:  # αν δεν έχει τερματίσει, έχει τελειώσει το κβάντο
                        self.quantum_left = self.quantum  # ανανέωση κβάντου χρονου
        # εαν εκετελείται διεργασία μειώνεται κατά 1 το κβάντο χρόνου
        if len(self.switching_processes) > 0:  # μεταγωγή
            if self.switching_left <= 0:
                self.do_context_switch(self.switching_processes)
            self.switching_left -= 1
        if self.cpu_process:
            self.quantum_left -= 1
        # ανανεώνουμε την κατάσταση σε όλες τις μη ολοκληρωμένες εργασίες
        if self.cpu_process and not self.cpu_process.end:
            self.cpu_process.new_state(R)
        for p in self.waiting_processes.queue():
            p.new_state(W)
        for p in self.switching_processes:
            p.new_state(M)


class Control(tk.Button):
    '''Κλάση δημιουργίας των πλήκτρων ελέγχου και βασικών μεθόδων-χειριστηρίων τους'''
    os_scheduler = None
    play = []
    step = 0

    @staticmethod
    def save_play():
        max_time = max([len(x.life) for x in Process.d_list])
        out = ""
        if DEBUG: print('t', end='\t\t')
        out += "t;"
        for p in Process.d_list:
            if DEBUG: print(p.name, end='\t\t')
            out += p.name + ";"  # header
        if DEBUG: print()
        out += "\n"
        for t in range(max_time):
            if DEBUG: print(t, end='\t\t')
            out += str(t) + ";"
            for p in Process.d_list:
                try:
                    if DEBUG: print(p.life[t], end='\t\t')
                    out += p.life[t] + ";"
                except:
                    if DEBUG: print('__', end='\t\t')
                    out += "_;"
            if DEBUG: print()
            out += "\n"
        with open('temp.schedule', 'w', encoding='utf-8') as fout:
            fout.write(out)
        Control.play = out.split("\n")[1:]
        if DEBUG: print(Control.play)

    def __init__(self, img, panel, i, **args):
        if i == 0:
            self.name = "step"
        elif i == 1:
            self.name = "run"
        else:
            self.name = "stop"
        self.img = img
        tk.Button.__init__(self, panel, image=img, command=self.run, **args)
        self.grid(row=0, column=i, sticky='wens')

    def run(self):
        if not len([x for x in Process.d_list if x.active.get()]): return  # αν δεν υπάρχουν ενεργές διεργασίες
        if self.name == 'stop':
            main.canvas.delete("all")
            main.results_box.delete('1.0', 'end')
            Control.os_scheduler = None
            Control.play = []
            Control.step = 0
            for p in Process.d_list:
                p.active.set(0)
                p.activate()
                p.reset()
        else:
            if not Control.os_scheduler:
                # create processes and check if conditions apply
                # ελέγχουμε ποιο scheduler έχει επιλεχθεί και καλούμε την ανάλογη κλάση
                if scheduler == "RR":
                    Control.os_scheduler = OS_Scheduler_RR(main.quantum.get(), main.switching.get(), Process.d_list)
                elif scheduler == "SJF":
                    Control.os_scheduler = OS_Scheduler_SJF(main.quantum.get(), main.switching.get(), Process.d_list)
                while True:
                    Control.os_scheduler.define_new_state()
                    if not Process.active_processes(): break
                # αποθήκευσε την εκτέλεση των διεργασιών σε αρχείο temp.schedule
                Control.save_play()
                # υπολογισμός μέσου χρόνου αναμονής
                if len(Control.os_scheduler.process_list):
                    waiting = 0
                    for x in Control.os_scheduler.process_list:
                        waiting += x.waiting_time()
                    waiting = waiting / len(Control.os_scheduler.process_list)
                    print("Μέσος χρόνος \nαναμονής = %.2f" % waiting)
                    out = "Μέσος χρόνος \nαναμονής = %.2f\n" % waiting
                    # υπολογισμός μέσου χρόνου απόκρισης
                    response = 0
                    for x in Control.os_scheduler.process_list:
                        response += x.response_time()
                    response = response / len(Control.os_scheduler.process_list)
                    print("Μέσος χρόνος \nαπόκρισης = %.2f\n" % response)
                    out += "Μέσος χρόνος \nαπόκρισης = %.2f\n" % response
                    print("Σύνολο βημάτων {}".format(max([len(x.life) for x in Process.d_list])))
                    out += "Σύνολο βημάτων {}\n".format(max([len(x.life) for x in Process.d_list]))
                    main.results_box.delete('1.0', 'end')
                    main.results_box.insert('end', out)

            if self.name == "step":
                try:
                    if DEBUG: print(Control.play[Control.step])
                    self.display_step(Control.play[Control.step])
                    Control.step += 1
                except:
                    print('end of steps')
            else:
                try:
                    for step in Control.play[Control.step:]:
                        if DEBUG: print(step)
                        self.display_step(step)
                    Control.step = len(Control.play)
                except:
                    print('end of steps')

    def display_step(self, pattern):
        if DEBUG: print("pattern=", pattern)
        if pattern:
            step = int(pattern.split(";")[0])
            states = pattern.split(";")[1:-1]
            size_x, size_y = 80, 20
            for k, state in enumerate(states):
                x, y = 4 + k * (size_x + 4), step * size_y + 5
                if state != "_" or not state:
                    sq = main.canvas.create_rectangle(x, y, x + size_x, y + size_y)
                    if state == "R":
                        main.canvas.itemconfig(sq, fill="red")
                    elif state == "W":
                        main.canvas.itemconfig(sq, fil="grey80")
                    elif state == ">":
                        main.canvas.itemconfig(sq, fil="yellow")
                    elif state == "~":
                        main.canvas.itemconfig(sq, fill="white")
                    if state in "R>": main.canvas.create_text(x + 5, y + 5, text=str(step + 1), font="Arial 12",
                                                              anchor="nw")
            main.canvas.config(
                scrollregion=main.canvas.bbox("all"))  # όρισε όλα τα αντικείμενα να είναι στην περιοχή κύλησης
            main.canvas.yview_moveto(1)  # μετακίνησε τη μπάρα κύλησης στο τέλος


class Main():
    '''η αρχική κλάση που δημιουργεί το γραφικό περιβάλλον'''

    def __init__(self, root):
        # Σχεδίαση της επιφάνειας εργασίας με
        self.root = root
        self.root.geometry('1090x780+10+10')
        self.root.resizable(False, False)
        # πάνελ των διεργασιών
        self.process_panel = tk.LabelFrame(self.root, text='Διεργασίες')
        self.process_panel.grid(row=0, column=0, sticky='wens', padx=5)
        # πάνελ των χαρακτηριστικών του λειτουργικού συστήματος
        self.os_panel = tk.LabelFrame(self.root, text='Λειτουργικό Σύστημα', bg='lightblue')
        self.os_panel.grid(row=0, column=1, sticky='wens')
        tk.Label(self.os_panel, text="Quantum", bg='lightblue').grid(column=0, row=1, sticky="w")
        self.quantum = tk.IntVar()
        self.quantum.set(5)
        tk.Entry(self.os_panel, textvar=self.quantum, width=3).grid(column=1, row=1, sticky="w")
        tk.Label(self.os_panel, text="Context \nswitch", bg='lightblue').grid(column=0, row=2, sticky="w")
        self.switching = tk.IntVar()
        self.os_procedure = None
        tk.Entry(self.os_panel, textvar=self.switching, width=3).grid(column=1, row=2, sticky="ew")
        self.switching.set(0)
        # κουμπιά επιλογής scheduler
        self.os_button1 = tk.Button(self.os_panel, text="Round Robin", height=1, width=9, bg='lightblue',
                                    command=lambda: self.set_os_scheduler("RR"))
        self.os_button1.grid(column=0, row=3, sticky="nw")
        self.os_button2 = tk.Button(self.os_panel, text="SJF", height=1, width=2, bg='lightblue',
                                    command=lambda: self.set_os_scheduler("SJF"))
        self.os_button2.grid(column=1, row=3, sticky="nw")
        # πάνελ της περιγραφής διεργασιών
        self.run_panel = tk.LabelFrame(self.root, text='Κατάσταση διεργασιών')
        self.run_panel.grid(row=1, column=0, rowspan=10, sticky='wens', padx=5)
        self.canvas = tk.Canvas(self.run_panel, width=850, height=650, bg='lightgreen')
        self.canvas.grid(row=0, column=0, sticky='wens')
        self.scroll = tk.Scrollbar(self.run_panel, orient='vertical', command=self.canvas.yview)
        self.scroll.grid(row=0, column=1, sticky='ns')
        self.canvas.config(yscrollcommand=self.scroll.set)
        self.results_panel = tk.LabelFrame(self.root, text='Αποτελέσματα')
        # πάνελ των πλήκτρων ελέγχου (step, run, reset)
        self.controls = tk.LabelFrame(self.root, text='Εκτέλεση')
        self.controls.grid(row=1, column=1, sticky='we')
        self.buttons = [tk.PhotoImage(file='step.gif'), tk.PhotoImage(file='run.gif'), tk.PhotoImage(file='reset.gif')]
        for i, b in enumerate(self.buttons):
            Control(b, self.controls, i, bg="white")
        # πάνελ αποτελεσμάτων
        self.results_panel.grid(row=2, column=1, rowspan=9, sticky='wens')
        self.results_box = tk.Text(self.results_panel, height=50, width=20, bg='lightyellow')
        self.results_box.grid(row=0, column=0, sticky='wens')
        # δημιουργία των αντικειμένων τύπου Process
        for i in range(10):
            Process(i, self.process_panel)

    def set_os_scheduler(self, os_scheduler):
        global scheduler
        scheduler = os_scheduler
        # self.os_button1.grid_forget()
        # self.os_button2.grid_forget()


if __name__ == '__main__':
    root = tk.Tk()
    main = Main(root)
    root.mainloop()
