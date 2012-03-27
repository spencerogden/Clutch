#!/usr/bin/python

# Main application file
# Sets up main loop and interfaces

VERSION = "0.1"

import Instruments
import WebApp
import Broadcast
import Core
import Logger
import geo

import shlex
import sys
import os
import time
import threading
import cmd
import readline
import logging

#Components
#Core - Number processing, calculation and short term logging
#Instruments - One way feed of data into system
#UIs - Feed of data and return of user events
#Logger - output and storage of data
#3 Categories:
#   Input Streams - Instruments
#   Output streams - Broadcast, Logger, Stream to UIs
#   Core - Processing
# Misc - UI events, Instrument settings

# Instrument test reading from log file
#log_insts = Instruments.LogReaderInstruments('log','logs/09Mar2006_0.csv')
#insts.addInstruments(log_insts)

# Random instruments to test variable ownership
# foo_insts = Instruments.RandomInstruments('foo',1)
# bar_insts = Instruments.RandomInstruments('bar',2)
# insts.addInstruments(foo_insts)
# insts.addInstruments(bar_insts)

# Start instrument capture in log
#log = Logger.Logger('log.sqlite')
#insts.subscribe(log.update) # Logger should probably subscribe to Core
#log.set_log_name("Testing")

# Create instruments
insts = Instruments.InstrumentsMerge()
# Instrument tester simulating boat sailing around
sim_insts = Instruments.SimulatorInstruments('sim')
insts.addInstruments(sim_insts)

# Create Clutch components
web = WebApp.Server(5011)
core = Core.ClutchCore()
udp = Broadcast.Broadcaster(5010)
log = Logger.Logger('log.sqlite')
log.set_log_name("Testing")

# Link components together
insts.subscribe(core.raw_data_handler) # Instruments send data to Core
web.subscribe(core.ui_event_handler) # Web sends UI events to Core
core.subscribe(web.update) # Core sends data to web
core.subscribe(udp.networkUpdate) # Core sends data to Broadcaster
core.subscribe(log.update) # Core sends data to Logger

# Start interfaces
#udp.start()
web.start()

# Set some marks for testing
core.course.port_end = Core.Mark(name="Pin",position=geo.Position(0,-0.001))
core.course.star_end = Core.Mark(name="Boat",position=geo.Position(0,+0.001))

print "ClutchControl %s started" % VERSION

class Console(cmd.Cmd,object):
    def __init__(self):
        self.watching = False
        cmd.Cmd.__init__(self,'\t')
        self.prompt = '>'
        self.logging = True

    def postcmd(self,stop,line):
        #print "Threads: %d" % threading.activeCount()
        pass
        
    def do_quit(self,line):
        print "Exiting"
        insts.stop()
        web.stop()
        udp.stop()
        if udp.is_alive(): 
            print "Waiting for instruments"
            udp.join()
        sys.exit()
        
    def do_watch(self,line):
        if(self.watching):
            insts.unsubscribe(self.consoleUpdate)
            self.watching = False
        else:
            insts.subscribe(self.consoleUpdate)
            self.watching = True
            
    def do_s(self,line):
        insts.changeOwner('rand1')
    
    def do_l(self,line):
        if self.logging:
            print "Unsubscribing log db"
            insts.unsubscribe(log.update)
        else:
            print "Subscribing Log db"
            insts.subscribe(log.update)
        self.logging = not self.logging
            
    def consoleUpdate(self,data):
        for d in data.keys():
            print "%s is %s from %s" % (d,repr(data[d]),source)
        
con = Console()         
con.cmdloop()
