
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

# Local libs
import measure
import tab2db
import utilDb
import utilPlot


compName = socket.gethostname()

os.chdir('d:\\downloads\\ClassIData')
fList = os.listdir('./')

plt.clf()
plt.hold(True)
colors  = ['red','blue','green','red','blue','green']
markers = ['o','*','+','d','s','^']
xMin = -110.1
xMax = -106.2
yMin = 35.1
yMax = 38.2

#for f in fList:
#  if f.endswith('.dat'):
    
for fNo,f in enumerate(['bandwild-recep.dat','laga2-recep.dat','meve-recep.dat',\
                         'pefo2-recep.dat','sape-recep.dat','wemi2-recep.dat']): 
    
  xcount = 0
  ycount = 0
  fi = open(f,'r')
  fo = open(f+'.1','w')
  for line in fi:
    x,y,z = map(float,line.split())
    #if x >= -110.07155 and x <= -106.18867:
    if x >= xMin and x <= xMax:
      xcount += 1
      #if y >= 34.67199 and y <= 38.66082:
      if y >= yMin and y <= yMax:
        ycount += 1
        xsav,ysav,zsav = (x,y,z)
        clr = colors[fNo]
        mkr = markers[fNo]
        plt.scatter(x,y,color=clr,marker=mkr,s=15)
  fi.close()
  if ycount > 1:
    print f,ycount,xsav,ysav,zsav
    fo.write('%g %g %g'%(xsav,ysav,zsav))
  fo.close()

sys.exit()

plt.hold(True)
plt.xlim([xMin,xMax])
plt.ylim([yMin,yMax])
plt.savefig('ClassI.png')


# Rewrite SCICHEM sam file with z set to 0
os.chdir('d:/SCIPUFF/runs/EPRI/IncrDose')
oFile = open('temp.sam','w')
for line in fileinput.input('tva_980825.sam'):
  if fileinput.isfirstline():
    oFile.write(line)
  else:
    x,y,z,mc,mn = line.split()
    oFile.write('%8s %8s %8s %8s %s\n'%(x.strip(),y.strip(),'0.0',mc.strip(),mn.strip()))
oFile.close()
fileinput.close()

'''
# Find minimum and maximum ustar
os.chdir('d:/SCIPUFF/runs/Validation/LSV')
#ustar = np.loadtxt('fort.77', delimiter=',', usecols=(0, 2), unpack=False)
ustar = np.loadtxt('fort.77',usecols=(1,), unpack=False)
x = [i for i in range(len(ustar))]
#plt.scatter(x,ustar)
#plt.show()
print ustar.min(), ustar.max()
'''

# Prints available only non-reverse color maps in matplotlib.cm 
#maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
#print maps

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


