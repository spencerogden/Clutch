from ClutchFunc import clutchfunc
from math import acos,radians, cos

@clutchfunc
def targTWAUp(TWS,tablelibrary):
    targs = tablelibrary.tables['polars'].lookup_targs(TWS)
    return targs.twa_up

@clutchfunc    
def targTWADn(TWS,tablelibrary):
    targs = tablelibrary.tables['polars'].lookup_targs(TWS)
    return targs.twa_dn

@clutchfunc    
def targBSPUp(TWS,tablelibrary):
    targs = tablelibrary.tables['polars'].lookup_targs(TWS)
    return targs.bsp_up

@clutchfunc    
def targBSPDn(TWS,tablelibrary):
    targs = tablelibrary.tables['polars'].lookup_targs(TWS)
    return targs.bsp_dn

@clutchfunc    
def targBSP(targBSPUp,targBSPDn,TWA):
    if abs(TWA) <= 90:
        return targBSPUp
    else:
        return targBSPDn

@clutchfunc    
def targTWA(targTWAUP, targTWADn, TWA):
    if abs(TWA) <= 90:
        return targTWAUp
    else:
        return targTWADn

@clutchfunc        
def targVMGUp(targBSPUp, targTWAUp):
    return targBSPUp * cos( radians(targTWAUp) )
    
@clutchfunc
def targVMGDn(targBSPDn, targTWADn):
    return targBSPDn * cos( radians(targTWADn) )
    
@clutchfunc
def targVMG(TWA, targVMGUp, targVMGDn):
    if abs(TWA) <= 90:
        return targVMGUp
    else:
        return targVMGDn
        
@clutchfunc
def polarBSP( TWS, TWA,tablelibrary ):
    return tablelibrary.tables['polars'].lookup( TWS, TWA )
    