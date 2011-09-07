#!/usr/bin/python

# Map always maps to or from Clutch varnames
# Map subclass defines a pair with other and Clutch
# Map from converts data from other to Clutch
# Map to converts

ClutchVars = {
    'Bsp': 'Boatspeed',
    'Hdg': 'Heading',
    'Crs': 'Course',
    'COG': 'Course Over Ground',
    'TWA': 'True Wind Angle',
    'TWS': 'True Wind Speed',
    'AWA': 'Apparent Wind Angle',
    'AWS': 'Apparent Wind Speed',
    }

class Map(object):
    def __init__(self):
        self.map = {} # Set to key=Other var name, value=Clutch var name
        self.revmap = {}

    def frm(self,data):
        return dict((self.map[k] if k in self.map else k,v) for k,v in data.iteritems())

    def to(self,data):
        if self.revmap == {}:
            self.revmap = dict(zip(self.map.values(),self.map.keys()))
        return dict((self.revmap[k],v) for k,v in data.iteritems() if k in self.revmap)
		
class ExpeditionLogMap(Map):
    def __init__(self):
        Map.__init__(self)
        self.map = {
            'Time':     'Time',
            'DATE':     'xlsDate',
            'Bsp':      'Bsp',
            'Awa':      'AWA',
            'Aws':      'AWS',
            'Twa':      'TWA',
            'Tws':      'TWS',
            'Twd':      'TWD',
            'Gwd':      'GWD',
            'Gws':      'GWS',
            'MkLat':    'MkLat',
            'MkLon':    'MkLon',
            'Leeway':   'Lee',
            'iSet':     'instSet',
            'iDrift':   'instDrift',
            'Hdg':      'Hdg',
            'AirTmp':   'TempAir',
            'SeaTmp':   'TempAir',
            'Baro':     'Baro',
            'Depth':    'Dpth',
            'Heel':     'Heel',
            'Trim':     'Trim',
            'Rudder':   'Rud',
            'Tab':      'TabAngle',
            'Forestay': 'ForeLoad',
            'Downhaul': 'Downhaul',
            'MastAng':  'MastAng',
            'FrstyLen': 'ForeLen',
            'MastButt': 'ButtPos',
            'StbJmpr':  'StbJmpLoad',
            'PrtJmpr':  'StbJmpLoad',
            'Rake':     'Rake',
            'Volts':    'Vlts',
            'Vmg':      'VMG',
            'WindWeight':'WindWeight',
            'DtOnStb':  'LayDistStb',
            'TmOnStb':  'LayTimeStb',
            'BrgOnPrt': 'LayBrgPrt',
            'DtOnPrt':  'LayDistPrt',
            'TmOnPrt':  'LayTimePrt',
            'BrgOnStb': 'LayBrgStb',
            'GpsQual':  'GPSQual',
            'HDOP':     'HDOP',
            'PDOP':     'VDOP',
            'GpsNum':   'GPSNum',
            'GpsAge':   'GPDSAge',
            'GpsGeoHt': 'GPSGeoHgt',
            'GpdAntHt': 'GPSAntHgt',
            'GpsPosFx': 'GPSPosFix',
            'Lat':      'Lat',
            'Lon':      'Lon',
            'Cog':      'COG',
            'Sog':      'SOG',
            'DiffStn':  'DiffStn', # Huh?
            'TargTwa':  'TargTWA',
            'TargBsp':  'TargBsp',
            'TargVmg':  'TargVMG',
            'TargHeel': 'TargHeel',
            'PolBsp':   'PolBsp',
            'PolBsp%':  'PolBsp%',
            'PolLeeway':'PolLee',
            'TargLeeway':'TargLee',
            'PolHeel':  'PolHeel',
            'iCalBsp':  'instCalBsp',
            'iCalBspOff':'instCalBspOff',
            'iCalAwa':  'instCalAWA',
            'iCalAws':  'instCalAWS',
            'iCalUpwash':'instCalUp',
            'iCalLeeway':'instCalLee',
            'iCalTwa':  'instCalTWA',
            'iCalTws':  'instCalTWS',
            'iCalUpSlp':'instCalUpSl',
            'StPrtLat': 'StartPrtLat',
            'StPrtLon': 'StartPrtLon',
            'StStbLat': 'StartStbLat',
            'StStbLon': 'StartStbLon',
            'Error':    'ExpError',
            'TmToGun':  'StartTimeGun',
            'Course':   'Course',
            'OppTrack': 'OppTack',
            'TmToLn':   'StartTimeLine',
            'Tm2Prt':   'StartTimePrt',
            'Tm2Stb':   'StartTimeStb',
            'LnSqWind': 'StartLnSqTWD',
            'DistToLn': 'StartDistLine',
            'TmToBurn': 'StartTimeBurn',
            'BiasA':    'StartLnBiasA',
            'BiasL':    'StartLnBiasL',
            'TargBsp%': 'TargBsp%',
            'XTE':      'XTE',
            }
            
class ExpeditionNumMap(Map):
    def __init__(self):
        Map.__init__(self)
        self.map = {
            '1':    'Bsp',
            '2':    'AWA',
            '3':    'AWS',
            '4':    'TWA',
            '5':    'TWS',
            '6':    'TWD',
            '94':   'GWD',
            '95':   'GWS',
            '10':   'Lee',
            '12':   'instSet',
            '11':   'instDrift',
            '13':   'Hdg',
            '17':   'Dpth',
            '18':   'Heel',
            '31':   'VMG',
            '33':   'LayDistStb',
            '34':   'LayTimeStb',
            '35':   'LayBrgPrt',
            '36':   'LayDistPrt',
            '37':   'LayTimePrt',
            '38':   'LayBrgStb',
            '48':   'Lat',
            '49':   'Lon',
            '50':   'COG',
            '51':   'SOG',
            '237':  'TargTWA',
            '238':  'TargBsp',
            '56':   'TargHeel',
            '57':   'PolBsp',
            '58':   'PolBsp%',
            '59':   'PolHeel',
            '204':  'StartTimeGun', # 15 Mins equals about ~0.01?
            '79':   'OppTack',
            '205':  'StartTimeLine',
            '81':   'StartTimePrt',
            '82':   'StartTimeStb',
            '83':   'StartLnSqTWD',
            '84':   'StartDistLine',
            '206':  'StartTimeBurn',
            '128':  'StartLnBiasA',
            '129':  'StartLnBiasL',
            '132':  'TargBsp%',
            '91':   'XTE',
            }
			