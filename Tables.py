#!/usr/bin/python

# Use Smooth Table to support a collection of lookup tables, polars (start, race, nav, etc), 
# calibration tables.

# Tables are simple 2D tables with dimensions tws and twa

import SmoothTable
import re, os, ast

class TableLibrary(object):
    def __init__(self):
        self.tables = {}
        
    def addTables(self, filename):
        # Take file name, load into a smooth table and add to the library
        # parse out individual points and add to smooth table
        fullpath = os.path.join(os.path.dirname(__file__), "Tables", filename)
        
        cur_table = ''
        table = None
        
        with open(fullpath) as table_file:
            for line in table_file:
                line = line.partition('#')[0]
                line = line.strip()
                if re.match(r'^[a-zA-Z]',line):
                    # We have a line starting with a letter, use it as a name and start a new table
                    # Finish current table if we are in one.
                    if cur_table:
                        table.rebuild_table(True)
                        self.tables[cur_table] = table
                        cur_table = ''
                        table = None
                    cur_table = re.sub(r'\s*','',line)
                    table = SmoothTable.Table()
                
                if re.match(r'^\d',line):
                    # Line start with a digit, try to add pairs to table
                    numbers = line.split()
                    tws = numbers.pop(0)
                    for p in zip(numbers[::2],numbers[1::2]):
                        # Iterate through pairs from the row
                        table.add_point(ast.literal_eval(tws), ast.literal_eval(p[0]), ast.literal_eval(p[1]))
        
        if cur_table:
            # If we ended a file with a table open, finish it off
            self.tables[cur_table] = table
        
        
    def lookup(self, table, tws, twa):
        return self.tables[table].lookup(tws, twa)
        
    def lookup_targ(self, table, tws):
        return self.tables[table].lookup_targ(tws)
        
    def __str__(self):
        lines = []
        for t in self.tables.keys():
            lines.append(t)
            lines.append(str(self.tables[t]))
            lines.append('')
        return"\n".join(lines)