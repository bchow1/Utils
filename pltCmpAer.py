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

def getObsArray(prjName,obsDir=None,obsName=None,iHr=1):
  
  if obsName is None:
    obsNameList = {'kinso2':'kinso2','kinsf6':'KINSF6.SUM','bowline':'bow','clifty':'CCR75'}
    obsNameList.update({'baldwin':'bal','martin':'MCR','tracy':'TRACY','pgrass':'PGRSF6.SUM'})
    obsName = obsNameList[prjName]  
  if obsDir is None:
    obsDir = os.path.join('..','Obs_Conc')
  # Read observations from obs directory from .obs files
  if prjName == 'pgrass':
    obsFile = os.path.join(obsDir,obsName)
    colList = (i for i in range(5,7))
    QCArray    = np.loadtxt(obsFile,skiprows=4,usecols=colList)
    obsArray   = QCArray[:,0]*QCArray[:,1]*1.e6 # ug/m3
    print np.shape(obsArray)
  elif prjName.startswith('KSF6'):
    obsFile = os.path.join(obsDir,obsName+'.db')
    YY = prjName[9:11]
    MM = prjName[5:6]
    DD = prjName[6:8]
    qryStr  = 'select max(CHI) from dataTable where YY = %s and MM = %s and DD = %s group by HH'%(YY,MM,DD)
    obsArray = utilDb.db2Array(obsFile,qryStr,dim=1)
    obsArray = obsArray/167.  # Convert from ppt to ug/m3 for SF6
  else:
    obsFile    = os.path.join(obsDir,obsName + '%02d.obs'%iHr)
    obsHrArray = np.loadtxt(obsFile)
    nHr        = len(obsHrArray)
    obsArray   = np.zeros(nHr) - 999.
    for hr in range(nHr):
      obsArray[hr] = max(obsHrArray[hr,4:])
  obsArray  = np.sort(obsArray)[::-1]
  print 'OBS max =', obsArray[0],obsArray[25]
  #for iSmp in range(nSmp):
  #  obsArray[:,iSmp] = np.sort(obsArray[:,iSmp])[::-1]
  #  print 'OBS max =', obsArray[0,iSmp],obsArray[25,iSmp]
  return obsArray

def getAerArray(prjName,aerDir=None,aerName=None,iHr=1):
  
  if aerName is None:
    aerNameList = {'kinso2':'KS2AER','kinsf6':None,'bowline':'BOWAER','clifty':'CCRAER'}
    aerNameList.update({'baldwin':'BALAER','martin':'MCRAT2','tracy':'TRAER','pgrass':'PGRASS'})
    aerName = aerNameList[prjName]  
    
  if aerDir is None:
    aerDir = os.path.join('..','Aermod')
 
  if prjName.startswith('KSF6'):
    aerName = os.path.join(aerDir,prjName).replace('I','R').replace('_','.')
    useCols = [i for i in range(8)]
    aerConc = np.loadtxt(aerName,skiprows=8,usecols=useCols)
    aerArray = aerConc[:,1]
    aerArray = np.sort(aerArray)[::-1]
  else:
    aerFile = os.path.join(aerDir,aerName + '%02d.PST.db'%iHr)
    aerConn = sqlite3.connect(aerFile)
    aerConn.row_factory = sqlite3.Row
    aerCur = aerConn.cursor()    
    #aerQry = 'select Cavg from datatable order by Cavg desc'
    # Remove duplicate data period similar to RANK-FILE
    aerQry = 'select max(Cavg) as cMax from datatable group by date order by cMax desc'
    aerArray = utilDb.db2Array(aerCur,aerQry,dim=1)
    print 'AERMOD max =', aerArray[0],aerArray[25]
    aerConn.close()
  
  return aerArray

def getSmpDb(prjName):
  mySciFiles = SCI.Files(prjName)
  smpDb = '%s.smp.db'%(prjName)
  (smpDbConn,smpDbCur,smpCreateDb) = utilDb.Smp2Db(smpDb,mySciFiles)
  return (smpDbConn,smpDbCur)

def countSmpDb(smpDbCur):
  smpIds = map(int,utilDb.db2Array(smpDbCur,'select distinct(smpid) from samTable'))
  nSmp   = len(smpIds)
  nTimes = utilDb.db2Array(smpDbCur,"select count(value) from samTable a, smptable p where a.colno=p.colno \
                          and varname='C' and smpId =1",dim=0)
  print 'nSmp,nTimes = ',nSmp,nTimes
  return (nTimes,nSmp,smpIds)

def smpDbMax(smpDbCur,iHr,smpFac,smpIds=None,nTimes=None):
  
  if nTimes is None:
    (nTimes,nSmp,smpIds) = countSmpDb(smpDbCur)
  else:
    nSmp = len(smpIds)
    
  if iHr > 1:
    preQry  = "select value from samTable a, smptable p where a.colno=p.colno "
    preQry += "and varname='C' and smpId ="
    sciMax  = np.zeros((nSmp,nTimes/iHr),float)
    for j,smpId in enumerate(smpIds):
      sciQry = preQry + str(smpId) + ' order by time'
      hrMax  =  utilDb.db2Array(smpDbCur,sciQry)
      # avgArray[j,:] = np.convolve(hrMax, np.ones(iHr)/iHr)
      for i in range(0,len(hrMax)-iHr+1,iHr):
        sciMax[j,i/iHr] = np.mean(hrMax[i:i+iHr])    
    sciMax   = np.reshape(sciMax,np.size(sciMax))  
    sciArray = np.sort(sciMax)[::-1]
  else:
    sciQry  = "select max(value) as maxVal from samTable a, smptable p where a.colno=p.colno "
    sciQry += "and varname='C' and (time -round(time)) = 0. group by time order by maxVal desc"
    sciArray = utilDb.db2Array(smpDbCur,sciQry,dim=1)
  sciArray = sciArray*smpFac
  print 'SCICHEM max = 1:',sciArray[0],', ',len(sciArray),':',sciArray[-1]
  
  return sciArray

# Code for SCICHEM 2012 plots
def runProg(prjName):
 
  if compName == 'sm-bnc':
    os.chdir('D:\\Aermod\\v12345\\runs\\' + prjName + '\\SCICHEM')
  if compName == 'sage-d600':
    os.chdir('D:\\SCICHEM-2012\\AermodTestCases\\' + prjName + '\\SCICHEM')

  print 'RunDir = ',os.getcwd()
  sciFac = 1.e+9 # kg/m3 to microg/m3
  MaxVals = ['1 hr', '3hr', '24hr', 'All']
  MaxObs  = [0,0,0,0]  # OBS
  MaxPre1 = [0,0,0,0]  # SCICHEM-2012
  MaxPre2 = [0,0,0,0]  # AERMOD
  
  if prjName == 'kinso2':
    sciName = 'kinso2'
    yMax = 2500
  if prjName == 'kinsf6':
    sciName = 'KSF6-420_80I'
    yMax = 2500
  if prjName == 'bowline':
    sciName = 'bowline'
    yMax = 850
  if prjName == 'baldwin':
    sciName = 'Baldwin'
    yMax = 3100
  if prjName == 'CLIFTY':
    sciName = 'CLIFTY75'
  if prjName == 'martin':
    sciName = 'MCR_AER'
  if prjName == 'tracy':
    sciName = 'TRACAER'
  if prjName == 'pgrass':
    sciName = 'PGRASS' 
  
  statFile = open(prjName+"_stat.csv","w")
  statFile.write("Case, Dur, maxObs, maxAER, maxSCI, RHC_AER, RHC_SCI\n")

  # SCICHEM predictions
  sciConn,sciCur       = getSmpDb(sciName)
  (nTimes,nSmp,smpIds) = countSmpDb(sciCur)
  
  for iHr in [1,3,24]:
    
    if iHr > 1 and (prjName == 'tracy' or prjName == 'PGRASS'):
      continue
    
    # Read observations from obs directory from .obs files
    obsArray = getObsArray(prjName,iHr=iHr)
    
    # Get AERMOD max concentration array
    aerArray = getAerArray(prjName,iHr=iHr)

    # Get SCIPUFF max concentration array
    sciArray = smpDbMax(sciCur,iHr,sciFac,smpIds=smpIds,nTimes=nTimes)
    
    # plot the arrays
    figName = prjName + str(iHr) +'_2.png'
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
  
def plotData(obsArray, aerArray, sciArray, figName, figTitle, cutoff=0.0, units=None):
  minLen = min(len(obsArray),len(aerArray),len(sciArray))
  aerArray = aerArray[:minLen][obsArray[:minLen] > cutoff]
  sciArray = sciArray[:minLen][obsArray[:minLen] > cutoff]
  obsArray = obsArray[:minLen][obsArray[:minLen] > cutoff] 
  maxVal = max(max(obsArray),max(aerArray),max(sciArray))
  plt.clf()
  plt.hold(True)
  ax = plt.subplot(111)
  LSCI = plt.scatter(obsArray,sciArray,marker='o',color='r')
  LAER = plt.scatter(obsArray,aerArray,marker='d',color='b')
  plt.xlim(0,maxVal)
  plt.ylim(0,maxVal)
  plt.plot([0,maxVal],[0,maxVal],'k-')
  plt.plot([0,maxVal],[0,maxVal*0.5],'r-')
  plt.plot([0,maxVal],[0,maxVal*2],'r-')
  if units is None:
    units = r'($\mu g/m^3$)'
  plt.xlabel(r'Observed('  + units + ')')
  plt.ylabel(r'Predicted(' + units + ')')
  #ax.set_xscale('log')
  #ax.set_yscale('log')
  plt.hold(False)
  plt.title(figTitle)
  plt.legend([LSCI,LAER],['SCICHEM', 'AERMOD'],loc='upper left')
  plt.savefig(figName)   
  return
              
# Main program
if __name__ == '__main__':
  
  for prjName in ['kinso2']: #['pgrass','baldwin','bowline','kinso2','CLIFTY','martin','tracy']:
    runProg(prjName)
