#!/usr/bin/python

# Types of lines:
# Variable setting: Python identifier followed by =, number or quoted string, optional datetime follows
# Date mark: dateteime, optional text on line alone
# Events: unquoted string, followed by : optional datetime, optional - and datetime
# Indentation before event is important. 
# Notes: Line of text which does not match any of the above

# ignore after #

import sys
import re
import dateutil.parser as du
import datetime 
import pytz

def parse( filename ):
    initial_split = re.compile(r'(\s+|[\-:=])')
    empty_line = re.compile(r'^\s*$')
    identifier = re.compile(r'^[^\d\W]\w*\Z$')
    
    tz = pytz.timezone('US/Eastern')
    last_time = datetime.datetime.today()
    last_time = last_time.replace(hour=0,minute=0,second=0,microsecond=0)
    last_time = tz.localize(last_time)
    print last_time
    
    
    with open(filename,"r") as log:
        for line in log:
            line_before_comment = line.rstrip().split('#')[0]
            if empty_line.match(line_before_comment):
                continue
                
            components = initial_split.split(line_before_comment)
            space_condensed_components = [0]
            for comp in components:
                if re.match(r'^\s*$',comp):
                    if len(space_condensed_components) == 1:
                        for char in  comp:
                            if char == ' ':
                                space_condensed_components[-1] += 1
                            elif char == '\t':
                                space_condensed_components[-1] += 4
                    else:
                        space_condensed_components.append(' ')
                else:
                    space_condensed_components.append(comp)
            # line = original line    
            # components = line split on space, -, : and =
            # space_condensed = [0] is number of leading spaces, followed by components, multiple spaces condensed to one
            
            
            print line.strip()
            #print space_condensed_components
            
            # Try to pull out times
            dt,space_condensed_components = extract_time( space_condensed_components, last_time, tz )
            if space_condensed_components and space_condensed_components[-1] == '-':
                # Its a range, we just found the end time
                # now get the start time
                end_time = dt
                dt,space_condensed_components = extract_time( space_condensed_components[:-1], last_time, tz )
                
            if dt == last_time:
                pass
                # No time found
            else:
                last_time = dt
                print "***Time:",last_time.isoformat()
            
            
            if len(space_condensed_components) > 1:
                if identifier.match(space_condensed_components[1]) and space_condensed_components[2] == '=':
                    try:
                            
                        if space_condensed_components[1] == 'TZ':
                            tz = pytz.timezone(space_condensed_components[3])
                            last_time = last_time.replace(tzinfo=tz)
                        else:
                            process_variable( space_condensed_components[1], space_condensed_components[3], last_time )
                    except:
                        print space_condensed_components
                    # Parse 3rd component into int, float or string
                elif ':' in space_condensed_components:
                    # Its an event
                    event_name = "".join(space_condensed_components[1:]).rstrip()[:-1]
                    indent_level = space_condensed_components[0]
                    #print "indent is",indent_level,"stack is",event_stack
                    process_event( event_name, indent_level, last_time, end_time )
                    # Need to clear event stack at end of file
                else:
                    #print components
                    print space_condensed_components
            end_time = None
            
        events = process_event("End Of File",0,last_time,None)
        vars = process_variable("",0,last_time)
        
        return (events[0,-1], vars)

        
def dump_results(events,vars):
    for v in vars:
        print v[0],'=',v[1],'from',v[2],'to',v[3]
    for e in events:
        print events.index(e),":",e[0],'from',e[1],'to',e[2],'parent',e[3]    
        
def extract_time( space_condensed_components , default, tz ):
    # Try to extract a time off the end of string
    dt = default
    num_components_used = 0
    for i in range(1,len(space_condensed_components)):
        test_string = "".join( space_condensed_components[-i:] )
        if space_condensed_components[-i-1] != '=':
            # We aren't working with the last component of an assignment
            if space_condensed_components[-i] == '-':
                # We are dealing with a time range and have just found the end time
                break
            try:
                dt = du.parse("".join( space_condensed_components[-i:] ), default=default )
                if dt.tzinfo is None:
                    #print "localizing",dt,"to",
                    dt = tz.localize(dt) # If time doesn't include a timezone, then localize to preset tz
                    #print dt
                num_components_used = i
            except ValueError:
                # No time found with this combo
                pass
    if num_components_used > 0:
        space_condensed_components = space_condensed_components[:-num_components_used]

    return (dt,space_condensed_components)

event_stack=[]
events_complete=[]
def process_event( name, indent_level, start_time, end_time ):
    while event_stack and indent_level <= event_stack[-1][1]:
        # While there are events on the stack, and they are more indented, remove, they are ended
        last_event = event_stack.pop()
        if last_event[3] is None:
            last_event[3] = start_time
            events_complete[last_event[4]][2] = start_time
        print "***End Event:",last_event[0],"from",last_event[2],"to",last_event[3]
        # Handle event by setting start and end times
        
    # Now either the stack is empty, or the head of the stack is the parent of this event    
    if event_stack:
        parent = event_stack[-1][4]
    else:
        parent = -1
    events_complete.append([name,start_time,end_time,parent])
    index = len(events_complete)-1        

    event_stack.append([name,indent_level,start_time,end_time,index])
    print "***Start Event:",name    
    return events_complete

variable_ranges = []
variable_last_setting = dict()
def process_variable( name, value, time ):
    # Create new variable seetting and close out old one
    if name == "":
        # Close all open Variables
        for v in variable_last_setting.keys():
            variable_ranges[variable_last_setting[v]][3] = time
        return variable_ranges
        
    if name in variable_last_setting:
        variable_ranges[variable_last_setting[name]][3] = time
        
    print "***Set",name,'to',value  
    variable_ranges.append([name,value,time,None])
    variable_last_setting[name] = len(variable_ranges)-1
    return variable_ranges

    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        es,vs = parse(sys.argv[1])
        dump_results(es,vs)
    else:
        print "Please supply filename of log to parse"
        