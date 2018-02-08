
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


# ***** Variables *****
entity = None

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

# Insert print terminal now on GDB Output
def printOutput(line):
    output = " > [ " + line + " ]"
    print output
    top.gdb_table.insert(END, output)

# Function when clicking on the "Open XML File" Button
def onClick_xmlFile():
    filenameXML = askopenfile()

    if filenameXML is None:
        return
    top.gdb_table.delete(0,END)	
    entity.importXML(filenameXML)
    printOutput("Opened < {0} > Successfully ... ".format(os.path.basename(filenameXML.name)))
    
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
    
    entity.importCFile(filenameC)
    printOutput("Opened < {0} > Successfully ... ".format(os.path.basename(filenameC)))

    top.connect_qemu.configure(state='active')
    printOutput("Ready to Connect to QEMU...")

# Function when clicking on the "Connect to Qemu" Button
def onClick_connectQemu():
	printOutput("Connecting to Qemu ...")
	entity.connect()
	printOutput("Connected to Qemu Sucessfully ...")

# Function when clicking on the "Enter" Button for the Command Line
def onClick_enter():
    entity.sendCommand(top.command_entry.get())
    #ity.readGDB()

# ***** GUI *****

# When Creating Application
def create_mainwindow():
    '''Starting point when module is the main routine.'''
    global val, w, root, top, entity
    root = Tk()
    top = mainwindow (root)
    entity = initModel(top)
    root.mainloop()

# When Exiting Application
def destroy_mainwindow():
    global w
    w.destroy()
    w = None

# GUI Core
class mainwindow:

    def __init__(self, top=None):

        top.geometry("1000x1000+335+110")
        top.title("mainwindow")
        top.configure(background="#ffffff")
        top.configure(highlightcolor="black")

        self.title(top)
        self.xml(top)
        self.gdb(top)
        self.reg(top)
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
        self.open_xml_file.place(relx=0.47, rely=0.29, height=30, width=150)
        self.open_xml_file.configure(activebackground="#d9d9d9")
        self.open_xml_file.configure(text='''1) Open XML File''')
        self.open_xml_file.configure(command=onClick_xmlFile)

        self.open_c_file = Button(self.title_frame)
        self.open_c_file.place(relx=0.64, rely=0.29, height=30, width=150)
        self.open_c_file.configure(activebackground="#d9d9d9")
        self.open_c_file.configure(text='''2) Open C File''')
        self.open_c_file.configure(command=onClick_cFile)
        self.open_c_file.configure(state='disabled')

        self.connect_qemu = Button(self.title_frame)
        self.connect_qemu.place(relx=0.81, rely=0.29, height=30, width=150)
        self.connect_qemu.configure(activebackground="#d9d9d9")
        self.connect_qemu.configure(text='''3) Connect To Qemu''')
        self.connect_qemu.configure(command=onClick_connectQemu)
        self.connect_qemu.configure(state='disabled')

    def xml(self, top):

        self.xml_frame = Frame(top)
        self.xml_frame.place(relx=0.01, rely=0.09, relheight=0.3, relwidth=0.49)
        self.xml_frame.configure(relief=GROOVE)
        self.xml_frame.configure(borderwidth="2")
        self.xml_frame.configure(relief=GROOVE)
        self.xml_frame.configure(width=485)

        self.xml_title = Label(self.xml_frame)
        self.xml_title.place(relx=0.02, rely=0.03, height=23, width=87)
        self.xml_title.configure(activebackground="#f9f9f9")
        self.xml_title.configure(font=font12)
        self.xml_title.configure(justify=LEFT)
        self.xml_title.configure(text='''XML Table''')

        self.xml_attr = Label(self.xml_frame)
        self.xml_attr.place(relx=0.02, rely=0.1, height=18, width=439)
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
        self.reg_frame.place(relx=0.5, rely=0.09, relheight=0.3, relwidth=0.49)
        self.reg_frame.configure(relief=GROOVE)
        self.reg_frame.configure(borderwidth="2")
        self.reg_frame.configure(relief=GROOVE)
        self.reg_frame.configure(width=485)

        self.reg_title = Label(self.reg_frame)
        self.reg_title.place(relx=0.02, rely=0.03, height=23, width=78)
        self.reg_title.configure(activebackground="#f9f9f9")
        self.reg_title.configure(anchor=W)
        self.reg_title.configure(font=font12)
        self.reg_title.configure(justify=LEFT)
        self.reg_title.configure(text='''Registers''')

        self.reg_attr = Label(self.reg_frame)
        self.reg_attr.place(relx=0.02, rely=0.1, height=18, width=414)
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
        #self.reg_table.insert(END,'''Info R not yet implemented''')

    def gdb(self, top):

        self.gdb_frame = Frame(top)
        self.gdb_frame.place(relx=0.01, rely=0.39, relheight=0.55, relwidth=0.98)
        self.gdb_frame.configure(relief=GROOVE)
        self.gdb_frame.configure(borderwidth="2")
        self.gdb_frame.configure(relief=GROOVE)
        self.gdb_frame.configure(width=990)

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

    def command(self, top):

        self.command_frame = Frame(top)
        self.command_frame.place(relx=0.01, rely=0.94, relheight=0.05, relwidth=0.98)
        self.command_frame.configure(relief=GROOVE)
        self.command_frame.configure(borderwidth="2")
        self.command_frame.configure(relief=GROOVE)
        self.command_frame.configure(width=990)

        self.command_title = Label(self.command_frame)
        self.command_title.place(relx=0.01, rely=0.27, height=23, width=46)
        self.command_title.configure(activebackground="#f9f9f9")
        self.command_title.configure(font=font9)
        self.command_title.configure(text='''(gdb)''')

        self.command_entry = Entry(self.command_frame)
        self.command_entry.place(relx=0.07, rely=0.16,height=30, relwidth=0.84)
        self.command_entry.configure(background="white")
        self.command_entry.configure(font="TkFixedFont")
        self.command_entry.configure(selectbackground="#c4c4c4")

        #self.command_entry.bind('<Return>', onClick_enter)

        self.command_enter = Button(self.command_frame)
        self.command_enter.place(relx=0.93, rely=0.22, height=26, width=59)
        self.command_enter.configure(activebackground="#d9d9d9")
        self.command_enter.configure(text='''Enter''')
        self.command_enter.configure(command=onClick_enter)

if __name__ == '__main__':
    create_mainwindow()

# ***** EOF *****