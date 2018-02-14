
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
from backend import initModel
import os
import inspect

# ***** Variables *****
entity = None
top = None

# ***** Functions *****

def automateTest():
	# onClick_xmlFile()
	# onClick_cFile()
	# onClick_connectQemu()
	return

# Insert print terminal now on GDB Output
def printOutput(line):
    output = " > [ " + line + " ]"
    print output
    top.gdb_table.insert(END, output)

def refreshRegisters():
    entity.sendCommand("info R")

# Function when clicking on the "Open XML File" Button
def onClick_xmlFile():
    filenameXML = askopenfilename(initialdir = "./documents",title = "Select XML file",filetypes = (("xml files","*.xml"),("all files","*.*")))
    if ".xml" not in filenameXML:
        top.gdb_table.delete(0,END)	
        top.gdb_table.insert(END,printOutput("ERROR: Not correct file type selected. Please select an XML file."))
        return
    entity.importXML(filenameXML)
    printOutput("Connected < {0} > Successfully ... ".format(os.path.basename(filenameXML)))
    top.xml_table.delete(0,END)	
    i = 1
    for item in entity.getFaults():
        item_list = "{}".format(i).ljust(10) + \
        "{}".format(item.bp).ljust(20) + \
        "{}".format(item.lp).ljust(10) + \
        "{}".format(item.regList).ljust(40) + \
        "{}".format(item.mask).ljust(10)
        top.xml_table.insert(END, item_list)
        i = i + 1

# Function when clicking on the "Open C File" Button
def onClick_cFile():
    filenameC = askopenfilename(initialdir = "./documents", title="Select Source file")
    if not filenameC:
    	top.gdb_table.delete(0,END)	
        top.gdb_table.insert(END,printOutput("ERROR: Not correct file type selected. Please select a Source file."))
        return
    basename = os.path.basename(filenameC)
    entity.importCFile(filenameC)
    top.gdb_table.delete(0,END)	
    printOutput("Connected < {0} > Successfully ... ".format(basename))
    top.source_table.delete(0,END)
    with open (filenameC, "r") as myfile:
    	strF = myfile.read() 	
    	for line in strF.split('\n'):
    		top.source_table.insert(END, line)
    	myfile.close()
    onClick_connectQemu()


# Function when clicking on the "Connect to Qemu" Button
# Put Events in here to first activate
def onClick_connectQemu():
	top.command_enter.configure(state='active')
	top.command_entry.configure(state='normal')
	top.ref_reg.configure(state='active')
	top.source_table.bind("<<ListboxSelect>>", clickProgLine)
	#top.machine_table.bind("<<ListboxSelect>>", clickProgLine2)
	entity.connect()
	#printOutput("Connected to Qemu Sucessfully ...")


def clickProgLine(event):
    w = event.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    top.trig_fault.configure(state='normal')
    printOutput('You selected line %d: "%s"' % (index +1, value))
    entity.showAssemCode(index)
    top.trig_fault.configure(state='active')

def clearBox(event):
	event.widget.delete(0,END)

# Function when clicking on the "Enter" Key for the Command Line
def enterKey(event):
	entity.sendCommand(event.widget.get())
	clearBox(event)

# Function when clicking on the "Enter" Button for the Command Line
def onClick_enter():
	entity.sendCommand(top.command_entry.get())
	clearBox(top)


def triggerFault():
    top.trig_fault.configure(state='disabled')
    #top.stop_fault.configure(state='active')
    entity.triggerFault()

# def stopFault():
# 	top.stop_fault.configure(state='disabled')
# 	print 'STOPPING FAULT IF NEEDED'

# ***** GUI *****

# When Creating Application
def create_mainwindow():
    '''Starting point when module is the main routine.'''
    global val, w, root, top, entity
    root = Tk()
    top = mainwindow(root)
    entity = initModel(top)
    automateTest()
    root.mainloop()

# When Exiting Application
def destroy_mainwindow():
    global w
    w.destroy()
    w = None

def mouseWheelEvent(event):
    top.scrollBar.yview('scroll',event.delta, 'units')

# GUI Core

lgrey = '#d9d9d9'
black = '#000000'
white = '#ffffff'

font_app_title = "-family {Bitstream Vera Serif} -size 20 -weight bold -slant roman -underline 0 -overstrike 0"
font_app_button = "-family {DejaVu Sans} -size 10 -weight normal -slant roman -underline 0 -overstrike 0"
font_table_title = "-family {DejaVu Sans} -size 12 -weight normal -slant roman -underline 1 -overstrike 0"
font_table_list = "-family {DejaVu Sans} -size 10 -weight normal -slant roman -underline 0 -overstrike 0"
font_table_attr = "-family {DejaVu Sans} -size 10 -weight normal -slant italic -underline 0 -overstrike 0"
font_command_title = "-family {DejaVu Sans} -size 12 -weight normal -slant roman -underline 0 -overstrike 0"

class mainwindow:

    def __init__(self, top):

        top.geometry("1500x1000+335+110")
        top.title("Fault Injection Simulator")
        top.configure(background=white)
        top.configure(highlightcolor=black)

        self.title(top)
        self.menu(top)
        self.xml(top)
        self.machine(top)
        self.source(top)
        self.reg(top)
        self.gdb(top)
        self.command(top)


    def title(self, top):

        self.title_frame = Frame(top)
        self.title_frame.configure(relief=GROOVE, borderwidth="1")
        self.title_frame.place(relx=0, rely=0, relheight=0.075, relwidth=1.00)
        
        self.title_label = Label(self.title_frame)
        self.title_label.configure(text="Fault Injection Simulator", font=font_app_title, anchor="center")
        self.title_label.place(relx=0, rely=0, relheight=1.00, relwidth=1.00)

        self.trig_fault = Button(self.title_frame)
        self.trig_fault.configure(text="Trigger Fault", font=font_app_button, state='disabled', command=triggerFault)
        self.trig_fault.place(relx=0.01, rely=0.3, height=30, width=150)

        # self.stop_fault = Button(self.title_frame)
        # self.stop_fault.configure(text="Stop Fault", font=font_button, state='disabled')
        # self.stop_fault.place(relx=0.13, rely=0.3, height=30, width=150)

        self.ref_reg = Button(self.title_frame)
        self.ref_reg.configure(text="Refresh Registers", font=font_app_button, state='disabled', command=refreshRegisters)
        self.ref_reg.place(relx=0.89, rely=0.3, height=30, width=150)

    def machine(self, top):

        self.machine_frame = Frame(top)
        self.machine_frame.configure(relief=GROOVE, borderwidth="1")
        self.machine_frame.place(relx=0, rely=0.075, relheight=0.4, relwidth=0.45)

        self.machine_title = Label(self.machine_frame)
        self.machine_title.configure(text="Machine Code", font=font_table_title, anchor=NW)
        self.machine_title.place(relx=0.02, rely=0.02, relheight=0.2, relwidth=0.2)

        self.machine_table = Listbox(self.machine_frame)
        self.machine_table_scrollBar = Scrollbar(self.machine_table, orient="vertical")
        self.machine_table_scrollBar.config(command=self.machine_table.yview)
        self.machine_table_scrollBar.pack(side="right", fill="y")
        self.machine_table.bind("<MouseWheel>", mouseWheelEvent)
        self.machine_table.configure(relief=RIDGE, font=font_table_list, yscrollcommand=self.machine_table_scrollBar.set)
        self.machine_table.place(relx=0.02, rely=0.09, relheight=0.875, relwidth=0.96)
        self.machine_table.bindtags((self.machine_table, self, "<MouseWheel>"))
        self.machine_table.insert(END,"Click on a Source Code line to view Machine Code")

    def source(self, top):

        self.source_frame = Frame(top)
        self.source_frame.configure(relief=GROOVE, borderwidth="1")
        self.source_frame.place(relx=0, rely=0.475, relheight=0.525, relwidth=0.45)

        self.source_title = Label(self.source_frame)
        self.source_title.configure(text="Source Code", font=font_table_title, anchor=NW)
        self.source_title.place(relx=0.02, rely=0.02, relheight=0.2, relwidth=0.2)
        
        self.source_table = Listbox(self.source_frame)
        self.source_table.configure(relief=RIDGE, font=font_table_list)
        self.source_table.place(relx=0.02, rely=0.075, relheight=0.9, relwidth=0.96)
        self.source_table.insert(END,"Select { Open Files > Open Source File } to view")
        self.source_table_scrollBar = Scrollbar(self.source_table, orient="vertical")
        self.source_table_scrollBar.config(command=self.source_table.yview)
        self.source_table_scrollBar.pack(side="right", fill="y")
        self.source_table.config(yscrollcommand=self.source_table_scrollBar.set)
        self.source_table.bind("<MouseWheel>", mouseWheelEvent)


    def xml(self, top):

        self.xml_frame = Frame(top)
        self.xml_frame.configure(relief=GROOVE, borderwidth="1")
        self.xml_frame.place(relx=0.45, rely=0.075, relheight=0.4, relwidth=0.32)

        self.xml_title = Label(self.xml_frame)
        self.xml_title.configure(text="XML Table", font=font_table_title, anchor=NW)
        self.xml_title.place(relx=0.02, rely=0.02, relheight=0.2, relwidth=0.2)

        self.xml_attr = Label(self.xml_frame)
        self.xml_attr.configure(text="Num   Breakpoint      Loop   Register                                 Mask", font=font_table_attr, anchor=NW)
        self.xml_attr.place(relx=0.02, rely=0.075, relheight=0.1, relwidth=0.96)

        self.xml_table = Listbox(self.xml_frame)
        self.xml_table.configure(relief=RIDGE, font=font_table_list)
        self.xml_table.place(relx=0.02, rely=0.125, relheight=0.85, relwidth=0.96)
        self.xml_table.insert(END,"Select { Open Files > Open XML File } to view")
        self.xml_table_scrollBar = Scrollbar(self.xml_table, orient="vertical")
        self.xml_table_scrollBar.config(command=self.xml_table.yview)
        self.xml_table_scrollBar.pack(side="right", fill="y")
        self.xml_table.config(yscrollcommand=self.xml_table_scrollBar.set)
        self.xml_table.bind("<MouseWheel>", mouseWheelEvent)

    def reg(self, top):

        self.reg_frame = Frame(top)
        self.reg_frame.configure(relief=GROOVE, borderwidth="1")
        self.reg_frame.place(relx=0.77, rely=0.075, relheight=0.4, relwidth=0.23)

        self.reg_title = Label(self.reg_frame)
        self.reg_title.configure(text="Register Table", font=font_table_title, anchor=NW)
        self.reg_title.place(relx=0.02, rely=0.02, relheight=0.2, relwidth=0.5)

        self.reg_attr = Label(self.reg_frame)
        self.reg_attr.configure(text="Name     Address      Value", font=font_table_attr, anchor=NW)
        self.reg_attr.place(relx=0.02, rely=0.075, relheight=0.1, relwidth=0.96)        

        self.reg_table = Listbox(self.reg_frame)
        self.reg_table.configure(relief=RIDGE, font=font_table_list)
        self.reg_table.place(relx=0.02, rely=0.125, relheight=0.85, relwidth=0.96)
        self.reg_table.insert(END,"Connect to Server to view Registers")
        self.reg_table_scrollBar = Scrollbar(self.reg_table, orient="vertical")
        self.reg_table_scrollBar.config(command=self.reg_table.yview)
        self.reg_table_scrollBar.pack(side="right", fill="y")
        self.reg_table.config(yscrollcommand=self.reg_table_scrollBar.set)
        self.reg_table.bind("<MouseWheel>", mouseWheelEvent)

    def gdb(self, top):

        self.gdb_frame = Frame(top)
        self.gdb_frame.configure(relief=GROOVE, borderwidth="1")
        self.gdb_frame.place(relx=0.45, rely=0.475, relheight=0.475, relwidth=0.55)

        self.gdb_title = Label(self.gdb_frame)
        self.gdb_title.configure(text="GNU Debugger", font=font_table_title, anchor=NW)
        self.gdb_title.place(relx=0.02, rely=0.02, relheight=0.2, relwidth=0.2)

        self.gdb_table = Listbox(self.gdb_frame)
        self.gdb_table.configure(relief=RIDGE, font=font_table_list)
        self.gdb_table.place(relx=0.015, rely=0.08, relheight=0.9, relwidth=0.98)
        self.gdb_table.insert(END,"Connect to Server to Debug")
        self.gdb_table_scrollBar = Scrollbar(self.gdb_table, orient="vertical")
        self.gdb_table_scrollBar.config(command=self.gdb_table.yview)
        self.gdb_table_scrollBar.pack(side="right", fill="y")
        self.gdb_table.config(yscrollcommand=self.gdb_table_scrollBar.set)
        self.gdb_table.bind("<MouseWheel>", mouseWheelEvent)

    def command(self, top):

        self.command_frame = Frame(top)
        self.command_frame.configure(relief=GROOVE, borderwidth="1")
        self.command_frame.place(relx=0.45, rely=0.95, relheight=0.05, relwidth=0.55)

        self.command_title = Label(self.command_frame)
        self.command_title.configure(text="(gdb)", font=font_command_title, anchor=NW)
        self.command_title.place(relx=0.02, rely=0.25, relheight=0.5, relwidth=0.1)

        self.command_entry = Entry(self.command_frame)
        self.command_entry.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.command_entry.bind('<Return>', enterKey)
        self.command_entry.place(relx=0.1, rely=0.25, relheight=0.5, relwidth=0.8)

        self.command_enter = Button(self.command_frame)
        self.command_enter.configure(text="Enter", font=font_app_button, state="disabled", command=onClick_enter)
        self.command_enter.place(relx=0.92, rely=0.25, relheight=0.5, width=60)

    def menu(self, top):
    	self.menuBar = Menu(top)
    	filemenu = Menu(self.menuBar)
    	filemenu.add_command(label="Open XML File", command=onClick_xmlFile)
    	filemenu.add_command(label="Open Source File", command=onClick_cFile)
    	self.menuBar.add_cascade(label="Open Files",menu=filemenu)
    	self.menuBar.add_command(label="Connect to Server",command=onClick_connectQemu)
    	self.menuBar.add_command(label="Exit Application",command=top.quit)
    	top.config(menu=self.menuBar)

if __name__ == '__main__':
    create_mainwindow()

# ***** EOF *****