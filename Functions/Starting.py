from ClutchFunc import clutchfunc
import datetime
import math    
    
@clutchfunc
def LnLength(course):
    if course.star_end and course.port_end:
        return course.star_end.range_to(course.port_end)
    else:   
        return None
   
@clutchfunc   
def LnBiasAng(course,TWD):
    """Line bias in degrees, negative is port end favored"""
    if course.star_end and course.port_end:
        return ((TWD+90)%360 - course.port_end.brng_to(course.star_end)+90)%180 - 90
    else:
        return None

@clutchfunc
def LnLengthTime(LnLength, TWS, TWD, tablelibrary):
    # Assume 90 TWA for now
    bsp = tablelibrary.tables['polars'].lookup(TWS,90)
    return datetime.timedelta(0,LnLength/bsp*3600)
    
# Break this calculation up:
# 1) Set positions for each intersection of target angle and 90 degree
# 2) Calculate distance to all
# 3) Calculate time to all
# 4) calculate minumums of the above.
    
@clutchfunc
def distToLine(course, Pos, TWD, TWS, distToPort, distToStar,distToLnPerp, targTWAUp, targTWADn, tablelibrary):
    """Distance to line or closest end of the line along possible polar angles
       (i.e. not above upwind targets or below downwind targets."""
    brngPort = Pos.brng_to(course.star_end.position)
    brngStar = Pos.brng_to(course.port_end.position)

    # Does a target angle intersect the line? point_target
    # Does a 90 degree line fall within the line? point_xte
    # pin and boat, point_port point_star
    # One of these 4 points must be the closest
    # Polar distance is always used
       
    targBrngUpStar = (TWD - targTWAUp) % 360
    targBrngUpPort = (TWD + targTWAUp) % 360
    targBrngDnStar = (TWD - targTWADn) % 360
    targBrngDnPort = (TWD + targTWADn) % 360    
    
    xteBrng = (course.star_end.brng_to(course.port_end) - cmp(distToLnPerp,0) * 90 ) % 360
    
    dist_list = []
    time_list = []
    def angleBetween( a,n, b ):
        # check if angle n is between a and b
        # all angle are [0,360)
        if a < b: return a < n < b
        else:     return a < n or n < b
        
    def polarDist( rng, brng ):
        TWA_at_brng = (TWD - brng) % 180 #a
        if targTWAUp <= TWA_at_brng <= targTWADn:
            return rng
        elif TWA_at_brng < targTWAUp:
            return rng * math.cos(math.radians(TWA_at_brng)) / math.cos(math.radians(targTWAUp))
        else:
            # brng must be below downwind targets
            return rng * math.cos(math.radians(TWA_at_brng)) / math.cos(math.radians(targTWADn))
    
    targ = tablelibrary.tables['polars'].lookup_targs( TWS )
    
    if angleBetween(brngPort,targBrngUpStar,brngStar):
        r = Pos.intersect( targBrngUpStar, course.star_end.position, course.port_end.position )
        dist_list.append(r)
        time_list.append(datetime.timedelta(0,r/targ.bsp_up*3600.0))
    if angleBetween(brngPort,targBrngUpPort,brngStar):
        r = Pos.intersect( targBrngUpPort, course.star_end.position, course.port_end.position )
        dist_list.append(r)
        time_list.append(datetime.timedelta(0,r/targ.bsp_up*3600.0))
    if angleBetween(brngPort,targBrngDnStar,brngStar):
        r = Pos.intersect( targBrngDnStar, course.star_end.position, course.port_end.position )
        dist_list.append(r)
        time_list.append(datetime.timedelta(0,r/targ.bsp_dn*3600.0))
    if angleBetween(brngPort,targBrngDnPort,brngStar):
        r = Pos.intersect( targBrngUpPort, course.star_end.position, course.port_end.position )
        dist_list.append(r)
        time_list.append(datetime.timedelta(0,r/targ.bsp_dn*3600.0))
    if angleBetween(brngPort,xteBrng,       brngStar):
        xte = Pos.xte(course.star_end.position, course.port_end.position)
        # This is the straight distance
        dist_list.append(polarDist( xte, xteBrng ))
        bsp = tablelibrary.tables['polars'].lookup( TWS, (TWD - xteBrng) % 180 )
        time_list.append(datetime.timedelta(0,r/bsp*3600.0))
    
    dist_list.append(polarDist( distToStar, brngStar ))
    bsp = tablelibrary.tables['polars'].lookup( TWS, (TWD - brngStar)%180 )
    time_list.append(datetime.timedelta(0,distToStar/bsp*3600.0))
    dist_list.append(polarDist( distToPort, brngPort ))
    bsp = tablelibrary.tables['polars'].lookup( TWS, (TWD - brngPort)%180 )
    time_list.append(datetime.timedelta(0,distToPort/bsp*3600.0))
    
    index = time_list.index(min(time_list))
        
    return {'distToLine': dist_list[index], 'timeToLine': time_list[index]}

@clutchfunc    
def distToLnPerp(course,Pos):   
    """Distance perpendicular to the line. Distance to an extension of the line is returned outside the line"""
    return Pos.xte(course.star_end.position, course.port_end.position)
    
@clutchfunc
def distToPort(course, Pos):
    if course.port_end:
        return Pos.range_to(course.port_end.position)
        
@clutchfunc
def distToStar(course, Pos):
    if course.star_end:
        return Pos.range_to(course.star_end.position)
    
def bearToLine():
    """Bearing to line either along target angle, or to closest end if outside the line"""
    pass
    
def timeToLine():
    """Time to the line according to starting polars."""
    pass
    
def timeToGun():
    """Time to starting gun"""
    pass
    
def timeToBurn():
    """Time to burn before full acceleration is needed to reach the line on time"""
    pass
    
def LnBiasBL():
    """Line bias measured by boat lengths."""
    pass
    
def startDeltaTime():
    """Time before or after the start line was crossed."""
    pass
    
def startDeltaBL():
    """Boat Lengths below or over the start line at the start."""
    pass
    