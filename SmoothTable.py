#!/usr/bin/python

# Boat related data
# Polars - Start, Performance
# Acceleration, Rate of Turn, Braking
# Auto learn boat specific cals by observing manuvers when race clock is negative
# Something like use 90% of the fastest turn, acceleration or brake

    
import math
import datetime
import operator
import sys

class Point:
    def __init__(self,x,y=None,z=None):
        print "Creating point with x %r, y %r, z %r" % (x,y,z)
        if isinstance(x, tuple):
            print "x is a tuple"
            self.x = x[0]
            self.y = x[1]
            if len(x) == 3:
                self.z = x[2]
        elif isinstance(x, Point):
            print "x is a Point"
            self.x = x.x
            self.y = x.y
            self.z = x.z
        else:
            print "x,y,z supplied"
            self.x = x
            self.y = y
            self.z = z
            
        print "New Point (%r,%r,%r)" % (self.x,self.y,self.z)
        
class Edge:
    def __init__(self,p1,p2):
        self.p1 = Point(p1)
        self.p2 = Point(p2)
        self.points = [p1,p2]
        
    def has_point(self,p):
        return p in self.points
        
class Triangle:
    def __init__(self,p1,p2,p3):
        self.p1 = Point(p1)
        self.p2 = Point(p2)
        self.p3 = Point(p3)
            
        self.points = [self.p1,self.p2,self.p3]
        
        self.e1 = Edge(p1,p2)
        self.e2 = Edge(p2,p3)
        self.e3 = Edge(p3,p1)
        
        self.edges = [self.e1,self.e2,self.e3]
        
        self.neighbors = {}
    
    def has_edge(self,e):
        return e in self.edges
    def has_point(self,p): 
        return p in self.points
    def point_opposite_edge(self, edge):
        return [p for p in self.points if p != edge.p1 and p != edge.p2][0]
    def other_edges(self,edge):
        return [e for e in self.edges if e != edge]

class Polars(object):
    def __init__(self):
        self.simple_polars = {
            0:  {0: 0, 35: 0,   45: 0.0, 60: 0.0, 90: 0, 120: 0.0, 145:  0.0, 180: 0.0}, 
            10: {0: 0, 35: 7.0, 45: 8.0, 60: 8.5, 90: 9, 120: 9.5, 145: 10.5, 180: 8.0},
            20: {0: 0, 35: 8.0, 45: 9.0, 60: 9.5, 90: 10, 120: 10.5, 145: 11.5, 180: 9.0},
            }
        self.simple_polars = {
            0.0: {0.0:0, 90.0:0},
            10.0:{0.0:0, 90.0:10},
        }
        
        self.defined_points = []
        # dict with points as keys, set of edges containin point as value
        for tws in self.simple_polars.keys():
            for twa in self.simple_polars[tws].keys():
                self.defined_points.append((tws,twa,self.simple_polars[tws][twa]))
                
        self.points = dict.fromkeys(self.defined_points)
        self.edges = {}
        
        # dict of edges as keys with containing triangles as values
        self.defined_triangles = delaunay(self.defined_points)
        self.triangles = self.defined_triangles
        
        #defiend_points and defined_triangles are the original inputs
        #further interpolation should store values in points, edges, and triangles
        
        self.buildIndex()
        
        self.interp_polars = {}
        self.polartws = sorted(self.simple_polars.keys())
        #self.polars[float('inf')] = self.polars[self.polartws[-1]]
        #self.polartws.append(float('inf'))
        
    def getTarget( self, tws, twa ):
        pass
        
    def interpPolar( self, tws, twa):
        for t in self.triangles:
            point = Point(tws,twa)
            v0 = (t.p3.x  - t.p1.x,  t.p3.y - t.p1.y)
            v1 = (t.p2.x  - t.p1.x,  t.p2.y - t.p1.y)
            v2 = (point.x - t.p1.x, point.y - t.p1.y)
            
            dot00 = sum(map(operator.mul,v0,v0))
            dot01 = sum(map(operator.mul,v0,v1))
            dot02 = sum(map(operator.mul,v0,v2))
            dot11 = sum(map(operator.mul,v1,v1))
            dot12 = sum(map(operator.mul,v1,v2))
            
            invDenom = 1/ float(dot00*dot11 - dot01*dot01)
            u = (dot11*dot02 - dot01*dot12) * invDenom
            v = (dot00*dot12 - dot01*dot02) * invDenom
            
            if u>=0 and v>=0 and (u+v) <= 1:
                # We are in the triangle
                z0 = t.p1.z
                z1 = t.p2.z
                z2 = t.p3.z
                
                return z0 + v*(z1-z0) + u*(z2-z0)
        return None # point is not within the defined area
        
    def buildIndex(self):
        self.edges = {}
        self.points = {}
        for t in self.triangles:
            for tn in self.triangles:
                # tn is a potential neighbor
                if t != tn: 
                    if   tn.has_edge(t.e1): t.neighbors[t.e1] = tn
                    elif tn.has_edge(t.e2): t.neighbors[t.e2] = tn
                    elif tn.has_edge(t.e3): t.neighbors[t.e3] = tn
            # fill out point and edge indices with objects triangles
            for e in t.edges:
                if e in self.edges:
                    self.edges[e].update({t})
                else:
                    self.edges[e] = set({t})
                for p in e.points:
                    if p in self.points:
                        self.points[p].update({e})
                    else:
                        self.points[p] = set({e})
                    
    def refine_polars(self):
        for e in self.edges.keys():
            # Set new point to midpoint, including z (bsp)
            new_point = Point((e.p1.x + e.p2.x) /2.0, 
                        ( e.p1.y + e.p2.y) /2.0, 
                        ( e.p1.z + e.p2.z) /2.0)
            containing_triangles = self.edges[e]
            neighboring_triangles = []
            number_of_points = 0
            sibling_point_sum = 0
            neighbor_point_sum = 0
            for t in containing_triangles:
                number_of_points += 1
                other_point = t.point_opposite_edge(e)
                sibling_point_sum += other_point.z
                eidx = t.edges.index(e) # Which edge are we dealing with
                # we want the neighbors on the other two edges
                other_edges = t.other_edges(e)
                for oe in other_edges:
                    neighbor = t.neighbors.get(oe,None)
                    if neighbor:
                        number_of_point += 1
                        neighbor_point_sum += neighbor.point_opposite_edge(e).z
            # w should be zero when either end of the edge is less than degree 6
            w = 1/16.0
            print "for edge %r with %d points the three components are %f, %f, %f" % (e,number_of_points,new_point[2],sibling_point_sum,neighbor_point_sum)
            new_point.z += 2*w*sibling_point_sum + w*neighbor_point_sum
            self.points[new_point] = set()
        self.defined_triangles = delaunay(points.keys())
        self.buildIndex()
                
    
def is_in_triangle(point,triangle):
    t = triangle
    v0 = (t.e2.x - t.e1.x,   t.e3.y - t.e1.y)
    v1 = (t.e2.x - t.e1.y,   t.e2.y - t.e1.y)
    v2 = (point.x - t.e1.x, point.y - t.e1.y)
    
    dot00 = sum(map(operator.mul,v0,v0))
    dot01 = sum(map(operator.mul,v0,v1))
    dot02 = sum(map(operator.mul,v0,v2))
    dot11 = sum(map(operator.mul,v1,v1))
    dot12 = sum(map(operator.mul,v1,v2))
    
    invDenom = 1/ float(dot00*dot11 - dot01*dot01)
    u = (dot11*dot02 - dot01*dot12) * invDenom
    v = (dot00*dot12 - dot01*dot02) * invDenom
    
    return u>0 and v>0 and (u+v) < 1


def delaunay(points):
    "Makes all calculation. You can specify the output type (curves or faces) and if you want to set a timer to see consumed time in the operation"
    numPoints = len(points)
    #create an empty triangle list
    triangles = []
    #and en empty list to store vertexes in order
    vertex = []
    
    for p in points:
        print p
    
    ##we need to start with a supertriangle which encompasses all the points
    ##this is done by getting the minimum and maximum bounds of all points
    ##and by adding a triangle to the triangles list which is a tad bigger than this bounds
    #copy the vertices list
    vs = points
    vertex.extend(vs)
    #make a series of operations to find minimum and maximum x and y values
    xmin = vs[0][0]
    ymin = vs[0][1]
    xmax = xmin
    ymax = ymin
    for i in range(numPoints):
        if vs[i][0] < xmin: xmin = vs[i][0]
        if vs[i][0] > xmax: xmax = vs[i][0]
        if vs[i][1] < ymin: ymin = vs[i][1]
        if vs[i][1] > ymax: ymax = vs[i][1] 
    #get min and max distances
    dx = xmax-xmin
    dy = ymax-ymin
    if dx > dy:
        dmax = dx
    else:
        dmax = dy
    #get mid points of these distances
    xmid = (xmax+xmin)/2
    ymid = (ymax+ymin)/2
    
    #calculate the coordinates of the vertices of the supertriangle
    #and add them to the end of the vertex list
    #and add this triangle to the triangles list (it is the first)
    v1x = xmid - 2*dmax
    v1y = ymid - dmax
    vertex.append([v1x, v1y])
    v2x = xmid
    v2y = ymid + 2*dmax
    vertex.append([v2x, v2y])
    v3x = xmid + 2*dmax
    v3y = ymid - dmax
    vertex.append([v3x, v3y])        
    triangles.append([numPoints,numPoints+1,numPoints+2])
    
    ##having already one triangle in the triangles list, we can start adding points
    ##and re-triangulate everytime we need
    
    #Include each point one at a time into the existing triangulations
    for i in range(len(vertex)):
        #if i is more than the original number of points, stop loop 
        #cos then it is a vertex of the supertriangle, and we don't need to calculate them
        if i >= numPoints: break
        #get current point i coordinates
        p = vertex[i]
        #Set up the edge buffer.
        #If the point (x,y) lies inside the circumcircle formed by each triangle, 
        #then the three edges of that triangle are added to the edge buffer.
        edges = []
        
        #create a copy of the triangles list to loop through
        tcopy = []
        tcopy.extend(triangles)
        #loop through the triangles to check the points
        for t in tcopy:
            #if the triangle is composed by the vertex in question (i), skip
            if i in t: continue
            #convert the triangle vertices to a list of coordinates
            tri=[ [vertex[k][0], vertex[k][1]] for k in t ]
            #check if the point i is in the circle formed by this triangle
            ic = inCircle(point=[p[0], p[1]], triangle=tri)
            if ic:
                #in case ic == true:
                #store the edges in the edges list
                edges.append([t[0], t[1]])
                edges.append([t[1], t[2]])
                edges.append([t[2], t[0]])
                #remove triangle from triangle list
                triangles.remove(t)
        
        #delete all duplicate edges from the edge buffer
        #this leaves the edges of the enclosing polygon only
        edges = removeDuplicates(edges)

        #add to the triangle list all triangles formed between the point
        #and the edges of the enclosing polygon (from the edge buffer
        for j in range(len(edges)):
            v1 = edges[j][0]
            v2 = edges[j][1]
            v3 = i
            triangles.append([v1,v2,v3])
        
    #end loop for vertices
    
    ###FINAL STEP
    # Filter triangle to remove triangles with are part of the super triangle and put into Triangle objects
    for v in vertex:
        print v
    triangles = [Triangle(vertex[i1],vertex[i2],vertex[i3]) for (i1,i2,i3) in triangles if i1 < numPoints and i2 < numPoints and i3 < numPoints]
            
    return triangles
        

def inCircle(point=[0,0], triangle=[[0,0],[0,0],[0,0]]):
    '''Series of calculations to check if a certain point lies inside lies inside the circumcircle
    made up by points in triangle (x1,y1) (x2,y2) (x3,y3)'''
    #adapted from Dimitrie Stefanescu's Rhinoscript version
    
    #Return TRUE if the point (xp,yp) 
    #The circumcircle centre is returned in (xc,yc) and the radius r
    #NOTE: A point on the edge is inside the circumcircle
    xp = float(point[0])
    yp = float(point[1])
    x1 = float(triangle[0][0])
    y1 = float(triangle[0][1])
    x2 = float(triangle[1][0])
    y2 = float(triangle[1][1])
    x3 = float(triangle[2][0])
    y3 = float(triangle[2][1])
    eps = 0.0001
    if math.fabs(y1-y2) < eps and math.fabs(y2-y3) < eps: return False
    
    if math.fabs(y2-y1) < eps:
        m2 = -(x3 - x2) / (y3 - y2)
        mx2 = (x2 + x3) / 2
        my2 = (y2 + y3) / 2
        xc = (x2 + x1) / 2
        yc = m2 * (xc - mx2) + my2
    elif math.fabs(y3-y2) < eps:
        m1 = -(x2 - x1) / (y2 - y1)
        mx1 = (x1 + x2) / 2
        my1 = (y1 + y2) / 2
        xc = (x3 + x2) / 2
        yc = m1 * (xc - mx1) + my1
    else:
        m1 = -(x2 - x1) / (y2 - y1)
        m2 = -(x3 - x2) / (y3 - y2)
        mx1 = (x1 + x2) / 2
        mx2 = (x2 + x3) / 2
        my1 = (y1 + y2) / 2
        my2 = (y2 + y3) / 2
        xc = (m1 * mx1 - m2 * mx2 + my2 - my1) / (m1 - m2)
        yc = m1 * (xc - mx1) + my1
    #end if
    dx = x2 - xc
    dy = y2 - yc
    rsqr = dx * dx + dy * dy
    r = math.sqrt(rsqr)
    dx = xp - xc
    dy = yp - yc
    drsqr = dx * dx + dy * dy
    
    return drsqr <= rsqr
    
def removeDuplicates(a):
	"Gets a list of lists and removes the duplicates"
	#first sort the sublists
	a = [sorted(i) for i in a]
	b = []
	for i in a:
		times = 0
		for j in a:
			if i==j: times +=1
		if times == 1: b.append(i)		
	return b
        