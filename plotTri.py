"""
Plot using SAG nodes and triangles
"""
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import matplotlib.cm as cm
from matplotlib import colors
import numpy as np
import numpy.ma as ma
import os
import sys
import optparse

def printUsage():
  print 'Usage: plotTri -i inFile[.ntv] [-n t ] [-l skiplines ] [-s log/linear ]'

#os.chdir('d:\\SCIPUFF\\runs\\EPRI\\IncrDose')
#os.chdir('d:\\SrcEst\\P1\\runs\\Outputs\\OnlySimple\\ETEX\\FwdRev')

arg = optparse.OptionParser()
arg.add_option("-i",action="store",type="string",dest="inFile")
arg.add_option("-n",action="store",type="string",dest="isLatLon")
arg.add_option("-l",action="store",type="int",dest="nSkip")
arg.add_option("-s",action="store",type="string",dest="isLog")
arg.add_option("-x",action="store",type="string",dest="xLim")
arg.add_option("-y",action="store",type="string",dest="yLim")
arg.add_option("-t",action="store",type="string",dest="terFile")
arg.set_defaults(inFile=None,nSkip=-1,isLatLon='F',isLog='linear',xLim=None,yLim=None,terFile=None)
opt,args = arg.parse_args()

print 'Current directory = ',os.getcwd()
nSkip   = -1
terSkip = -1
nodeTer = None

for tbreak in range(1):

  #inFile = 'RevEtex_t%04d.ntv'%(tbreak+1)
  #print inFile
  # Check arguments

  if opt.inFile:
    inFile = opt.inFile
  else:
    inFile = 'RevEtex_t%4d.ntv'%tbreak
    #print 'Error: inFile must be specified'
    #printUsage()

  if opt.nSkip:
    nSkip = opt.nSkip
  
  #print 'Error: inFile must be specified'
  #printUsage()
  #sys.exit()
  print 'Plotting inFile ',inFile
 
  if opt.isLatLon[0].lower() == 't':
    isLatLon = True
  else:
    isLatLon = False
  
  if opt.isLog.lower().strip() == 'log':
    isLog = True
  else:
    isLog = False
    
  if opt.xLim is not None:
    if ',' in opt.xLim:
      xMin,xMax = map(float,opt.xLim.split(','))
    else:
      printUsage
      sys.exit()
    xLim = [xMin,xMax] 
  else:
    xLim = None
    
  if opt.yLim is not None:
    if ',' in opt.yLim:
      yMin,yMax = map(float,opt.yLim.split(','))
    else:
      printUsage
      sys.exit()
    yLim = [yMin,yMax] 
  else:
    yLim = None
    
  if opt.terFile is not None:
    terFile = opt.terFile
    inFiles = [inFile,terFile]
  else:
    terFile = None
    inFiles = [inFile]
  
  for fNo in range(len(inFiles)):
    
    fName = inFiles[fNo]
    
    if fName.endswith('.ntv'):
      inFiles[fNo] = fName.replace('.ntv','')
    
    fName = inFiles[fNo]
    
    if not os.path.exists(fName + '.ntv'):
      print 'Error: cannot find file %s.ntv'%fName
      sys.exit()
    
    if not os.path.exists(fName + '.tri'):
      print 'Error: cannot find file %s.tri'%fName
      sys.exit()
  
  inFile = inFiles[0]
  if terFile is not None:
    terFile = inFiles[1] 
    
  if nSkip == -1:
    if opt.nSkip != -1:
      nSkip = opt.nSkip
    else:
      ntvFile = open(inFile+'.ntv')
      nSkip = 0
      for line in ntvFile:
        nSkip += 1
        if '!NODES' in line:
          break
      ntvFile.close()
  
  nodeData = np.loadtxt(inFile+'.ntv', skiprows=nSkip, usecols=(0, 1, 2, 5), dtype={'names':('nId','x','y','cmean'),\
                        'formats':('int','float','float','float')})
  triData  = np.loadtxt(inFile+'.tri', skiprows=1, usecols=(0, 1, 2, 3), dtype={'names':('tId','nIda','nIdb','nIdc'),\
                        'formats':('int','int','int','int')})
  
  nodeData = np.sort(nodeData,order='nId')
  triData  = np.sort(triData,order='tId')
  
  triangles = np.array([triData['nIda']-1,triData['nIdb']-1,triData['nIdc']-1])
  
  # Rotate for LatLon
  if isLatLon:
    y = nodeData['x']
    x = nodeData['y']
  else:
    x = nodeData['x']
    y = nodeData['y']
  c = nodeData['cmean']
  
  npts = len(x)
  maxc = max(c)
  if maxc == 0: 
    maxc = 1.
  
  print 'Max Value = ',maxc
  print 'No. of points = ',npts
  
  c = c/maxc
  c = ma.masked_where(c<1e-30,c)
  c = ma.filled(c,1e-30)
  
  if isLog:
    logBase = 10.
    clrmin = -6
    clrmax = 0
    clrlev = (clrmax - clrmin + 1)
    levels = np.logspace(clrmin,clrmax,num=clrlev,base=logBase)
    clrmap = cm.get_cmap('jet',clrlev-1)
    lnorm  = colors.LogNorm(levels,clip=False)
  else:
    clrmin = 0.
    clrmax = 1.
    clrlev = 11 
    levels = np.linspace(clrmin,clrmax,num=clrlev)
    clrmap = cm.get_cmap('jet',clrlev-1)
    lnorm  = colors.Normalize(levels,clip=False)
  
  print levels
  
  # tricontour.
  fig = plt.figure()
  plt.clf()
  plt.hold(True)
  if isLog:
    cax = plt.tricontourf(x,y,c, triangles=triangles, norm= lnorm, levels = levels, cmap=plt.cm.jet, vmin = 10**clrmin)
  else:
    cax = plt.tricontourf(x,y,c, triangles=triangles, norm= lnorm, levels = levels, cmap=plt.cm.jet, vmin=0.01,extend='both')
  cax.cmap.set_under('white')
  
  if isLog:
    cax.set_clim(10**clrmin,10**clrmax)
    cbar = plt.colorbar(ticks=levels,format="%5.3e")
    cbar.ax.set_yticklabels(levels)
  else:
    cax.set_clim(0.01,1.01)
    cbar = plt.colorbar(ticks=levels,format="%3.1f")
    cbar.ax.set_yticklabels(levels-0.01)
  plt.tricontour(x,y,c, triangles=triangles, norm= lnorm, levels = levels, colors='k')
  
  # Read Terrain file
  if terFile is not None:

    if nodeTer is None:
      
      if terSkip == -1:
        ntvFile = open(inFile+'.ntv')
        terSkip = 0
        for line in ntvFile:
          terSkip += 1
          if '!NODES' in line:
            break
        ntvFile.close()
      
      nodeTer = np.loadtxt(terFile+'.ntv', skiprows=terSkip, usecols=(0, 1, 2, 5), dtype={'names':('nId','xTer','yTer','hTer'),\
                        'formats':('int','float','float','float')})
      triTer  = np.loadtxt(terFile+'.tri', skiprows=1, usecols=(0, 1, 2, 3), dtype={'names':('tId','nIda','nIdb','nIdc'),\
                            'formats':('int','int','int','int')})
      
      nodeTer = np.sort(nodeTer,order='nId')
      triTer  = np.sort(triTer,order='tId')
      
      terTri  = np.array([triTer['nIda']-1,triTer['nIdb']-1,triTer['nIdc']-1])
      
      # Rotate for LatLon
      if isLatLon:
        yTer = nodeTer['xTer']
        xTer = nodeTer['yTer']
      else:
        xTer = nodeTer['xTer']
        yTer = nodeTer['yTer']
        
      hTer = nodeTer['hTer']
      
      clrmin = hTer.min()
      clrmax = hTer.max()
      idmax = np.where(hTer == clrmax)[0][0]
      clrlev = 11 
      terLevels = np.linspace(clrmin,clrmax,num=clrlev)
      terLnorm  = colors.Normalize(terLevels,clip=False)
      
    terH = plt.tricontour(xTer, yTer, hTer, triangles=terTri, norm=terLnorm, levels=terLevels, colors='k')
    plt.clabel(terH, inline=1, fontsize=10)
    
  if isLatLon:
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
  else:
    plt.xlabel('X')
    plt.ylabel('Y')
    
  if xLim is not None:     
    plt.xlim(xLim)  

  if yLim is not None:  
    plt.ylim(yLim)

  plt.hold(False)
  plt.title('Concentrations for '+ inFile + ' scaled with %8.3e'%maxc)
  fig.savefig(inFile+'.png')
  #plt.show()

