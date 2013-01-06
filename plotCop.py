
#
import os
import sys
import fileinput
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import measure

def readcOP(fileName, run):
  cOP1 = []
  cOP2 = []
  cOP3 = []
  #for line in fileinput.input('../SCICHEM-01/cop.all'):'D:\\SCICHEM-2012\\Cop\\cop.all'
  for line in fileinput.input(fileName):
    if line.startswith('time'):
      
      arc1 = line.split()[3:5]
      arc2 =  line.split()[5:7]
      arc3 = line.split()[7:9]
      print arc1, arc2, arc3
      cOP1.append(map(float,arc1))
      cOP2.append(map(float,arc2))
      cOP3.append(map(float,arc3))
  cOP1 = getMaskedArray(cOP1)
  cOP2 = getMaskedArray(cOP2)
  cOP3 = getMaskedArray(cOP3)
  getStats(cOP1[:,0], cOP1[:,1], statFile, run ,"1")
  getStats(cOP2[:,0], cOP2[:,1], statFile, run, "2")
  getStats(cOP3[:,0], cOP3[:,1], statFile, run, "3")
  print cOP1, cOP2, cOP3
  #
  
  #print cOP1.shape
  return (cOP1, cOP2, cOP3)

def getMaskedArray(cOP):
    cOP = np.array(cOP)
    cOP = ma.masked_where(cOP<-98.0,cOP)*1e-3
    cOP[:,0] = np.sort(cOP[:,0])
    cOP[:,1] = np.sort(cOP[:,1])
    return cOP
def readcOP1(fileName, run):
  cOP1 = []
  #for line in fileinput.input('../SCICHEM-01/cop.all'):'D:\\SCICHEM-2012\\Cop\\cop.all'
  for line in fileinput.input(fileName):
    if line.startswith('time'):
      cOP1.append(map(float,line.split()[3:5]))
      cOP1.append(map(float,line.split()[5:7]))
      cOP1.append(map(float,line.split()[7:9]))
  cOP1 = np.array(cOP1)
  getStats(cOP1[:,0], cOP1[:,1], statFile, run)
  cOP1[:,0] = np.sort(cOP1[:,0])
  cOP1[:,1] = np.sort(cOP1[:,1])
  cOP1 = ma.masked_where(cOP1<-98.0,cOP1)*1e-3
  print cOP1.shape
  return cOP1

def getStats(data1, data2, statFile, case,arc):
  upa = measure.upa(data1, data2)
  rnmse = measure.rnmse_2(data1, data2, cutoff = 0.)
  biasFac = measure.bf(data1, data2)
  fac2 = measure.fac2(data1, data2)
  fac5 = measure.fac5(data1, data2)
  mfbe = measure.mfbe(data1, data2, cutoff=0.0)          
  print 'in get stats'
  if statFile is not None:
    statFile.write("%s,%s,%8.3f, %8.3f, %8.3f, %8.3f,%8.3f,%8.3f\n"%(case,arc, upa,rnmse,biasFac,mfbe, fac2, fac5))
    
runDir = 'D:\\SCICHEM-2012\\Cop' 
os.chdir(runDir)
statFile = open("COP_stat.csv","w")
statFile.write("Case, Arc, upa,rnmse,biasFac,mfbe,fac2, fac5\n")

fileName = 'D:\\SCICHEM-2012\\Cop\\cop.all'
(cOP, cOPa, cOPb) = readcOP(fileName, "Skew")
#np.loadtxt('cop.tab',skiprows=1)
#cOP = ma.masked_where(cOP>9.99999E+35,cOP)
#cOP = cOP.filled(-99.0)
#cOP[:,0] = np.sort(cOP[:,0])
#cOP[:,1] = np.sort(cOP[:,1])
#cOP = ma.masked_where(cOP<-98.0,cOP)*1e-3
#cOP = np.loadtxt('cop_ord.tab',skiprows=1)
#cOP = ma.masked_where(cOP>9.999999E+35,cOP)

fileName = 'D:\\SCICHEM-2012\\Cop\\SCICHEM-01\\cop.all'
(cOP1, cOP2, cOP3) = readcOP(fileName, "Standard")
print cOP1
print cOP
#getStats(cOP[:,0], cOP[:,1], statFile,"Skew" )

print cOPa[:,1]
print cOP[:,1]
print "COP"
print  cOP1[:,1]
print  cOP2[:,1]
print "COP1"
plt.clf()
plt.hold(True)
hskew1 = plt.scatter(cOP[:,0],cOP[:,1],color='g',marker='o')
hstd1  = plt.scatter(cOP1[:,0],cOP1[:,1],color='b',marker='s')
hskew2 = plt.scatter(cOPa[:,0],cOPa[:,1],color='g',marker='o')
hstd2  = plt.scatter(cOP2[:,0],cOP2[:,1],color='b',marker='s')
hskew3 = plt.scatter(cOPb[:,0],cOPb[:,1],color='g',marker='o')
hstd3  = plt.scatter(cOP3[:,0],cOP3[:,1],color='b',marker='s')

vmin = 0.
vmax = max(cOP.max(),cOP1.max())
print vmin,vmax
plt.xlim([vmin,vmax])
plt.ylim([vmin,vmax])
plt.title('Comparison of Maximum Concentration')
#plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5])
plt.plot([vmin,vmax],[vmin,vmax],'r-')
plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5],'r-')
plt.plot([vmin,vmax],[vmin*2,vmax*2],'r-')
plt.xlabel(r'Observed ($\mu g/m^3$)')
plt.ylabel(r'Predicted ($\mu g/m^3$)')
plt.legend([hskew1,hstd1],['Skew Model','Standard Model'],bbox_to_anchor=(0.4,0.97))
plt.hold(False)
plt.show()

plt.savefig('cop_ord.png')

