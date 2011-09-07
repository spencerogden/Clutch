#!/usr/bin/python

import socket
import threading
import time
import sys

import varmaps
import Message

# A Broadcaster should:
# Handle all network socket setup and breakdown
# Translate variables from Clutch to desired message format 
#   using Map and Message
# Be parsimonious, try to only send updated data with full data set sent
# less frequently

class Broadcaster(threading.Thread):
    def __init__(self,port=51234):
        threading.Thread.__init__(self)
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('',0))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print "Network Broadcast started on port " + str(self.port)
        self.curdata = {}
        self.datalock = threading.Lock()
        self.halt = False
        self.map = varmaps.ExpeditionNumMap()
        
    def networkUpdate(self,data,source):
        with self.datalock:
            self.curdata.update(self.map.to(data))
    
    def stop(self):
        self.halt = True
            
    def run(self):
        msg = Message.ExpeditionUDPMessage()
        while not self.halt:
            self.datalock.acquire
            if self.curdata:
                data = self.curdata
                self.curdata = {}
                self.datalock.release
                msg.set_data(data)
                self.s.sendto(str(msg),0,('<broadcast>', self.port))
            time.sleep(.1)

            