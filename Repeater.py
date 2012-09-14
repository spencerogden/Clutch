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
import ConfigParser

app_config = ConfigParser.SafeConfigParser({
    "web_port": "5011",
    })
app_config.read('clutch.conf')

inst_config = ConfigParser.SafeConfigParser()
inst_config.read('instruments.conf')

insts = Instruments.InstrumentsMerge()
available_instruments = {
    "simulation": Instruments.SimulatorInstruments,
    "expedition_udp": Instruments.ExpeditionUDPInstruments,
    "logreader": Instruments.LogReaderInstruments
    }

for instrument_section in inst_config.sections():
    inst_type = inst_config.get(instrument_section, "type")
    params = dict(inst_config.items(instrument_section))
    del params['type']
    # Create the instrument and name it after the section, pass section settings to constructor
    if inst_type in available_instruments:
        i = available_instruments[inst_type](instrument_section,**params) 
    else:
        print "Instrument type %s in %s not recognized" % (type, instrument_section)
    insts.addInstruments(i)

# Create Clutch components
web = WebApp.Server(app_config.getint("Clutch","web_port"),app_type='repeater')
web.start()
insts.subscribe(web.update) # Insts sends data to web

# Setup optional modules
try:
    udp = Broadcast.Broadcaster(app_config.getint("Clutch","broadcast_port"))
    insts.subscribe(udp.networkUpdate) # Core sends data to Broadcaster
    udp.start()
except ConfigParser.NoOptionError:
    pass
        
try:
    log = Logger.Logger(app_config.get("Clutch","log_file"))
    insts.subscribe(log.update) # Insts sends data to Logger
except ConfigParser.NoOptionError:
    pass

print "ClutchRepeater %s started" % VERSION

class Console(cmd.Cmd,object):
    def __init__(self):
        self.watching = False
        cmd.Cmd.__init__(self,'\t')
        self.prompt = '>'
        self.logging = True

    def postcmd(self,stop,line):
        # Something to run after every command
        pass
        
    def do_quit(self,line):
        print "Exiting Clutch"
        insts.stop()
        print "Insts stopped"
        web.stop()
        print "Web stopped"
        try:
            udp.stop()
            if udp.is_alive(): 
                print "Waiting for instruments"
                udp.join()
        except NameError:
            pass
        sys.exit()
        
    def do_watch(self,line):
        # log vars to screen
        if(self.watching):
            insts.unsubscribe(self.consoleUpdate)
            self.watching = False
        else:
            insts.subscribe(self.consoleUpdate)
            self.watching = True
            
    def do_log(self,line):
        if self.logging:
            print "Unsubscribing log db"
            insts.unsubscribe(log.update)
        else:
            print "Subscribing Log db"
            insts.subscribe(log.update)
        self.logging = not self.logging
        
    def do_calc(self,line):
        # force calc of var
        print core.var(line,True)
        
    def do_var(self, line):
        # print value of var
        for v in line.split(" "):
            res = core.var(v, False)
            if res is not None:
                print res
            else:
                print "No such variable"
    
    def do_data(self,line):
        # dump data
        print core.data
            
    def consoleUpdate(self,data):
        for d in data.keys():
            print "%s is %s" % (d,repr(data[d]))
        
con = Console()         
con.cmdloop()
