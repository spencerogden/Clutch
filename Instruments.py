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
import math
import sys

import geo

import observable
import varmaps

import socket
import Message

class Instruments(observable.Observable):
    def __init__(self,name):
        super(Instruments,self).__init__()
        self.name = name
        self.data = {}

class SimulatorInstruments(Instruments,threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        Instruments.__init__(self,name)
        self.halt = False
        
    def stop(self):
        self.halt = True
    
    def run(self):
        print "Instrument Simulator Started"
        t = 0
        pos = geo.Position(lat=0,lon=0)
        while not self.halt:
            
            time.sleep(0.01)
            t = (t+1) % sys.maxint
            
            twd = math.sin(t/1000.0)*15 % 360
            tws = math.sin(t/2000.0)*5 + 12.5
            
            base_heading = 90 * ((t/500) % 4 +1) - 45 + twd
            heading = base_heading + math.sin(t/50.0)*2 # in true
            
            base_boatspeed = 9 + cmp( abs(base_heading), 90)*2
            bsp = base_boatspeed + math.sin(t/100.0)*.25
            
            twa = 180 - ( heading - twd + 180 ) % 360 
            y = math.radians(90 - abs(twa)) # perform trig in absolute angles
            a = tws * math.cos(y)
            b = tws * math.sin(y)
            bb = bsp + b
            awa = math.degrees(math.radians(90) - math.atan( bb/a)) * cmp(twa,0) # recover sign of angle
            aws = (a**2 + bb**2)**0.5
            
            pos = pos.pos_at_range_bearing( (0.01/(60.0*60.0))*bsp, heading )
            
            newdata = {
                'Bsp': bsp,
                'Hdg': heading,
                'TWA': twa,
                'TWS': tws,
                'TWD': twd,
                'AWA': awa,
                'AWS': aws,
                'Lat': pos.lat,
                'Lon': pos.lon,
                'Pos': pos,
                }
                
            self.notifyObservers(newdata)
            
            #print "twd:%3.0f tws:%3.2f hdg:%3.0f bsp:%4.2f twa:%3.0f awa:%3.0f aws:%4.2f pos:%s" % \
            #    (twd,tws,heading,bsp,twa,awa,aws,pos)
        
class RandomInstruments(Instruments,threading.Thread):
    def __init__(self,name,num):
        threading.Thread.__init__(self)
        Instruments.__init__(self,name)
        self.halt = False
        self.num = num
        
    def run(self):
        print self.name + " Random Instrument monitor started"
        newdata = {'source': self.name}
        time.sleep(int(random.random()*5))
        while not self.halt:
            time.sleep(.1)
            for i in range(1,self.num+1):
                newdata['rand'+str(i)] = random.random() * 10
            self.notifyObservers(newdata)

        print self.name + " Random Instrument monitor stopped"
            
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

            self.fh.seek(0)
            
    def stop(self):
        self.halt = True
        
class ExpeditionUDPInstruments(Instruments,threading.Thread):    
    def __init__(self, name, port=5010):
        self.port = port
        self.halt = False
        Instruments.__init__(self,name)
    
    def run(self):
        print self.name + " Expedition UDP on port " + str(self.port) + " started"
        newdata = {'source': self.name}
        map = varmaps.ExpeditionNumMap()
        expmsg = Message.ExpeditionUDPMessage()
        
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        sock.bind(('0.0.0.0',self.port))
        sockfile = sock.makefile()
        
        while not self.halt:
            msg = sockfile.readline()
            expmsg.set_msg(msg.rstrip())
            newdata.update(expmsg.as_dict())
            self.notifyObservers(map.frm(newdata))
                    
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