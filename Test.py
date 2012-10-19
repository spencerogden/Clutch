#/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('Functions')

import geo
import Core
import Starting
import Polars
import Tables

import unittest

m_in_nm = 1852

error = 0.085

class TestGeolocation(unittest.TestCase):
    
    # Test different know distances
    # edge cases:
    # Near prime meridian
    # near 180 degree meridian
    # near poles
    # across equator
    def test_distance_equator_ew(self):
        # 1 degree of longitude at the equator, to the east of prime
        (d, fwd, rev) = geo.vincenty_inverse( 0, 0, 0, 1 )
        self.assertAlmostEqual( d, 111319.491, places=3 )
        
    def test_distance_equator_ns(self):
        (d1, fwd, rev) = geo.vincenty_inverse(  0  , 0,  1  , 0 )
        (d2, fwd, rev) = geo.vincenty_inverse( -0.5, 0,  0.5, 0 )
        (d3, fwd, rev) = geo.vincenty_inverse(  0.5, 0, -0.5, 0 )
        self.assertAlmostEqual( d1, 110574.389, places=3 )
        self.assertAlmostEqual( d1, d2 + error, places=3 )
        self.assertAlmostEqual( d1, d3 + error, places=3 )
        
    def test_distance_meridian_cross_ew(self):
        (d, fwd, rev) = geo.vincenty_inverse( 0, -0.5, 0, 0.5)
        self.assertAlmostEqual( d, 111319.491, places=3 )
        (drev, fwd, rev) = geo.vincenty_inverse( 0, 0.5, 0, -0.5)
        self.assertAlmostEqual( d, drev, places=3 )
        
    def test_distance_date_line_ew(self):
        # All of these distances should be approximatly equal
        (d1, fwd, rev) = geo.vincenty_inverse( 0, 180, 0, 179)
        self.assertAlmostEqual( d1, 111319.491, places=3 )
        (d2, fwd, rev) = geo.vincenty_inverse( 0, 180, 0, -179)
        (d3, fwd, rev) = geo.vincenty_inverse( 0, 179.5, 0, -179.5)
        self.assertAlmostEqual( d1, d2, places=3 )
        self.assertAlmostEqual( d1, d3, places=3 )
        
    def test_distance_date_line_ns(self):
        (d1, fwd, rev) = geo.vincenty_inverse( 0, 180, 1, 180)
        (d2, fwd, rev) = geo.vincenty_inverse( 0, -180, 1, -180)
        (d3, fwd, rev) = geo.vincenty_inverse( -0.5, 180, 0.5, 180)
        
        self.assertAlmostEqual( d1, 110574.389, places=3 )
        self.assertAlmostEqual( d1, d2, places=3 )
        
        # Known error in this scenario? 8cm
        self.assertAlmostEqual( d1, d3 + error, places=3 )
        
    def test_distance_poles(self):
        (d1, fwd, rev) = geo.vincenty_inverse( 90  , 0 , 89  , 180 ) 
        (d2, fwd, rev) = geo.vincenty_inverse( 90  , 0 , 89  , 76  )
        (d3, fwd, rev) = geo.vincenty_inverse( 89.5, 90, 89.5, -90 )
        (d4, fwd, rev) = geo.vincenty_inverse( 89.5, 0 , 89.5, 180 )
        (d5, fwd, rev) = geo.vincenty_inverse( 89.5, 0 , 89.5, -180)
        (d6, fwd, rev) = geo.vincenty_inverse( 90  , 50, 89  , 76  )
        
        self.assertAlmostEqual( d1, 111693.865, places=3 )
        self.assertAlmostEqual( d1, d2, places=3 )
        # Again, known errors of about 8cm when crossing lat
        
        self.assertAlmostEqual( d1, d3 - error - 0.001, places=3 )
        self.assertAlmostEqual( d1, d4 - error - 0.001, places=3 )
        self.assertAlmostEqual( d1, d5 - error - 0.001, places=3 )
        self.assertAlmostEqual( d1, d6, places=3 )
        
    def test_direct_inverse(self):
        (d1, fwd, rev1) = geo.vincenty_inverse(  0  , 0,  1  , 0 )
        (lat, lon, rev2) = geo.vincenty_direct( 0,0,d1,fwd)
        self.assertAlmostEqual( lat,1, places=3 )
        self.assertAlmostEqual( lon,0, places=3 )
        self.assertAlmostEqual( rev1,rev2, places=3 )
        
    def test_bearing_ew(self):
        (d1, fwd, rev) = geo.vincenty_inverse( 0  , 0 , 0  , 1 )
        self.assertAlmostEqual( fwd, 90 )
        self.assertAlmostEqual( rev, 90 )
        
    def test_bearing_ns(self):
        (d1, fwd, rev) = geo.vincenty_inverse( 0  , 0 , 1  , 0 )
        self.assertAlmostEqual( fwd, 0 )
        
    def test_bearing_diag(self):
        error = 0.1924
        (d1, fwd, rev) = geo.vincenty_inverse( -0.001  , -0.001 , 0.001  , 0.001 )
        self.assertAlmostEqual( fwd, 45 + error , places = 3)
        
    def test_bearing_pole(self):
        (d1, fwd1, rev) = geo.vincenty_inverse( 89  , 90  , 90  , 0 )
        (d1, fwd2, rev) = geo.vincenty_inverse( 89  , 270  , 90  , 0 )
        self.assertAlmostEqual( round(fwd1,3) % 360, 0 )
        self.assertAlmostEqual( round(fwd2,3) % 360, 0 )
        
    def test_pos_string_init(self):
        # Different string reps of the same position
        pos1 = geo.Position("41* 5' 7.2 N", "73* 24' 38.6 W")
        # Degree symbol not working, need to better figure out unicode stuff
        #pos2 = geo.Position("41° 5' 7.2 N", "73° 24' 38.6 W")
        pos3 = geo.Position("N 41* 5' 7.2", "W 73* 24' 38.6")
        pos4 = geo.Position("41* 5' 7.2", "-73* 24' 38.6")
        # Not matching digits after decimal point, why?
        pos5 = geo.Position("+0410507.2", "-0732438.6")
        pos6 = geo.Position("41* 5' 7.2 +", "73* 24' 38.6 -")
        pos7 = geo.Position("N41* 5' 7\"", "W 73* 24' 38\"")
        
        
        self.assertAlmostEqual( pos1.lat, 41.085333333  )
        self.assertAlmostEqual( pos1.lon, -73.41072222222 )
        #self.assertAlmostEqual( pos1.lat, pos2.lat )
        #self.assertAlmostEqual( pos1.lon, pos2.lon )        
        self.assertAlmostEqual( pos1.lat, pos3.lat )
        self.assertAlmostEqual( pos1.lon, pos3.lon )
        self.assertAlmostEqual( pos1.lat, pos4.lat )
        self.assertAlmostEqual( pos1.lon, pos4.lon )
        self.assertAlmostEqual( pos1.lat, pos5.lat )
        self.assertAlmostEqual( pos1.lon, pos5.lon )
        self.assertAlmostEqual( pos1.lat, pos6.lat )
        self.assertAlmostEqual( pos1.lon, pos6.lon )
        self.assertAlmostEqual( 41.085277777777, pos7.lat )
        self.assertAlmostEqual( -73.410555555555, pos7.lon )
        
    def test_mag_var(self):
        pos = geo.Position("41* 5' 7.2 N", "73* 24' 38.6 W")
        # Valid as of 2012-04-29
        self.assertAlmostEqual( pos.dec, -13.50, places=1 )
        
    def test_pos_brng(self):
        pos1 = geo.Position(0,0)
        pos2 = geo.Position("N1*",0)
        b = pos1.brng_to(pos2)
        self.assertAlmostEqual( b, 0 )
        
    def test_pos_range(self):
        pos1 = geo.Position(0,0)
        pos2 = geo.Position("N1*",0)
        r = pos1.range_to(pos2)
        self.assertAlmostEqual( r, 110574.389 / m_in_nm, places=5 )
        
class TestMarkObjects(unittest.TestCase):
    def test_mark(self):
        pos = geo.Position(0,0)
        mark = Core.Mark('Test mark',pos)
        self.assertEqual( mark.position.lat , 0 )
        self.assertEqual( mark.position.lon , 0 )
        
    def test_mark_dist(self):
        pos1 = geo.Position(0, -0.5)
        pos2 = geo.Position(0,  0.5)
        m1 = Core.Mark("1",pos1)
        m2 = Core.Mark("2",pos2)
        d = m1.range_to(m2)
        self.assertAlmostEqual( d, 111319.491 / m_in_nm, places=3 )
        
    def test_mark_brng(self):
        pos1 = geo.Position(0, -0.5)
        pos2 = geo.Position(0,  0.5)
        m1 = Core.Mark("1",pos1)
        m2 = Core.Mark("2",pos2)
        b = m1.brng_to(m2)
        self.assertAlmostEqual( b, 90, places=3 )
        b = m2.brng_to(m1)
        self.assertAlmostEqual( b, 270, places=3 )
        
class TestPolars(unittest.TestCase):
    def setUp(self):
        self.tl = Tables.TableLibrary()
        self.tl.addTables("Polars")
        
    def test_load(self):
        self.assertIn( 'polars', self.tl.tables )
    
    def test_exact_lookup(self):
        self.assertAlmostEqual( self.tl.tables['polars'].lookup( 12, 52 ), 8.41 )
        
    def test_interp_lookup(self):
        self.assertAlmostEqual( self.tl.tables['polars'].lookup( 13, 52 ),(8.41+8.62)/2.0)
        
    def test_target_exact(self):
        t = self.tl.tables['polars'].lookup_targs( 12 )
        self.assertAlmostEqual( t.bsp_up, 7.290489130434783 ) # Better checking with known targets
        t = self.tl.tables['polars'].lookup_targs( 14 )
        self.assertAlmostEqual( t.bsp_up, 7.436374269005848 )
        
    def test_target_between(self):
        t = self.tl.tables['polars'].lookup_targs( 13 )
        self.assertTrue( 7.290489130434783 < t.bsp_up < 7.436374269005848 )
        self.assertAlmostEqual( t.bsp_up, 7.364836956521739 )

    def test_target_interp(self):
        t = self.tl.tables['polars'].lookup_targs( 12.5 )
        self.assertAlmostEqual( t.bsp_up, (7.290489130434783+7.364836956521739)/2 )


# Test polar distance and time Starting.distToLine or new function which calculates distance to a given point?

# test favored end of line calc

        
if __name__ == '__main__':
    unittest.main()
    