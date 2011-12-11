import ClutchFunc
import time

ClutchFunc.clutchfunc.loadFuncs('Functions')
mon = ClutchFunc.functionMonitor()
mon.start()


data = {'a':1,'b':2}
print data
new_data = ClutchFunc.clutchfunc.runFuncs(data,['a','b'],[])
data.update(new_data)
print data
new_data = ClutchFunc.clutchfunc.runFuncs(data,['a','b'],[])


# for i in range(10):
    # time.sleep(5)
    # print "----------------------------------"
    # ClutchFunc.clutchfunc.runFuncs()
    