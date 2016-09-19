from __future__ import print_function, division
#import shapefiles; require library pyshp: pip install pyshp
import shapefile

class ShpWrap(object):
    def __init__(self, shpfile, names=None, verbose=False):
        self.shpfile = shpfile
        self.names = names
        self.verbose = verbose
        self.sf = shapefile.Reader(shpfile)
        self.shapes = (self.sf).shapes()
        self.points_dict = self.make_points_dict()

    def make_points_dict(self):
        names = self.names
        num_shapes = len(self.shapes)
        if type(names) == str:
            area_prefix = names
            names = None
        else:
            area_prefix = "AREA"
        if names == None or type(names) != list or len(names) != num_shapes:
            #use default
            names = [area_prefix + "_" + str(i) for i in range(num_shapes)]
        if self.names != names: self.names = names
        points_dict = dict()
        for i in range(num_shapes):
            parts = self.shapes[i].parts
            pR = 0
            tot_xs = []
            tot_ys = []
            if len(parts) > 1:
                for j in range(len(parts) - 1):
                    xs = []
                    ys = []
                    pL = parts[j]
                    pR = parts[j+1]
                    for x,y in self.shapes[i].points[pL:pR]:
                        xs.append(x)
                        ys.append(y)
                    tot_xs.append(xs)
                    tot_ys.append(ys)
            xs = []
            ys = []
            for x,y in self.shapes[i].points[pR:]:
                xs.append(x)
                ys.append(y)
            tot_xs.append(xs)
            tot_ys.append(ys)
            points_dict[names[i]] = zip(tot_xs,tot_ys)
        return points_dict

    def make_points_list(self):
        xs = []
        ys = []
        names = []
        for key in self.points_dict.keys():
            for x,y in self.points_dict[key]:
                names.append(key)
                xs.append(x)
                ys.append(y)
        return xs,ys,names
