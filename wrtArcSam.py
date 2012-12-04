#
import sys
import math
import matplotlib.pyplot as plt

def getFloat(x):
  xr = x.split(',')
  yr = []
  for x in xr:
    try:
      yr.append(float(x))
    except ValueError:
      print 'Error: Must enter real number ',x
      sys.exit()
  return yr

#ht = getFloat(raw_input('Heights? ')
#dt = getFloat(raw_input('Distances? ')

arcIn = open('samArc.in','r')
for line in arcIn:
  if len(line.strip()) == 0:
    continue
  varName,varData = line.split('=')
  varName = varName.strip()
  if varName == 'Source':
    xS,yS = map(float,varData.split(','))
  if varName == 'Theta':
    minTheta,maxTheta,dTheta = map(int,varData.split(','))
  if varName == 'smpStr':
    smpStr = varData.strip()
  if varName == 'Arc':
    arcs = map(float,varData.split(','))
  if varName == 'Height':
    hghts = map(float,varData.split(','))
arcIn.close()

smpFile = open('temp.sam','w')
smpFile.write('SCIPUFF SENSOR\n')
for arcNo in range(len(arcs)):
  dist = arcs[arcNo]
  xr = []
  yr = []
  for theta in range(minTheta,maxTheta+1,dTheta):
    x = dist*math.cos(math.pi/180.*theta)
    y = dist*math.sin(math.pi/180.*theta)
    xr.append(x)
    yr.append(y)
    smpFile.write('%7.3f  %7.3f  %5.1f  %s Arc@%skm\n'%(x, y, hghts[arcNo], smpStr, dist ))
  print xr[0],yr[0],xr[-1],yr[-1]
  plt.clf()
  plt.hold(True)
  plt.scatter(xr,yr,c='g',marker='o')
  plt.scatter(xS,yS,c='r',marker='d')
  plt.title('Arc @ %s(km)'%dist)
  plt.hold(False)
  plt.show()

smpFile.close()


  

