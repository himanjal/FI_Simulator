
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

_bgcolor = '#d9d9d9'  # X11 color: 'gray85'
_fgcolor = '#000000'  # X11 color: 'black'
_compcolor = '#d9d9d9' # X11 color: 'gray85'
_ana1color = '#d9d9d9' # X11 color: 'gray85' 
_ana2color = '#d9d9d9' # X11 color: 'gray85' 
font10 = "-family {Bitstream Vera Serif} -size 20 -weight bold"  \
    " -slant roman -underline 0 -overstrike 0"
font11 = "-family {DejaVu Sans} -size 10 -weight normal -slant"  \
    " italic -underline 0 -overstrike 0"
font12 = "-family {DejaVu Sans} -size 12 -weight normal -slant"  \
    " roman -underline 1 -overstrike 0"
font15 = "-family {DejaVu Sans} -size 0 -weight normal -slant "  \
    "roman -underline 0 -overstrike 0"
font17 = "TkDefaultFont"
font18 = "TkDefaultFont"
font9 = "-family {DejaVu Sans} -size 12 -weight normal -slant "  \
    "roman -underline 0 -overstrike 0"

# ***** Functions *****

def automateTest():
	onClick_xmlFile()
	onClick_cFile()
	onClick_connectQemu()

# Insert print terminal now on GDB Output
def printOutput(line):
    output = " > [ " + line + " ]"
    print output
    top.gdb_table.insert(END, output)

# Function when clicking on the "Open XML File" Button
def onClick_xmlFile():
    filenameXML = askopenfile()
    basename = os.path.basename(filenameXML.name)
    if filenameXML is None:
        return
    top.gdb_table.delete(0,END)	
    entity.importXML(filenameXML)
    printOutput("Opened < {0} > Successfully ... ".format(basename))
    
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
    
    top.open_c_file.configure(state='active')
    printOutput("Ready to Open C File...")

# Function when clicking on the "Open C File" Button
def onClick_cFile():
    filenameC = askopenfilename()
    if filenameC is None:
        return
    basename = os.path.basename(filenameC)
    entity.importCFile(filenameC)
    printOutput("Connected < {0} > Successfully ... ".format(basename))
    
    top.cprog_table.delete(0,END)	

    #print inspect.getsource(basename)
    with open (filenameC, "r") as myfile:
    	strF = myfile.read()
    	
    	for line in strF.split('\n'):
    		top.cprog_table.insert(END, line)

    	myfile.close()

    top.connect_qemu.configure(state='active')
    printOutput("Ready to Connect to QEMU...")

def clickProgLine(event):
	w = event.widget
	index = int(w.curselection()[0])
	value = w.get(index)
	top.addBreakpoint.configure(state='active')
	top.trigFault.configure(state='normal')

	printOutput('You selected line %d: "%s"' % (index, value))

# Function when clicking on the "Connect to Qemu" Button
def onClick_connectQemu():
	top.command_enter.configure(state='active')
	top.command_entry.configure(state='normal')
	entity.connect()
	#printOutput("Connected to Qemu Sucessfully ...")

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

# GUI Core
class mainwindow:

    def __init__(self, top):

        top.geometry("1500x1000+335+110")
        top.title("Fault Injection Simulator")
        top.configure(background="#ffffff")
        top.configure(highlightcolor="black")

        self.title(top)
        self.xml(top)
        self.cfile(top)
        self.reg(top)
        self.gdb(top)
        self.command(top)


    def title(self, top):

        self.title_frame = Frame(top)
        self.title_frame.place(relx=0.01, rely=0.01, relheight=0.08, relwidth=0.98)
        self.title_frame.configure(relief=GROOVE)
        self.title_frame.configure(borderwidth="2")
        self.title_frame.configure(relief=GROOVE)
        self.title_frame.configure(width=980)

        self.title_label = Label(self.title_frame)
        self.title_label.place(relx=0.01, rely=0.16, height=50, width=425)
        self.title_label.configure(activebackground="#f9f9f9")
        self.title_label.configure(anchor=W)
        self.title_label.configure(font=font10)
        self.title_label.configure(text='''Fault Injection Simulator''')

        self.open_xml_file = Button(self.title_frame)
        self.open_xml_file.place(relx=0.55, rely=0.29, height=30, width=150)
        self.open_xml_file.configure(activebackground="#d9d9d9")
        self.open_xml_file.configure(text='''1) Open XML File''')
        self.open_xml_file.configure(command=onClick_xmlFile)

        self.open_c_file = Button(self.title_frame)
        self.open_c_file.place(relx=0.7, rely=0.29, height=30, width=150)
        self.open_c_file.configure(activebackground="#d9d9d9")
        self.open_c_file.configure(text='''2) Open C File''')
        self.open_c_file.configure(command=onClick_cFile)
        self.open_c_file.configure(state='disabled')

        self.connect_qemu = Button(self.title_frame)
        self.connect_qemu.place(relx=0.85, rely=0.29, height=30, width=200)
        self.connect_qemu.configure(activebackground="#d9d9d9")
        self.connect_qemu.configure(text='''3) Connect To GDB Server''')
        self.connect_qemu.configure(command=onClick_connectQemu)
        self.connect_qemu.configure(state='disabled')

    def cfile(self, top):

        self.cprog_frame = Frame(top)
        self.cprog_frame.place(relx=0.01, rely=0.09, relheight=0.9, relwidth=0.49)
        self.cprog_frame.configure(relief=GROOVE)
        self.cprog_frame.configure(borderwidth="2")
        self.cprog_frame.configure(relief=GROOVE)
        self.cprog_frame.configure(width=450)

        self.cprog_title = Label(self.cprog_frame)
        self.cprog_title.place(relx=0.02, rely=0.02, height=23, width=420)
        self.cprog_title.configure(activebackground="#f9f9f9")
        self.cprog_title.configure(font=font12)
        self.cprog_title.configure(anchor=W)
        self.cprog_title.configure(justify=LEFT)
        self.cprog_title.configure(text='''Assembly Program''')

        self.addBreakpoint = Button(self.cprog_frame)
        self.addBreakpoint.place(relx=0.5, rely=0.01, height=30, width=150)
        self.addBreakpoint.configure(activebackground="#d9d9d9")
        self.addBreakpoint.configure(text='''Add Breakpoint''')
        #self.connect_qemu.configure(command=onClick_addBreakpoint)
        self.addBreakpoint.configure(state='disabled')

        self.trigFault = Button(self.cprog_frame)
        self.trigFault.place(relx=0.75, rely=0.01, height=30, width=150)
        self.trigFault.configure(activebackground="#d9d9d9")
        self.trigFault.configure(text='''Trigger Fault''')
        #self.connect_qemu.configure(command=onClick_addBreakpoint)
        self.trigFault.configure(state='disabled')

        self.cprog_table = Listbox(self.cprog_frame)
        self.cprog_table.place(relx=0.02, rely=0.055, relheight=0.935, relwidth=0.96)
        self.cprog_table.configure(font=font18)
        self.cprog_table.configure(relief=RIDGE)
        self.cprog_table.configure(selectbackground="#c4c4c4")
        self.cprog_table.configure(width=470)
        self.cprog_table.insert(END,'''Assembly File not yet Imported''')
        self.cprog_table.bind("<<ListboxSelect>>", clickProgLine)

    def xml(self, top):

        self.xml_frame = Frame(top)
        self.xml_frame.place(relx=0.5, rely=0.09, relheight=0.3, relwidth=0.29)
        self.xml_frame.configure(relief=GROOVE)
        self.xml_frame.configure(borderwidth="2")
        self.xml_frame.configure(relief=GROOVE)
        self.xml_frame.configure(width=450)

        self.xml_title = Label(self.xml_frame)
        self.xml_title.place(relx=0.02, rely=0.03, height=23, width=87)
        self.xml_title.configure(activebackground="#f9f9f9")
        self.xml_title.configure(font=font12)
        self.xml_title.configure(justify=LEFT)
        self.xml_title.configure(text='''XML Table''')

        self.xml_attr = Label(self.xml_frame)
        self.xml_attr.place(relx=0.02, rely=0.1, height=18, width=420)
        self.xml_attr.configure(activebackground="#f9f9f9")
        self.xml_attr.configure(anchor=W)
        self.xml_attr.configure(font=font11)
        self.xml_attr.configure(justify=LEFT)
        self.xml_attr.configure(text='''Num   Breakpoint      Loop   Register                                 Mask''')

        self.xml_table = Listbox(self.xml_frame)
        self.xml_table.place(relx=0.02, rely=0.17, relheight=0.8, relwidth=0.96)
        self.xml_table.configure(font=font18)
        self.xml_table.configure(relief=RIDGE)
        self.xml_table.configure(selectbackground="#c4c4c4")
        self.xml_table.configure(width=470)
        self.xml_table.insert(END,'''XML not yet Imported''')

    def reg(self, top):

        self.reg_frame = Frame(top)
        self.reg_frame.place(relx=0.79, rely=0.09, relheight=0.3, relwidth=0.2)
        self.reg_frame.configure(relief=GROOVE)
        self.reg_frame.configure(borderwidth="2")
        self.reg_frame.configure(relief=GROOVE)
        self.reg_frame.configure(width=450)

        self.reg_title = Label(self.reg_frame)
        self.reg_title.place(relx=0.02, rely=0.03, height=23, width=90)
        self.reg_title.configure(activebackground="#f9f9f9")
        self.reg_title.configure(anchor=W)
        self.reg_title.configure(font=font12)
        self.reg_title.configure(justify=LEFT)
        self.reg_title.configure(text='''Registers''')

        self.reg_attr = Label(self.reg_frame)
        self.reg_attr.place(relx=0.02, rely=0.1, height=18, width=200)
        self.reg_attr.configure(activebackground="#f9f9f9")
        self.reg_attr.configure(anchor=W)
        self.reg_attr.configure(font=font11)
        self.reg_attr.configure(text='''Name     Address     Value''')

        self.reg_table = Listbox(self.reg_frame)
        self.reg_table.place(relx=0.02, rely=0.17, relheight=0.8, relwidth=0.96)
        self.reg_table.configure(font=font17)
        self.reg_table.configure(relief=RIDGE)
        self.reg_table.configure(selectbackground="#c4c4c4")
        self.reg_table.configure(width=480)
        self.reg_table.insert(END,'''Registers not yet Implemented''')

    def gdb(self, top):

        self.gdb_frame = Frame(top)
        self.gdb_frame.place(relx=0.5, rely=0.39, relheight=0.55, relwidth=0.49)
        self.gdb_frame.configure(relief=GROOVE)
        self.gdb_frame.configure(borderwidth="2")
        self.gdb_frame.configure(relief=GROOVE)

        self.gdb_title = Label(self.gdb_frame)
        self.gdb_title.place(relx=0.01, rely=0.015, height=18, width=226)
        self.gdb_title.configure(activebackground="#f9f9f9")
        self.gdb_title.configure(anchor=W)
        self.gdb_title.configure(font=font12)
        self.gdb_title.configure(justify=LEFT)
        self.gdb_title.configure(text='''GNU Debugger''')

        self.gdb_table = Listbox(self.gdb_frame)
        self.gdb_table.place(relx=0.01, rely=0.06, relheight=0.92, relwidth=0.98)
        self.gdb_table.configure(background="white")
        self.gdb_table.configure(font="TkFixedFont")
        self.gdb_table.configure(selectbackground="#c4c4c4")
        self.gdb_table.configure(width=970)
        self.gdb_table.insert(END, '''Nothing Imported''')

        self.scrollbar = Scrollbar(top)
        self.scrollbar.pack(side=RIGHT, fill=Y)

    def command(self, top):

        self.command_frame = Frame(top)
        self.command_frame.place(relx=0.5, rely=0.94, relheight=0.05, relwidth=0.49)
        self.command_frame.configure(relief=GROOVE)
        self.command_frame.configure(borderwidth="2")
        self.command_frame.configure(relief=GROOVE)
        self.command_frame.configure(width=990)

        self.command_title = Label(self.command_frame)
        self.command_title.place(relx=0.01, rely=0.26, height=23, width=46)
        self.command_title.configure(activebackground="#f9f9f9")
        self.command_title.configure(font=font9)
        self.command_title.configure(text='''(gdb)''')

        self.command_entry = Entry(self.command_frame)
        self.command_entry.place(relx=0.08, rely=0.16,height=30, relwidth=0.8)
        self.command_entry.configure(background="white")
        self.command_entry.configure(font="TkFixedFont")
        self.command_entry.configure(state='disabled')
        self.command_entry.configure(selectbackground="#c4c4c4")
        self.command_entry.bind('<Return>', enterKey)

        self.command_enter = Button(self.command_frame)
        self.command_enter.place(relx=0.90, rely=0.22, height=26, width=59)
        self.command_enter.configure(activebackground="#d9d9d9")
        self.command_enter.configure(text='''Enter''')
        self.command_enter.configure(state='disabled')
        self.command_enter.configure(command=onClick_enter)

if __name__ == '__main__':
    create_mainwindow()

# ***** EOF *****