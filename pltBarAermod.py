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
def mainProg():

  #prjName = 'baldwin'
  #prjName = 'bowline'
  prjName = 'kinso2'
  #prjName = 'CLIFTY'
  
  if compName == 'sm-bnc':
    os.chdir('d:\\Aermod\\v12345\\runs\\' + prjName + '\\SCICHEM')
  if compName == 'sage-d600':
    os.chdir('D:\\SCICHEM-2012\\AermodTestCases\\' + prjName + '\\SCICHEM')

  pre2Fac = 1.e+9
  MaxVals = ['1 hr', '3hr', '24hr', 'All']
  MaxObs  = [0,0,0,0]  # OBS
  MaxPre1 = [0,0,0,0]  # SCICHEM-2012
  MaxPre2 = [0,0,0,0]  # AERMOD
  
  print os.getcwd()
  if prjName == 'kinso2':
    #prePrj1 = os.path.join('..','fromSS','scipuff_prj')
    prePrj2 = 'kinso2'
    obs1HrFile  = 'kinso201.obs'
    obs3HrFile  = 'kinso203.obs'
    obs24HrFile = 'kinso224.obs'
    pre2_1HrFile = 'KS2AER01.PST.db'
    pre2_3HrFile = 'KS2AER03.PST.db'
    pre2_24HrFile = 'KS2AER24.PST.db'
    
    MaxPre2 = [1489.92, 1157.56, 241.85, 4.26] 
    MaxObs[3]= 14.54
    yMax = 2500
  if prjName == 'bowline':
    prePrj2 = 'bowline'
    obs1HrFile  = 'bow01.obs'
    obs3HrFile  = 'bow03.obs'
    obs24HrFile = 'bow24.obs'
     
    
    pre2_1HrFile  = 'BOWAER01.PST.db'
    pre2_3HrFile  = 'BOWAER03.PST.db'
    pre2_4HrFile  = 'BOWAER24.PST.db'
    MaxPre2 = [511.55, 467.66, 289.50, 20.22] # From SS spread sheet
    MaxObs[3]= 14.23
    yMax = 850
  if prjName == 'baldwin':
    #prePrj1 = os.path.join('..','fromSS','scipuff_prj')
    prePrj2 = 'baldwin'
    obs1HrFile  = 'bal01.obs'
    obs3HrFile  = 'bal03.obs'
    obs24HrFile = 'bal24.obs'
    MaxPre2 = [2997.35, 2261.82, 327.92, 12.17] # From SS spread sheet
    MaxObs[3]= 12.6
    yMax = 3100
  if prjName == 'CLIFTY':
     prePrj2 = 'CLIFTY'
     pre2_1HrFile  = 'CCRAER01.PST.db'
     pre2_3HrFile  = 'CCRAER03.PST.db'
     pre2_4HrFile = 'CCRAER024.PST.db'
  
  obsDir = os.path.join('..','Obs_Conc')
  statFile = open(prjName+"_stat.csv","w")
  statFile.write("Case, Maxhr, Fac1, Fac5, upa \n")

  # Predicted data set 1
  preConn1,preCur1 = getSmpDb(prjName)

  # Predicted data set 2
  preConn2,preCur2 = getSmpDb(prePrj2)
    
  smpIds = map(int,utilDb.db2Array(preCur1,'select distinct(smpid) from samTable'))
  nSmp   = len(smpIds)
  print nSmp
   
  #print smpIds
  for i in range(0,1):
    print i
    pre2Dir = os.path.join('..','AERMOD')
    print pre2Dir
    pre2DbName = pre2Dir +'\\'+ pre2_1HrFile #+ '.csv.db'  
         
    print 'pre2_DB', pre2DbName
    pre2Conn = sqlite3.connect(pre2DbName)
    pre2Conn.row_factory = sqlite3.Row
    pre2Cur = pre2Conn.cursor()
    print pre2Cur
    
    #pre2Qry = 'select max(Cavg) from dataTable group by Date order by max(Cavg) desc limit 26'
    pre2Qry = 'select max(Cavg) maxConc,x, y from dataTable group by x,y order by maxConc desc'
    print pre2Qry
    pre2Array = utilDb.db2Array(pre2Cur,pre2Qry)
    print pre2Array
    pre2Max1Hr = pre2Array[:,0]
    print 'AermodMax', pre2Max1Hr
    
    preQry  = "select max(value) from samTable a, smptable p where a.colno=p.colno "
    preQry += "and varname='C' and smpId ="
  
    pre1Max1Hr = []
    for smpId in smpIds:
      preQry1 = preQry + str(smpId)
      pre1Max1Hr.append(utilDb.db2Array(preCur1,preQry1)[0][0]*pre2Fac)
    print 'pre1Max1Hr = ',pre1Max1Hr
    
  # Obs data 
  
  obs1Hr = np.loadtxt(os.path.join(obsDir,obs1HrFile))[:,-nSmp:]
  obs3Hr = np.loadtxt(os.path.join(obsDir,obs3HrFile))[:,-nSmp:]
  obs24Hr = np.loadtxt(os.path.join(obsDir,obs24HrFile))[:,-nSmp:]
  obsMax1Hr = []
  obsMax3Hr = []
  obsMax24Hr = []
  for Id in range(nSmp):
    obsMax1Hr.append(obs1Hr[:,Id].max())
    obsMax3Hr.append(obs3Hr[:,Id].max())
    obsMax24Hr.append(obs24Hr[:,Id].max())
  print 'obsMax1Hr = ',obsMax1Hr
  
  if statFile is not None:
      statFile.write("%s, %s"%(prjName, '1 hr'))
  #calcStats(obsMax1Hr,pre1Max1Hr,statFile)
  
  pre2Max1Hr = []
  for smpId in smpIds:
    preQry2 = preQry + str(smpId)
    pre2Max1Hr.append(utilDb.db2Array(preCur2,preQry2)[0][0]*pre2Fac)
    #pre2Max1Hr = [511.55,230.86,499.87,67.85]

    print preQry2," = ",utilDb.db2Array(preCur2,preQry2)[0][0]*pre2Fac
  print 'pre2Max1Hr = ',pre2Max1Hr

  title = '%s: 1 Hr Max for Receptors'%prjName.upper()
  pltName = prjName + '_1hrMax.png'
  plotBarGraph(obsMax1Hr,pre1Max1Hr,pre2Max1Hr,title,pltName)
  
  '''
  ######## 3 Hour Max ###############
  print 'obsMax3Hr = ',obsMax3Hr

  preQry  = "select value from samTable a, smptable p where a.colno=p.colno "
  preQry += "and varname='C' and smpId ="

  pre1Max3Hr = np.zeros(nSmp)
  for j,smpId in enumerate(smpIds):
    preQry1 = preQry + str(smpId) + ' order by time'
    hrMax3  =  utilDb.db2Array(preCur1,preQry1)
    for i in range(0,len(hrMax3)-2,3):
      curVal =  np.mean(hrMax3[i:i+3])         
      if (curVal > pre1Max3Hr[j]):
        pre1Max3Hr[j] = curVal
  pre1Max3Hr = pre1Max3Hr*pre2Fac
  print 'pre1Max3Hr = ',pre1Max3Hr
  if statFile is not None:
    statFile.write("%s, %s"%(prjName, '3 hr'))
  calcStats(obsMax3Hr,pre1Max3Hr,statFile)
  '''
  '''
  pre2Max3Hr = np.zeros(nSmp)
  for j,smpId in enumerate(smpIds):
    preQry2 = preQry + str(smpId) + ' order by time'
    hrMax3  =  utilDb.db2Array(preCur2,preQry2)
    for i in range(0,len(hrMax3)-2,3):
      curVal =  np.mean(hrMax3[i:i+3])         
      if (curVal > pre2Max3Hr[j]):
        pre2Max3Hr[j] = curVal
  pre2Max3Hr = pre2Max3Hr*pre2Fac
  print 'pre2Max3Hr = ',pre2Max3Hr

  title = '%s: 3 Hr Max for Receptors'%prjName.upper()
  pltName = prjName + '_3hrMax.png'
  plotBarGraph(obsMax3Hr,pre1Max3Hr,pre2Max3Hr,title,pltName,yMax=1000)
  print 'three hr max done'
  '''
  '''
   ######## 24 Hour Max ###############
  print 'obsMax24Hr = ',obsMax24Hr

  preQry  = "select value from samTable a, smptable p where a.colno=p.colno "
  preQry += "and varname='C' and smpId ="

  pre1Max24Hr = np.zeros(nSmp)
  for j,smpId in enumerate(smpIds):
    preQry1 = preQry + str(smpId) + ' order by time'
    hrMax24  =  utilDb.db2Array(preCur1,preQry1)
    for i in range(0,len(hrMax24)-2,3):
      curVal =  np.mean(hrMax24[i:i+24])         
      if (curVal > pre1Max24Hr[j]):
        pre1Max24Hr[j] = curVal
  pre1Max24Hr = pre1Max24Hr*pre2Fac
  print 'pre1Max24Hr = ',pre1Max24Hr
  print 'Max val for 24 hrs = ', max(pre1Max24Hr)
  if statFile is not None:
    statFile.write("%s, %s"%(prjName, '24 hr'))
  calcStats(obsMax24Hr,pre1Max24Hr,statFile)
  
  pre2Max24Hr = np.zeros(nSmp)
  for j,smpId in enumerate(smpIds):
    preQry2 = preQry + str(smpId) + ' order by time'
    hrMax24  =  utilDb.db2Array(preCur2,preQry2)
    for i in range(0,len(hrMax24)-2,3):
      curVal =  np.mean(hrMax24[i:i+24])         
      if (curVal > pre2Max24Hr[j]):
        pre2Max24Hr[j] = curVal
  pre2Max24Hr = pre2Max24Hr*pre2Fac
  print 'pre2Max24r = ',pre2Max24Hr
  print 'Max val for 24 hrs = ', max(pre2Max24Hr)

  title = '%s: 24 Hr Max for Receptors'%prjName.upper()
  pltName = prjName + '_24hrMax.png'
  plotBarGraph(obsMax24Hr,pre1Max24Hr,pre2Max24Hr,title,pltName,yMax=1000)
  print '24 hr max done'
  '''
  
  # Full period
  '''
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

  ## 1 hr Max
  MaxObs[0]  = max(obsMax1Hr)
  MaxPre1[0] = max(pre1Max1Hr)
  print '1Hr: Obs,Pre1,Pre2,rat1,rat2 = ',MaxObs[0],MaxPre1[0],MaxPre2[0],\
         MaxPre1[0]/MaxObs[0],MaxPre2[0]/MaxObs[0]
  #MaxPre2[0] = max(pre2Max1Hr)
  
  ## 3 hr Max
  MaxObs[1]  = max(obsMax3Hr)
  MaxPre1[1] = max(pre1Max3Hr)
  #MaxPre2[1] = max(pre2Max3Hr)
  print '3Hr: Obs,Pre1,Pre2,rat1,rat2 = ',MaxObs[1],MaxPre1[1],MaxPre2[1],\
         MaxPre1[1]/MaxObs[1],MaxPre2[1]/MaxObs[1] 
  ## 24 hr Max
  MaxObs[2]  = max(obsMax24Hr)
  MaxPre1[2] = max(pre1Max24Hr)
  #MaxPre2[2] = max(pre2Max24Hr)
  print '24Hr: Obs,Pre1,Pre2,rat1,rat2 = ',MaxObs[2],MaxPre1[2],MaxPre2[2],\
         MaxPre1[2]/MaxObs[2],MaxPre2[2]/MaxObs[2]
  
  ## Period Max
  
  MaxPre1[3] = max(pre1MaxPerHr)
  #MaxPre2[3] = max(max(pre2Max1Hr), max(pre2Max3Hr),max(pre2Max24Hr))
  print 'Period: Obs,Pre1,Pre2,rat1,rat2 = ',MaxObs[3],MaxPre1[3],MaxPre2[3],\
         MaxPre1[3]/MaxObs[3],MaxPre2[3]/MaxObs[3]
  
  print  MaxObs, MaxPre1 , MaxPre2
  
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
      
def calcStats(obsArray, preArray,statFile=None):
  print "In calcStats"
  obsArray = np.array(obsArray)
  preArray = np.array(preArray)
  print obsArray
  print preArray
  #print max(obsArray), max(preArray)
  upa =  measure.upa(preArray, obsArray)
  fac2 = measure.fac2(preArray, obsArray, cutoff=0.0)
  #pearCoeff = pearsonr(obsArray[:,1],preArray[:,1])
  #upa = measure.upa(obsArray, preArray)
  print "<--obsMean %%%%%%%%%% NMSE--> %%%%%%%%%%%% Pearson Coeff"
  print fac2, upa
  if statFile is not None:
    statFile.write(",  %8.3f, %8.3f\n"%(fac2, upa))

def plotBarGraph(obsArr, preArr1, preArr2, title, pltName,yMax=None, xTicLab=None, title2=None):
  
  params1 = {'axes.labelsize': 10, 'text.fontsize': 10,'text.family':'Helvetica' ,'xtick.labelsize': 8,
            'ytick.labelsize': 8, 'legend.pad': 0.1,  
            'legend.fontsize': 8, 'lines.markersize': 6, 'lines.width': 2.0,
            'font.size': 8, 'text.usetex': False}
  
  plt.rcParams.update(params1)
  
  print pltName
  N = len(preArr1)

  width = 0.25                # the width of the bars
  ind = np.arange(N) + width  # the x locations for the groups

  fig = plt.figure()
  ax = fig.add_subplot(111)
  
  """
  kwargs = {'hatch':'|'}
  rects2 = ax.bar(theta, day7, width,fill=False, align='edge', alpha=1, **kwargs)

  kwargs = {'hatch':'-'}
  rects1 = ax.bar(theta, day1, width,fill=False, align='edge', alpha=1, **kwargs)
  """
  
  kwargs = {'hatch':'|'}
  rectsO  = ax.bar(ind, obsArr, width, color='black',)
  rects1  = ax.bar(ind+width, preArr1, width, color='.75')  
  rects2  = ax.bar(ind+width*2, preArr2, width, color='.25')

  # add some
  ax.set_ylabel('Concentration(ug/m3)')
  if yMax is not None:
    ax.set_ylim([0,yMax])
  #ax.set_title(title)
  #ax.text(0.9,0.9,title,fontsize=10)
  #plt.text(50, -0.5, 'Cohort Size', horizontalalignment='center', size='small')
  plt.text(-.01,-0.07,title,transform=ax.transAxes,fontsize=10)
  if title2 is not None:
    plt.text(.10,-0.11,title2,transform=ax.transAxes,fontsize=10)

  ax.set_xticks(ind+width)
  if xTicLab is None:
    xTicLab = []
    xTicPos = []
    for i in range(N):
      xTicLab.append('R%d'%i )
      xTicPos.append(2.5*width + i*4.*width)
  #ax.set_xticklabels( xTicLab )
  else:
    xTicPos = []
    for i in range(len(xTicLab)):
      xTicPos.append(2.5*width + i*4.*width)
  plt.xticks(xTicPos,xTicLab)
 
  ax.legend( (rectsO[0],rects1[0],rects2[0]),( 'OBS','SCICHEM','AERMOD'),\
              loc=1)
  #bbox_to_anchor=(0.02,0.98),loc=2)
  lgnd  = plt.gca().get_legend()
  ltext = lgnd.get_texts()
  plt.setp(ltext,fontsize=9)
  
  def autolabel(rects):
      # attach some text labels
      for rect in rects:
          height = rect.get_height()
          ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                  ha='center', va='bottom')

  autolabel(rectsO[3:])
  autolabel(rects1[3:])
  autolabel(rects2[3:])

  plt.savefig(pltName,dpi=300)
  print 'Plotted %s in '%pltName,os.getcwd()
  #plt.show()
              
# Main program
if __name__ == '__main__':
  mainProg()
