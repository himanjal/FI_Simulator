from subprocess import *
import subprocess
import tempfile
import time
import untangle


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

    def __init__(self, top):
        self.topLevel = top

    def populateFaults(self):
        self.faults = []
        for item in xmlFile.xml.action:
            newTrigger = trigger()
            newTrigger.regList = []
            for reg in item.rg['registerList'][1:-1].split(','):
                newTrigger.regList.append(reg.split()[0])
            newTrigger.bp = item.bp['breakpointAddress']
            newTrigger.lp = item.lp['loopCounter']
            newTrigger.mask = item.mk['mask']
            self.faults.append(newTrigger)
            



    def importXML(self, fileName):
        global xmlFile
        xmlFile = untangle.parse(fileName)
        self.populateFaults()



    def getFaults(self):
        return self.faults

def initModel(top):
    model = Model(top)
    return model




