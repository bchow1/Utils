#!/bin/env python
import os
import sys
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3
from utilDb import *
import setSCIparams as SCI
from mpl_toolkits.basemap import Basemap, cm
# requires netcdf4-python (netcdf4-python.googlecode.com)
#from netCDF4 import Dataset as NetCDFFile

def mainProg():
  # setup Lambert Conformal basemap.
  #m = Basemap(width=12000000,height=9000000,projection='lcc',
  #          resolution='c',lat_1=45.,lat_2=55,lat_0=50,lon_0=-107.)
  m = Basemap(llcrnrlon=-95, llcrnrlat=30, urcrnrlon=-75,
  urcrnrlat=45, projection='lcc', lat_1=33, lat_2=45,
  lon_0=-95, resolution='h', area_thresh=5)

  # draw a boundary around the map, fill the background.
  # this background will end up being the ocean color, since
  # the continents will be drawn on top.
  
  m.drawstates(linewidth=0.5, color='k', antialiased=1, ax=None, zorder=None)
  m.drawmapboundary(fill_color='aqua')
  # fill continents, set lake color same as ocean color.
  m.fillcontinents(color='coral',lake_color='aqua')
  # draw parallels and meridians.
  # label parallels on right and top
  # meridians on bottom and left
  parallels = np.arange(30.,55,5.)
  #labels = [left,right,top,bottom]
  m.drawparallels(parallels,color='k', linewidth=0.5, zorder=None, dashes=[1, 3],labels=[False,True,True,False])
  meridians = np.arange(10.,351.,5.)
  m.drawmeridians(meridians,color='k', linewidth=0.5, zorder=None, dashes=[1, 3],labels=[True,False,False,True])
  # plot blue dot on Boulder, colorado and label it as such.
  lon, lat = -87.65230, 36.39000     # Location of Cumberland
  # convert to map projection coords.
  # Note that lon,lat can be scalars, lists or numpy arrays.
  xpt,ypt = m(lon,lat)
  # convert back to lat/lon
  lonpt, latpt = m(xpt,ypt,inverse=True)
  m.plot(xpt,ypt,'bo')  # plot a blue dot there
  # put some text next to the dot, offset a little bit
  # (the offset is in map projection coordinates)
  plt.text(xpt+10000,ypt+10000,'Cumberland (%5.1fW,%3.1fN)' % (lonpt,latpt))
  plt.show()


def mainProgBak():
  
  # set up orthographic map projection with
  # perspective of satellite looking down at 50N, 100W.
  # use low resolution coastlines.
  lats = [ -30, 30, 30, -30 ]
  lons = [ -50, -50, 50, 50 ]

  map  = Basemap(projection='stere',lon_0=lon_0,lat_0=90.,lat_ts=lat_0,\
            llcrnrlat=latcorners[0],urcrnrlat=latcorners[2],\
            llcrnrlon=loncorners[0],urcrnrlon=loncorners[2],\
            rsphere=6371200.,resolution='l',area_thresh=10000)
  # draw coastlines, country boundaries, fill continents.
  map.drawcoastlines(linewidth=0.25)
  map.drawcountries(linewidth=0.25)
  map.fillcontinents(color='coral',lake_color='aqua')
  # draw the edge of the map projection region (the projection limb)
  map.drawmapboundary(fill_color='aqua')
  # draw lat/lon grid lines every 30 degrees.
  map.drawmeridians(np.arange(0,360,30))
  map.drawparallels(np.arange(-90,90,30))
  # make up some data on a regular lat/lon grid.
  nlats = 73; nlons = 145; delta = 2.*np.pi/(nlons-1)
  lats = (0.5*np.pi-delta*np.indices((nlats,nlons))[0,:,:])
  lons = (delta*np.indices((nlats,nlons))[1,:,:])
  wave = 0.75*(np.sin(2.*lats)**8*np.cos(4.*lons))
  mean = 0.5*np.cos(2.*lats)*((np.sin(2.*lats))**2 + 2.)
  # compute native map projection coordinates of lat/lon grid.
  x, y = map(lons*180./np.pi, lats*180./np.pi)
  # contour data over the map.
  cs = map.contour(x,y,wave+mean,15,linewidths=1.5)
  plt.title('contour lines over filled continent background')
  plt.show()

# Main program
if __name__ == '__main__':
  obsDb = 'Case001Obs.db'
  prjName = 'FwdCase001'
  fltDb = 'RevCase001_10_Filtered.sen.db'
  pltFname = 'Case001_10_TimeSeries.pdf'
  cFactor = 1.    # kg/m3 to kg/m3
  cCut = 1e-4
  mainProg()
