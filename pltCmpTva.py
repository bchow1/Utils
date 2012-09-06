
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

  prjName = 'tva_980825'
  preDbName1 = 'tva_980825.smp.db'
  #preDbName2 = 'SCICHEM-01\\071599_vo3_lin_intel.smp.db'
  preDbName2 = 'SCICHEM-01\\tva_082598.smp.db'

  # Predicted data
  preConn1 = sqlite3.connect(preDbName1)
  preConn1.row_factory = sqlite3.Row
  preCur1 = preConn1.cursor()

  # Predicted data
  preConn2 = sqlite3.connect(preDbName2)
  preConn2.row_factory = sqlite3.Row
  preCur2 = preConn2.cursor()
  
  varNames = ["SO2", "O3", "NO",  "NO2"]

  if prjName == "tva_990715":
    distance = [16, 62, 106]
    times    = [11.5, 12.5, 17.0]
    zSmp     = [415, 584, 582]

  if prjName == "tva_980825":
    distance = [20, 55, 110]
    times    = [12, 12.75, 14.5]
    zSmp     = [520, 600, 620]
  
  for idt,dist in enumerate(distance):    

    lArc = 2.*dist*np.pi/180.
   
    for varName in varNames:

      print '\n',dist,' km, ',varName

      # Prediction query
      preQry1  = "select xSmp,Value from samTable a,smpTable p where a.colNo=p.colNo and "
      preQry1 += "varName = '%s' and zSmp = %f and time = %3f"%(varName,zSmp[idt],times[idt])
      print preQry1

      # Predictions #1 (2012)
      preArray1 = utilDb.db2Array(preCur1,preQry1)
      if varName == 'SO2':
        iMax1 = np.where(preArray1[:,1] == preArray1[:,1].max())[0][0]
          
      # Predictions #2 (v2100)
      preArray2 = utilDb.db2Array(preCur2,preQry1)
      if varName == 'SO2':
        iMax2 = np.where(preArray2[:,1] == preArray2[:,1].max())[0][0]
          
      # Observed data
      if prjName == "tva_990715":
        if dist == 16:
          pls = [1,2,3,4]
        if dist == 62:
          pls = [6,7,8]
        if dist == 106:
          pls = [9,10,11]

      if prjName == "tva_980825":
        if dist == 20:
          pls = [3,4,5]
        if dist == 55:
          pls = [6,7,8]
        if dist == 110:
          pls = [9,10,11]

      oMax  = [0 for i in range(12)]
      
      for ipl in pls:
        
        #obsDbName = 'OBS\\tva_071599_' + str(dist) + 'km_obs' + str(ipl) + '.csv.db'
        obsDbName = 'OBS\\cumb1_'+ str(dist) + 'km_obs' + str(ipl) + '.csv.db'
        print '\n',obsDbName
      
        obsConn = sqlite3.connect(obsDbName)
        obsConn.row_factory = sqlite3.Row
        obsCur = obsConn.cursor()

        # Observations
        obsQry = 'select plumeKM, ' + varName + ' from dataTable'
        print obsQry
        
        obsArray = utilDb.db2Array(obsCur,obsQry)
        if varName == 'SO2':
          oMax[ipl] = np.where(obsArray[:,1] == obsArray[:,1].max())[0][0]
          print oMax[ipl],obsArray[oMax[ipl],0],obsArray[oMax[ipl],1]

        # Align the prediction1 and observed centerlines

        for i in range(len(preArray1)):
          preArray1[i,0] = float(i-iMax1)*lArc + obsArray[oMax[ipl],0] 

        # Align the prediction2 and observed centerlines

        for i in range(len(preArray2)):
          preArray2[i,0] = float(i-iMax2)*lArc + obsArray[oMax[ipl],0] 
           
        # Plot
        figName  = str(dist) +'km_' +varName +'_'+ str(times[idt]) + 'hr_obs' + str(ipl) + '.png'
        figTitle = '%s (@ %d km for plume %d)'%(varName,dist,ipl)
        print figName

        pltCmpConc(zSmp, varName, obsArray, preArray1, preArray2, figTitle, figName)

        obsConn.close()
    
  preConn1.close()
  preConn2.close()
      
def pltCmpConc(zSmp, varName, obsData, preData1, preData2, figTitle, figName):
  #import pdb; pdb.set_trace()
  fig = plt.figure()
  plt.clf()
  fig.hold(True)
  #print obsData[:,1]
  LhO  = plt.plot(obsData[:,0],obsData[:,1],'ro')
  LkO  = 'OBS'
  C = ma.masked_where(preData1[:,1]<0.,preData1[:,1])
  LhP1 = plt.plot(preData1[:,0],C,'gs-')
  LkP1 = 'SCICHEM-2012'
  C = ma.masked_where(preData2[:,1]<0.,preData2[:,1])
  LhP2 = plt.plot(preData2[:,0],C,'b^-')
  LkP2 = 'SCICHEM-v2100'
  plt.ylabel('Concentration (ppm)')
  plt.xlabel('Cross plume distance (km)')
  plt.title(figTitle)
  plt.xlim([-50,50])
  plt.legend([LkO,LkP1,LkP2],bbox_to_anchor=(0.72,0.98),loc=2,borderaxespad=0.)
  lgnd  = plt.gca().get_legend()
  ltext = lgnd.get_texts()
  plt.setp(ltext,fontsize=9)
  fig.hold(False)
  plt.savefig(figName)
  #plt.show()
  return
            
# Main program
if __name__ == '__main__':
  #os.chdir('d:\\SCIPUFF\\runs\\EPRI\\Nash99')
  #os.chdir('d:\\SCICHEM-2012\\TVA_990715')
  os.chdir('d:\\SCICHEM-2012\\TVA_980825')
  mainProg()
