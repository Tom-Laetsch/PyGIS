from __future__ import absolute_import
from os.path import join, dirname
from .GIShelpers import *
from .ShpFileHandler import *

__all__ = ['SHP_DIR', 'US_NATION', 'US_STATES']

SHP_DIR = dirname(__file__)
US_STATES = ShPy( join(SHP_DIR,'Shapefiles/us_states/us_states_5m.shp'), record_key = 4 )
US_NATION = ShPy( join(SHP_DIR,'Shapefiles/us_nation/us_nation_5m.shp') )
