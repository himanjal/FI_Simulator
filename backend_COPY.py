import untangle
from tkFileDialog import askopenfilename

# class trigger:
#     bp = ""
#     lp =""
#     regList = []
#     mask = ""

class trigger:
	reg = ""
	val = ""
	op = ""

faults = []

def populateFaults(xmlFile):
    for item in xmlFile.xml.fault:
        addr = item.addr['breakpointAddress']
        
        trig = []
        for masks in item.trigger.mask:
	        newTrigger = trigger()
	        newTrigger.reg = masks.rg['register'] 
	        newTrigger.val = masks.mk['op']
	        newTrigger.op = masks.mk['val']
	        trig.append(newTrigger)

        faults.append((addr, trig))


# Open XML File

filenameXML = askopenfilename(initialdir = "./documents",title = "Select XML file",filetypes = (("xml files","*.xml"),("all files","*.*")))
populateFaults(untangle.parse(filenameXML))

for item in faults:
    print item[0]
    for masks in item[1]:
    	print masks.reg, masks.val, masks.op