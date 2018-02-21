from subprocess import *
import subprocess
import tempfile
import time
import untangle
import re
import string
from mask import mask



from Tkinter import *


class trigger1:
    bp = ""
    lp =""
    regList = []
    mask = ""


class trigger:
    reg = ""
    val = ""
    op = ""


class Model:


    faults = []
    cFile = ""
    xmlFile = ""
    topLevel = None
    pluginProcess = None
    tempf = None
    feedbackLine = None
    #machineCode =[]
    pointer = 0
    #machineIndex = 0
    regList = ['r0', 'r1', 'r3', 'pc']#, 'r5', 'r6', 'r7', 'r8', 'r9', 'r11', 'r12']#, 'sp', 'lr', 'pc', 'cpsr']

    def __init__(self, top):
        self.topLevel = top
        self.tempf = tempfile.TemporaryFile()


    def printOutput(self, lines):
        #print line
        time.sleep(0.1)
        for line in lines.split('\n'):
            if line == "(gdb) ": return
            line = " > [" + line + "]"
            self.topLevel.gdb_table.insert(END, line)
            self.topLevel.gdb_table.update()
            self.topLevel.gdb_table.see("end")

    def selectFeedback(self, lineNo):
        
        #print "Selecting FeedBack"

        if self.feedbackLine is None:
            self.feedbackLine = lineNo
            self.topLevel.source_table.itemconfig(int(lineNo) - 1,{'bg':'#98FB98'})
        else:
            self.topLevel.source_table.itemconfig(int(self.feedbackLine) - 1,{'bg':'white'})
            self.topLevel.source_table.itemconfig(int(lineNo) - 1,{'bg':'#98FB98'})
            self.feedbackLine = lineNo

        self.topLevel.source_table.update()
             
    def populateFaults(self):
        self.faults = []
        for item in self.xmlFile.xml.fault:
            addr = item.addr['breakpointAddress']
            
            trig = []
            for masks in item.trigger.mask:
                newTrigger = trigger()
                newTrigger.reg = masks.rg['register'] 
                newTrigger.val = masks.mk['val']
                newTrigger.op = masks.mk['op']
                trig.append(newTrigger)

            self.faults.append((addr, trig))



    def populateFaults1(self):
        self.faults = []
        for item in self.xmlFile.xml.action:
            newTrigger = trigger()
            newTrigger.regList = []
            for reg in item.rg['registerList'][1:-1].split(','):
                newTrigger.regList.append(reg.split()[0])
            newTrigger.bp = item.bp['breakpointAddress']
            newTrigger.lp = item.lp['loopCounter']
            newTrigger.mask = item.mk['mask']
            self.faults.append(newTrigger)


    def connect(self):
        file = self.cFile
        subprocess.call("arm-linux-gnueabi-gcc -g {0} -o {1}-arm -static".format(file, file.split('.')[0]) , shell=True, stdout=subprocess.PIPE)
        subprocess.call("fuser -n tcp -k 1234", shell=True,stdout=subprocess.PIPE)
        qemuProcess = Popen("qemu-arm -singlestep -g 1234 {0}-arm".format(file.split('.')[0]), shell=True)
        #self.printOutput("QEMU launched on port 1234")

        self.pluginProcess = Popen('arm-none-eabi-gdb', stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=self.tempf)
        self.pluginProcess.stdin.write("file {0}-arm\n".format(file.split('.')[0]))
        self.pluginProcess.stdin.write("target remote localhost: 1234\n")
        self.pluginProcess.stdin.write("set pagination off\n")

        line = self.read()

        self.sendCommand("info R")
        #self.addBreakpoints()


    def showAssemCode(self, lineNo):

        #print lineNo
        self.topLevel.machine_table.delete(0, END)
        self.pluginProcess.stdin.write("B " + str(lineNo + 1) + "\n")
        #self.sendCommand("B " + str(lineNo + 1))
        lines = self.read().split()
        #print lines

        if "(gdb)" in lines[0].lower():
            bpNum = lines[2]
            bpAddr = lines[4][:-1]
        else:
            bpNum = lines[1]
            bpAddr = lines[3][:-1]

        self.updateMachineCode(bpAddr)
        #self.sendCommand("info B")
        self.pluginProcess.stdin.write("del " + str(bpNum) + "\n")



    def updateMachineCode(self, bpAddr):

        
        #print "Address: " + bpAddr
        self.topLevel.machine_table.delete(0, END)
        self.pluginProcess.stdin.write("disassemble " + bpAddr + "\n")
        asmCode = self.read()
        #self.machineCode = []

        i = 0
        for line in asmCode.split("\n"):
            if "dump" in line.lower() or "(gdb)" in line: continue
            #self.machineCode.append(line)
            self.topLevel.machine_table.insert(END, line)
            
            if bpAddr[2:] in line.split()[0]:
                self.topLevel.machine_table.select_set(i)
                #self.machineIndex = i
            i = i + 1

        self.topLevel.machine_table.update()



    def triggerFault(self):

        self.connect()
        line = self.topLevel.machine_table.get(self.topLevel.machine_table.curselection())
        bpAddr = line.split()[0]


        # ADD BreakPOint
        self.sendCommand("B *" + bpAddr)

        # Continue Code
        self.sendCommand("continue")

        
        #Del Current BP
        self.sendCommand("del")

        #ADD FeedBack BreakPoint
        self.sendCommand("B " + self.feedbackLine)

        #Update REG Values
        self.updateRegs()

        self.sendCommand("info R")

        self.readGDB()

        self.checkFeedback()
        return
        #Continue for feedback 
        self.sendCommand("continue")




    def checkFeedback(self):
        #Continue for feedback 
        self.pluginProcess.stdin.write("c\n")

        response = self.read()
        self.printOutput(response)

        if "Breakpoint 2" in response:
            self.printOutput("SUCCESS Reached Feedback Line")
            self.topLevel.trig_fault_progress.create_oval(1,1,20,20, outline='black',fill='#98FB98',width=1)
        else:
            self.topLevel.trig_fault_progress.create_oval(1,1,20,20, outline='black',fill='red',width=1)
            self.printOutput("FAILED to reach FeedBack")
            self.connect()





    def updateRegs(self):
        for reg in self.regList:
            self.pluginProcess.stdin.write("info R " + reg + "\n")
            val = self.read()
            regVal = val.split()[2]
            #print reg , regVal ,
            newVal = str(mask("flipAlt", regVal))
            self.sendCommand("set $" + reg + "=" + newVal)



    def addBreakpoints(self):
        for item in self.faults:
            bp = item[0]

            self.connect()

            if bp[0:2] == "0x":
                self.sendCommand("B *" + bp)
            else: self.sendCommand("B " + bp)
            
            # Continue Code
            self.sendCommand("continue")

            
            #Del Current BP
            self.sendCommand("del")

            #ADD FeedBack BreakPoint
            self.sendCommand("B " + self.feedbackLine)


            for trigger in item[1]:
                reg = trigger.reg

                if trigger.op == "const":
                    newVal = trigger.val
                    self.sendCommand("set $" + reg + "=" + newVal)
                    continue

                self.pluginProcess.stdin.write("info R " + reg + "\n")
                val = self.read()
                regVal = val.split()[2]

                newVal = str(mask(trigger.op, regVal, trigger.val))
                self.sendCommand("set $" + reg + "=" + newVal)


            self.sendCommand("info R")

            self.readGDB()

            self.checkFeedback()




    def addBreakpoints1(self):

        bpNum = 1
        for trigger in self.faults:
            bp = trigger.bp


            if bp[0:2] == "0x":
                self.pluginProcess.stdin.write("B *" + bp + "\n")
            else: self.pluginProcess.stdin.write("B " + bp + "\n")
            

            self.pluginProcess.stdin.write("ignore " + str(bpNum) + " " + trigger.lp + "\n")
            
            self.pluginProcess.stdin.write("commands\n")
            
            self.pluginProcess.stdin.write("info R\n")
            

            for reg in trigger.regList:
                self.pluginProcess.stdin.write("set $" + reg + "=0\n")
            
            self.pluginProcess.stdin.write("del " + str(bpNum) + "\n")

            if bpNum == len(self.faults):
                self.pluginProcess.stdin.write("B add\n")
            
            self.pluginProcess.stdin.write("info R\n")

            self.pluginProcess.stdin.write("c\n")

            self.pluginProcess.stdin.write("end\n")

            bpNum = bpNum + 1 
            self.readGDB()
        


    def readReg(self):
        self.topLevel.reg_table.delete(*self.topLevel.reg_table.get_children())
        line = self.read()
        for text in line.split('\n')[:-1]:
            row = ""
            for word in text.split():
                row = "{0}{1:15}".format(row, word)
            self.topLevel.reg_table.insert('', END, values=row)

    
    def sendCommand(self, line):
    	self.pluginProcess.stdin.write(line + "\n")

    	if line == "info R" or line == "info r":
    		self.readReg()
    	else:
            self.printOutput(line)
            self.readGDB()


    def read(self):
        time.sleep(0.1)
        self.tempf.seek(self.pointer)
        line  = self.tempf.read()
        self.pointer = self.tempf.tell()
        return line


    def readGDB(self):
    	data = self.read()
        for line in data.split('\n'):
            #if "(gdb)" in line: continue
            self.printOutput(line)
        

    def importXML(self, fileName):
        self.xmlFile = untangle.parse(fileName)
        self.populateFaults()

    def importCFile(self,fileName):
        self.cFile = fileName

    def getFaults(self):
        return self.faults

def initModel(top):
    model = Model(top)
    return model




