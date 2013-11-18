"""
Plot using SAG nodes and triangles
"""
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from matplotlib import colors
import numpy as np
import os
import sys
import optparse

def printUsage():
  print 'Usage: plotTri -i inFile[.ntv] [-n t ] [-l skiplines ]'

os.chdir('d:\\SCIPUFF\\runs\\EPRI\\IncrDose')
arg = optparse.OptionParser()
arg.add_option("-i",action="store",type="string",dest="inFile")
arg.add_option("-n",action="store",type="string",dest="isLatLon")
arg.add_option("-l",action="store",type="int",dest="nSkip")
arg.set_defaults(inFile=None,nSkip=13,isLatLon='F')
opt,args = arg.parse_args()

print 'Current directory = ',os.getcwd()

# Check arguments
if opt.inFile:
  inFile = opt.inFile
else:
  print 'Error: inFile must be specified'
  printUsage()
  sys.exit()
    
if opt.nSkip:
  nSkip = opt.nSkip

if opt.isLatLon[0].lower() == 't':
  isLatLon = True
else:
  isLatLon = False
  
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

levels = np.linspace(0.,1.,num=11)
print levels
lnorm  = colors.Normalize(levels,clip=False)

#outFile = open(inFile+'_out.dat','w',0)
#for i in range(len(c)):
#  if c[i] > 1e-18:
#    outFile.write('%g %g %g\n'%(x[i],y[i],c[i]))
#outFile.close()

# tricontour.
fig = plt.figure()
plt.clf()
plt.hold(True)
plt.tricontourf(x,y,c, triangles=triangles, norm= lnorm, levels = levels, cmap=plt.cm.jet)
cbar = plt.colorbar(ticks=levels,format="%4.2f")
cbar.ax.set_yticklabels(levels)
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

