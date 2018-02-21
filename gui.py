
import sys
from Tkinter import *
from tkFileDialog import askopenfile
from tkFileDialog import askopenfilename
import untangle
from subprocess import *
import subprocess
import tempfile
import time
import ttk
import tkFont
from backend import initModel
import os
import inspect

# ***** Variables *****

entity = None
top = None
sourceSelectedLine = None
selectReg = None

lgrey = '#d9d9d9'
black = '#000000'
white = '#ffffff'
green = '#98FB98'
yellow = '#ffff00'
pink ='#ffa797'

buttonHeight = 30
buttonWidth = 150

font_app_title = "-family {Bitstream Vera Serif} -size 20 -weight bold -slant roman -underline 0 -overstrike 0"
font_app_button = "-family {DejaVu Sans} -size 10 -weight normal -slant roman -underline 0 -overstrike 0"
font_table_title = "-family {DejaVu Sans} -size 12 -weight normal -slant roman -underline 1 -overstrike 0"
font_table_list = "-family {DejaVu Sans} -size 10 -weight normal -slant roman -underline 0 -overstrike 0"
font_table_attr = "-family {DejaVu Sans} -size 10 -weight normal -slant italic -underline 0 -overstrike 0"
font_command_title = "-family {DejaVu Sans} -size 12 -weight normal -slant roman -underline 0 -overstrike 0"


# ***** Functions *****

def normalizeButtons():
    top.reg_refresh.configure(state='normal')
    top.source_feedback_button.configure(state='normal')
    top.source_feedback_entry.configure(state='normal')
    top.source_feedback_button.configure(state='normal')
    top.source_feedback_entry.configure(state='normal')
    top.gdb_connect.configure(state='normal')
    top.gdb_clear.configure(state='normal')
    top.gdb_enter.configure(state='normal')
    top.gdb_entry.configure(state='normal')
    top.source_table.bind("<<ListboxSelect>>", onClick_sourcecode)
    top.reg_table.bind("<<TreeviewSelect>>", onClick_registers)

### Machine Code Functions ###

# Trigger Fault in Machine Code

def triggerFault():
    top.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=yellow,width=1)
    top.trig_fault_button.configure(state='disabled')
    entity.triggerFault()
    top.trig_fault_progress.update()
    top.trig_fault_button.configure(state='normal')

### Source Code Functions ###

# Update the Feedback in Source Code
def getFeedback():
    lineNo = top.source_feedback_entry.get()
    if lineNo.isdigit() and int(lineNo) <= top.source_table.size() and int(lineNo) >0:
        top.source_feedback_entry.config(background=green)
        top.source_feedback_entry.update()
        entity.printOutput("Feedback selected at line " + lineNo)
        top.trig_fault_button.configure(state='normal')
        entity.selectFeedback(lineNo)
    else:
        top.source_feedback_entry.config(background=pink)
        entity.printOutput("ERROR: Input Valid Line No. between 1 and " + str(top.source_table.size()))
        top.source_feedback_entry.update()

# Click on line of Source Code
def onClick_sourcecode(event):
    global sourceSelectedLine
    w = top.source_table
    if not  w.curselection():
        return
    index = int(w.curselection()[0])
    value = w.get(index)
    top.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=black,width=1)
    top.trig_fault_progress.update()
    top.source_feedback_entry.config(background=green)
    top.source_feedback_entry.delete(0,END)
    top.source_feedback_entry.insert(0,index+1)
    entity.showAssemCode(index)

# Open C File
def open_cfile():
    filenameC = askopenfilename(initialdir = "./documents", title="Select Source file")
    if not filenameC:
        top.gdb_table.delete(0,END) 
        top.gdb_table.insert(END,entity.printOutput("ERROR: Not correct file type selected. Please select a Source file."))
        return
    basename = os.path.basename(filenameC)
    entity.importCFile(filenameC)
    top.gdb_table.delete(0,END) 
    entity.printOutput("Connected < {0} > Successfully ... ".format(basename))
    top.source_table.delete(0,END)
    with open (filenameC, "r") as myfile:
        strF = myfile.read()
        index = 0
        for line in strF.split('\n'):
            index = index + 1
            top.source_table.insert(END, "{0:10}{1}".format(str(index), line))
        myfile.close()
    normalizeButtons()
    connectGDB()

### XML Table Functions ###

# Add breakpoint to the registers
def addBreakpoint():
	entity.printOutput("Breakpoints Added Successfully")

### Register Table Functions ###

# Refresh Registers
def refreshRegisters():
    entity.sendCommand("info R")

# Update Register Value
def updateRegisters():
    reg = selectReg
    w = top.reg_entry
    val = w.get()
    w.delete(0,END)
    entity.sendCommand("set $" + reg + "=" + val)
    refreshRegisters()

def enterkeyRegisters(event):
    updateRegisters()

# When Clicking on Registers
def onClick_registers(event):
    global selectReg
    w = top.reg_table
    sel = w.selection()
    selectReg = w.item(sel)['values'][0]
    top.reg_label.configure(text="Register: " + selectReg + "\tmask: ")
    top.reg_update.configure(state='normal')
    top.reg_entry.configure(state='normal')

# Open XML File
def open_xmlfile():
    filenameXML = askopenfilename(initialdir = "./documents",title = "Select XML file",filetypes = (("xml files","*.xml"),("all files","*.*")))
    if ".xml" not in filenameXML:
        top.gdb_table.delete(0,END) 
        top.gdb_table.insert(END,entity.printOutput("ERROR: Not correct file type selected. Please select an XML file."))
        return
    entity.importXML(filenameXML)
    entity.printOutput("Connected < {0} > Successfully ... ".format(os.path.basename(filenameXML)))
    top.xml_table.delete(*top.xml_table.get_children())
    i = 1   
    for item in entity.getFaults():
        trig_list = (i,item[0])
        top.xml_table.insert('', END, values=trig_list)
        for masks in item[1]:
            mask_list = (masks.reg, masks.val, masks.op)
            top.xml_table.insert('', END, values=mask_list)
        i = i + 1
    top.xml_addBreak.configure(state='normal')

### GNU Debugger Functions ###

# Connect to GDB Server
def connectGDB():
    entity.connect()
    entity.printOutput("Connected to GDB Server")
    refreshRegisters()

# Clear entry after sending to GDB
def clearGDB():
    top.gdb_table.delete(0,END) 
    entity.printOutput("Clearing Successfully")

# Function when clicking on the "Enter" Button for the Command Line
def commandGDB():
    entity.sendCommand(top.gdb_entry.get())
    top.gdb_entry.delete(0,END)

# Function when clicking on the "Enter" Key for the Command Line
def enterkeyGDB(event):
    commandGDB()

### GUI Core ###

# When Creating Application
def create_mainwindow():
    global val, w, root, top, entity, sourceSelectedLine
    root = Tk()
    top = mainwindow(root)
    entity = initModel(top)
    root.mainloop()
    sourceSelectedLine = None

# Don't click on other tables
def handle_click(event):
    if top.xml_table.identify_region(event.x, event.y) == "separator":
        return "break"   
    if top.reg_table.identify_region(event.x, event.y) == "separator":
        return "break"  

# Exiting Application
def destroy_mainwindow():
    global w
    w.destroy()
    w = None

# Mouse Wheel Event
def mouseWheelEvent(event):
    top.scrollBar.yview('scroll',event.delta, 'units')

# Initializing

class mainwindow:

    def __init__(self, top):

        top.geometry("1500x1000")
        top.title("Fault Injection Simulator")
        top.configure(highlightcolor=black, background=white)

        self.title(top)
        self.menu(top)
        self.xml(top)
        self.machine(top)
        self.source(top)
        self.reg(top)
        self.gdb(top)

    # Title Frame
    def title(self, top):

        self.title_frame = Frame(top)
        self.title_frame.configure(relief=GROOVE, borderwidth="1")
        self.title_frame.place(relx=0, rely=0, relheight=0.075, relwidth=1.00)
        
        self.title_label = Label(self.title_frame)
        self.title_label.configure(text="Fault Injection Simulator", font=font_app_title, anchor="center")
        self.title_label.place(relx=0, rely=0, relheight=1.00, relwidth=1.00)

    # Machine Code Frame
    def machine(self, top):

        self.machine_frame = Frame(top)
        self.machine_frame.configure(relief=GROOVE, borderwidth="1")
        self.machine_frame.place(relx=0, rely=0.075, relheight=0.4, relwidth=0.45)

        self.machine_title = Label(self.machine_frame)
        self.machine_title.configure(text="Machine Code", font=font_table_title, anchor=NW)
        self.machine_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.2)

        self.trig_fault_button = Button(self.machine_frame)
        self.trig_fault_button.configure(text="Trigger Fault", font=font_app_button, state='disabled', command=triggerFault)
        self.trig_fault_button.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth, anchor=NE)

        self.trig_fault_progress = Canvas(self.machine_frame)
        self.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=black,width=2)
        self.trig_fault_progress.place(relx=0.7, rely=0.02, relheight=0.075, relwidth=0.05)

        self.machine_table = Listbox(self.machine_frame)
        self.machine_table.configure(relief=RIDGE, font=font_table_list)
        self.machine_table.place(relx=0.01, rely=0.09, relheight=0.89, relwidth=0.98)
        self.machine_table.insert(END,"Click on a Source Code line to view Machine Code")
        self.machine_table_scrollBar = ttk.Scrollbar(self.machine_table, orient="vertical")
        self.machine_table_scrollBar.config(command=self.machine_table.yview)
        self.machine_table_scrollBar.pack(side="right", fill="y")
        self.machine_table.config(yscrollcommand=self.machine_table_scrollBar.set)
        self.machine_table.bind("<MouseWheel>", mouseWheelEvent)

    # Source Code Frame
    def source(self, top):

        self.source_frame = Frame(top)
        self.source_frame.configure(relief=GROOVE, borderwidth="1")
        self.source_frame.place(relx=0, rely=0.475, relheight=0.525, relwidth=0.45)

        self.source_title = Label(self.source_frame)
        self.source_title.configure(text="Source Code", font=font_table_title, anchor=NW)
        self.source_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.2)

        self.source_feedback_label = Label(self.source_frame)
        self.source_feedback_label.configure(text="Line No.", font=font_app_button)
        self.source_feedback_label.place(relx=0.5, rely=0.01, height=30, width=150)

        self.source_feedback_entry = Entry(self.source_frame)
        self.source_feedback_entry.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        #self.source_feedback_entry.bind('<Return>', getFeedback)
        self.source_feedback_entry.place(relx=0.66, rely=0.01, height=30, width=60)
        
        self.source_feedback_button = Button(self.source_frame)
        self.source_feedback_button.configure(text="Update Feedback", font=font_app_button, state='disabled', command=getFeedback)
        self.source_feedback_button.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth, anchor=NE)
        
        self.source_table = Listbox(self.source_frame)
        self.source_table.configure(relief=RIDGE, font=font_table_list, selectbackground=lgrey)
        self.source_table.place(relx=0.01, rely=0.075, relheight=0.91, relwidth=0.98)
        self.source_table.insert(END,"Select { Open Source File } to view")
        self.source_table_scrollBar = ttk.Scrollbar(self.source_table, orient="vertical")
        self.source_table_scrollBar.config(command=self.source_table.yview)
        self.source_table_scrollBar.pack(side="right", fill="y")
        self.source_table.config(yscrollcommand=self.source_table_scrollBar.set)
        self.source_table.bind("<MouseWheel>", mouseWheelEvent)
    
    # XML Table Frame
    def xml(self, top):

        self.xml_frame = Frame(top)
        self.xml_frame.configure(relief=GROOVE, borderwidth="1")
        self.xml_frame.place(relx=0.45, rely=0.075, relheight=0.4, relwidth=0.32)

        self.xml_title = Label(self.xml_frame)
        self.xml_title.configure(text="XML Table", font=font_table_title, anchor=NW)
        self.xml_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.2)

        self.xml_addBreak = Button(self.xml_frame)
        self.xml_addBreak.configure(text="Add Breakpoints", font=font_app_button, state='disabled', command=addBreakpoint)
        self.xml_addBreak.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth, anchor=NE)

        header = ["#","Breakpoint","Loop","Register","Mask"]
       	self.xml_table = ttk.Treeview(self.xml_frame,columns=header, show="headings")
       	self.xml_table.place(relx=0.01, rely=0.09, relheight=0.89, relwidth=0.98)
        self.xml_table_scrollBar = ttk.Scrollbar(self.xml_table, orient="vertical", command=self.xml_table.yview)
        self.xml_table_scrollBar.pack(side="right", fill="y")
       	self.xml_table.configure(yscrollcommand=self.xml_table_scrollBar.set)
        #self.xml_table.bind('<Button-1>', handle_click)
       	self.xml_table.column('#1', width=10)
        self.xml_table.column('#2', width=75)
        self.xml_table.column('#3', width=75)
        self.xml_table.column('#4', width=75)
        self.xml_table.column('#5', width=75)
       	for col in header:
       		self.xml_table.heading(col, text=col.title())
		
    # Register Table Frame
    def reg(self, top):

        self.reg_frame = Frame(top)
        self.reg_frame.configure(relief=GROOVE, borderwidth="1")
        self.reg_frame.place(relx=0.77, rely=0.075, relheight=0.4, relwidth=0.23)

        self.reg_title = Label(self.reg_frame)
        self.reg_title.configure(text="Register Table", font=font_table_title, anchor=NW)
        self.reg_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.5)

        self.reg_refresh = Button(self.reg_frame)
        self.reg_refresh.configure(text="Refresh", font=font_app_button, state='disabled', command=refreshRegisters)
        self.reg_refresh.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth/2, anchor=NE)

        header = ["Name","Address","Value"]
       	self.reg_table = ttk.Treeview(self.reg_frame, columns=header, show="headings")
       	self.reg_table.place(relx=0.01, rely=0.0925, relheight=0.8, relwidth=0.98)
        self.reg_table_scrollBar = ttk.Scrollbar(self.reg_table, orient="vertical", command=self.reg_table.yview)
        self.reg_table_scrollBar.pack(side="right", fill="y")
       	self.reg_table.configure(yscrollcommand=self.reg_table_scrollBar.set)
        #self.reg_table.bind('<Button-1>', handle_click)
        self.reg_table.column('#1', width=10)
        self.reg_table.column('#2', width=100)
        self.reg_table.column('#3', width=100)
       	for col in header:
       		self.reg_table.heading(col, text=col.title())
       	
        self.reg_label = Label(self.reg_frame)
        self.reg_label.configure(text="Select a Register:", font=font_app_button, anchor=NW)
        self.reg_label.place(relx=0.01, rely=0.925, relheight=0.05, width=200)
        
        self.reg_entry = Entry(self.reg_frame)
        self.reg_entry.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.reg_entry.place(relx=0.75, rely=0.9125, relheight=0.075, width=75, anchor=NE)
        self.reg_entry.bind('<Return>', enterkeyRegisters)

        self.reg_update = Button(self.reg_frame)
        self.reg_update.configure(text="Update", font=font_app_button, state='disabled', command=updateRegisters)
        self.reg_update.place(relx=0.99, rely=0.9125, height=buttonHeight, width=buttonWidth/2, anchor=NE)

    # GNU Debugger Frame
    def gdb(self, top):

        self.gdb_frame = Frame(top)
        self.gdb_frame.configure(relief=GROOVE, borderwidth="1")
        self.gdb_frame.place(relx=0.45, rely=0.475, relheight=0.525, relwidth=0.55)

        self.gdb_title = Label(self.gdb_frame)
        self.gdb_title.configure(text="GNU Debugger", font=font_table_title, anchor=NW)
        self.gdb_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.2)

        self.gdb_clear = Button(self.gdb_frame)
        self.gdb_clear.configure(text="Clear GDB", font=font_app_button, state='disabled', command=clearGDB)
        self.gdb_clear.place(relx=0.73, rely=0.01, height=buttonHeight, width=buttonWidth, anchor=NE)

        self.gdb_connect = Button(self.gdb_frame)
        self.gdb_connect.configure(text="Connect to GDB Server", font=font_app_button, state='disabled', command=connectGDB)
        self.gdb_connect.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth+50, anchor=NE)

        self.gdb_table = Listbox(self.gdb_frame)
        self.gdb_table.configure(relief=RIDGE, font=font_table_list)
        self.gdb_table.place(relx=0.01, rely=0.075, relheight=0.85, relwidth=0.98)
        self.gdb_table.insert(END,"Connect to Server to Debug")
        self.gdb_table_scrollBar = ttk.Scrollbar(self.gdb_table, orient="vertical")
        self.gdb_table_scrollBar.config(command=self.gdb_table.yview)
        self.gdb_table_scrollBar.pack(side="right", fill="y")
        self.gdb_table.config(yscrollcommand=self.gdb_table_scrollBar.set)
        self.gdb_table.bind("<MouseWheel>", mouseWheelEvent)

        self.gdb_label = Label(self.gdb_frame)
        self.gdb_label.configure(text="(gdb)", font=font_command_title, anchor=NW)
        self.gdb_label.place(relx=0.01, rely=0.94, relheight=0.05, relwidth=0.1)

        self.gdb_entry = Entry(self.gdb_frame)
        self.gdb_entry.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.gdb_entry.bind('<Return>', enterkeyGDB)
        self.gdb_entry.place(relx=0.075, rely=0.94, relheight=0.05, relwidth=0.8)

        self.gdb_enter = Button(self.gdb_frame)
        self.gdb_enter.configure(text="Enter", font=font_app_button, state="disabled", command=commandGDB)
        self.gdb_enter.place(relx=0.99, rely=0.935, height=buttonHeight, width=buttonWidth/2, anchor=NE)

    def menu(self, top):
    	self.menuBar = Menu(top)
    	self.menuBar.add_command(label="Open Source File",command=open_cfile)
    	self.menuBar.add_command(label="Open XML File",command=open_xmlfile)
    	self.menuBar.add_command(label="Exit Application",command=top.quit)
    	top.config(menu=self.menuBar)

# ***** EOF *****