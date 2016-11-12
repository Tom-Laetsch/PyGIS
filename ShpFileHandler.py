from __future__ import print_function, division
#import shapefiles; require library pyshp: pip install pyshp
from os.path import basename
import shapefile
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from .GIShelpers import in_polygon

__all__ = ['ShPy']

def show_ShPy( ShPy_Obj,
               figsize = 5,
               xlim = None,
               ylim = None,
               facecolor = 'blue',
               alpha = .33,
               key = None ):
        if key in ShPy_Obj.parts_dict.keys():
            xs = ShPy_Obj.parts_dict[key]["lons"]
            ys = ShPy_Obj.parts_dict[key]["lats"]
            names = [key]*len(xs)
            bottom_left, top_right = ShPy_Obj.bounding_box_by_key( key )
            title = key
        else: #whole enchalada
            xs, ys, names = ShPy_Obj.lons_lats_keys
            bottom_left, top_right = ShPy_Obj.bounding_box
            title = ShPy_Obj.title
        all_codes = []
        all_verts = []
        for lons, lats in zip(xs,ys):
            all_verts.append( list(zip(lons,lats)) )
            all_codes.append( [Path.MOVETO] + [Path.LINETO]*(len(lons) - 2) + [Path.CLOSEPOLY] )

        try:
            x0,x1 = xlim
        except:
            x0,x1 = bottom_left[0], top_right[0]
            xbuff = 0.01 * (x1 - x0)
            x0 = x0 - xbuff
            x1 = x1 + xbuff
        try:
            y0,y1 = ylim
        except:
            y0,y1 = bottom_left[1], top_right[1]
            ybuff = 0.01 * (y1 - y0)
            y0 = y0 - ybuff
            y1 = y1 + ybuff

        try:
            xlen, ylen = figsize
        except:
            dx = x1-x0
            dy = y1-y0
            xy_ratio = dx/dy
            if not isinstance(figsize,int): figsize = 5
            xlen = int(xy_ratio * figsize)
            ylen = figsize

        fig = plt.figure( figsize = (xlen,ylen) )
        ax = fig.add_subplot(111)
        for i in range(len(all_verts)):
            path = Path(all_verts[i], all_codes[i])
            patch = patches.PathPatch(path, facecolor=facecolor, alpha =alpha, lw=1)
            ax.add_patch(patch)
        ax.set_xlim(x0,x1)
        ax.set_ylim(y0,y1)
        plt.title( title )
        plt.show()

class ShPy(object):
    def __init__( self,
                  shpfile,
                  record_key = None,
                  title = None,
                  verbose=False ):
        self._shpfile = shpfile
        self.verbose = verbose
        self._sfreader = shapefile.Reader(shpfile)
        if title is None:
            self._title = basename(self.shpfile)
        else:
            self._title = title
        #create the dictionary of points
        parts_dict = dict()
        keys = []
        lons = []
        lats = []
        for shape_n, rs in enumerate(self._sfreader.iterShapeRecords()):
            record = rs.record
            shape = rs.shape
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
            part_lon_min, part_lat_min, part_lon_max, part_lat_max = shape.bbox
            #parts dictionary
            parts_dict[key] = dict( lons = part_lons,
                                    lats = part_lats,
                                    bottom_left = (part_lon_min, part_lat_min),
                                    top_right = (part_lon_max, part_lat_max) )

        self._parts_dict = parts_dict
        lon_min, lat_min, lon_max, lat_max = self._sfreader.bbox
        self._bottom_left = (lon_min, lat_min)
        self._top_right = (lon_max, lat_max)

        #store the overall lons/lats/keys
        self._lons_lats_keys = (lons,lats,keys)

    @property
    def title( self ):
        return self._title

    @title.setter
    def title( self, value ):
        self._title = value


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
        if key in self._parts_dict.keys():
            bottom_left = self._parts_dict[key]["bottom_left"]
            top_right = self._parts_dict[key]["top_right"]
        else:
            bottom_left, top_right = self.bounding_box
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

    def point_in_key( self,point,key ):
        """
        point = (lon,lat)
        returns the (first found) key in parts_dict where point lands inside
        If no key found, returns None
        """
        key_dict = self.parts_dict.get(key,None)
        if not key_dict is None:
            for lons, lats in zip( key_dict['lons'],key_dict['lats'] ):
                if in_polygon(point = point, poly = (lons,lats)):
                    return True
        return False

    def show( self,
              figsize = 5,
              xlim = None,
              ylim = None,
              facecolor = "blue",
              alpha = 0.33,
              key = None ):
        show_ShPy( self, figsize = figsize, xlim = xlim, ylim = ylim,
                   facecolor = facecolor, alpha = alpha, key = key )
