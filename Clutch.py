#!/usr/bin/python

# Main application file
# Sets up main loop and interfaces

VERSION = "0.1"

import Instruments
import WebApp
import Broadcast
import Core

import shlex
import sys
import os
import time
import threading
import cmd
import readline
import logging


insts = Instruments.InstrumentsMerge()

# foo_insts = Instruments.RandomInstruments('foo',1)
# bar_insts = Instruments.RandomInstruments('bar',2)
log_insts = Instruments.LogReaderInstruments('log','09Mar2006_0.csv')

# insts.addInstruments(foo_insts)
# insts.addInstruments(bar_insts)
insts.addInstruments(log_insts)

web = WebApp.Server(5011)
insts.subscribe(web.update)
web.start()

udp = Broadcast.Broadcaster(5010)
#udp.start()
#insts.addObserver(udp.networkUpdate)

print "ClutchControl %s started" % VERSION

class Console(cmd.Cmd,object):
    def __init__(self):
        self.watching = False
        cmd.Cmd.__init__(self,'\t')
        self.prompt = '>'

    def postcmd(self,stop,line):
        print "Threads: %d" % threading.activeCount()
            
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
            
    def consoleUpdate(self,data):
        for d in data.keys():
            print "%s is %s from %s" % (d,repr(data[d]),source)
        
con = Console()         
con.cmdloop()
