
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

sbl = []
sxy = []
rxy = []

isSrc = False
isRec = False
for line in fileinput.input('TRACAER.AERMOD'):
  lstrip = line.strip()
  if ' STARTING' in lstrip:
    if 'SO ' in lstrip:
      isSrc = True
    if 'RE ' in lstrip: 
      isRec = True 
    continue
  if ' FINISHED' in lstrip:
    if 'SO ' in lstrip:
      if len(sxy) == 1:
        sxy.append(sxy[0])
      isSrc = False
    if 'RE ' in lstrip: 
      isRec = False 
    continue
  if isSrc:
    if 'LOCATION ' in lstrip:
      lsplit = lstrip.split()
      indx   = lsplit.index('LOCATION')
      sbl.append(lsplit[indx+1])
      sxy.append([float(lsplit[indx+3]),float(lsplit[indx+4])])
  if isRec:
    if 'DISCCART ' in lstrip:
      lsplit = lstrip.split()
      indx   = lsplit.index('DISCCART')
      rxy.append([float(lsplit[indx+1]),float(lsplit[indx+2])])
fileinput.close()

sxy = np.array(sxy)
rxy = np.array(rxy) 

plt.clf()
plt.hold(True)

hr = plt.scatter(rxy[:,0],rxy[:,1],color='red',marker='o',s=50)
hs = plt.scatter(sxy[:,0],sxy[:,1],color='green',marker='^',s=50)

labels = ['R{0}'.format(i) for i in range(len(rxy))]
for label, x, y in zip(labels, rxy[:, 0], rxy[:, 1]):
  plt.annotate(label, xy = (x, y), xytext = (0, 0), textcoords = 'offset points')

isAdded = []
for label, x, y in zip(sbl, sxy[:, 0], sxy[:, 1]):
  if label in isAdded:
    continue
  isAdded.append(label)
  plt.annotate(label, xy = (x, y), xytext = (0, 0), textcoords = 'offset points')

plt.xlabel('x')
plt.ylabel('y')
plt.hold(False)
plt.show()
#plt.savefig('cop_ord.png')

