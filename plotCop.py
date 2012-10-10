#
import os
import sys
import fileinput
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

def readcOP1():
  cOP1 = []
  for line in fileinput.input('../SCICHEM-01/cop.all'):
    if line.startswith('time'):
      cOP1.append(map(float,line.split()[3:5]))
      cOP1.append(map(float,line.split()[5:7]))
      cOP1.append(map(float,line.split()[7:9]))
  cOP1 = np.array(cOP1)
  #cOP1[:,0] = np.sort(cOP1[:,0])
  #cOP1[:,1] = np.sort(cOP1[:,1])
  cOP1 = ma.masked_where(cOP1<-98.0,cOP1)*1e-3
  print cOP1.shape
  return cOP1

cOP = np.loadtxt('cop.tab',skiprows=1)
cOP = ma.masked_where(cOP>9.99999E+35,cOP)
cOP = cOP.filled(-99.0)
#cOP[:,0] = np.sort(cOP[:,0])
#cOP[:,1] = np.sort(cOP[:,1])
cOP = ma.masked_where(cOP<-98.0,cOP)*1e-3
#cOP = np.loadtxt('cop_ord.tab',skiprows=1)
#cOP = ma.masked_where(cOP>9.999999E+35,cOP)

cOP1 = readcOP1()
plt.clf()
plt.hold(True)
hskew = plt.scatter(cOP[:,0],cOP[:,1],color='g',marker='o')
hstd  = plt.scatter(cOP1[:,0],cOP1[:,1],color='b',marker='s')
vmin = 0.
vmax = max(cOP.max(),cOP1.max())
print vmin,vmax
plt.xlim([vmin,vmax])
plt.ylim([vmin,vmax])
plt.title('Comparison of Maximum Concentration')
#plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5])
#plt.plot([vmin,vmax],[vmin,vmax],'r-')
#plt.plot([vmin,vmax],[vmin*2,vmax*2])
plt.xlabel(r'Observed ($\mu g/m^3$)')
plt.ylabel(r'Predicted ($\mu g/m^3$)')
plt.legend([hskew,hstd],['Skew Model','Standard Model'],bbox_to_anchor=(0.4,0.97))
plt.hold(False)
plt.show()

#plt.savefig('y.png')

