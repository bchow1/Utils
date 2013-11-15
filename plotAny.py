
#
import os
import sys
import socket
import fileinput
import math
import numpy as np
import numpy.ma as ma
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from matplotlib import colors
import matplotlib.cm as cm
import measure

# Local libs
import tab2db
import utilDb
import utilPlot


compName = socket.gethostname()

# Prints available color maps in matplotlib.cm 
maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
# Only non-reverse colormaps
print maps
# Only reversed colormaps
#maps = sorted(m for m in plt.cm.datad if m.endswith("_r"))
#print maps
#sys.exit()

'''
# Example for scatter plot showing source and receptor locations
# read from AERMOD input file

if  compName == 'pj-linux4':
  runDir = ''
else:
  runDir = 'D:\\Aermod\\v12345\\runs\\kinsf6'
os.chdir(runDir)

sxy = []
rxy = []

for line in fileinput.input('TRACAER.INP'):
  lstrip = line.strip()
  if lstrip.startswith('SO LOCATION  STACK1  POINT'):
    sxy.append(map(float,lstrip[26:].split()[0:2]))
  if lstrip.startswith('DISCCART'):
    rxy.append(map(float,lstrip[8:].split()[0:2]))
fileinput.close()

sxy = np.array(sxy)
rxy = np.array(rxy)

plt.clf()
plt.hold(True)

hr = plt.scatter(rxy[:,0],rxy[:,1],color='red',marker='o',s=50)
hs = plt.scatter(sxy[:,0],sxy[:,1],color='green',marker='^',s=50)

'''
'''
# Example of scatter plots with legend and factor of 2 lines.

if compName == 'sage-d600':
  runDir = 'D:\\SCICHEM-2012\\Cop'
if compName == 'sm-bnc':
  runDir = 'D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\runs\\COP'

os.chdir(runDir)

fileName = os.path.join(runDir,'cop.all')
cSkewOP  = readcOP(fileName, "Skew")
print 'cSkewOP',cSkewOP

fileName = os.path.join(runDir,'SCICHEM-01','cop.all')
cStdOP   = readcOP(fileName, "Standard")
print 'cStdOP',cStdOP

plt.clf()
plt.hold(True)
hskew = plt.scatter(cSkewOP[:,0],cSkewOP[:,1],color='black',marker='o',s=50)
hstd  = plt.scatter(cStdOP[:,0],cStdOP[:,1],color='black',marker='^',s=50)

vmin = 0.
vmax = max(cSkewOP.max(),cStdOP.max())
plt.xlim([vmin,vmax])
plt.ylim([vmin,vmax])
plt.title('Comparison of Maximum Concentration')
plt.plot([vmin,vmax],[vmin,vmax],'k-')
plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5],'r-')
plt.plot([vmin,vmax],[vmin*2,vmax*2],'r-')
plt.xlabel('x')
plt.ylabel('y')
plt.legend([hskew,hstd],['Skew Model','Standard Model'],bbox_to_anchor=(0.4,0.97))
plt.hold(False)
plt.show()
plt.savefig('cop_ord.png')
'''


