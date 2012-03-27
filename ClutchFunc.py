import sys,os,glob,threading,time,types

# How to use:
# import ClutchFunc
# Load functions and start the monitor: ClutchFunc.load_and_monitor(<directory to monitor>)
# Run functions on new data: ClutchFunc.clutchfunc.runFuncs(data,changed,unchanged)
#   Pass in all data that might be needed, try to set changed and unchanged to cut down on calculation
#   Be conservative on unchanged, it might be less efficient, but it will be correct

def loadFuncs(directory):
    with clutchfunc.func_lock:
        # Load any new modules in this directory, do not reload modules already loaded
        clutchfunc.directory = directory
        clutchfunc.path = os.path.join(os.getcwd(),os.path.dirname(__file__),directory)
        standard_syspath = sys.path
        sys.path.insert(0,clutchfunc.path)
        pyfiles = glob.glob(os.path.join(clutchfunc.path,"*.py"))
        for f in pyfiles:
            if f in [ m.__fullfile__ for m in clutchfunc.modules ]:
                # We have already imported this file once, changes will be picked up in the rescan
                # continue with next file
                continue
            filename = os.path.basename(f)[:-3]
            print "Importing",filename,":",
            try:
                clutchfunc.modules.append(__import__(filename))
            except:
                print "Error loading %s, try correcting the error and resave. Error: %s" % (filename, sys.exc_info()[0])
            else:
                clutchfunc.modules[-1].__fullfile__ = f
                try:
                    stat = os.stat(f)
                except OSError:
                    continue
                clutchfunc.modules[-1].__mtime__ = stat.st_mtime
                print
        sys.path = standard_syspath


def rescanFuncs():
    # Rescan existing files for changes
    with clutchfunc.func_lock:
        for m in clutchfunc.modules:
            try:
                stat = os.stat(m.__fullfile__)
            except OSError:
                continue
            if stat.st_mtime != m.__mtime__:
                print "Reloading",m.__name__,":",
                funcs_to_remove = [getattr(m,f) for f in dir(m) if isinstance(getattr(m,f),clutchfunc)]
                for f in funcs_to_remove:
                    local_funcs = set()
                    local_funcs.update(clutchfunc.funcs.values())
                    for cf in local_funcs:
                        if f.func.target == cf.target:
                            del clutchfunc.funcs[f.func.__name__]
                            clutchfunc.func_order = [] # Function removed, order might be invalid, recheck
                try:
                    reload(m)
                    print
                    m.__mtime__ = stat.st_mtime
                except:
                    print "Error reloading %s, try to correct the error and resave, the correction will be reloaded: %s" % (m.__fullname__,sys.exc_info()[0]) 
            
def runFuncs(data,changed=None,unchanged=None):
    # data is the data required to calc
    # changed and unchaged can give hints as to what is changed. Being specific about what is changed
    # can help reduce calc time by not recalculating functions uneccessarily
    with clutchfunc.func_lock:
        if not changed:
            ch = set(data.keys())
        else:
            ch = set(changed)
            
        if not unchanged:
            unch = set(data).difference(ch) # Vars that are changed shouldn't be here
            unch = unch.difference(set(clutchfunc.funcs.keys())) # Vars that are based on functions might be changed, we don't know yet
            # Its better to err on the side of not marking something unchanged, it may lead to 
            # more computation, but won't accidentally skip
        else:
            unch = set(unchanged)
            
        new_data = {}
        
        if not clutchfunc.func_order:   
            clutchfunc.func_order = clutchfunc.funcs.values() # load up in whatever order
            # We'll sort out the correct order below
        
        seen = set()
        pos = 0
        while pos < len(clutchfunc.func_order):
            f = clutchfunc.func_order[pos]
            if f.dependencies.issubset(unch):
                # this function does not need to run
                unch.add(f.target)
                pos += 1
            elif f.dependencies.issubset(unch.union(ch)):
                # All of this fucntions dependencies are in a known state, we can calc
                #inputs = map(dict(data.items() + new_data.items()).get,f.dependencies)
                #inputs = dict([ (k,data[k]) for k in f.dependencies ])
                try:
                    res = f(**dict([ (k,data[k]) for k in f.dependencies ])) # Extract needed inputs from available data
                except:
                    print "Error running function: %s, try implementing a fix in %s. Dependents will likely fail. : %s" % (f.__name__, f.__module__,sys.exc_info()[0])
                else:
                    new_data[f.target] = res
                    data[f.target] = res
                    ch.add(f.target)
                pos += 1
            else:
                # Dependency are unknown, try to wait for later, move to end of list
                if f in seen:
                    print "Function error, all functions tried and inputs of",f.target,"not found"
                    break
                del clutchfunc.func_order[pos]
                clutchfunc.func_order.append(f)
            seen.add(f)
        
        return new_data

def load_and_monitor(directory,interval=5):
    loadFuncs(directory)
    startMonitor(interval)

def startMonitor(interval=5):
    clutchfunc.mon = functionMonitor(interval)
    clutchfunc.mon.start()
    
def stopMonitor():
    clutchfunc.mon.halt = True
    
def call(funcname,*args,**kwargs):
    f = clutchfunc.funcs[funcname]
    return f(*args,**kwargs)

class functionMonitor(threading.Thread):
    def __init__(self,interval=5):
        threading.Thread.__init__(self)
        self.daemon = True
        self.mtime = {}
        self.queue = []
        self.interval = interval
        self.halt = False
        
    def run(self):
        while not self.halt:
            self._scan()
            time.sleep(self.interval)
            
    def _scan(self):
        loadFuncs(clutchfunc.directory) # Rescan director for new modules
        rescanFuncs() # Rescan existing modules for new or changed functions

class clutchfunc(object):
    
    modules = []
    funcs = {}
    func_order = []
    func_lock = threading.Lock()
    directory = None

    def __init__(self, f):
        # Init is used by the function decorator
        if f.__name__ in clutchfunc.funcs:
            print "Variable name must be unique (func will not load):",f.__name__," in ",f.__module__
        else:
            print f.__name__,
            f.target = f.__name__
            f.dependencies = set(f.func_code.co_varnames[:f.func_code.co_argcount])
            self.func = f
            clutchfunc.funcs[f.target] = f
            clutchfunc.func_order = [] # Since we've added a func, order is unknown
        


   #  Need to catch errors on import and reload in these functions to avoid a syntax
   # error bringing down the system, just don't load that module
        
