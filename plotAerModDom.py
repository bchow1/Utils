
#
import os
import sys
import socket
import fileinput
import numpy as np
import matplotlib.pyplot as plt

def getAerDom(AerInpFile):

  sbl = []
  sxy = []
  rxy = []
  
  isSrc = False
  isRec = False
  isMet = False
  
  for line in fileinput.input(AerInpFile):
    lstrip = line.strip()
    if ' STARTING' in lstrip:
      if 'SO ' in lstrip:
        isSrc = True
      if 'RE ' in lstrip: 
        isRec = True 
      if 'ME ' in lstrip: 
        isMet = True       
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
      if 'EVALCART ' in lstrip:
        lsplit = lstrip.split()
        indx   = lsplit.index('EVALCART')
        rxy.append([float(lsplit[indx+1]),float(lsplit[indx+2])])
    if isMet:
      if 'SURFFILE' in lstrip:
        lsplit = lstrip.split()
        indx   = lsplit.index('SURFFILE')
        srfFile = lsplit[indx+1]
  fileinput.close()
  
  '''
  for line in fileinput.input(srfFile):
    if fileinput.isfirstline():
      lsplit    = line.strip().split()
      try:
        (lat,lon) = (lsplit[0],lsplit[1])
      except ValueError:
        break
      if lat.endswith('N'):
        lat = float(lat[:-1])
      else:
        lat = -float(lat[:-1])
      if lon.endswith('E'):
        lon = float(lon[:-1])
      else:
        lon = -float(lon[:-1])
    else:
      break
  latlon = (lat,lon)
  fileinput.close()
  '''
  latlon = (-99,-99)
         
  sxy = np.array(sxy)
  rxy = np.array(rxy)
  
  return (sbl,sxy,rxy,latlon)

if __name__ == '__main__':

  compName = socket.gethostname()
  
  # Local modules
  if  compName == 'pj-linux4':
    sys.path.append('/home/user/bnc/python')
    runDir = ''
  if compName == 'sm-bnc':
    #runDir = 'D:\\Aermod\\v12345\\runs\\pgrass\\SCICHEM'
    #AerInpFile = 'PGRASS.AERMOD'
    runDir = 'd:\\SCIPUFF\\runs\\EPRI\\NO2_PVRM\\SCICHEM'
    AerInpFile = 'nox.2005.st.sci'
    
  os.chdir(runDir)
  
  (sbl,sxy,rxy,latlon) = getAerDom(AerInpFile)
  
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

