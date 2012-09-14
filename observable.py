#!/usr/bin/python

import weakref

class Observable (object):
    def __init__(self):
        super(Observable,self).__init__()
        self._observers = {}
        #self._observers = weakref.WeakKeyDictionary({})

    def subscribe(self, callback, *keys_of_interest):
        if not keys_of_interest:
            keys_of_interest = (None,)
        for key in keys_of_interest:
            if not key in self._observers:
                self._observers[key] = weakref.WeakKeyDictionary({})
            try:
                self._observers[key][callback.im_self] = callback.im_func
            except AttributeError:
                self._observers[key][callback] = callback

        
    def unsubscribe(self, callback):
        for key in self._observers.keys():
            try:
                del self._observers[key][callback.im_self]
            except AttributeError:
                del self._observers[key][callback]
                
    def is_subscribed(self, callback):
        # Currently not working
        return callback in self._observers.keys()
        
        
    def notifyObservers(self, data):
        notified = set()
        keys = set(data.keys())
        keys.add(None)
        keys.intersection_update(set(self._observers.keys()))
        for key in keys:
            for obj,cb in self._observers[key].items():
                if not cb in notified:
                    if obj == cb:
                        cb(data)
                    else:
                        cb(obj,data)
                notified.add(cb)
            
            