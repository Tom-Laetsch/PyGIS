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
            tot_xs = []
            tot_ys = []
            if len(parts) > 1:
                for j in range(len(parts) - 1):
                    xs = []
                    ys = []
                    pL = parts[j]
                    pR = parts[j+1]
                    for x,y in shape.points[pL:pR]:
                        xs.append(x)
                        ys.append(y)
                    tot_xs.append(xs)
                    tot_ys.append(ys)
            xs = []
            ys = []
            for x,y in shape.points[pR:]:
                xs.append(x)
                ys.append(y)
            tot_xs.append(xs)
            tot_ys.append(ys)
            points_dict[keys[key_cnt]] = zip(tot_xs,tot_ys)
            key_cnt += 1
        self._points_dict = points_dict

        xs = []
        ys = []
        keys = []
        for key in points_dict.keys():
            for x,y in points_dict[key]:
                keys.append(key)
                xs.append(x)
                ys.append(y)
        self._xs_ys_keys = (xs,ys,keys)

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
    def xs_ys_keys(self):
        return self._xs_ys_keys

    def key_by_point(self,point):
        # point = (x,y)
        # returns the (first found) key in points_dict where point lands inside
        # If no key found, returns None
        xs,ys,keys = self.xs_ys_keys
        for i, key in enumerate(keys):
            if in_polygon(point = point, poly = (xs[i],ys[i])):
                return key
        return None
