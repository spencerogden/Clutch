#!/usr/bin/python

# Position objects
#   Parsing of various lat lon formats
#   Create new position given range and bearing
#   Distance between position and list of points
#   Distance from position to closet point on a line (signed and unsigned)
#   bearing between two points (true, mag later)
#   bounding boxes/regions, see if point is within an area
#   new position based on average of points

# Check out pyproj for future more complicated math

from math import sin, cos, asin, atan2, radians, degrees

class Position(object):
    def __init__(self,lat=None,lon=None,datum='WGS84'):
        self.lat = lat # Assume lat and lon are passed as floats for now
        self.lon = lon
        self.datum = datum # Only support WGS84, this just for future use

    def pos_at_range_bearing(self, range, bearing):
        # given a position, a range in nm, and a bearing in true, return the position
        lat1 = self.lat
        lon1 = self.lon
        dR = range / 3440.07 # Earth's Radius in nm
        theta = radians( bearing )
        lat2 = asin( sin(lat1)*cos(dR) + cos(lat1)*sin(dR)*cos(theta))
        lon2 = lon1 + atan2( sin(theta)*sin(dR)*cos(lat1), cos(dR)-sin(lat1)*sin(lat2))
        
        return Position(lat=lat2,lon=lon2)
        
    def __str__(self):
        return "lat/lon: %0+10.6f/%0+11.6f" % (self.lat,self.lon)