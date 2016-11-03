from __future__ import print_function, division
#import shapefiles; require library pyshp: pip install pyshp
import shapefile
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from .GIShelpers import in_polygon

__all__ = ['ShPy']

class ShPy(object):
    def __init__(self, shpfile, record_key = None, verbose=False ):
        self._shpfile = shpfile
        self.verbose = verbose
        self._sfreader = shapefile.Reader(shpfile)
        #create the dictionary of points
        parts_dict = dict()
        keys = []
        lons = []
        lats = []
        lon_min = None
        lon_max = None
        lat_min = None
        lat_max = None
        for shape_n, (record, shape) in enumerate(zip(self._sfreader.iterRecords(),
                                                      self._sfreader.iterShapes())):
            rec_len = len(record)
            while record_key not in range( rec_len + 1 ):
                print("Current part label types:")
                for r in range( rec_len ):
                    print("\t%d) %s" % (r,record[r]))
                print("\t%d) %s" % (rec_len, "Use Default Labels"))
                record_key = int(input("Selection? "))
            self.record_key = record_key
            if self.record_key in range( rec_len ):
                key = record[self.record_key]
            else: #use default
                key = "Record_%d" % shape_n
            parts = shape.parts
            part_lons = []
            part_lats = []
            if len(parts) > 1:
                #extract parts for all but last of parts
                for j in range(len(parts) - 1):
                    patch_lons, patch_lats = zip(*shape.points[parts[j]:parts[j+1]])
                    #part specific lon/lat patch list
                    part_lons.append(list(patch_lons))
                    part_lats.append(list(patch_lats))
                    #overall lon/lat patch list
                    lons.append( list(patch_lons) )
                    lats.append( list(patch_lats) )
            #extract last part
            patch_lons, patch_lats = zip(*shape.points[parts[-1]:])
            #part specific lon/lat patch list
            part_lons.append(list(patch_lons))
            part_lats.append(list(patch_lats))
            #overall lon/lat patch list with key association
            lons.append( list(patch_lons) )
            lats.append( list(patch_lats) )
            #associate key per part
            keys += [key]*len(part_lons)
            #bounding values for this part
            part_lon_min = min([min(xs) for xs in part_lons])
            part_lon_max = max([max(ys) for ys in part_lons])
            part_lat_min = min([min(xs) for xs in part_lats])
            part_lat_max = max([max(ys) for ys in part_lats])
            #parts dictionary
            parts_dict[key] = dict( lons = part_lons,
                                    lats = part_lats,
                                    bottom_left = (part_lon_min, part_lat_min),
                                    top_right = (part_lon_max, part_lat_max) )

            if lon_min is None:
                lon_min = part_lon_min
            elif lon_min > part_lon_min:
                lon_min = part_lon_min
            if lon_max is None:
                lon_max = part_lon_max
            elif lon_max < part_lon_max:
                lon_max = part_lon_max
            if lat_min is None:
                lat_min = part_lat_min
            elif lat_min > part_lat_min:
                lat_min = part_lat_min
            if lat_max is None:
                lat_max = part_lat_max
            elif lat_max < part_lat_max:
                lat_max = part_lat_max

        self._parts_dict = parts_dict
        self._bottom_left = (lon_min, lat_min)
        self._top_right = (lon_max, lat_max)

        #store the overall lons/lats/keys
        self._lons_lats_keys = (lons,lats,keys)

    @property
    def parts_dict(self):
        return self._parts_dict

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
        return self._bottom_left, self._top_right

    def bounding_box_by_key( self, key ):
        bottom_left = self._parts_dict.get( key, None )
        top_right = self._parts_dict.get( key, None )
        return bottom_left, top_right

    def key_by_point( self,point ):
        """
        point = (lon,lat)
        returns the (first found) key in parts_dict where point lands inside
        If no key found, returns None
        """
        lons,lats,keys = self.lons_lats_keys
        for i, key in enumerate(keys):
            if in_polygon(point = point, poly = (lons[i],lats[i])):
                return key
        return None

    def show( self, figsize = 5, xlim = None, ylim = None, key = None ):
        xs, ys, names = self.lons_lats_keys
        if key is None:
            bottom_left, top_right = self.bounding_box
        else:
            bottom_left, top_right
        all_codes = []
        all_verts = []
        for i in range(len(xs)):
            codes = [Path.MOVETO]
            for j in range( 1, len(xs[i])-1 ):
                codes.append(Path.LINETO)
            codes.append(Path.CLOSEPOLY)
            all_codes.append(codes)
            all_verts.append(list(zip(xs[i],ys[i])))
        if xlim is None:
            x0,x1 = bottom_left[0], top_right[0]
            xbuff = 0.005 * (x1 - x0)
            x0 = x0 - xbuff
            x1 = x1 + xbuff
        else:
            x0,x1 = xlim
        if ylim is None:
            y0,y1 = bottom_left[1], top_right[1]
            ybuff = 0.005 * (y1 - y0)
            y0 = y0 - ybuff
            y1 = y1 + ybuff
        else:
            y0,y1 = ylim
        dx = x1-x0
        dy = y1-y0
        if isinstance(figsize,int):
            xy_ratio = dx/dy
            ylen = figsize
            xlen = int(xy_ratio * ylen)
        else:
            xlen, ylen = figsize
        fig = plt.figure(figsize = (xlen,ylen))
        ax = fig.add_subplot(111)
        for i in range(len(all_verts)):
            path = Path(all_verts[i], all_codes[i])
            patch = patches.PathPatch(path, facecolor='none', lw=1)
            ax.add_patch(patch)
        ax.set_xlim(x0,x1)
        ax.set_ylim(y0,y1)
        plt.show()
