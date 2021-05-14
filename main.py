import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from serial import Serial
from serial.tools.list_ports import comports
from PIL import Image, ImageTk
import threading
import json
import dependencies.db as db

class App(threading.Thread):
    comboBox = None
    infoLabel = None
    button = None
    ser = Serial()
    ser.baudrate = 115200

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        # setting title
        self.root.title("CAPIZ STATE UNIVERSITY")
        # setting window size
        width = 400
        height = 300
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

        logo = Image.open("capsu-logo.png")
        test = ImageTk.PhotoImage(logo)
        label1 = tk.Label(image=test)
        label1.image = test
        label1.place(x=30, y=20)

        GLabel_964 = tk.Label(self.root)
        ft = tkFont.Font(family='Times', size=16)
        GLabel_964["font"] = ft
        GLabel_964["fg"] = "#333333"
        GLabel_964["justify"] = "center"
        GLabel_964["text"] = "RFID VEHICLE GATE PASS"
        GLabel_964.place(x=114, y=35, width=250, height=34)

        GLabel_50 = tk.Label(self.root)
        ft = tkFont.Font(family='Times', size=10)
        GLabel_50["font"] = ft
        GLabel_50["fg"] = "#333333"
        GLabel_50["justify"] = "center"
        GLabel_50["text"] = "Select port:"
        GLabel_50.place(x=30, y=110, width=70, height=25)

        App.comboBox = ttk.Combobox(self.root)
        ft = tkFont.Font(family='Times', size=10)
        App.comboBox["font"] = ft
        App.comboBox["justify"] = "left"
        App.comboBox.place(x=30, y=140, width=146, height=30)
        ports = [port.name for port in comports()]
        App.comboBox['values'] = ports
        App.comboBox['state'] = 'readonly'
        App.comboBox.bind('<<ComboboxSelected>>', self.port_changed)

        App.button = tk.Button(self.root)
        App.button["activebackground"] = "#11ba44"
        App.button["activeforeground"] = "#ffffff"
        App.button["bg"] = "#cccccc"
        ft = tkFont.Font(family='Times', size=10)
        App.button["font"] = ft
        App.button["fg"] = "#ffffff"
        App.button["justify"] = "center"
        App.button["text"] = "Connect"
        App.button.place(x=210, y=120, width=160, height=51)
        App.button["command"] = self.connect_disconnect
        App.button['state'] = 'disable'

        App.infoLabel = tk.Label(self.root)
        ft = tkFont.Font(family='Times', size=12)
        App.infoLabel["font"] = ft
        App.infoLabel["fg"] = "#000000"
        App.infoLabel["justify"] = "center"
        App.infoLabel["text"] = "Select port to connect"
        App.infoLabel.place(x=30, y=220, width=341, height=30)

        # Check db credentials from .env file
        if not db.db_status:
            App.comboBox["state"] = "disable"
            App.infoLabel["fg"] = "#ff0000"
            App.infoLabel["text"] = "Database error. Please run again."
        else:
            print("System started")

        self.root.mainloop()

    def connect_disconnect(self):
        if not App.ser.is_open:
            App.ser.port = App.comboBox.get()
            App.button['text'] = 'Disconnect'
            App.button['bg'] = '#fb4545'
            App.infoLabel['text'] = 'Connected at port: ' + App.ser.port + '. Baud rate: ' + str(App.ser.baudrate)
            App.comboBox['state'] = 'disable'
            App.ser.open()

        else:
            App.ser.close()
            App.button['text'] = 'Connect'
            App.button['bg'] = '#1cd751'
            App.infoLabel['text'] = 'Disconnected. Select port to connect.'
            App.comboBox['state'] = 'readonly'


    def port_changed(self, event):
        App.button['state'] = 'normal'
        App.button['bg'] = "#1cd751"


def read_serial():
    try:
        msg = App.ser.readline()
        if len(msg):
            # Replace chars to make a JSON
            data = json.loads(msg.decode("utf-8").replace("'", '"').replace(" ", ""))
            try:
                driver_registered = db.check_driver(data['uid'], data['reader'])
                if driver_registered:
                    app.ser.write(data["reader"].encode())

            except:
                print('Database error. Please run again.')
                app.ser.close()
                app.comboBox["state"] = "disable"
                app.button["state"] = "disable"
                app.infoLabel["fg"] = "#ff0000"
                app.infoLabel["text"] = "Database error. Please run again."

    except:
        # do nothing
        disconnected = True

if __name__ == "__main__":

    app = App()

    while True:
        if App.ser.is_open:
            read_serial()
