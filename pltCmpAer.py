#!/bin/env python
import os
import sys
import socket
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import measure

compName = socket.gethostname()

# Local modules
if compName == 'sm-bnc' or compName == 'sage-d600':
  sys.path.append('C:\\cygwin\\home\\sid\\python')
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')
import utilDb
import setSCIparams as SCI


def getSmpDb(prjName):
    mySciFiles = SCI.Files(prjName)

    smpDb = '%s.smp.db'%(prjName)
    (smpDbConn,smpDbCur,smpCreateDb) = utilDb.Smp2Db(smpDb,mySciFiles)
    return (smpDbConn,smpDbCur)

# Code for SCICHEM 2012 plots
def runProg(prjName):
 
  if compName == 'sm-bnc':
    os.chdir('d:\\SCICHEM-2012\\' + prjName)
  if compName == 'sage-d600':
    os.chdir('D:\\SCICHEM-2012\\AermodTestCases\\' + prjName + '\\SCICHEM')

  print 'RunDir = ',os.getcwd()
  sciFac = 1.e+9
  MaxVals = ['1 hr', '3hr', '24hr', 'All']
  MaxObs  = [0,0,0,0]  # OBS
  MaxPre1 = [0,0,0,0]  # SCICHEM-2012
  MaxPre2 = [0,0,0,0]  # AERMOD
  
  if prjName == 'kinso2':
    sciName = 'kinso2'
    obsName = 'kinso2'
    aerName = 'KS2AER'
    yMax = 2500
  if prjName == 'bowline':
    sciName = 'bowline'
    obsName = 'bow'
    aerName = 'BOWAER'
    #obs3HrFile  = 'bow03.obs'
    #pre2_1HrFile  = 'BOWAER01.PST.db'
    yMax = 850
  if prjName == 'baldwin':
    #prePrj1 = os.path.join('..','fromSS','scipuff_prj')
    sciName = 'Baldwin'
    obsName  = 'bal'
    aerName = 'BALAER'
    #MaxPre2 = [2997.35, 2261.82, 327.92, 12.17] # From SS spread sheet
    #MaxObs[3]= 12.6
    yMax = 3100
  if prjName == 'CLIFTY':
     sciName = 'CLIFTY75'
     obsName = 'CCR75'
     aerName = 'CCRAER'
  if prjName == 'martin':
     sciName = 'MCR_AER'
     obsName = 'MCR'
     aerName = 'MCRAT2'
  if prjName == 'tracy':
     sciName = 'TRACAER'
     obsName = 'TRACY'
     aerName = 'TRAER'
  
  obsDir = os.path.join('..','Obs_Conc')
  aerDir = os.path.join('..','Aermod')
  statFile = open(prjName+"_stat.csv","w")
  statFile.write("Case, Dur, maxObs, maxAER, maxSCI, RHC_AER, RHC_SCI\n")

  # SCICHEM predictions
  sciConn,sciCur = getSmpDb(sciName)
  smpIds = map(int,utilDb.db2Array(sciCur,'select distinct(smpid) from samTable'))
  nSmp   = len(smpIds)
  nTimes = utilDb.db2Array(sciCur,"select count(value) from samTable a, smptable p where a.colno=p.colno \
                          and varname='C' and smpId =1",dim=0)
  print nSmp,nTimes
  
  for iHr in [1,3,24]:
    
    # Read observations from obs directory from .obs files
    obsFile     = os.path.join(obsDir,obsName + '%02d.obs'%iHr)
    colList = (i for i in range(3,3+nSmp))
    obsArray    = np.loadtxt(obsFile,usecols=colList)
    obsArray    = np.hstack(obsArray)
    print np.shape(obsArray)
    obsArray = np.sort(obsArray)[::-1]
    print 'OBS max =', obsArray[0],obsArray[25]
    #for iSmp in range(nSmp):
    #  obsArray[:,iSmp] = np.sort(obsArray[:,iSmp])[::-1]
    #  print 'OBS max =', obsArray[0,iSmp],obsArray[25,iSmp]
    
    
    aerFile = os.path.join(aerDir,aerName + '%02d.PST.db'%iHr)
    aerConn = sqlite3.connect(aerFile)
    aerConn.row_factory = sqlite3.Row
    aerCur = aerConn.cursor()    
    aerQry = 'select Cavg from datatable order by Cavg desc'
    aerArray = utilDb.db2Array(aerCur,aerQry,dim=1)
    print 'AERMOD max =', aerArray[0],aerArray[25]
    aerConn.close()
            
    if iHr > 1:
      preQry  = "select value from samTable a, smptable p where a.colno=p.colno "
      preQry += "and varname='C' and smpId ="
      sciMax  = np.zeros((nSmp,nTimes/iHr),float)
      for j,smpId in enumerate(smpIds):
        sciQry = preQry + str(smpId) + ' order by time'
        hrMax  =  utilDb.db2Array(sciCur,sciQry)
        # avgArray[j,:] = np.convolve(hrMax, np.ones(iHr)/iHr)
        for i in range(0,len(hrMax)-iHr+1,iHr):
          sciMax[j,i/iHr] = np.mean(hrMax[i:i+iHr])
      
      sciMax = np.reshape(sciMax,np.size(sciMax))  
      sciArray = np.sort(sciMax)[::-1]
      sciArray = sciArray*sciFac
      print 'SCICHEM max = ',sciArray[0],sciArray[25]
    else:
      sciQry  = "select value from samTable a, smptable p where a.colno=p.colno "
      sciQry += "and varname='C' order by value desc"
      sciArray = utilDb.db2Array(sciCur,sciQry,dim=1)
      sciArray = sciArray*sciFac
      print 'SCICHEM max = ',sciArray[0],sciArray[25]  
    
    # plot the arrays
    figName = prjName + str(iHr) +'.png'
    figTitle = '%s: Max Concentration for %02d Hr Average Concentrations'%(prjName.upper(),iHr)
    plotData(obsArray, aerArray, sciArray, figName, figTitle)
    
    obsRHC = measure.rhc(obsArray)
    sciRHC = measure.rhc(sciArray)
    aerRHC = measure.rhc(aerArray)
    print aerRHC/obsRHC,sciRHC/obsRHC
    #calcStats(obsMax1Hr,pre1Max1Hr,statFile)
  
    if statFile is not None:
      # Case, Dur, maxObs, maxAER, maxSCI, RHC_AER, RHC_SCI
      statFile.write("%s, %02d hr, %10.3f, %10.3f, %10.3f, %6.3f, %6.3f\n"%\
                    (prjName,iHr,obsArray[0],aerArray[0],sciArray[0],aerRHC/obsRHC,sciRHC/obsRHC))

  '''
  # Full period
  preQry  = "select avg(value)from samTable a, smptable p where a.colno=p.colno and varname='C' and smpId = "
  pre1MaxPerHr = np.zeros(nSmp)
  for j,smpId in enumerate(smpIds):
    preQry1 = preQry + str(smpId) + ' group by smpId'
    print preQry1
    hrMaxPer  =  utilDb.db2Array(preCur1,preQry1)
    print hrMaxPer
    if (hrMaxPer > pre1MaxPerHr[j]):
        pre1MaxPerHr[j] = hrMaxPer
    
  pre1MaxPerHr = pre1MaxPerHr*pre2Fac
  
  print 'pre1MaxPerHr = ',hrMaxPer
  print 'Max val for Period = ', max(pre1MaxPerHr)

  if statFile is not None:
    statFile.write("%s, %s"%(prjName, 'Max'))
  calcStats(MaxObs,MaxPre1,statFile)
  
  title = '%s: Maximum of Time Averaged Concentration'%prjName.upper()
  pltName = prjName + '_Max.png'
  plotBarGraph(MaxObs,MaxPre1,MaxPre2,title,pltName,yMax,MaxVals)
  
  
  #sys.exit()
  
  preConn1.close()
  preConn2.close()
  '''
  print '**Done :-)'
  
def plotData(obsArray, aerArray, sciArray, figName, figTitle, cutoff=0.0):
  minLen = min(len(obsArray),len(aerArray),len(sciArray))
  aerArray = aerArray[:minLen][obsArray[:minLen] > cutoff]
  sciArray = sciArray[:minLen][obsArray[:minLen] > cutoff]
  obsArray = obsArray[:minLen][obsArray[:minLen] > cutoff] 
  maxVal = max(max(obsArray),max(aerArray),max(sciArray))
  plt.clf()
  plt.hold(True)
  LSCI = plt.scatter(obsArray,sciArray,marker='o',color='r')
  LAER = plt.scatter(obsArray,aerArray,marker='d',color='b')
  plt.xlim(0,maxVal)
  plt.ylim(0,maxVal)
  plt.plot([0,maxVal],[0,maxVal],'k-')
  plt.plot([0,maxVal],[0,maxVal*0.5],'r-')
  plt.plot([0,maxVal],[0,maxVal*2],'r-')
  plt.xlabel(r'Observed ($\mu g/m^3$)')
  plt.ylabel(r'Predicted ($\mu g/m^3$)')
  plt.hold(False)
  plt.title(figTitle)
  plt.legend([LSCI,LAER],['SCICHEM', 'AERMOD'])
  plt.savefig(figName)   
  return
              
# Main program
if __name__ == '__main__':
  
  for prjName in ['baldwin','bowline','kinso2','CLIFTY','martin','tracy']:
    runProg(prjName)
