from subprocess import *
import subprocess
import tempfile
import time
import untangle
import re


from Tkinter import *


class trigger:
    bp = ""
    lp =""
    regList = []
    mask = ""



class Model:


    faults = []
    cFile = ""
    xmlFile = ""
    topLevel = None
    pluginProcess = None
    tempf = None
    machineCode =[]
    pointer = 0
    machineIndex = 0

    def __init__(self, top):
        self.topLevel = top
        self.tempf = tempfile.TemporaryFile()


    def printOutput(self, line):
        #print line
        self.topLevel.gdb_table.insert(END, line)
        self.topLevel.gdb_table.update()
        self.topLevel.gdb_table.see("end")



    def populateFaults(self):
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

        #self.printOutput("GDB Connected to QEMU")
        self.readGDB()
        self.sendCommand("info R")
        self.addBreakpoints()


    def showAssemCode(self, lineNo):

        #print lineNo
        self.topLevel.machine_table.delete(0, END)
        self.pluginProcess.stdin.write("B " + str(lineNo + 1) + "\n")
        #self.sendCommand("B " + str(lineNo + 1))
        time.sleep(0.1)
        self.tempf.seek(self.pointer)
        lines = self.tempf.read().split()
        print lines
        if "note" in lines[0].lower():
            bpNum = lines[9]
            bpAddr = lines[11][:-1]
        else:
            bpNum = lines[1]
            bpAddr = lines[3][:-1]

        self.pointer = self.tempf.tell()
        self.updateMachineCode(bpAddr)
        #self.sendCommand("info B")
        self.sendCommand("del " + str(bpNum))



    def updateMachineCode(self, bpAddr):

        self.topLevel.machine_table.delete(0, END)
        print "Address: " + bpAddr
        self.pluginProcess.stdin.write("disassemble " + bpAddr + "\n")
        asmCode = self.read()
        self.machineCode = []

        i = 0
        for line in asmCode.split("\n"):
            if "dump" in line.lower() or "(gdb)" in line: continue
            self.machineCode.append(line)
            self.topLevel.machine_table.insert(END, line)
            
            if bpAddr[2:] in line.split()[0]:
                self.topLevel.machine_table.select_set(i)
                self.machineIndex = i
            i = i + 1

        self.topLevel.machine_table.update()



    def triggerFault(self):
        print self.topLevel.machine_table.get(self.topLevel.machine_table.curselection())






    def triggerFault2(self):

        index = self.machineIndex
        length = len(self.machineCode) - 1
        while True:
            #self.topLevel.machine_table.itemconfig(i,{'bg':'white'})
            #self.topLevel.machine_table.itemconfig(i+1,{'bg':'light grey'})
            #self.topLevel.machine_table.update()
            line = self.machineCode[self.machineIndex]
            print line
            reg = re.findall("r\d{1}",line)
            if not reg:
                print "no reg"
            else:
                for r in reg:
                    print r ,
                print ""
                #self.sendCommand("i r " + r)

            print "index = " + str(self.machineIndex) + "Length = " + str(len(self.machineCode)) 
            if self.machineIndex == len(self.machineCode) - 1:
                break

            self.pluginProcess.stdin.write("si\n")
            add = self.read()
            self.printOutput(add)
            address = add.split()[0] 
            if address.startswith("0x"):
                self.updateMachineCode(address)
            time.sleep(2)




    def addBreakpoints(self):

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
        self.topLevel.reg_table.delete(0,END)
    	line = self.read()
    	for text in line.split('\n')[:-1]:
    		row = ""
    		for word in text.split():
    			row = "{0}{1:12}".format(row, word)
    		self.topLevel.reg_table.insert(END, row)





    def sendCommand(self, line):
        self.topLevel.gdb_table.insert(END,line)
    	self.pluginProcess.stdin.write(line + "\n")

    	if line == "info R" or line == "info r":
    		self.readReg()
    	else:
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
            if "(gdb)" in line: continue
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




