# -*- coding: utf-8 -*-
"""
Uses of GLScatterPlotItem with rapidly-updating plots.
"""
import os
import sys
import OpenGL
OpenGL.USE_ACCELERATE = False

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np

# local 
import readPuf
global hr, maxC

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 3
w.show()

g = gl.GLGridItem()
w.addItem(g)

os.chdir('D:\\Aermod\\v12345\\runs\\martin\\SCICHEM')
env = os.environ.copy()
if sys.platform == 'win32':
  compiler = "intel"
  version = "Debug"
  SCIPUFF_BASEDIR="D:\\SCIPUFF\\Repository\\"
  binDir = os.path.join(SCIPUFF_BASEDIR,"workspace","EPRI","bin",compiler,"Win32",version)
  iniFile = "D:\\SCIPUFF\\Repository\\workspace\\EPRI\\scipuff.ini"
  env["PATH"] = "%s" % (binDir)
  readpuf  = ["%s\\scipp.exe"%binDir,"-I:%s"%iniFile,"-R:RP"]
  
prjName = 'MCR_AER_TER'

def setHrDat(hr,maxC=None):

  vNames,hrDat = readPuf.getHrDat(readpuf,env,prjName,hr,tail='\n')
  
  nPuf,nVar = np.shape(hrDat)
  print 'Npuf = %d for hr %d'%(nPuf,hr)
  
  pos = np.empty((nPuf, 3))
  size = np.empty((nPuf))
  color = np.empty((nPuf, 4))
  
  iX  = vNames['X']
  iY  = vNames['Y']
  iZ  = vNames['Z']
  iC  = vNames['C']
  iSx = vNames['SXX']
  iSy = vNames['SYY']
  iSz = vNames['SZZ']
  
  maxX = hrDat[:,iX].max()
  maxY = hrDat[:,iY].max()
  maxZ = hrDat[:,iZ].max()
  if maxC is None:
    maxC = hrDat[:,iC].max()
  
  if maxX > 1e-10:
    hrDat[:,iX] = hrDat[:,iX]/maxX
  if maxY > 1e-10:
    hrDat[:,iY] = hrDat[:,iY]/maxY
  if maxZ > 1e-10:
    hrDat[:,iZ] = hrDat[:,iZ]/maxZ
  #if maxC > 1e-10:
  #  hrDat[:,iC] = 1. + 0.1*max(-10.,np.log10(hrDat[:,iC]/maxC))
  
  for iPuf in range(nPuf):
    pos[iPuf]   = (hrDat[iPuf,iX],hrDat[iPuf,iY],hrDat[iPuf,iZ])
    size[iPuf]  = 0.05 # 1. + 0.1*max(-10.,np.log10(hrDat[iPuf,iC]/maxC))
    #color[iPuf] = (0.0, 1.0, 0.0, 0.5) # Green
    cScale = 1. + 0.33*max(-3.,np.log10(hrDat[iPuf,iC]/maxC))
    color[iPuf] = pg.glColor((cScale,1.))

  return pos,size,color,maxC

hr = 12
pos,size,color,maxC = setHrDat(hr)
sp1 = gl.GLScatterPlotItem(pos=pos, size=size*.1, color=color, pxMode=False)
#sp1.translate(5,5,0)
ax = gl.GLAxisItem()
ax.setSize(1,1,1)
w.addItem(ax)
w.setWindowTitle('Puff at %d hr'%hr)
w.addItem(sp1)

def update():
  ## update surface positions and colors
  global hr,maxC
  
  hr += 1
  if hr > 21:
    hr   = 12
    pos,size,color,maxC = setHrDat(hr)
  else:
    pos,size,color,dumC = setHrDat(hr,maxC=maxC)
  w.setWindowTitle('Puff at %d hr'%hr)
  #if np.remainder(hr,2) == 0:
  #  color[:] = (0.0, 1.0, 0.0, 0.5)
  #else:
  #  color[:] = (1.0, 0.0, 0.0, 0.5)
  sp1.setData(pos=pos,size=size*.1,color=color)
    
t = QtCore.QTimer()
t.timeout.connect(update)
t.start(500)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()