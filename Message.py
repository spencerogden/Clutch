#!/usr/bin/python

import array
import operator
import itertools

class ExpeditionUDPMessage(object):
    def __init__(self,data=None):
        if data:
            self.set_data(data)
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
		
    def __str__(self):
        return self.msg