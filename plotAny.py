
#
import os
import sys
import socket
import fileinput
import math
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import measure

compName = socket.gethostname()

# Local modules
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')
  runDir = ''
if compName == 'sm-bnc':
  runDir = 'D:\\Aermod\\v12345\\runs\\tracy\\SCICHEM'
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

#vmin = 0.
#vmax = max(cSkewOP.max(),cStdOP.max())
#plt.xlim([vmin,vmax])
#plt.ylim([vmin,vmax])
#plt.title('Comparison of Maximum Concentration')
#plt.plot([vmin,vmax],[vmin,vmax],'k-')
#plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5],'r-')
#plt.plot([vmin,vmax],[vmin*2,vmax*2],'r-')
plt.xlabel('x')
plt.ylabel('y')
#plt.legend([hskew,hstd],['Skew Model','Standard Model'],bbox_to_anchor=(0.4,0.97))
plt.hold(False)
plt.show()
#plt.savefig('cop_ord.png')
