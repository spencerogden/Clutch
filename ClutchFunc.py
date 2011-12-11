import sys,os,glob,threading,time,types

class functionMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.mtime = {}
        self.queue = []
        self.interval = 1
        
    def run(self):
        while True:
            self._scan()
            time.sleep(self.interval)
            
    def _scan(self):
        for m in clutchfunc.modules:
            try:
                stat = os.stat(m.__fullfile__)
            except OSError:
                continue
            #print "Checking",m.__fullfile__,"with previous mtime",m.__mtime__,"and mtime",stat.st_mtime
            if stat.st_mtime != m.__mtime__:
                print "Reloading",m.__name__
                print "dir",dir(m)
                funcs_to_remove = [getattr(m,f) for f in dir(m) if isinstance(getattr(m,f),clutchfunc)]
                print "Removing",funcs_to_remove
                for f in funcs_to_remove:
                    local_funcs = set()
                    local_funcs.update(clutchfunc.funcs)
                    for cf in local_funcs:
                        if f.func.target == cf.target:
                            print "Removed",f.func.target
                            clutchfunc.funcs.remove(cf)
                reload(m)
                m.__mtime__ = stat.st_mtime

class clutchfunc(object):
        
        modules = []
        funcs = []

        def __init__(self, f):
            f.target = f.__name__
            if f.target in clutchfunc.funcs:
                print "Variable name must be unique:",f.target," in ",f.__module__
            f.dependencies = set(f.func_code.co_varnames[:f.func_code.co_argcount])
            self.func = f
            clutchfunc.funcs.append(f)
			
        # def __call__(self):
			# print "Entering ", self.func.__name__
			# self.func(1,2)
			# print "Exited ", self.func.__name__ 

        @staticmethod
        def loadFuncs(directory):
            clutchfunc.directory = directory
            clutchfunc.path = os.path.join(os.getcwd(),os.path.dirname(__file__),directory)
            standard_syspath = sys.path
            sys.path.insert(0,clutchfunc.path)
            pyfiles = glob.glob(os.path.join(clutchfunc.path,"*.py"))
            for f in pyfiles:
                filename = os.path.basename(f)[:-3]
                print "importing " + filename
                clutchfunc.modules.append(__import__(filename))
                clutchfunc.modules[-1].__fullfile__ = f
                try:
                    stat = os.stat(f)
                except OSError:
                    continue
                clutchfunc.modules[-1].__mtime__ = stat.st_mtime
            sys.path = standard_syspath
            
        @staticmethod
        def runFuncs(data,changed,unchanged):
            #unknown = [var for var in data.keys() if not(var in changes or var in unchanged)]
            print "changed",changed
            print "unchanged",unchanged
            ch = set(changed)
            unch = set(unchanged)
            #print "unknown",unknown
            fs = []
            fs.extend(clutchfunc.funcs)
            
            new_data = {}
            
            seen = set()
            pos = 0
            while pos < len(clutchfunc.funcs):
                f = clutchfunc.funcs[pos]
                print "Trying to run",f.target,"needs",f.dependencies
                print "Know states for",ch.union(unch)
                if f.dependencies.issubset(unch):
                    # this function does not need to run
                    unch.add(f.target)
                    pos += 1
                elif f.dependencies.issubset(unch.union(ch)):
                    # All of this fucntions dependencies are in a known state, we can calc
                    inputs = map(dict(data.items() + new_data.items()).get,f.dependencies)
                    new_data[f.target] = f(*inputs)
                    ch.add(f.target)
                    pos += 1
                else:
                    # Depency are unknown, try to wait for later, move to end of list
                    if f in seen:
                        print "Function error, all functions tried and inputs of",f.target,"not found"
                        break
                    del clutchfunc.funcs[pos]
                    clutchfunc.funcs.append(f)
                seen.add(f)
            return new_data
 
        