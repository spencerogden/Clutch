#!/usr/bin/python

# Instrument interface
# Focus on USDB/Serial interface with H3000
# Input of all available variables and storing of current value
# Syncing of calibration settings
# Interaction with Clock, Active Mark, etc
# Display control

import threading
import random
import time
import csv

import observable
import varmaps

class Instruments(observable.Observable):
    def __init__(self,name):
        super(Instruments,self).__init__()
        self.name = name
        self.data = {}
#        self.observers = []
            
#     def dataUpdate(self,data,source):        
#         self.data.update(data)
#         self.notifyObservers(data)
#         for obs in self.observers:
#             obs(data=data,source=source)
#                 
#     def addObserver(self,observerFunction):
#         self.observers.append(observerFunction)
#        
#     def removeObserver(self,observerFunction):
#         self.observers.remove(observerFunction)    
    
        
class RandomInstruments(Instruments,threading.Thread):
    def __init__(self,name,num):
        threading.Thread.__init__(self)
        Instruments.__init__(self,name)
        self.halt = False
        self.num = num
        
    def run(self):
        print self.name + " Random Instrument monitor started\n"
        newdata = {'source': self.name}
        time.sleep(int(random.random()*5))
        while not self.halt:
            time.sleep(.1)
            for i in range(1,self.num+1):
                newdata['rand'+str(i)] = random.random() * 10
            self.notifyObservers(newdata)

        print self.name + " Random Instrument monitor stopped\n"
            
    def stop(self):
        self.halt = True

class LogReaderInstruments(Instruments,threading.Thread):
    def __init__(self,name,file):
        threading.Thread.__init__(self)
        Instruments.__init__(self,name)
        self.halt = False
        self.file = file
        self.fh = open(file,'rb')
        
    def run(self):
        print self.name + " Log Reader started: " + self.file
        newdata = {'source': self.name}
        map = varmaps.ExpeditionLogMap()
        
        while not self.halt:
            log = csv.DictReader(self.fh)
            for rawdata in log:
                time.sleep(.01)
                if self.halt:
                    break
                newdata.update(dict((k, rawdata[k]) for k,v in rawdata.iteritems() if not(v == '' or v == None)))
                self.notifyObservers(map.frm(newdata))
                #print '.'
            print "Restarting log " + self.file
            self.fh.seek(0)
            
    def stop(self):
        self.halt = True
        
class InstrumentsMerge(Instruments):
    def __init__(self):
        Instruments.__init__(self,"Master")
        self.instruments = {}
        self.observers = []

        self.var_owners = {} # A dict of sources, values are sets of which vars they own

        self.datalock = threading.Lock()
        
    def addInstruments(self, inst):
        self.instruments[inst.name] = inst
        inst.subscribe(self.dataUpdate)
        inst.start()
        
    def stop(self):
        for insts in self.instruments.values():
            if insts.is_alive():
                insts.stop()
                insts.join()
        print "instruments stopped"
            
    def dataUpdate(self,data):
        with self.datalock:
            source = data.get('source')
            newvars = set(data.keys())

            unowned_vars = newvars.difference(*self.var_owners.values()) # These vars are not owned and can be claimed
            source_owns = newvars.intersection(self.var_owners.get(source,set())) # These vars are owned by this source
            update_vars = source_owns.union(unowned_vars) # we can update unowned vars and vars owned by this source

            if update_vars:
                self.var_owners.get(source,set()).union(update_vars) # Source claims these vars
                newdata = dict((k, data[k]) for k in update_vars)
                newdata['source']=source
                self.notifyObservers(data=newdata)
      
    def changeOwner(self,var_name):
        with self.datalock:
            s = set([var_name,])
            for owner in self.var_owners.keys():
                self.var_owners[owner].difference_update(s)
            self.var_owners.get(source,set()).update(s)