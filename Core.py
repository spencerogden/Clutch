#!/usr/bin/python

# Should merge happen in Instruments or Core? Go with what is working right now

import threading
import collections
import observable
import geo
import datetime

import ClutchFunc
import Tables
import Boat

class ClutchCore(observable.Observable):
    def __init__(self):
        observable.Observable.__init__(self)
        
        # Current values of all variables
        self.data = {} # Unique data for each variable from primary source
        self.data_by_source = {} # All current data submitted from all sources, [variable][key]

        # Race course data needed for calculation
        self.course = Course()
        self.course.subscribe(self.update_course) # Notify me on any changes to the course
        
        self.boat = Boat.Boat()
        
        self.tl = Tables.TableLibrary()
        self.tl.addTables("Polars")
        self.update_tablelibrary( {} )

        ClutchFunc.load_and_monitor("Functions")

        # Short term buffer of data we need on hand
        self.buffer = collections.deque([],5000)
        self.buffer_last_found = 0
        
    def update_course(self, data):
        # Something changed in course, push the whole update
        self.update_data( { 'course': self.course } )
        
    def update_tablelibrary(self, data):
        self.update_data( { 'tablelibrary': self.tl } )
	
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
        self.update_data( { 'course': self.course } )
        
    def var(self, var, calc=False):
        if calc or ((var not in self.data.keys()) and (var in ClutchFunc.clutchfunc.funcs.keys())):
            print "calc",var,
            return ClutchFunc.runFunc( var, self.data)
        elif var in self.data.keys() :
            print "retr",var,
            return self.data[var]
        return None
            
    def raw_data_handler(self,newdata):
        # Handler for new data from instruments, dict of variable=data pairs
        
        # Feed neccessary data points into short term buffer
        if 'Lat' in newdata and 'Lon' in newdata:
            newdata['Pos'] = geo.Position(newdata['Lat'],newdata['Lon'])
            self.buffer.appendleft( { 'Time': datetime.datetime.now(), 
                                      'Lat': newdata['Lat'], 
                                      'Lon': newdata['Lon'] } )
        self.update_data( newdata )
        
    def update_data( self, newdata ):
        self.data.update(newdata)
        calced_data = ClutchFunc.runFuncs(self.data, newdata.keys())
        self.data.update( calced_data )
        self.notifyObservers(dict(newdata.items() + calced_data.items()))

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
    
    def range_to(self, mark):
        return self.position.range_to(mark.position)
    
    def brng_to(self, mark):
        return self.position.brng_to(mark.position)
    
    def __str__(self):
        return "Mark: %s at %s" % (self.name, self.position)

class Course(observable.Observable):
    def __init__(self, marks=[], name=None):
        observable.Observable.__init__(self)
        self.marks = marks
        self.name = name
        
        nullMark = Mark(name="Not Set",position=geo.Position(0,0))
        
        # Special marks
        self.port_end = None
        self.star_end = None
        self.wind_mrk = None
        self.leew_mrk = None # Middle of gate if one
        self.leew_prt = None # Port gate mark
        self.leew_str = None # starboard gate mark (looking upwind)
        self.gybe_mrk = None

    def set_port_end(self, mark):
        self.port_end = mark
        self.notifyObservers({'course_port_end':mark})
        if mark not in self.marks:
            self.add_mark(mark)

    def set_star_end(self, mark):
        self.star_end = mark
        self.notifyObservers({'course_star_end':mark})
        if mark not in self.marks:
            self.add_mark(mark)
        
    def set_wind_mrk(self, mark):
        self.wind_mrk = mark
        self.notifyObservers({'course_wind_mrk':mark})
        if mark not in self.marks:
            self.add_mark(mark)
        
    def set_leew_mrk(self, mark):
        self.leew_mrk = mark
        self.notifyObservers({'course_leew_mrk':mark})
        if mark not in self.marks:
            self.add_mark(mark)
        
    def set_leew_prt(self, mark):
        self.leew_prt = mark
        self.notifyObservers({'course_leew_prt':mark})
        if mark not in self.marks:
            self.add_mark(mark)
        
    def set_leew_str(self, mark):
        self.leew_str = mark
        self.notifyObservers({'course_leew_str':mark})
        if mark not in self.marks:
            self.add_mark(mark)
        
    def set_gybe_mrk(self, mark):
        self.gybe_mrk = mark
        self.notifyObservers({'course_gybe_mrk':mark})
        if mark not in self.marks:
            self.add_mark(mark)

    def add_mark(self,mark): # Shouldn't add mark every time, what if we are moving an existing mark?
        self.marks.append(mark)
        self.notifyObservers({'course': self})
        
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
        if self.star_end: strs.append("Star: %s" % self.star_end)
        if self.wind_mrk: strs.append("Wind: %s" % self.wind_mrk)
        if self.leew_mrk: strs.append("Leew: %s" % self.leew_mrk)
        other_marks = map(str,self.marks)
        strs.extend(other_marks)
        return "\n".join(strs)

def get_total_seconds(td): return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6