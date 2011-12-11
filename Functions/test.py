from ClutchFunc import clutchfunc

print "Imported " + __name__

@clutchfunc
def layer(test):
    return test+5
    

@clutchfunc
def test(a,b):
    print "test function"
    return a+b
    
@clutchfunc
def TWA(BSP):
    pass
    