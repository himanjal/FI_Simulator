from subprocess import *
import subprocess
import tempfile
import time
import untangle



faults = []

class trigger:
	bp = ""
	lp =""
	regList = []
	mask = ""


def createTable():
	for item in obj.xml.action:
		newTrigger = trigger()
		newTrigger.regList = []
		for reg in item.rg['registerList'][1:-1].split(','):
			newTrigger.regList.append(reg.split()[0])
		newTrigger.bp = item.bp['breakpointAddress']
		newTrigger.lp = item.lp['loopCounter']
		newTrigger.mask = item.mk['mask']
		faults.append(newTrigger)
		


def printTrigger(self):
	print "{0}\t{1}\t{2}\t\t{3}".format(
		self.bp, 
		self.lp, 
		self.regList, 
		self.mask)


def readreg(text):

    for line in text.split('\n'):
        for word in line.split():
            print word, "\t" ,
        print " "
    print ""




def addBreakpoints():


	bpNum = 1
	for trigger in faults:
		bp = trigger.bp


		if bp[0:2] == "0x":
			pluginProcess.stdin.write("B *" + bp + "\n")
		else: pluginProcess.stdin.write("B " + bp + "\n")
		

		pluginProcess.stdin.write("ignore " + str(bpNum) + " " + trigger.lp + "\n")
		
		pluginProcess.stdin.write("commands\n")
		
		pluginProcess.stdin.write("info R\n")
		

		for reg in trigger.regList:
			pluginProcess.stdin.write("set $" + reg + "=0\n")
		
		pluginProcess.stdin.write("del " + str(bpNum) + "\n")

		if bpNum == len(faults):
			pluginProcess.stdin.write("B add\n")
		
		pluginProcess.stdin.write("info R\n")

		pluginProcess.stdin.write("c\n")

		pluginProcess.stdin.write("end\n")

		bpNum = bpNum + 1 
		
			


#file = raw_input("Enter File Name? ")
file = "test.c"


obj = untangle.parse('importXML.xml')
createTable()

subprocess.call("arm-linux-gnueabi-gcc -g {0} -o {1}-arm -static".format(file, file.split('.')[0]) , shell=True, stdout=subprocess.PIPE)
subprocess.call("fuser -n tcp -k 1234", shell=True,stdout=subprocess.PIPE)
qemuProcess = Popen("qemu-arm -singlestep -g 1234 {0}-arm".format(file.split('.')[0]), shell=True, stdout=subprocess.PIPE)


print "File ", file, " successfully compiled"
print "QEMU launched at port 1234"
print "\nConnecting to QEMU\n\n"


tempf = tempfile.TemporaryFile()



pluginProcess = Popen('arm-none-eabi-gdb', stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=tempf)
pluginProcess.stdin.write("file {0}-arm\n".format(file.split('.')[0]))
pluginProcess.stdin.write("target remote localhost: 1234\n")
pluginProcess.stdin.write("set pagination off\n")

print "Connected to Qemu using GDB"

addBreakpoints()


pointer = 0
time.sleep(0.1)
tempf.seek(pointer)
print tempf.read()
pointer = tempf.tell()
user_input = ""

while (True):

	user_input = raw_input("INPUT?")
	if user_input is None: break
	pluginProcess.stdin.write(user_input + "\n")
	time.sleep(0.1)
	tempf.seek(pointer)
	if user_input == "info R":
		readreg(tempf.read())
	else:
		print tempf.read()
	pointer = tempf.tell()

	


print "EOF"

