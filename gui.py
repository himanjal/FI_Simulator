
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

lgrey = '#d9d9d9'
black = '#000000'
white = '#ffffff'
green = '#98FB98'
red = '#ff0000'
pink ='#ffa797'

font_app_title = "-family {Bitstream Vera Serif} -size 20 -weight bold -slant roman -underline 0 -overstrike 0"
font_app_button = "-family {DejaVu Sans} -size 10 -weight normal -slant roman -underline 0 -overstrike 0"
font_table_title = "-family {DejaVu Sans} -size 12 -weight normal -slant roman -underline 1 -overstrike 0"
font_table_list = "-family {DejaVu Sans} -size 10 -weight normal -slant roman -underline 0 -overstrike 0"
font_table_attr = "-family {DejaVu Sans} -size 10 -weight normal -slant italic -underline 0 -overstrike 0"
font_command_title = "-family {DejaVu Sans} -size 12 -weight normal -slant roman -underline 0 -overstrike 0"


# ***** Functions *****

def automateTest():
	# onClick_xmlFile()
	# onClick_cFile()
	# onClick_connectQemu()
	return

def refreshRegisters():
    reg = top.reg_entry1.get()
    val = top.reg_entry2.get()
    entity.sendCommand("set $" + reg + "=" + val)
    entity.sendCommand("info R")

# Function when clicking on the "Open XML File" Button
def onClick_xmlFile():
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
        item_list = (i, item.bp, item.lp, item.regList, item.mask)
        top.xml_table.insert('', END, values=item_list)
        i = i + 1
    top.xml_addBreak.configure(state='normal')


# Function when clicking on the "Open C File" Button
def onClick_cFile():
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
	top.command_enter.configure(state='normal')
	top.command_entry.configure(state='normal')
	top.reg_refresh.configure(state='normal')
    top.reg_entry1.configure(state='normal')
    top.reg_entry2.configure(state='normal')
    top.source_feedback_button.configure(state='normal')
    top.source_feedback_entry.configure(state='normal')
    top.source_table.bind("<<ListboxSelect>>", onClick_sourcecode)
    #top.machine_table.bind("<<ListboxSelect>>", onClick_machinecode)
    entity.connect()

# def onClick_machinecode(event):
#     try:
#         w = top.machine_table
#         index = int(w.curselection()[0])
#         value = w.get(index)
#         top.trig_fault_button.configure(state='normal')
#         entity.printOutput('You selected line %d: "%s"' % (index +1, value))
#         entity.showAssemCode(index)
#     except:
#         return 
    
    #top.trig_fault.configure(state='normal')

def onClick_sourcecode(event):
    w = top.source_table
    if not  w.curselection():
        return
    index = int(w.curselection()[0])
    value = w.get(index)
    top.source_feedback_button.configure(state='normal')
    top.source_feedback_entry.configure(state='normal')
    #top.source_feedback_entry.bind('<Return>', getFeedback)
    entity.selectFeedback(index+1)
    top.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=black,width=1)
    top.trig_fault_progress.update()
    top.source_feedback_entry.delete(0,END)
    top.source_feedback_entry.insert(0,index+1)
    getFeedback()
    #entity.printOutput('You selected line %d: "%s"' % (index +1, value))
    entity.showAssemCode(index)
    top.trig_fault_button.configure(state='normal')


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
    top.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=red,width=1)
    top.trig_fault_button.configure(state='disabled')


    entity.triggerFault()


    #when trigger ends
    top.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=green,width=1)
    top.trig_fault_progress.update()
    top.trig_fault_button.configure(state='normal')
    

def getFeedback():
	#dialog box of source code to select line
    lineNo = top.source_feedback_entry.get()

    print top.source_table.size()
    if lineNo.isdigit() and int(lineNo) <= top.source_table.size() and int(lineNo) >0:
        top.source_feedback_entry.config(background=green)
        top.source_feedback_entry.update()
        entity.printOutput("Feedback selected at line " + lineNo)
        entity.selectFeedback(lineNo)
    else:
        top.source_feedback_entry.config(background=pink)
        entity.printOutput("ERROR: Input Valid Line No. between 1 and " + str(top.source_table.size()))
        top.source_feedback_entry.update()

def addBreakpoint():
	print "add breakpoint"

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

def handle_click(event):
    if top.xml_table.identify_region(event.x, event.y) == "separator":
        return "break"   
    if top.reg_table.identify_region(event.x, event.y) == "separator":
        return "break"  

# When ExitinFeedbackg Application
def destroy_mainwindow():
    global w
    w.destroy()
    w = None

def mouseWheelEvent(event):
    top.scrollBar.yview('scroll',event.delta, 'units')

# GUI Core

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
        self.command(top)


    def title(self, top):

        self.title_frame = Frame(top)
        self.title_frame.configure(relief=GROOVE, borderwidth="1")
        self.title_frame.place(relx=0, rely=0, relheight=0.075, relwidth=1.00)
        
        self.title_label = Label(self.title_frame)
        self.title_label.configure(text="Fault Injection Simulator", font=font_app_title, anchor="center")
        self.title_label.place(relx=0, rely=0, relheight=1.00, relwidth=1.00)

    def machine(self, top):

        self.machine_frame = Frame(top)
        self.machine_frame.configure(relief=GROOVE, borderwidth="1")
        self.machine_frame.place(relx=0, rely=0.075, relheight=0.4, relwidth=0.45)

        self.machine_title = Label(self.machine_frame)
        self.machine_title.configure(text="Machine Code", font=font_table_title, anchor=NW)
        self.machine_title.place(relx=0.02, rely=0.02, relheight=0.2, relwidth=0.2)

        self.trig_fault_button = Button(self.machine_frame)
        self.trig_fault_button.configure(text="Trigger Fault", font=font_app_button, state='disabled', command=triggerFault)
        self.trig_fault_button.place(relx=0.75, rely=0.01, height=30, width=150)

        self.trig_fault_progress = Canvas(self.machine_frame)
        self.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=black,width=2)
        self.trig_fault_progress.place(relx=0.7, rely=0.02, relheight=0.075, relwidth=0.05)

        self.machine_table = Listbox(self.machine_frame)
        self.machine_table.configure(relief=RIDGE, font=font_table_list)
        self.machine_table.place(relx=0.02, rely=0.09, relheight=0.875, relwidth=0.96)
        self.machine_table.insert(END,"Click on a Source Code line to view Machine Code")
        self.machine_table_scrollBar = ttk.Scrollbar(self.machine_table, orient="vertical")
        self.machine_table_scrollBar.config(command=self.machine_table.yview)
        self.machine_table_scrollBar.pack(side="right", fill="y")
        self.machine_table.config(yscrollcommand=self.machine_table_scrollBar.set)
        self.machine_table.bind("<MouseWheel>", mouseWheelEvent)

    def source(self, top):

        self.source_frame = Frame(top)
        self.source_frame.configure(relief=GROOVE, borderwidth="1")
        self.source_frame.place(relx=0, rely=0.475, relheight=0.525, relwidth=0.45)

        self.source_title = Label(self.source_frame)
        self.source_title.configure(text="Source Code", font=font_table_title, anchor=NW)
        self.source_title.place(relx=0.02, rely=0.02, relheight=0.2, relwidth=0.2)

        self.source_feedback_label = Label(self.source_frame)
        self.source_feedback_label.configure(text="Line No.", font=font_app_button)
        self.source_feedback_label.place(relx=0.5, rely=0.01, height=30, width=150)

        self.source_feedback_entry = Entry(self.source_frame)
        self.source_feedback_entry.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.source_feedback_entry.bind('<Return>', getFeedback)
        self.source_feedback_entry.place(relx=0.66, rely=0.01, height=30, width=60)
        
        self.source_feedback_button = Button(self.source_frame)
        self.source_feedback_button.configure(text="Update Feedback", font=font_app_button, state='disabled', command=getFeedback)
        self.source_feedback_button.place(relx=0.75, rely=0.01, height=30, width=150)
        
        self.source_table = Listbox(self.source_frame)
        self.source_table.configure(relief=RIDGE, font=font_table_list)
        self.source_table.place(relx=0.02, rely=0.075, relheight=0.9, relwidth=0.96)
        self.source_table.insert(END,"Select { Open Source File } to view")
        self.source_table_scrollBar = ttk.Scrollbar(self.source_table, orient="vertical")
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

        self.xml_addBreak = Button(self.xml_frame)
        self.xml_addBreak.configure(text="Add Breakpoints", font=font_app_button, state='disabled', command=addBreakpoint)
        self.xml_addBreak.place(relx=0.65, rely=0.01, height=30, width=150)

        header = ["#","Breakpoint","Loop","Register","Mask"]
       	self.xml_table = ttk.Treeview(self.xml_frame, selectmode="none",columns=header, show="headings")
       	self.xml_table.place(relx=0.02, rely=0.0925, relheight=0.87, relwidth=0.945)
        self.xml_table_scrollBar = ttk.Scrollbar(self.xml_table, orient="vertical", command=self.xml_table.yview)
        self.xml_table_scrollBar.pack(side="right", fill="y")
       	self.xml_table.configure(yscrollcommand=self.xml_table_scrollBar.set)
        self.xml_table.bind('<Button-1>', handle_click)
       	self.xml_table.column('#1', width=10)
        self.xml_table.column('#2', width=75)
        self.xml_table.column('#3', width=75)
        self.xml_table.column('#4', width=75)
        self.xml_table.column('#5', width=75)
       	for col in header:
       		self.xml_table.heading(col, text=col.title())
		

    def reg(self, top):

        self.reg_frame = Frame(top)
        self.reg_frame.configure(relief=GROOVE, borderwidth="1")
        self.reg_frame.place(relx=0.77, rely=0.075, relheight=0.4, relwidth=0.23)

        self.reg_title = Label(self.reg_frame)
        self.reg_title.configure(text="Register Table", font=font_table_title, anchor=NW)
        self.reg_title.place(relx=0.02, rely=0.02, relheight=0.2, relwidth=0.5)

        self.reg_label = Label(self.reg_frame)
        self.reg_label.configure(text="set       to", font=font_app_button)
        self.reg_label.place(relx=0.4, rely=0.01, height=30, width=100)

        self.reg_entry1 = Entry(self.reg_frame)
        self.reg_entry1.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.reg_entry1.place(relx=0.52, rely=0.01, height=30, width=25)

        self.reg_entry2 = Entry(self.reg_frame)
        self.reg_entry2.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.reg_entry2.place(relx=0.65, rely=0.01, height=30, width=30)

        self.reg_refresh = Button(self.reg_frame)
        self.reg_refresh.configure(text="Refresh", font=font_app_button, state='disabled', command=refreshRegisters)
        self.reg_refresh.place(relx=0.75, rely=0.01, height=30, width=75)

        header = ["Name","Address","Value"]
       	self.reg_table = ttk.Treeview(self.reg_frame, columns=header, show="headings")
       	self.reg_table.place(relx=0.02, rely=0.0925, relheight=0.87, relwidth=0.945)
        self.reg_table_scrollBar = ttk.Scrollbar(self.reg_table, orient="vertical", command=self.reg_table.yview)
        self.reg_table_scrollBar.pack(side="right", fill="y")
       	self.reg_table.configure(yscrollcommand=self.reg_table_scrollBar.set)
        self.reg_table.bind('<Button-1>', handle_click)
        self.reg_table.column('#1', width=10)
        self.reg_table.column('#2', width=100)
        self.reg_table.column('#3', width=100)
       	for col in header:
       		self.reg_table.heading(col, text=col.title())
       	


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
        self.gdb_table_scrollBar = ttk.Scrollbar(self.gdb_table, orient="vertical")
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
    	self.menuBar.add_command(label="Open Source File",command=onClick_cFile)
    	self.menuBar.add_command(label="Open XML File",command=onClick_xmlFile)
    	self.menuBar.add_command(label="Exit Application",command=top.quit)
    	top.config(menu=self.menuBar)

if __name__ == '__main__':
    create_mainwindow()

# ***** EOF *****