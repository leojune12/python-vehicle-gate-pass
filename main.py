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
    lastScanLabel = None
    driverImage = None
    driverNameLabel = None
    driverRfidLabel = None
    driverLogTypeLabel = None
    driverLogTimeLabel = None
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
        height = 380
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

        # logo
        logo = Image.open("capsu-logo.png")
        test = ImageTk.PhotoImage(logo)
        logoLabel = tk.Label(image=test)
        logoLabel.image = test
        logoLabel.place(x=30, y=20)

        # driver profile photo
        fixed_height = 115
        profile_photo = Image.open("C:/laragon/www/vehicle-gate-pass-system/public/anonymous.png")
        height_percent = (fixed_height / float(profile_photo.size[1]))
        width_size = int((float(profile_photo.size[0]) * float(height_percent)))
        profile_photo = profile_photo.resize((width_size, fixed_height), Image.NEAREST)
        photo = ImageTk.PhotoImage(profile_photo)
        App.driverImage = tk.Label(self.root)
        App.driverImage['image'] = photo
        App.driverImage.place(x=30, y=230)

        # last scan label
        App.lastScanLabel = tk.Label(self.root)
        ft = tkFont.Font(family='Times', size=12)
        App.lastScanLabel["font"] = ft
        App.lastScanLabel["fg"] = "#333333"
        App.lastScanLabel["justify"] = "left"
        App.lastScanLabel["text"] = "Last scanned:"
        App.lastScanLabel.place(x=30, y=200, width=90, height=30)
        
        # Driver name
        App.driverNameLabel = tk.Label(self.root, anchor='w')
        ft = tkFont.Font(family='Times',size=10)
        App.driverNameLabel["font"] = ft
        App.driverNameLabel["fg"] = "#333333"
        App.driverNameLabel["justify"] = "left"
        App.driverNameLabel["text"] = "Name:"
        App.driverNameLabel.place(x=160, y=230, width=200, height=30)
        
        # Driver RFID
        App.driverRfidLabel=tk.Label(self.root, anchor='w')
        ft = tkFont.Font(family='Times',size=10)
        App.driverRfidLabel["font"] = ft
        App.driverRfidLabel["fg"] = "#333333"
        App.driverRfidLabel["justify"] = "left"
        App.driverRfidLabel["text"] = "RFID:"
        App.driverRfidLabel.place(x=160, y=260, width=200, height=30)   
        
        # Driver Log Type
        App.driverLogTypeLabel=tk.Label(self.root, anchor='w')
        ft = tkFont.Font(family='Times',size=10)
        App.driverLogTypeLabel["font"] = ft
        App.driverLogTypeLabel["fg"] = "#333333"
        App.driverLogTypeLabel["justify"] = "left"
        App.driverLogTypeLabel["text"] = "Log Type:"
        App.driverLogTypeLabel.place(x=160, y=290, width=210, height=30)  
        
        # Driver Log Time
        App.driverLogTimeLabel=tk.Label(self.root, anchor='w')
        ft = tkFont.Font(family='Times',size=10)
        App.driverLogTimeLabel["font"] = ft
        App.driverLogTimeLabel["fg"] = "#333333"
        App.driverLogTimeLabel["justify"] = "left"
        App.driverLogTimeLabel["text"] = "Time:"
        App.driverLogTimeLabel.place(x=160, y=320, width=210, height=30)          
        GLabel_964 = tk.Label(self.root)
        ft = tkFont.Font(family='Times', size=16)
        GLabel_964["font"] = ft
        GLabel_964["fg"] = "#333333"
        GLabel_964["justify"] = "center"
        GLabel_964["text"] = "RFID VEHICLE GATE PASS"
        GLabel_964.place(x=114, y=35, width=250, height=34)

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

        App.infoLabel = tk.Label(self.root, anchor='w')
        ft = tkFont.Font(family='Times', size=10)
        App.infoLabel["font"] = ft
        App.infoLabel["fg"] = "#333333"
        App.infoLabel["justify"] = "left"
        App.infoLabel["text"] = "Select port:"
        App.infoLabel.place(x=30, y=110, width=180, height=30)

        # Check db credentials from .env file
        if not db.db_status:
            App.comboBox["state"] = "disable"
            App.infoLabel["fg"] = "#ff0000"
            App.infoLabel["text"] = "Database error. Please run again."
        else:
            print("System started")
            set_last_scanned_driver(db.get_last_scanned())

        self.root.mainloop()

    def connect_disconnect(self):
        if not App.ser.is_open:
            App.ser.port = App.comboBox.get()
            App.button['text'] = 'Disconnect'
            App.button['bg'] = '#fb4545'
            App.infoLabel['text'] = 'Connected:'
            App.comboBox['state'] = 'disable'
            App.ser.open()

        else:
            App.ser.close()
            App.button['text'] = 'Connect'
            App.button['bg'] = '#1cd751'
            App.infoLabel['text'] = 'Select port:'
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
                    # send command to arduino to open gate
                    app.ser.write(data["reader"].encode())
                    
                    # update last scanned
                    set_last_scanned_driver(db.get_last_scanned())
                else:
                    set_last_scanned_driver({'name': 'Unregistered RFID', 'rfid': 'RFID: ' + data['uid'], 'photo': None, 'log_type': '', 'time': ''})

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
        
def set_last_scanned_driver(last_scanned):
    App.driverNameLabel['text'] = last_scanned['name']
    App.driverRfidLabel['text'] = last_scanned['rfid']
    App.driverLogTypeLabel['text'] = last_scanned['log_type']
    App.driverLogTimeLabel['text'] = last_scanned['time']
    
    if last_scanned['photo'] != None:
        fixed_height = 115
        profile_photo = Image.open("C:/laragon/www/vehicle-gate-pass-system/public/storage/"+last_scanned['photo'])
        height_percent = (fixed_height / float(profile_photo.size[1]))
        width_size = int((float(profile_photo.size[0]) * float(height_percent)))
        profile_photo = profile_photo.resize((width_size, fixed_height), Image.NEAREST)
        new_photo = ImageTk.PhotoImage(profile_photo)
        App.driverImage.configure(image=new_photo)
        App.driverImage.image = new_photo
        
    else:
        fixed_height = 115
        profile_photo = Image.open("C:/laragon/www/vehicle-gate-pass-system/public/anonymous.png")
        height_percent = (fixed_height / float(profile_photo.size[1]))
        width_size = int((float(profile_photo.size[0]) * float(height_percent)))
        profile_photo = profile_photo.resize((width_size, fixed_height), Image.NEAREST)
        new_photo = ImageTk.PhotoImage(profile_photo)
        App.driverImage.configure(image=new_photo)
        App.driverImage.image = new_photo

if __name__ == "__main__":

    app = App()

    while True:
        if App.ser.is_open:
            read_serial()
