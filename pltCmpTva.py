
#!/bin/env python
import os
import sys
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3

# Local modules
sys.path.append('C:\\cygwin\\home\\sid\\python')
import utilDb

# Code for SCICHEM 2012 plots

def mainProg():

  preDbName1 = 'tva_990715.smp.db'
  preDbName2 = 'SCICHEM-01\\071599_vo3_lin_intel.smp.db'

  # Predicted data
  preConn1 = sqlite3.connect(preDbName1)
  preConn1.row_factory = sqlite3.Row
  preCur1 = preConn1.cursor()

  # Predicted data
  preConn2 = sqlite3.connect(preDbName2)
  preConn2.row_factory = sqlite3.Row
  preCur2 = preConn2.cursor()
  
  varNames = ["SO2", "O3", "NO",  "NO2"]
  
  distance = [62] #16, 62, 106]
  times    = [11.25] #, 11.5, 11.5]
  zSmp     = [582] #415, 582, 584]
  
  for idt,dist in enumerate(distance):

    # Observed data
    obsDbName = 'OBS\\tva_071599_' + str(dist) + 'km_obs6.csv.db'
    obsConn = sqlite3.connect(obsDbName)
    obsConn.row_factory = sqlite3.Row
    obsCur = obsConn.cursor()

    lArc = 2.*dist*np.pi/180.
   
    for varName in varNames:

      #print dist,' km, ',varName
      figName = str(dist) +'km_' +varName +'_'+ str(times[idt]) + 'hr.png'
      print figName

      # Observations
      obsQry = 'select plumeKM, ' + varName + ' from dataTable'
      obsArray = utilDb.db2Array(obsCur,obsQry)
      if varName == 'SO2':
        oMax = np.where(obsArray[:,1] == obsArray[:,1].max())[0][0]
        print oMax,obsArray[oMax,0],obsArray[oMax,1]

      # Prediction query
      preQry1  = "select xSmp,Value from samTable a,smpTable p where a.colNo=p.colNo and "
      preQry1 += "varName = '%s' and zSmp = %f and time = %3f"%(varName,zSmp[idt],times[idt])
      #print preQry1

      # Predictions #1 (2012)
      preArray1 = utilDb.db2Array(preCur1,preQry1)
      if idt == 0 and varName == 'SO2':
        iMax1 = np.where(preArray1[:,1] == preArray1[:,1].max())[0][0]
        for i in range(len(preArray1)):
          preArray1[i,0] = float(i-iMax1)*lArc + obsArray[oMax,0] 
        dArray1 = preArray1[:,0]
      else:
        preArray1[:,0] = dArray1

      # Predictions #2 (v2100)
      preArray2 = utilDb.db2Array(preCur2,preQry1)
      if idt == 0 and varName == 'SO2':
        iMax2 = np.where(preArray2[:,1] == preArray2[:,1].max())[0][0]
        for i in range(len(preArray2)):
          preArray2[i,0] = float(i-iMax2)*lArc + obsArray[oMax,0] 
        dArray2 = preArray2[:,0]
      else:
        preArray2[:,0]= dArray2

      #
      pltCmpConc(zSmp, varName, obsArray, preArray1, preArray2, varName, figName)

    obsConn.close()
    
  preConn1.close()
  preConn2.close()
      
def pltCmpConc(zSmp, varName, obsData, preData1, preData2, title, figName):
  #import pdb; pdb.set_trace()
  fig = plt.figure()
  plt.clf()
  fig.hold(True)
  #print obsData[:,1]
  plt.plot(obsData[:,0],obsData[:,1],'ro')
  plt.plot(preData1[:,0],preData1[:,1],'gs-')
  plt.plot(preData2[:,0],preData2[:,1],'b^-')
  plt.ylabel(zSmp)
  plt.xlabel(varName)
  plt.title(title)
  fig.hold(False)
  plt.savefig(figName)
  #plt.show()
  return
            
# Main program
if __name__ == '__main__':
  os.chdir('d:\\SCIPUFF\\runs\\EPRI\\Nash99')
  mainProg()
