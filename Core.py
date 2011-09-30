#!/usr/bin/python

# Function Calculation
# Bring in list of changed vars
# Global list of vars with a flag that is either changed,unchanged,unknown
# Mark vars in changed list as changed, mark all other no dependency vars unchanged
# for each unknown var, if all dependencies are unchanged, mark unchanged
#      if any dependency is unknown, recurse and find status of that dependency
#      if any dependecy is changed, add this var to update list
# cache update list in dict of (updated var)-->(list of vars in order they should be calced)

import threading

class ClutchCore(object):
    def __init__(self):
        data = {} # Unique data for each variable from primary source
        data_by_source = {} # All current data submitted from all sources
        
        self.datalock = threading.Lock()

        subscribers = {}
        
        function_files = ()
	
    def publish(self, *args, **kwargs):
        newdata = kwargs['data']
        source = kwargs['source']
        with self.datalock:
            newvars = set(newdata.keys())

            unowned_vars = newvars.difference(*self.var_owners.values()) # These vars are not owned and can be claimed
            source_owns = newvars.intersection(self.var_owners.get(source,set())) # These vars are owned by this source
            update_vars = source_owns.union(unowned_vars) # we can update unowned vars and vars owned by this source

            if update_vars:
                self.var_owners.get(source,set()).union(update_vars) # Source claims these vars
                newdata = dict((k, newdata[k]) for k in update_vars)
                self.data.update(newdata)
                for sub in self.subscribers.keys():
                    if self.subscribers[sub].intersection(update_vars):
                        sub(newdata,source)
		
	def subscribe(self, variables, callable):
        # Subscribe a callback and set the dict value to the set of variables it is interested in
		self.subscribers[callable] = set(variables)
		
	def load_function_file(self):
		# Load file containing functions and subscribe properly
		pass
		
# Another class to monitor function files for changes?