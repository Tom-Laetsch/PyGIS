from __future__ import print_function, division
#import shapefiles; require library pyshp: pip install pyshp
import shapefile
from .GIShelpers import in_polygon

__all__ = ['ShPy']

class ShPy(object):
    def __init__(self, shpfile, record_key = None, verbose=False):
        self._shpfile = shpfile
        self.verbose = verbose
        self._sfreader = shapefile.Reader(shpfile)

        #create the dictionary of points
        points_dict = dict()
        keys = []
        key_cnt = 0
        lon_min = None
        lon_max = None
        lat_min = None
        lat_max = None
        for record, shape in zip(self._sfreader.iterRecords(), self._sfreader.iterShapes()):
            while record_key not in range( len(record) ):
                print("Current part label types:")
                for r in range( len(record) ):
                    print("\t%d) %s" % (r,record[r]))
                record_key = int(input("Selection? "))
            self.record_key = record_key
            keys.append(record[record_key])
            parts = shape.parts
            pR = 0
            tot_lons = []
            tot_lats = []
            if len(parts) > 1:
                for j in range(len(parts) - 1):
                    lons = []
                    lats = []
                    pL = parts[j]
                    pR = parts[j+1]
                    for lon,lat in shape.points[pL:pR]:
                        if any(val is None for val in [lon_min,lon_max,lat_min,lat_max]):
                            lon_min = lon
                            lon_max = lon
                            lat_min = lat
                            lat_max = lat
                        else:
                            if lon_min > lon:
                                lon_min = lon
                            if lon_max < lon:
                                lon_max = lon
                            if lat_min > lat:
                                lat_min = lat
                            if lat_max < lat:
                                lat_max = lat
                        lons.append(lon)
                        lats.append(lat)
                    tot_lons.append(lons)
                    tot_lats.append(lats)
            lons = []
            lats = []
            for lon,lat in shape.points[pR:]:
                lons.append(lon)
                lats.append(lat)
            tot_lons.append(lons)
            tot_lats.append(lats)
            points_dict[keys[key_cnt]] = zip(tot_lons,tot_lats)
            key_cnt += 1
        self._points_dict = points_dict
        self._lon_min = lon_min
        self._lon_max = lon_max
        self._lat_min = lat_min
        self._lat_max = lat_max

        lons = []
        lats = []
        keys = []
        for key in points_dict.keys():
            for lon,lat in points_dict[key]:
                keys.append(key)
                lons.append(lon)
                lats.append(lat)
        self._lons_lats_keys = (lons,lats,keys)

    @property
    def points_dict(self):
        return self._points_dict

    @property
    def sfreader(self):
        return self._sfreader

    @property
    def shpfile(self):
        return self._shpfile

    @property
    def lons_lats_keys(self):
        return self._lons_lats_keys

    @property
    def bounding_box( self ):
        """
        returns bounding box in two tuples: (x_min,y_min), (x_max,y_max)
        """
        return tuple([self._lon_min, self._lat_min]), tuple([self._lon_max, self._lat_max])

    def key_by_point(self,point):
        """
        point = (lon,lat)
        returns the (first found) key in points_dict where point lands inside
        If no key found, returns None
        """
        lons,lats,keys = self.lons_lats_keys
        for i, key in enumerate(keys):
            if in_polygon(point = point, poly = (lons[i],lats[i])):
                return key
        return None
