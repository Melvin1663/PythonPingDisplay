from ctypes import alignment
import threading, time, os, re, sys
import tkinter as tk
import tkinter.ttk as ttk

class setInterval:
    def __init__(self,interval,action):
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()

    def setInterval(self, newInterval):
        self.interval = newInterval

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

app = tk.Tk()
app.geometry("300x150")
app.title('Ping Monitor')

icon = tk.PhotoImage(file=resource_path('icon.png'))
app.iconphoto(True, icon)
app.resizable(False, False)

ping = 0
err = 0
interval = 1
server = 'localhost'
blink = 0
aot = False
clock = None

pingTxt = tk.Label(app, text=str(ping) + " ms", font=("Segoe UI Symbol", 40, 'bold'), justify=tk.CENTER)
pingTxt.pack()

def update_vars(*idk):
    try: 
        global ping
        global interval
        global server
        global clock
        global err
        server = serverInput.get()
        ping = 0
        pingTxt.config(text="-- ms")
        interval = int(intervalInput.get())
        blinker.config(fg="#ff6f00")
        blinkerDesc.config(text='Reconnecting')
        clock.cancel()
        clock = setInterval(interval, execute)
    except Exception as e: print(e)

blinker = tk.Label(app, text='•', font=('arial', 30), fg="#696969")
blinker.place(relx=0.05, y=109)

blinkerDesc = tk.Label(app, text='Initializing')
blinkerDesc.place(relx=0.125, y=124)

okButton = ttk.Button(app, text="OK", command=update_vars)
okButton.place(relx=0.68, rely=0.73)

serverTxt = tk.Label(app, text='Ping')
serverTxt.place(relx=0.05, y=75)

intervalTxt = tk.Label(app, text='Interval                     seconds')
intervalTxt.place(relx=0.05, y=100)

serverInput = ttk.Entry(app, width=31)
serverInput.insert(0, 'localhost')
serverInput.place(relx=0.17, y=75)
serverInput.bind('<Return>', update_vars)

intervalInput = ttk.Spinbox(app, from_=1, to=1000, width=5)
intervalInput.delete(0,"end")
intervalInput.insert(0,1)
intervalInput.place(relx=0.22, y=100)
intervalInput.bind('<Return>', update_vars)

def pinger():
    try:
        response = os.popen('ping -n 1 ' + server).read()
        str = response.split('\n')[2]
        res = re.findall("time(<|=)(\\w+)", str)
        if (res): res = res[0][1]
        global ping
        global clock
        ping = int(res.replace('ms', ''))
        global err
        if err > 0: 
            clock.cancel()
            clock = setInterval(interval, execute)
        err = 0
    except Exception as e: 
        print(e)
        err+=1

def update():
    try:
        global blink
        if err > 2: 
            pingTxt.config(text="-- ms")
            # blinker.config(text='•', fg="#ff0000")
            blinkerDesc.config(text='Lost Connection')
            if blink == 0:
                blink = 1
                blinker.config(text='•', fg="#ff0000")
            elif blink == 1:
                blink = 0
                blinker.config(text='•', fg="#ff5252")
        elif err > 0 or ping == 0:
            pingTxt.config(text=str(ping) + " ms")

            blinkerDesc.config(text='Reconnecting')
            if blink == 0:
                blink = 1
                blinker.config(text='•', fg="#ff872b")
            elif blink == 1:
                blink = 0
                blinker.config(text='•', fg="#ff6f00")
        else: 
            pingTxt.config(text=str(ping) + " ms")
            blinkerDesc.config(text='Established')
            if blink == 0: 
                blink = 1
                blinker.config(text='•', fg="#15cf00")
            elif blink == 1: 
                blink = 0
                blinker.config(text='•', fg="#1aff00")
    except Exception as e: print(e)

def execute():
    try:
        pinger()
        update()
    except Exception as e: print(e)

clock = setInterval(interval,execute)

def copy_ping():
    app.clipboard_clear()
    app.clipboard_append(str(ping) + 'ms')

def copy_server():
    app.clipboard_clear()
    app.clipboard_append(server)

def copy_interval():
    app.clipboard_clear()
    app.clipboard_append(str(interval) + 's')

def toggleAOT():
    global aot
    if aot == False:
        aot = True
        app.attributes('-topmost', True)
        app.title('Ping Monitor (On Top)')
    else:
        aot = False
        app.attributes('-topmost', False)
        app.title('Ping Monitor')

m = tk.Menu(app, tearoff=0)
m.add_command(label="Copy Ping", command=copy_ping)
m.add_command(label="Copy Server IP", command=copy_server)
m.add_command(label="Copy Interval", command=copy_interval)
m.add_separator()
m.add_command(label="On Top", command=toggleAOT)


def do_popup(event):
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()

app.bind('<Button-3>', do_popup)
    
def on_closing():
    clock.cancel()
    app.destroy()

def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

center(app)
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop() #display