from __future__ import print_function, division

__all__ = ['in_polygon']

def in_polygon(point, #(x,y) tuple to test if in polygon
               poly, #([xs], [ys]) tuple of xs and ys tracing polygon
               verbose = False):
    x_min = min(poly[0])
    x_max = max(poly[0])
    y_min = min(poly[1])
    y_max = max(poly[1])

    if point[0] < x_min or point[0] > x_max or point[1] < y_min or point[1] > y_max :
       return False

    #count number of crossings
    cnt = 0
    for i in range(len(poly[0])):
        if poly[0][i-1] > point[0] or poly[0][i] > point[0]:
            continue
        if max(poly[1][i-1], poly[1][i]) < point[1] or min(poly[1][i-1],poly[1][i]) > point[1] :
            continue
        #else, the ray to the left intersects the point
        cnt += 1
    if verbose:
        print("Intersection Count: %d" % cnt)
    if cnt % 2 == 0:
        #if it intersects an even number of times, it is outside
        return False
    else:
        #if it intersects an odd number of times, it is inside
        return True
