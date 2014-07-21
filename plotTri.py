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
import os
import sys
import optparse

def printUsage():
  print 'Usage: plotTri -i inFile[.ntv] [-n t ] [-l skiplines ] [-s log/linear ]'

#os.chdir('d:\\SCIPUFF\\runs\\EPRI\\IncrDose')
os.chdir('d:\\SrcEst\\P1\\runs\\Outputs\\OnlySimple\\Simple\\ETEX')

arg = optparse.OptionParser()
arg.add_option("-i",action="store",type="string",dest="inFile")
arg.add_option("-n",action="store",type="string",dest="isLatLon")
arg.add_option("-l",action="store",type="int",dest="nSkip")
arg.add_option("-s",action="store",type="string",dest="isLog")
arg.set_defaults(inFile=None,nSkip=13,isLatLon='F',isLog='linear')
opt,args = arg.parse_args()

print 'Current directory = ',os.getcwd()

# Check arguments
if opt.inFile:
  inFile = opt.inFile
else:
  inFile = 'rev_etex_mle.ntv'
  #print 'Error: inFile must be specified'
  #printUsage()
  #sys.exit()
    
if opt.nSkip:
  nSkip = opt.nSkip

if opt.isLatLon[0].lower() == 't':
  isLatLon = True
else:
  isLatLon = False

if opt.isLog.lower().strip() == 'log':
  isLog = True
else:
  isLog = False
  
if inFile.endswith('.ntv'):
  inFile = inFile.replace('.ntv','')

if not os.path.exists(inFile + '.ntv'):
  print 'Error: cannot find file %s.ntv'%inFile
  sys.exit()

if not os.path.exists(inFile + '.tri'):
  print 'Error: cannot find file %s.tri'%inFile
  sys.exit()

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

print 'Max Value = ',maxc
print 'No. of points = ',npts

c = c/maxc

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

#outFile = open(inFile+'_out.dat','w',0)
#for i in range(len(c)):
#  if c[i] > 1e-18:
#    outFile.write('%g %g %g\n'%(x[i],y[i],c[i]))
#outFile.close()

# tricontour.
fig = plt.figure()
plt.clf()
plt.hold(True)
cax = plt.tricontourf(x,y,c, triangles=triangles, norm= lnorm, levels = levels, cmap=plt.cm.jet, vmin=0.01,extend='both')
cax.cmap.set_under('white')
cax.set_clim(0.01,1.01)
cbar = plt.colorbar(ticks=levels,format="%3.1f")
cbar.ax.set_yticklabels(levels-0.01)
plt.tricontour(x,y,c, triangles=triangles, norm= lnorm, levels = levels, colors='k')

if isLatLon:
  plt.xlabel('Longitude')
  plt.ylabel('Latitude')
else:
  plt.xlabel('X')
  plt.ylabel('Y')
plt.hold(False)
plt.title('Concentrations for '+ inFile + ' scaled with %8.3e'%maxc)
fig.savefig(inFile+'.png')
#plt.show()

