
#
import os
import sys
import socket
import fileinput
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import measure

compName = socket.gethostname()

# Local modules
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')

def readcOP(fileName, run):
  cOP   = []
  arcOP = [[] for i in range(3)]
  for line in fileinput.input(fileName):
    if line.startswith('time'):    
      arc1 = line.split()[3:5]
      arc2 = line.split()[5:7]
      arc3 = line.split()[7:9]
      print arc1, arc2, arc3
      arcOP[0].append(map(float,arc1))
      arcOP[1].append(map(float,arc2))
      arcOP[2].append(map(float,arc3))
      cOP.append(map(float,arc1))
      cOP.append(map(float,arc2))
      cOP.append(map(float,arc3))
  cOP = getMaskedArray(cOP)
  arcOP = np.array(arcOP)
  #print arcOP.shape
  for arc in range(3):
    getStats(arcOP[arc,:,1], arcOP[arc,:,0], statFile, run ,str(arc))
  #print cOP  #

  return (cOP)

def getMaskedArray(cOP):
    cOP = np.array(cOP)
    cOP[:,0] = np.sort(cOP[:,0])
    cOP[:,1] = np.sort(cOP[:,1])
    cOP = ma.masked_where(cOP<-98.0,cOP)*1e-3
    print cOP
    return cOP

def getStats(data1, data2, statFile, case, arc):
  upa = measure.upa(data1, data2)
  rnmse = measure.rnmse_2(data1, data2, cutoff = 0.)
  biasFac = measure.bf(data1, data2)
  fac2 = measure.fac2(data1, data2)
  fac5 = measure.fac5(data1, data2)
  mfbe = measure.mfbe(data1, data2, cutoff=0.0)          
  print 'in get stats'
  print 'obs:',data2
  print 'pre:',data1
  if statFile is not None:
    statFile.write("%s,%s,%8.3f, %8.3f, %8.3f, %8.3f,%8.3f,%8.3f\n"%(case,arc, upa,rnmse,biasFac,mfbe, fac2, fac5))

if compName == 'sage-d600':
  runDir = 'D:\\SCICHEM-2012\\Cop'
if compName == 'sm-bnc':
  runDir = 'D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\runs\\COP'
  
os.chdir(runDir)
statFile = open("COP_stat.csv","w")
statFile.write("Case, Arc, upa, rnmse, biasFac, mfbe, fac2, fac5\n")

fileName = os.path.join(runDir,'cop.all')
cSkewOP  = readcOP(fileName, "Skew")
print 'cSkewOP',cSkewOP

fileName = os.path.join(runDir,'SCICHEM-01','cop.all')
cStdOP   = readcOP(fileName, "Standard")
print 'cStdOP',cStdOP

params1 = {'axes.labelsize': 16, 'text.fontsize': 16, 'xtick.labelsize': 16,
           'ytick.labelsize': 16, 'legend.pad': 0.1,  # empty space around the legend box
           'legend.fontsize': 14, 'lines.markersize': 6, 'lines.width': 2.0,
           'font.size': 12}

plt.rcParams.update(params1)
plt.clf()
plt.hold(True)
hskew = plt.scatter(cSkewOP[:,0],cSkewOP[:,1],color='0.1',marker='o',s=100)
hstd  = plt.scatter(cStdOP[:,0],cStdOP[:,1],color='0.3',marker='s',s=100)

vmin = 0.
vmax = max(cSkewOP.max(),cStdOP.max())
print vmin,vmax
plt.xlim([vmin,vmax])
plt.ylim([vmin,vmax])
plt.title('Comparison of Maximum Concentration')
plt.plot([vmin,vmax],[vmin,vmax],'k-')
#plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5],'r-')
#plt.plot([vmin,vmax],[vmin*2,vmax*2],'r-')
plt.xlabel(r'Observed ($\mu g/m^3$)')
plt.ylabel(r'Predicted ($\mu g/m^3$)')
plt.legend([hskew,hstd],['Skew Model','Standard Model'],bbox_to_anchor=(0.4,0.97))
plt.hold(False)
#plt.show()
plt.savefig('cop_ord.png')

