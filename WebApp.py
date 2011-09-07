#!/usr/bin/python

import tornado.web
import tornado.ioloop
import threading
import uuid
import os.path
import sys
import json

import mako.lookup
mako = mako.lookup.TemplateLookup(directories=['templates'],module_directory='mako')

class Server(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.streams = set()
        self.data = {}
        self.ioloop = tornado.ioloop.IOLoop.instance()
        
        self.app = tornado.web.Application([
            (r"/stream/",InstStream,dict(streams=self.streams)),
            (r"/sse-stream/",SSEStream,dict(streams=self.streams)),
            (r"/static/(.*)",tornado.web.StaticFileHandler,{"path":"static"}),
            (r"/",MainHandler),
        ])
        
        self.app.listen(self.port)

        
    def run(self):
        print "tornado started on %d" % self.port
        scheduler = tornado.ioloop.PeriodicCallback(self.send,100, io_loop = self.ioloop )
        scheduler.start()
        self.ioloop.start()
        print "tornado stopped"

    def stop(self):
        print "tornado stopping"
        self.ioloop.stop()
        self.streams = None
        
    def update(self,data):
        self.data.update(data)
            
    def send(self):
        if self.data:
            for s in self.streams:
                s(data=self.data,source="")
            self.data = {}
        
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        temp = mako.get_template('index.html')
        self.write(temp.render())
        
# Deprecated        
class InstStream(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def initialize(self,streams):
        print "initstart"
        self.streams = streams
        streams.add(self.streamUpdate)
        print "new stream"
        
    def get(self):
        pass
        
    def streamUpdate(self,source,data):
        self.write("<script type='text/javascript'>parent.updatePage( '%s' )</script>" % json.dumps(data))
        self.flush()
        
    def stream_close(self):
        self.streams.difference_update([self.streamUpdate])
        self.finish()
        
    def on_connection_close(self):
        print "client stream disconnect"
        self.streams.difference_update([self.streamUpdate])
        
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
        self.write("data:%s\n\n" % json.dumps(data))
        self.flush()
        
    #def stream_close(self):
    #    self.streams.difference_update([self.streamUpdate])
    #    self.finish()
        
    def on_connection_close(self):
        print "Closed connection with %s" % self.request.remote_ip
        self.streams.difference_update([self.streamUpdate])
        
if __name__ == "__main__":
    web = Server()
    web.start()
   