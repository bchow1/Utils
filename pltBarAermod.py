
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

  #os.chdir('d:\\SCICHEM-2012\\Baldwin')

  prjName = 'bowline'
  pre2Fac = 1.e+9
  
  if prjName == 'bowline':
    os.chdir('D:\\SCIPUFF\\runs\\EPRI\\aermod\\Bowline\\SCICHEM')
    preDbName1 = '..\\fromSS\\scipuff_prj.smp.db'
    preDbName2 = 'bowline.smp.db'
    obs1HrFile  = 'bow01.obs'
    obs3HrFile  = 'bow03.obs'
    obs24HrFile = 'bow24.obs'

  obsDir = os.path.join('..','Obs_Conc')

  # Predicted data set 1
  preConn1 = sqlite3.connect(preDbName1)
  preConn1.row_factory = sqlite3.Row
  preCur1 = preConn1.cursor()

  # Predicted data
  preConn2 = sqlite3.connect(preDbName2)
  preConn2.row_factory = sqlite3.Row
  preCur2 = preConn2.cursor()
    
  smpIds = map(int,utilDb.db2Array(preCur2,'select distinct(smpid) from samTable'))
  nSmp   = len(smpIds)
  #print smpIds

  # Obs data 
  obs1Hr = np.loadtxt(os.path.join(obsDir,obs1HrFile))[:,-nSmp:]
  obs3Hr = np.loadtxt(os.path.join(obsDir,obs3HrFile))[:,-nSmp:]
  obsMax1Hr = []
  obsMax3Hr = []
  for Id in range(nSmp):
    obsMax1Hr.append(obs1Hr[:,Id].max())
    obsMax3Hr.append(obs3Hr[:,Id].max())
  print obsMax1Hr

  preQry  = "select max(value) from samTable a, smptable p where a.colno=p.colno "
  preQry += "and varname='C' and smpId ="
  
  pre1Max1Hr = []
  for smpId in smpIds:
    preQry1 = preQry + str(smpId)
    pre1Max1Hr.append(utilDb.db2Array(preCur1,preQry1)[0][0]*pre2Fac)
  print pre1Max1Hr

  pre2Max1Hr = []
  for smpId in smpIds:
    preQry2 = preQry + str(smpId)
    pre2Max1Hr.append(utilDb.db2Array(preCur2,preQry2)[0][0]*pre2Fac)
  print pre2Max1Hr

  title = '%s: 1 Hr Max for Receptors'%prjName.upper()
  pltName = prjName + '_1hrMax.png'
  plotBarGraph(obsMax1Hr,pre1Max1Hr,pre2Max1Hr,title,pltName)

  ######## 3 Hour Max ###############
  print obsMax3Hr  

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
  print pre1Max3Hr
  
  pre2Max3Hr = np.zeros(nSmp)
  for j,smpId in enumerate(smpIds):
    preQry2 = preQry + str(smpId) + ' order by time'
    hrMax3  =  utilDb.db2Array(preCur2,preQry2)
    for i in range(0,len(hrMax3)-2,3):
      curVal =  np.mean(hrMax3[i:i+3])         
      if (curVal > pre2Max3Hr[j]):
        pre2Max3Hr[j] = curVal
  pre2Max3Hr = pre2Max3Hr*pre2Fac
  print pre2Max3Hr

  title = '%s: 3 Hr Max for Receptors'%prjName.upper()
  pltName = prjName + '_3hrMax.png'
  plotBarGraph(obsMax3Hr,pre1Max3Hr,pre2Max3Hr,title,pltName,yMax=1000)
  print 'three hr max done'
  
  #sys.exit()
  
  preConn1.close()
  preConn2.close()
      

def plotBarGraph(obsArr, preArr1, preArr2, title, pltName,yMax=None):
  
  N = len(preArr1)

  ind = np.arange(N)  # the x locations for the groups
  width = 0.25        # the width of the bars

  fig = plt.figure()
  ax = fig.add_subplot(111)

  rectsO  = ax.bar(ind, obsArr, width, color='r')
  rects1  = ax.bar(ind+width, preArr1, width, color='b')  
  rects2  = ax.bar(ind+width*2, preArr2, width, color='g')

  # add some
  ax.set_ylabel('Concentration(ug/m3)')
  if yMax is not None:
    ax.set_ylim([0,yMax])
  ax.set_title(title)
  ax.set_xticks(ind+width)
  xTicLab = []
  xTicPos = []
  for i in range(N):
    xTicLab.append('R%d'%i )
    xTicPos.append(1.5*width + i*4.*width)
  #ax.set_xticklabels( xTicLab )
  plt.xticks(xTicPos,xTicLab)
 
  ax.legend( (rectsO[0],rects1[0],rects2[0]),( 'OBS','SCIPUFF(2010)','SCICHEM-2012'),\
             bbox_to_anchor=(0.02,0.98),loc=2)
  lgnd  = plt.gca().get_legend()
  ltext = lgnd.get_texts()
  plt.setp(ltext,fontsize=9)
  
  def autolabel(rects):
      # attach some text labels
      for rect in rects:
          height = rect.get_height()
          ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                  ha='center', va='bottom')

  autolabel(rectsO)
  autolabel(rects1)
  autolabel(rects2)

  plt.savefig(pltName)
  #plt.show()
              
# Main program
if __name__ == '__main__':
  mainProg()
