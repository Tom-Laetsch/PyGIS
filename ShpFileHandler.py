from __future__ import print_function, division
#import shapefiles; require library pyshp: pip install pyshp
import shapefile

class ShpWrap(object):
    def __init__(self, shpfile, names=None, verbose=False):
        self._shpfile = shpfile
        self.verbose = verbose
        self._sfreader = shapefile.Reader(shpfile)
        self._points_dict = self._make_points_dict()

    def _make_points_dict(self):
        points_dict = dict()
        names = []
        name_cnt = 0
        for record, shape in zip(self._sfreader.iterRecords(), self._sfreader.iterShapes()):
            names.append(record[4])
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
            points_dict[names[name_cnt]] = zip(tot_xs,tot_ys)
            name_cnt += 1
        return points_dict

    @property
    def points_dict(self):
        return self._points_dict

    def make_points_list(self):
        xs = []
        ys = []
        names = []
        for key in self._points_dict.keys():
            for x,y in self._points_dict[key]:
                names.append(key)
                xs.append(x)
                ys.append(y)
        return xs,ys,names
