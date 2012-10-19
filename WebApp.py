#!/usr/bin/python

import  observable

import tornado.web
import tornado.websocket
import tornado.ioloop
import threading
import uuid
import os.path
import sys
import json
import socket
import time
import datetime
import numbers
import math

# Fallback json encoder
def default(o):
    return o.__dict__

import ConfigParser

client_config = ConfigParser.SafeConfigParser()
client_config.read('clients.conf')

import mako.lookup
mako = mako.lookup.TemplateLookup(directories=['web/templates'],module_directory='web/templates/mako')

class Server(threading.Thread,observable.Observable):
    def __init__(self, port,app_type='full'):
        threading.Thread.__init__(self)
        observable.Observable.__init__(self)
        
        main_handlers = {
            'full': (r"/",FullMainHandler),
            'repeater': (r"/",RepeaterMainHandler),
        }
        
        self.port = port
        self.streams = set()
        self.data = {}
        self.ioloop = tornado.ioloop.IOLoop.instance()
        
        self.app = tornado.web.Application([
            (r"/timesync/",TimeStream),
            (r"/sse-stream/",SSEStream,dict(streams=self.streams)),
            (r"/static/(.*)",tornado.web.StaticFileHandler,{"path":"web/static"}),
            main_handlers[app_type],
            (r"/ping",PingHandler,dict(server=self)),
            (r"/log",LogHandler),
            ])
        
        self.app.listen(self.port)
        
    def run(self):
        print "Web Interface Started on %s:%d" % (socket.gethostname(),self.port)
        scheduler = tornado.ioloop.PeriodicCallback(self.send,100, io_loop = self.ioloop )
        scheduler.start()
        self.ioloop.start()
        print "Web Interface Stopped"

    def stop(self):
        self.ioloop.stop()
        self.streams = None
        
    def update(self,data):
        self.data.update(data)
            
    def send(self):
        if self.data and self.streams:
            for s in self.streams:
                s(data=self.data,source="")
            self.data = {}
        
class FullMainHandler(tornado.web.RequestHandler):
    def get(self):
        temp = mako.get_template('index.html')
        self.write(temp.render())
        
class RepeaterMainHandler(tornado.web.RequestHandler):
    def get(self):
        temp = mako.get_template('repeater.html')
        self.write(temp.render())

class PingHandler(tornado.web.RequestHandler):
    def initialize(self, server):
        self.notifyObservers = server.notifyObservers
        
    def post(self):
        object = self.get_argument('object','Unknown') # Get the name of the pinged object
        ping_time = float(self.get_argument('time', '0')) # Get time of ping
        if ping_time == 0:
            ping_time = datetime.datetime.now()
        else:
            ping_time = datetime.datetime.fromtimestamp( ping_time )
        ping_data = { 'event_type': "ping",
                      'object':     object,
                      'time':       ping_time,
                    }
        self.notifyObservers(data=ping_data)

class LogHandler(tornado.web.RequestHandler):
    def post(self):
        print str(datetime.datetime.now()) + ": " + self.get_argument('text','')
        
class UserInteractionHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "UserInteraction socket opened"
    
    def on_mesage(self, message):
        self.write_message(u"You said: " + message)
    
    def on_close(self):
        print "UserInteraction socket closed"
                
class SSEStream(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def initialize(self,streams):
        self.streams = streams
        streams.add(self.streamUpdate)
        print "New connection from %s" % self.request.remote_ip
        
    def get(self):
        self.write(":SSE Stream from Clutch\n\n")
        self.set_header('Content-Type', 'text/event-stream')
        self.flush
        
    def streamUpdate(self,source,data):
        #self.write("data:%s\n\n" % json.dumps(dict([(k,v) for (k,v) in data.items() if isinstance(k, str) and isinstance(v,numbers.Number)]),default=default))
        self.write("data:%s\n\n" % json.dumps(dict([(k,v) for (k,v) in data.items() if isinstance(k, str) and  v == v]),default=default))
        self.flush()
        
    #def stream_close(self):
    #    self.streams.difference_update([self.streamUpdate])
    #    self.finish()
        
    def on_connection_close(self):
        print "Closed connection with %s" % self.request.remote_ip
        #self.streams.difference_update([self.streamUpdate])
        
class TimeStream(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def initialize(self):
        self.scheduler = tornado.ioloop.PeriodicCallback(self.sendTime,1000 )
        self.scheduler.start()

    def get(self):
        self.write(":TimeSync\n\n")
        self.set_header('Content-Type', 'text/event-stream')
        self.flush
        
    def sendTime(self):
        self.write("data:%s\n\n" % json.dumps(time.time()))
        self.flush()
        
    def on_connection_close(self):
        self.scheduler.stop()
        
if __name__ == "__main__":
    web = Server()
    web.start()

   
