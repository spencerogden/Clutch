#!/usr/bin/python

# Should merge happen in Instruments or Core? Go with what is working right now

import threading
import collections
import observable
import geo
import datetime

import ClutchFunc

class ClutchCore(observable.Observable):
    def __init__(self):
        observable.Observable.__init__(self)
        
        # Current values of all variables
        self.data = {} # Unique data for each variable from primary source
        self.data_by_source = {} # All current data submitted from all sources, [variable][key]

        # Race course data needed for calculation
        self.course = Course()
        
        # List of all files we have loaded functions from. Needed?
        self.function_files = ()
        
        # Short term buffer of data we need on hand
        self.buffer = collections.deque([],5000)
        self.buffer_last_found = 0
	
    def ui_event_handler(self,event):
        # This will be subscribed to UI events like pings
        if event['event_type'] == 'ping':
            self.handle_ping(event['time'],event['object'])
        
    def handle_ping(self, time, object):
        pos = self.buffer_last_found
        length = len(self.buffer)
        buf = self.buffer
        
        while pos < 5000:
            if buf[pos]['Time'] > time:
                pos += 1
            else:
                break
                
        before = buf[pos]
        after = buf[pos-1]
        
        after_weight = get_total_seconds(time - before['Time'])/get_total_seconds(after['Time'] - before['Time'])
        
        lat = (1-after_weight)*float(before['Lat']) + after_weight*float(after['Lat'])
        lon = (1-after_weight)*float(before['Lon']) + after_weight*float(after['Lon'])
        
        if object == "Port End":
            if self.course.port_end:
                self.course.port_end.move(geo.Position(lat,lon))
            else:
                self.course.port_end = Mark(name=object,position=geo.Position(lat,lon))
        elif object == "Starboard End":
            if self.course.star_end:
                self.course.star_end.move(geo.Position(lat,lon))
            else:
                self.course.star_end = Mark(name=object,position=geo.Position(lat,lon))
        elif object == "Windward Mark":
            if self.course.wind_mrk:
                self.course.wind_mrk.move(geo.Position(lat,lon))
            else:
                self.course.wind_mrk = Mark(name=object,position=geo.Position(lat,lon))
        elif object == "Leeward Mark":
            if self.course.leew_mrk:
                self.course.leew_mrk.move(geo.Position(lat,lon))
            else:
                self.course.leew_mrk = Mark(name=object,position=geo.Position(lat,lon))
        else:
            self.course.add_mark(Mark(name=object,position=geo.Position(lat,lon)))
        
        print self.course
        
    def raw_data_handler(self,newdata):
        # Handler for new data from instruments, dict of variable=data pairs
        self.data.update(newdata)
        
        # Feed neccessary data points into short term buffer
        if 'Lat' in newdata and 'Lon' in newdata:
            self.buffer.appendleft( { 'Time': datetime.datetime.now(), 
                                      'Lat': newdata['Lat'], 
                                      'Lon': newdata['Lon'] } )
        

        calced_data = ClutchFunc.runFuncs(self.data, newdata.keys())

        # should we only pass on changed data, or all data? I think only changed.
        self.data.update( calced_data )  # save calculated data
        self.notifyObservers(dict(newdata.items() + calced_data.items())) # only send updated data we received, as well as data we jst calced

class Mark(object):
    def __init__(self, 
                 name=None, 
                 position=None, 
                 rounding="GoTo", 
                 permanent=False, 
                 description=None ):
        self.name = name
        self.position = position
        self.rounding = rounding
        self.permanent = permanent
        self.desc = description 

    def move(self,position):
        self.pos = position
        
    def reset(self, mark):
        self.position = mark.position
        
    def __str__(self):
        return "Mark: %s at %s" % (self.name, self.position)

class Course(object):
    def __init__(self, marks=[], name=None):
        self.marks = marks
        self.name = name
        
        # Special marks
        self.port_end = None
        self.star_end = None
        self.wind_mrk = None
        self.leew_mrk = None # Middle of gate if one
        self.leew_prt = None # Port gate mark
        self.leew_str = None # starboard gate mark (looking upwind)
        self.gybe_mrk = None

    def add_mark(self,mark):
        self.marks.append(mark)
        
    def length(self, units="nm"):
        # Compute length of whole course
        pass
    
    def legbearing(self, leg):
        # Return bearing of given leg
        pass
        
    def legrange(self, leg):
        # Return length of given leg
        pass
        
    def __str__(self):
        strs = ["Course: %s" % self.name,]
        if self.port_end: strs.append("Port: %s" % self.port_end)
        if self.star_end: strs.append("Star: %s" % self.port_end)
        if self.wind_mrk: strs.append("Wind: %s" % self.port_end)
        if self.leew_mrk: strs.append("Leew: %s" % self.port_end)
        other_marks = map(str,self.marks)
        strs.extend(other_marks)
        return "\n".join(strs)

def get_total_seconds(td): return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6