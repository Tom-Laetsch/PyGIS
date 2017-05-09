from __future__ import absolute_import
from os.path import join, dirname
from .GIShelpers import *
from .ShpFileHandler import *

__all__ = ['SHP_DIR', 'US_NATION', 'US_STATES', 'NYC_BOROUGHS', 'CHICAGO_NBHDS']

SHP_DIR = dirname(__file__)
US_STATES = ShPy( join(SHP_DIR,'Shapefiles/us_states/us_states_5m.shp'), record_key = 4 )
US_NATION = ShPy( join(SHP_DIR,'Shapefiles/us_nation/us_nation_5m.shp'), record_key = 1 )
# State specific shapefiles
NYC_BOROUGHS = ShPy( join(SHP_DIR,'Shapefiles/nyc_boroughs/nyc_boroughs.shp'), record_key = 0 )
CHICAGO_NBHDS = ShPy( join(SHP_DIR,'Shapefiles/chicago_nbhds/chicago_nbhds.shp'), record_key = 1 )
