#!/usr/bin/python

import sqlite3
import os
import shutil
import time
import cPickle as pickle
import numbers

LOG_DB_VERSION = 2

class Logger:
    def __init__(self,logdbfile):
        self.data = dict()
        file_exists = os.path.exists(logdbfile)
        self.dbfile = logdbfile
        
        try:
            self.con = sqlite3.connect(logdbfile, check_same_thread = False)
            self.cur = self.con.cursor()
        except sqlite3.OperationalError, msg:
            print "Not a valid Clutch Log File, check log path"
            raise
            
        if file_exists:
            # We have a SQLite DB, it's not empty, is a format we can handle?
            db_rev = self.get_ver()
            if db_rev > LOG_DB_VERSION:
                raise Exception, "Log DB is from a newer version of Clutch, can't work with it"
        else:
            # We have a blank SQLite DB, need to create structure, blank is version 0
            db_rev = 0
        
        self.ver = db_rev
        self.upgrade_db() # Upgrade DB from version DB_rev to present version
        
        
        
    def __del__(self):
        print "Closing %s at %s" % ("log file", self.dbfile)
        self.con.commit()
        self.con.close()
        
    def get_ver(self):
        try:
            self.cur.execute("SELECT max(version) FROM clutch_control")
        except sqlite3.OperationalError, msg:
            print "Not a valid Clutch Log File, check log path"
        self.ver = self.cur.fetchone()[0] 
        if self.ver is None:
            self.ver = 0
        return self.ver 
        
    def upgrade_db(self):
        if self.ver == LOG_DB_VERSION:
            print "Log DB is the correct version"
            return
        
        if self.ver > 0:
            # If version is 0, we are building from scratch, no need to backup
            print("Upgrading Log DB file:",self.dbfile,"from version",self.ver,"to",LOG_DB_VERSION);
            shutil.copy(self.dbfile, self.dbfile + ".backup")
        
        while self.ver < LOG_DB_VERSION:
            prior_ver = self.ver
            build_meth = getattr(self, 'build_' + str(self.ver+1))
            build_meth()
            if prior_ver + 1 != self.get_ver():
                raise Exception, "Upgrade did not succeed"
            
            
    def build_1(self):
        # We have a blank db in sql.cur, build initial structure
        if self.ver != 0:
            raise Exception, "Can't upgrade this version"
        self.cur.execute('''
            CREATE TABLE position ( timestamp FLOAT PRIMARY KEY, 
                                    latitude  FLOAT,
                                    longitude FLOAT)
            ''')
            
        self.cur.execute('''
            CREATE TABLE clutch_control ( version INTEGER, name TEXT ) 
            ''')
        self.cur.execute('''
            INSERT INTO clutch_control(version) VALUES (1)
            ''')
        self.con.commit()
        
    def build_2(self):
        if self.ver != 1:
            raise Exception, "Can't upgrade this version"
        self.cur.execute('''
            CREATE TABLE rawdata ( timestamp FLOAT PRIMARY KEY,
                                    data BLOB )
            ''')
        self.cur.execute('''
            INSERT INTO clutch_control(version) VALUES (2)
            ''')  
        self.con.commit()
        
    def set_log_name(self,newname):
        self.name = newname
        self.cur.execute("UPDATE clutch_control SET name=?", (newname,))
        self.con.commit()
        
    def get_log_name(self):
        self.cur.execute("SELECT name FROM clutch_control WHERE version = ?",(LOG_DB_VERSION,))
        self.name = self.cur.fetchone()[0] 
        return self.name
        
    def get_pos_at_time(self, timestamp):
        # Get position closest to time within 5 seconds
        self.cur.execute('''
            SELECT position.rowid, position.timestamp, position.latitude, position.longitude
            FROM
                (SELECT max(timestamp) as t
                FROM position 
                WHERE 
                    timestamp <= ? and
                    timestamp > (? - 5)) lower,
                position
            WHERE
                lower.t = position.timestamp
            ''', (timestamp, timestamp))
        # Get next position
        (low_id, low_time, low_lat, low_lon) = self.cur.fetchone()
        high_id = low_id+1
        self.cur.execute('''
            SELECT rowid, timestamp, latitude, longitude
            FROM position
            WHERE rowid = ?
            ''', (high_id,))
        print "Want rowid = %r or rowid = %r" % (low_id, low_id+1)
        res = self.cur.fetchone()
        print "high res is %r"% res
        (high_id, high_time, high_lat, high_lon) = res
        # Maybe there should be a warning or exception if the timestamps are too far apart?
        
        # Interpolate positions
        w = ( timestamp - low_time ) / ( high_time - low_time )
        int_lat = (1-w) * low_lat + w * high_lat
        int_lon = (1-w) * low_lon + w * high_lon
        
        return (int_lat, int_lon)
        
    def update(self,data):
        timestamp = time.time()
        pdata = pickle.dumps(dict([(k,v) for (k,v) in data.items() if isinstance(k, str) and isinstance(v,numbers.Number)]),pickle.HIGHEST_PROTOCOL)
        if 'Lon' in data:
            self.cur.execute('''INSERT INTO position(timestamp, latitude, longitude)
                                VALUES (?,?,?)''',
                                (timestamp, data['Lat'], data['Lon']))
            self.cur.execute("INSERT INTO rawdata (timestamp, data) values (:ts,:data)", (timestamp, sqlite3.Binary(pdata)))

            self.con.commit()
        
    def test_pos(self):
        self.cur.execute('''INSERT INTO position(timestamp, latitude, longitude, source)
                        VALUES (?,?,?,?)''',
                        (time.time(), 1.23, 4.56, "testing"));
        self.cur.execute("SELECT * FROM position WHERE source='testing'")
        for r in self.cur.fetchall():
            print r
            
            

# Contains interface for all logging activity
# Database SQLite
# Data retrieval
# File export
