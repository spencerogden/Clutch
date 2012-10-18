#!/usr/bin/python
# -*- coding: utf-8 -*-

# Position objects
#   Parsing of various lat lon formats
#   Create new position given range and bearing
#   Distance between position and list of points
#   Distance from position to closet point on a line (signed and unsigned)
#   bearing between two points (true, mag later)
#   bounding boxes/regions, see if point is within an area
#   new position based on average of points

# Check out pyproj for future more complicated math

# TODO
# Testing of intersection calc
# Set module variable to set print format of lat/lon to several common options
# Check against another source of distances and bearings
# Possible future optimization. If we judge that positions are "close", or range is small
#   Use simple haversine formula instead
# Can declination calc be simplified? At least should have maybe save calcs by assuming all calls will be at the same clock time

from math import sin, cos, tan, asin, acos, atan, atan2, radians, degrees, sqrt, pi, fabs
import weakref
from datetime import date
import os
import re

# Formulas and constants for Vincenty calcs from
# http://www.movable-type.co.uk/scripts/latlong-vincenty.html

# WGS-84 Parameters in meters 
m_in_nm = 1852 # meters in a nautical mile
a = 6378137
b = 6356752.314245
f = 1 / 298.257223563
fSq = (a*a - b*b) / (b*b)
R = (a+b)/2
iter_max = 100

class Position(object):
    def __init__(self,lat=None,lon=None,datum='WGS84'):
        if isinstance(lat, str):
            self.lat = deg(lat)
        else:
            self.lat = lat
        
        if isinstance(lon, str):
            self.lon = deg(lon)
        else:
            self.lon = lon
            
        self.datum = datum # Only support WGS84, this just for future use
        self.pos_cache = weakref.WeakKeyDictionary()
        self.rb_cache = dict()
        self.dec = gm.mag_decl( self.lat , self.lon ) # Get magnetic variation at this Position now.
            # Positions are unlikely to live long enough for time variation to matter
            # gm is an instance of GeoMag below
        
    def true(bearing_mag):
        """Convert mag bearing to true at this position"""
        return bearing_mag - self.dec
        
    def mag(bearing_true):
        """Convert true to mag at this position"""
        return bearing_true + self.dec
        
    def pos_at_range_bearing(self, range, bearing):
        """Return a new Position at a range (nm) and bearing (T) from this position, great circle"""
        (r,b) = (range * m_in_nm, bearing)
        # given a position, a range in nm, and a bearing in true, return the position
        if (r,b) not in self.rb_cache:
            (lat, lon, revBrng) = vincenty_direct( self.lat, self.lon, r, b )
            self.rb_cache[(r,b)] = Position(lat, lon)
        return self.rb_cache[(r,b)]
        
    def range_to(self, pos2):
        """ Return range (nm) between the two points, great circle"""
        if pos2 not in self.pos_cache:
            self.pos_cache[pos2] = vincenty_inverse( self.lat, self.lon, pos2.lat, pos2.lon )
        return self.pos_cache[pos2][0] / m_in_nm
        
    def brng_to(self, pos2):
        """Returns bearing (T) from position to pos2, great circle route is used, so start bearing may differ from end bearing"""
        if pos2 not in self.pos_cache:
            self.pos_cache[pos2] = vincenty_inverse( self.lat, self.lon, pos2.lat, pos2.lon )
        return self.pos_cache[pos2][1]
        
    def brng_from(self, pos2):
        """Returns the bearing (T) from a position on the great circle route"""
        if pos2 not in self.pos_cache:
            self.pos_cache[pos2] = vincenty_inverse( self.lat, self.lon, pos2.lat, pos2.lon )
        return (self.pos_cache[pos2][2] + 180 ) % 360
        
    def xte(self, pos2, pos3):
        """Returns the distance to great cirlce route defined by pos2 and pos3"""   
        x = cross_track_distance( self.lat,self.lon,pos2.lat,pos2.lon,pos3.lat,pos3.lon)
        return x[0] / m_in_nm
        
    def dfs(self, pos2, pos3):
        """Return the distance from the start of the route from pos2 to pos3"""
        x = cross_track_distance( self.lat,self.lon,pos2.lat,pos2.lon,pos3.lat,pos3.lon)
        return x[1] / m_in_nm
    
    def dtf(self, pos2, pos3):
        """Return distance to finish of route from pos2 to pos3"""
        x = cross_track_distance( self.lat,self.lon,pos2.lat,pos2.lon,pos3.lat,pos3.lon)
        return x[2] - x[1]
        
    def intersect( self, brng, pos2, pos3):
        # Return the range at which a line from self along brng intersects a line defined by pos2, pos3
        brng1 = brng
        brng2 = pos2.brng_to(pos3)
        (r,b) = intersection( self.lat, self.lon, brng1, pos2.lat, pos2.lon, brng2)
        return r
        
    def __str__(self):
        return "lat/lon: %0+10.6f/%0+11.6f" % (self.lat,self.lon)
        
# Latitude/longitude spherical geodesy formulae & scripts (c) Chris Veness 2002-2011
# - www.movable-type.co.uk/scripts/latlong.html  
     
def vincenty_inverse( lat1, lon1, lat2, lon2 ):
    lat1 = radians( lat1 )
    lon1 = radians( lon1 )
    
    lat2 = radians( lat2 )
    lon2 = radians( lon2 )
    
    L = lon2 - lon1
    U1 = atan((1-f) * tan(lat1))
    U2 = atan((1-f) * tan(lat2))
    sinU1 = sin(U1)
    cosU1 = cos(U1)
    sinU2 = sin(U2)
    cosU2 = cos(U2)
    
    l = L
    for i in range(iter_max):
        sinLambda = sin(l)
        cosLambda = cos(l)
        sinSigma = sqrt( cosU2*sinLambda * cosU2*sinLambda + 
                         (cosU1*sinU2 - sinU1*cosU2*cosLambda) * (cosU1*sinU2 - sinU1*cosU2*cosLambda) )
        cosSigma = sinU1*sinU2 + cosU1*cosU2*cosLambda
        sigma = atan2( sinSigma, cosSigma )
        sinAlpha = cosU1*cosU2*sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha * sinAlpha
        try:
            cos2SigmaM = cosSigma - 2*sinU1*sinU2/cosSqAlpha
        except:
            cos2SigmaM = 0
        C = f/16*cosSqAlpha*(4+f*(4-3*cosSqAlpha))
        lambda_prev = l
        l = L + (1-C) * f * sinAlpha * (sigma + C*sinSigma*(cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))
        if abs(lambda_prev-l) < 1e-12:
            break
            
    # Should raise exception if above doesn't converge, ie all iters are run
    
    uSq = cosSqAlpha * (a*a - b*b) / (b*b)
    A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
    B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
    deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM) - B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
    rng = b*A*(sigma - deltaSigma)
    initBearing = degrees(atan2(cosU2*sinLambda, cosU1*sinU2 - sinU1*cosU2*cosLambda)) 
    finalBearing = degrees(atan2(cosU1*sinLambda, -sinU1*cosU2 + cosU1*sinU2*cosLambda)) 
    return (rng,(initBearing)%360,(finalBearing)%360) 
    
def vincenty_direct( lat, lon, rng, brng ):
    s = rng
    alpha1 = radians(brng)
    sinAlpha1 = sin(alpha1)
    cosAlpha1 = cos(alpha1)
    
    tanU1 = (1-f) * tan( radians(lat) )
    cosU1 = 1 / sqrt( 1+tanU1*tanU1 )
    sinU1 = tanU1 * cosU1
    sigma1 = atan2(tanU1, cosAlpha1)
    sinAlpha = cosU1 * sinAlpha1
    cosSqAlpha = 1 - sinAlpha*sinAlpha
    uSq = cosSqAlpha * (a*a - b*b) / (b*b)
    A = 1 + uSq/16384 * (4096+uSq*(-768+uSq*(320-175*uSq)))
    B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
    
    sigma = s / (b*A)
    sigma_prev = 2*pi
    while abs(sigma - sigma_prev) > 1e-12:
        cos2SigmaM = cos(2*sigma1 + sigma)
        sinSigma = sin(sigma)
        cosSigma = cos(sigma)
        deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)-B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
        sigma_prev = sigma
        sigma = s / (b*A) + deltaSigma
        
    tmp = sinU1*sinSigma - cosU1*cosSigma*cosAlpha1
    lat2 = atan2( sinU1*cosSigma + cosU1*sinSigma*cosAlpha1,(1-f)*sqrt(sinAlpha*sinAlpha + tmp*tmp))
    l = atan2(sinSigma*sinAlpha1, cosU1*cosSigma - sinU1*sinSigma*cosAlpha1)
    C = f/16*cosSqAlpha*(4+f*(4-3*cosSqAlpha))
    L = l - (1-C) * f * sinAlpha * (sigma + C*sinSigma*(cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))
    lon2 = (radians(lon) + L + 3*pi)%(2*pi) - pi
    
    revBrng = atan2(sinAlpha, -tmp)
    return ( degrees(lat2), degrees(lon2), degrees(revBrng) )
    
def haversine_direct( lat, lon, rng, brng ):
    # given a position, a range in nm, and a bearing in true, return the position
    dR = range / 3440.07 # Earth's Radius in nm
    theta = radians( brng )
    lat2 = asin( sin(lat)*cos(dR) + cos(lat)*sin(dR)*cos(theta))
    lon2 = lon + atan2( sin(theta)*sin(dR)*cos(lat), cos(dR)-sin(lat)*sin(lat))
    return ( degrees(lat2), degrees(lat2), None )
    
def pythag_inverse( lat1, lon1, lat2, lon2 ):
    x = (lon2 - lon1)*cos((lat1+lat2)/2)
    y = lat2 - lat1
    rng = (a+b)/2 * sqrt(x*x + y*y)
    brng = degrees(atan2( x, y ))
    return (rng, brng, brng)
    
def intersection( lat1, lon1, brng1, lat2, lon2, brng2 ):
    """Return Position of intersection of two lines defined by points and bearings"""
    # Three points, point 3 is the intersection
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    brng13 = radians(brng1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    brng23 = radians(brng2)
    
    (dist12, brngA, brngB) = vincenty_inverse( lat1, lon1, lat2, lon2 )
    #dist12 = dist / ((a+b)/2) * 2 * pi # Radial distance
    
    if sin(lon2-lon1) > 0:
        brng12 = radians(brngA)
        brng21 = 2*pi - radians(brngB)
    else:
        brng12 = 2*pi - radians(brngA)
        brng21 = radians(brngB)
        
    alpha1 = (brng13 - brng12 + pi) % (2*pi) - pi # angle 2-1-3
    alpha2 = (brng21 - brng23 + pi) % (2*pi) - pi # angle 1-2-3
    
    if sin(alpha1)==0 and sin(alpha2)==0:
        return (R*4,R*4)
        # exception no intersection, point is inifinite
    if sin(alpha1)*sin(alpha2) < 0:
        return (R*4,R*4)
        # Ambiguous
        
    # angle 2-3-1
    alpha3 = acos (-cos(alpha1)*cos(alpha2) + sin(alpha1)*sin(alpha2)*cos(dist12) )
    dist13 = atan2( sin(dist12)*sin(alpha1)*sin(alpha2), cos(alpha2)+cos(alpha1)*cos(alpha3) )
    
    rng = dist13 / (2*pi) * (a-b)/2
    # range in meters from p1 to p3
    brng = brng1 # Bearing in degrees from p1 to p3
    #return vincenty_direct( lat1, lon1, rng, brng )
    return (rng,brng)
    
def cross_track_distance( lat1, lon1, lat2, lon2, lat3, lon3 ):
    """Return distance in meters p3 is from the great circle route defiend by p1 and p2
       also distance along track"""
    ( d13, brng13, revBrng13 ) = vincenty_inverse( lat1, lon1, lat3, lon3 )
    ( d12, brng12, rebBrng12 ) = vincenty_inverse( lat1, lon1, lat2, lon2 )
    dxt =  asin(sin(d13/R)*sin(radians(brng13-brng12))) * R
    dat = acos(cos(d13/R)/cos(dxt/R)) * R
    return (dxt, dat, d12)
    
# Declination Calculations from geomag.py
# by Christopher Weiss cmweiss@gmail.com
# http://nullege.com/codes/show/src@geomag-0.9@geomag@geomag.py

class GeoMag:
    def mag_decl(self, dlat, dlon, h=0, time=date.today()): # latitude (decimal degrees), longitude (decimal degrees), altitude (feet), date
        time = time.year+((time - date(time.year,1,1)).days/365.0)
        alt = h/3280.8399
  
        otime = oalt = olat = olon = -1000.0
  
        dt = time - self.epoch
        glat = dlat
        glon = dlon
        rlat = radians(glat)
        rlon = radians(glon)
        srlon = sin(rlon)
        srlat = sin(rlat)
        crlon = cos(rlon)
        crlat = cos(rlat)
        srlat2 = srlat*srlat
        crlat2 = crlat*crlat
        self.sp[1] = srlon
        self.cp[1] = crlon
  
        # CONVERT FROM GEODETIC COORDS. TO SPHERICAL COORDS. 
        if (alt != oalt or glat != olat):
            q = sqrt(self.a2-self.c2*srlat2)
            q1 = alt*q
            q2 = ((q1+self.a2)/(q1+self.b2))*((q1+self.a2)/(q1+self.b2))
            ct = srlat/sqrt(q2*crlat2+srlat2)
            st = sqrt(1.0-(ct*ct))
            r2 = (alt*alt)+2.0*q1+(self.a4-self.c4*srlat2)/(q*q)
            r = sqrt(r2)
            d = sqrt(self.a2*crlat2+self.b2*srlat2)
            ca = (alt+d)/r
            sa = self.c2*crlat*srlat/(r*d)
  
        if (glon != olon):
            for m in range(2,self.maxord+1):
                self.sp[m] = self.sp[1]*self.cp[m-1]+self.cp[1]*self.sp[m-1]
                self.cp[m] = self.cp[1]*self.cp[m-1]-self.sp[1]*self.sp[m-1]
  
        aor = self.re/r
        ar = aor*aor
        br = bt = bp = bpp = 0.0
        for n in range(1,self.maxord+1):
            ar = ar*aor
  
            m=0
            D3=1
            D4=(n+m+1)
            
            while D4>0:
                # COMPUTE UNNORMALIZED ASSOCIATED LEGENDRE POLYNOMIALS
                # AND DERIVATIVES VIA RECURSION RELATIONS
                if (alt != oalt or glat != olat):
                    if (n == m):
                        self.p[m][n] = st * self.p[m-1][n-1]
                        self.dp[m][n] = st*self.dp[m-1][n-1]+ct*self.p[m-1][n-1]
  
                    elif (n == 1 and m == 0):
                        self.p[m][n] = ct*self.p[m][n-1]
                        self.dp[m][n] = ct*self.dp[m][n-1]-st*self.p[m][n-1]
  
                    elif (n > 1 and n != m):
                        if (m > n-2):
                            self.p[m][n-2] = 0
                        if (m > n-2):
                            self.dp[m][n-2] = 0.0
                        self.p[m][n] = ct*self.p[m][n-1]-self.k[m][n]*self.p[m][n-2]
                        self.dp[m][n] = ct*self.dp[m][n-1] - st*self.p[m][n-1]-self.k[m][n]*self.dp[m][n-2]
  
                # TIME ADJUST THE GAUSS COEFFICIENTS
                if (time != otime):
                    self.tc[m][n] = self.c[m][n]+dt*self.cd[m][n]
                    if (m != 0):
                        self.tc[n][m-1] = self.c[n][m-1]+dt*self.cd[n][m-1]
  
                # ACCUMULATE TERMS OF THE SPHERICAL HARMONIC EXPANSIONS
                par = ar*self.p[m][n]
  
                if (m == 0):
                    temp1 = self.tc[m][n]*self.cp[m]
                    temp2 = self.tc[m][n]*self.sp[m]
                else:
                    temp1 = self.tc[m][n]*self.cp[m]+self.tc[n][m-1]*self.sp[m]
                    temp2 = self.tc[m][n]*self.sp[m]-self.tc[n][m-1]*self.cp[m]
  
                bt = bt-ar*temp1*self.dp[m][n]
                bp = bp + (self.fm[m] * temp2 * par)
                br = br + (self.fn[n] * temp1 * par)

                # SPECIAL CASE:  NORTH/SOUTH GEOGRAPHIC POLES
                if (st == 0.0 and m == 1):
                    if (n == 1):
                        self.pp[n] = self.pp[n-1]
                    else:
                        self.pp[n] = ct*self.pp[n-1]-self.k[m][n]*self.pp[n-2]
                    parp = ar*self.pp[n]
                    bpp = bpp + (self.fm[m]*temp2*parp)
  
                D4=D4-1
                m=m+1
  
        if (st == 0.0):
            bp = bpp
        else:
            bp = bp/st

        # ROTATE MAGNETIC VECTOR COMPONENTS FROM SPHERICAL TO
        # GEODETIC COORDINATES
        bx = -bt*ca-br*sa
        by = bp
        bz = bt*sa-br*ca
        
        # COMPUTE DECLINATION (DEC), INCLINATION (DIP) AND
        # TOTAL INTENSITY (TI)
        bh = sqrt((bx*bx)+(by*by))
        ti = sqrt((bh*bh)+(bz*bz))
        dec = degrees(atan2(by,bx))
        dip = degrees(atan2(bz,bh))

        # COMPUTE MAGNETIC GRID VARIATION IF THE CURRENT
        # GEODETIC POSITION IS IN THE ARCTIC OR ANTARCTIC
        # (I.E. GLAT > +55 DEGREES OR GLAT < -55 DEGREES)
        # OTHERWISE, SET MAGNETIC GRID VARIATION TO -999.0
        gv = -999.0
        if (fabs(glat) >= 55.):
            if (glat > 0.0 and glon >= 0.0):
                gv = dec-glon
            if (glat > 0.0 and glon < 0.0):
                gv = dec+fabs(glon);
            if (glat < 0.0 and glon >= 0.0):
                gv = dec+glon
            if (glat < 0.0 and glon < 0.0):
                gv = dec-fabs(glon)
            if (gv > +180.0):
                gv = gv - 360.0
            if (gv < -180.0):
                gv = gv + 360.0
  
        otime = time
        oalt = alt
        olat = glat
        olon = glon
  
        # Available outputs
        # dec = declination, magnetic variation
        # dip = inclination
        # ti
        # bh
        # bx
        # by
        # bz
        # dlat
        # dlon
        # h
        # time
  
        return dec
  
    def __init__(self, wmm_filename="WMM/WMM.COF"):
        import sys
        if getattr(sys, 'frozen', None):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(__file__)
            
        fullpath = os.path.join(basedir, wmm_filename)
        wmm=[]
        with open(fullpath) as wmm_file:
            for line in wmm_file:
                linevals = line.strip().split()
                if len(linevals) == 3:
                    self.epoch = float(linevals[0])
                    self.model = linevals[1]
                    self.modeldate = linevals[2]
                elif len(linevals) == 6:
                    linedict = {'n': int(float(linevals[0])),
                    'm': int(float(linevals[1])),
                    'gnm': float(linevals[2]),
                    'hnm': float(linevals[3]),
                    'dgnm': float(linevals[4]),
                    'dhnm': float(linevals[5])}
                    wmm.append(linedict)
  
        z = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.maxord = self.maxdeg = 12
        self.tc = [z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13]]
        self.sp = z[0:14]
        self.cp = z[0:14]
        self.cp[0] = 1.0
        self.pp = z[0:13]
        self.pp[0] = 1.0
        self.p = [z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14]]
        self.p[0][0] = 1.0
        self.dp = [z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13]]
        self.a = 6378.137
        self.b = 6356.7523142
        self.re = 6371.2
        self.a2 = self.a*self.a
        self.b2 = self.b*self.b
        self.c2 = self.a2-self.b2
        self.a4 = self.a2*self.a2
        self.b4 = self.b2*self.b2
        self.c4 = self.a4 - self.b4
  
        self.c = [z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14]]
        self.cd = [z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14]]
  
        for wmmnm in wmm:
            m = wmmnm['m']
            n = wmmnm['n']
            gnm = wmmnm['gnm']
            hnm = wmmnm['hnm']
            dgnm = wmmnm['dgnm']
            dhnm = wmmnm['dhnm']
            if (m <= n):
                self.c[m][n] = gnm
                self.cd[m][n] = dgnm
                if (m != 0):
                    self.c[n][m-1] = hnm
                    self.cd[n][m-1] = dhnm
  
        # CONVERT SCHMIDT NORMALIZED GAUSS COEFFICIENTS TO UNNORMALIZED
        self.snorm = [z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13]]
        self.snorm[0][0] = 1.0
        self.k = [z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13]]
        self.k[1][1] = 0.0
        self.fn = [0.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0]
        self.fm = [0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0]
        for n in range(1,self.maxord+1):
            self.snorm[0][n] = self.snorm[0][n-1]*(2.0*n-1)/n
            j=2.0
            m=0
            D1=1
            D2=(n-m+D1)/D1
            while (D2 > 0):
                self.k[m][n] = (((n-1)*(n-1))-(m*m))/((2.0*n-1)*(2.0*n-3.0))
                if (m > 0):
                    flnmj = ((n-m+1.0)*j)/(n+m)
                    self.snorm[m][n] = self.snorm[m-1][n]*sqrt(flnmj)
                    j = 1.0
                    self.c[n][m-1] = self.snorm[m][n]*self.c[n][m-1]
                    self.cd[n][m-1] = self.snorm[m][n]*self.cd[n][m-1]
                self.c[m][n] = self.snorm[m][n]*self.c[m][n]
                self.cd[m][n] = self.snorm[m][n]*self.cd[m][n]
                D2=D2-1
                m=m+D1             
                
gm = GeoMag()

def deg(dms_string):
    # ISO 6709 = +DDDMMSS.sss
    # \u00B0 unicode degree symbol
    # DDD* MM' SS.sss"
    # DDD*
    dms_re = ur'^\s*([+NE]?)([-WS]?)\s*(\d+\.?\d*)\s*[*\u00B0°]?\s*(\d+\.?\d*)?\s*\'?\s*(\d+\.?\d*)?\s*"?\s*([+NE]?)([-WS]?)\s*$'
    iso_re = r'^\s*([+-])?(\d{1})?(\d{2})(\d{2})?(\d{2}\.?\d*)?\s*$'
    iso_lat_re = r"^\s*([-+])?(\d{2})(\d{2})?(\d{2}\.?\d*)?\s*$"
    iso_lon_re = r"^\s*([-+])?(\d{3})(\d{2})?(\d{2}\.?\d*)?\s*$"
    dms_m =     re.search(dms_re, dms_string)
    iso_lat_m = re.search(iso_lat_re, dms_string)
    iso_lon_m = re.search(iso_lon_re, dms_string)
    
    if iso_lat_m:
        iso_m = iso_lat_m
    else:   
        iso_m = iso_lon_m
        
    sign = 1
    deg  = 0
    min  = 0
    sec  = 0
    
    if iso_m: 
        if iso_m.group(1) == "-":
            sign = -1
        deg = float(iso_m.group(2))
        min = float(iso_m.group(3)) if iso_m.group(3) else 0
        sec = float(iso_m.group(4)) if iso_m.group(4) else 0
    elif dms_m:
        # We have a match for DMS
        if dms_m.group(2) or dms_m.group(7):
            sign = -1 # If w matched a -, W, or S sign is negative
        deg = float(dms_m.group(3))
        min = float(dms_m.group(4)) if dms_m.group(4) else 0
        sec = float(dms_m.group(5)) if dms_m.group(5) else 0
        
    else:
        # Can't parse
        raise "Invalid Lat or Lon format"
    
    deg = sign * (deg + min / 60.0 + sec / (60.0*60.0))
    
    return deg
        
    