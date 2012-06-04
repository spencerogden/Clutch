#!/usr/bin/python

import array
import operator
import itertools
import varmaps
import exceptions

class ExpeditionUDPMessage(object):
    def __init__(self,data=None):
        if data:
            self.set_data(data)
        else:
            self.data = dict()
        self.chksep = '*'
        self.itemsep = ','
		
    def set_data(self,data):
        self.data = data
        boat = '#0'
        msgitems = list(itertools.chain(*data.iteritems()))
        msgitems.insert(0,boat)
        msgpart = self.itemsep.join(msgitems)
        self.msg  = msgpart + self.chksep + self.comp_checksum(msgpart)    
        return self.msg
        
    def comp_checksum(self,msgpart):
        a = array.array('B', msgpart)
        return "%0.2X" % reduce(operator.xor,a)
        
    def set_msg(self,msg):
        self.msg = msg
        message, checksum = self.msg.split(self.chksep)
        
        parts = message.split(self.itemsep)
        self.boat = parts[0]
        
        # Checksum calc not working?
        if self.comp_checksum(message) == checksum:
            self.data = dict(zip(map(int,parts[1::2]), map(self.try_num,parts[2::2])))
        else:
            return
            
    def try_num(self, string):
        try:
            return int(string)
        except exceptions.ValueError:
            try:
                return float(string)
            except exceptions.ValueError:
                return string
        
    def as_dict(self):
        return self.data
		
    def __str__(self):
        return self.msg