
#!/bin/env python
import os
import sys
import socket
import numpy as np
import numpy.ma as ma
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

# Code for SCICHEM 2012 plots
def pltCmpConc(dist, varName, preData1,figTitle, figName):
    # Set up plot parameters
    params1 = {'axes.labelsize': 10, 'text.fontsize': 10, 'xtick.labelsize': 10,
                  'ytick.labelsize': 10, 'legend.pad': 0.1,  
                  'legend.fontsize': 8, 'lines.markersize': 6, 'lines.width': 2.0,
                  'font.size': 10, 'text.usetex': False}
    plt.rcParams.update(params1)
    
    fig = plt.figure()
    plt.clf()
    fig.hold(True)
    ax = fig.add_subplot(111)
    #print obsData[:,1]
    if varName == 'O3':
      c1 = max(preData1[-1,1],preData1[0,1])
    else:
      c1 = min(preData1[-1,1],preData1[0,1])
    C = ma.masked_where(preData1[:,1]<0.,preData1[:,1]) # - c1
    plt.plot(preData1[:,0],C,linestyle='-',color='0.5',marker='s',markersize=6,markerfacecolor='0.5')
    plt.ylabel('Perturbation Concentration (ppm)')
    plt.xlabel('Cross plume distance (km)')
    plt.title(figTitle)
    if dist < 21:
      plt.xlim([-20,20])
    else:
      plt.xlim([-50,50])
    #if varName == 'O3':
    #  plt.ylim([0,0.1])
    fig.hold(False)
    plt.savefig(figName)
    return

def mainProg(prjName=None,preCur1=None):

  if prjName is None:
    print "Must provide project name"
    return
  else:
    print 'prjName = ',prjName
  
  varNames = ["SO2", "O3", "NOx",  "NOy"] #["SO2", "O3", "NOx",  "NOy"]

  dist = 106.
  tSmp = 17.
  zSmp = 587.
  
  lArc = 2.*dist*np.pi/180.
  
  for varName in varNames:

    print '\n',dist,' km, ',varName

    # Prediction query
    if varName == "NOx":
      preQry1 = 'select xSmp,Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo'
      preQry1 += " and varName in ('NO2', 'NO' ) "
      preQry1 += " and zSmp = %f and time = %3f group by smpId"%(zSmp,tSmp)
    elif varName == 'NOy':
      preQry1 = "select xSmp,Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo"
      preQry1 += " and varName in ('NO2','NO','NO3','N2O5','HNO3','HONO','PAN'  ) "
      preQry1 += " and zSmp = %f and time = %3f group by smpId"%(zSmp,tSmp)
    else:  
      preQry1  = "select xSmp,Value from samTable a,smpTable p where a.colNo=p.colNo and "
      preQry1 += "varName = '%s' and zSmp = %f and time = %3f order by smpId"%(varName,zSmp,tSmp)      
    print preCur1, preQry1
    
    # Predictions #1 (2012)
    preArray1 = utilDb.db2Array(preCur1,preQry1)
    if varName == 'SO2':
      # Set x index where SO2 is max. Same for all obs plumes
      iMax1 = np.where(preArray1[:,1] == preArray1[:,1].max())[0][0]
      
    # Align the prediction1 and observed centerlines
    for i in range(len(preArray1)):
      # Set x values at iMax1(index where SO2 is max) to 0 for plume ipl. 
      preArray1[i,0] = float(i-iMax1)*lArc 
      if i == iMax1:
        print 'Adjusted preArray1 x,c = ',preArray1[i,:] 
         
    # Plot
    figName  = str(dist) +'km_' +varName +'_'+ str(tSmp) + 'hr' + '.png'
    figTitle = '%s (@ %d km)'%(varName,dist)
    print figName
    pltCmpConc(dist, varName, preArray1, figTitle, figName)
             
  return
            
# Main program
if __name__ == '__main__':

  if compName == 'sm-bnc':
    runDir = 'd:\\scipuff\\EPRIx\\SCICHEM-2012\\runs\\tva\\tva_990715'
  if compName == 'pj-linux4':
    runDir = '/home/user/bnc/scipuff/EPRI_121001/runs/tva'
  if compName == 'sage-d600':
    runDir = 'D:\\SCICHEM-2012' 

  prjName = 'tva_990715_wdep'

  #runDir = os.path.join(runDir,prjName)
  os.chdir(runDir)
  print 'runDir = ',runDir

  # Predicted SCICHEM-2012 data
  dbName = prjName + '.smp.db'
  print prjName,dbName
  preConn1 = sqlite3.connect(dbName)
  preConn1.row_factory = sqlite3.Row
  preCur1 = preConn1.cursor()
  
  mainProg(prjName=prjName,preCur1=preCur1)
  preConn1.close()

