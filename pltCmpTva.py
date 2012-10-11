
#!/bin/env python
import os
import sys
import socket
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3

compName = socket.gethostname()

# Local modules
if compName == 'sm-bnc' or compName == 'sage-d600':
  sys.path.append('C:\\cygwin\\home\\sid\\python')
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')
  
import utilDb
import setSCIparams as SCI

# Code for SCICHEM 2012 plots

def mainProg(prjName=None,obsPfx=None,preCur1=None,preCur2=None,prePfx2=None):

  if prjName is None:
    print "Must provide project name"
    return
  else:
   print 'prjName = ',prjName
  
  varNames = ["SO2", "O3", "NOx",  "NOy"] #["SO2", "O3", "NOx",  "NOy"]

  if "tva_990715" in prjName:
    distance = [16, 62, 106]
    times    = [11.5, 12.5, 17.0]
    zSmp     = [415, 584, 582]

  if "tva_980825" in prjName:
    distance = [20, 55, 110]
    times    = [12, 12.75, 14.5]
    zSmp     = [520, 600, 620]
    
  if "tva_980826" in prjName:
    distance = [18, 27, 86, 59, 93, 126]
    times    = [10.25, 10.5, 12, 12.5, 12.75, 13]
    zSmp     = [465, 500, 659, 910, 819, 662]   
  
  for idt,dist in enumerate(distance): 

    if preCur2 is None:
      if prePfx2 is None:
        print "Must provide prefix for SCICHEM-01 prediction"
        return
      # Predictions SCICHEM-01
      pre2DbName =  prePfx2 + '_' + str(dist) + 'km' + '.csv.db'       
      print 'Predicted DB SCICHEM99', pre2DbName
      preConn2 = sqlite3.connect(pre2DbName)
      preConn2.row_factory = sqlite3.Row
      preCur2 = preConn2.cursor()
      print preConn2
    
    lArc = 2.*dist*np.pi/180.
   
    for varName in varNames:

      print '\n',dist,' km, ',varName

      # Prediction query
      if varName == "NOx":
        preQry1 = 'select xSmp,Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo'
        preQry1 += " and varName in ('NO2', 'NO' ) "
        preQry1 += " and zSmp = %f and time = %3f group by smpId"%(zSmp[idt],times[idt])
      elif varName == 'NOy':
        preQry1 = "select xSmp,Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo"
        preQry1 += " and varName in ('NO2','NO','NO3','N2O5','HNO3','HONO','PAN'  ) "
        preQry1 += " and zSmp = %f and time = %3f group by smpId"%(zSmp[idt],times[idt])
      else:  
        preQry1  = "select xSmp,Value from samTable a,smpTable p where a.colNo=p.colNo and "
        preQry1 += "varName = '%s' and zSmp = %f and time = %3f order by smpId"%(varName,zSmp[idt],times[idt])      
      print preCur1, preQry1
      
      # Predictions #1 (2012)
      preArray1 = utilDb.db2Array(preCur1,preQry1)
      if varName == 'SO2':
        # Set x index where SO2 is max. Same for all obs plumes
        iMax1 = np.where(preArray1[:,1] == preArray1[:,1].max())[0][0]
          
      # Predictions #2 (v2100)
      if prePfx2 is None:
        preArray2 = utilDb.db2Array(preCur2,preQry1)
      else:
        preQry2 = 'select dist, ' + varName + ' from dataTable'
        preArray2 = utilDb.db2Array(preCur2,preQry2)
        
      if varName == 'SO2':
        # Set x index where SO2 is max. Same for all obs plumes
        iMax2 = np.where(preArray2[:,1] == preArray2[:,1].max())[0][0]
          
      # Observed data
      if "tva_990715" in prjName:
        if dist == 16:
          pls = [1,2,3,4]
        if dist == 62:
          pls = [6,7,8]
        if dist == 106:
          pls = [9,10,11]

      if "tva_980825" in prjName:
        if dist == 20:
          pls = [3,4,5]
        if dist == 55:
          pls = [6] #[6,7,8]
        if dist == 110:
          pls = [9,10,11]
          
      if "tva_980826" in prjName:
        if dist == 18:
          pls = [1,2]
        if dist == 27:
          pls = [4,5,6]
        if dist == 86:
          pls = [8]
        if dist == 59:
          pls = [9] 
        if dist ==93:
          pls = [10]
        if dist == 126:
          pls = [11]    

      # Set Omax to zero for max plume no.
      if varName == 'SO2':
        oMax  = [0 for i in range(12)]
      
      for ipl in pls:
        
        obsDbName = obsPfx + str(dist) + 'km_obs' + str(ipl) + '.csv.db'
        print '\n obsDbName = ',obsDbName
      
        obsConn = sqlite3.connect(obsDbName)
        obsConn.row_factory = sqlite3.Row
        obsCur = obsConn.cursor()

        # Observations
        obsQry = 'select CAST(plumeKM as real), ' + varName + ' from dataTable'
        print obsQry
        
        obsArray = utilDb.db2Array(obsCur,obsQry)
        if varName == 'SO2':
          oMax[ipl] = np.where(obsArray[:,1] == obsArray[:,1].max())[0][0]
          print 'Max Obs SO2 at x index = ', oMax[ipl],' with x, value = ',obsArray[oMax[ipl],0],obsArray[oMax[ipl],1]


        print '\nFor varName %s, plume no. %d,x index = %d, x = %f ,conc = %f\n'%\
              (varName,ipl,oMax[ipl],obsArray[oMax[ipl],0],obsArray[oMax[ipl],1])
        
        # Align the prediction1 and observed centerlines
        for i in range(len(preArray1)):
          # Set x values where SO2 max to obs x value for plume ip1
          preArray1[i,0] = float(i-iMax1)*lArc + obsArray[oMax[ipl],0]
          if i == iMax1:
            print 'Adjusted preArray1 x,c = ',preArray1[i,:] 
          

        # Align the prediction2 and observed centerlines

        for i in range(len(preArray2)):
          # Set x values where SO2 max to obs x value for plume ip1
          preArray2[i,0] = float(i-iMax2)*lArc + obsArray[oMax[ipl],0] 
          if i == iMax2:
            print 'Adjusted preArray2 x,c = ',preArray2[i,:]
           
        # Plot
        figName  = str(dist) +'km_' +varName +'_'+ str(times[idt]) + 'hr_obs' + str(ipl) + '.png'
        #figTitle = '%s (@ %d km for plume %d)'%(varName,dist,ipl)
        figTitle = '%s (@ %d km)'%(varName,dist)
        print figName

        pltCmpConc(dist, varName, obsArray, preArray1, preArray2, figTitle, figName)

        obsConn.close()
    if prePfx2 is not None:
      print 'preConn2 is still open'
      #preConn2.close()
          
  return
          
def pltCmpConc(dist, varName, obsData, preData1, preData2, figTitle, figName):
  #import pdb; pdb.set_trace()
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
    fac = 1
  else:
    fac = 1
  C = obsData[:,1] - fac*obsData[-1,1]
  LhO  = plt.plot(obsData[:,0],C,linestyle='-',marker='o',markersize=6,markerfacecolor='blue') 
  LkO  = 'OBS'
  C = ma.masked_where(preData1[:,1]<0.,preData1[:,1]) - fac*preData1[-1,1]
  LhP1 = plt.plot(preData1[:,0],C,linestyle='-',marker='s',markersize=6,markerfacecolor='green')
  LkP1 = 'SCICHEM-2012'
  C = ma.masked_where(preData2[:,1]<0.,preData2[:,1]) - fac*preData2[-1,1]
  LhP2 = plt.plot(preData2[:,0],C,linestyle='-',marker='d',markersize=6,markerfacecolor='red')
  LkP2 = 'SCICHEM-99'
  plt.ylabel('Concentration (ppm)')
  plt.xlabel('Cross plume distance (km)')
  plt.title(figTitle)
  if dist < 21:
    plt.xlim([-20,20])
  else:
    plt.xlim([-50,50])
  #if varName == 'O3':
  #  plt.ylim([0,0.1])
  plt.legend([LkO,LkP1,LkP2],bbox_to_anchor=(0.02,0.98),loc=2,borderaxespad=0.)
  lgnd  = plt.gca().get_legend()
  ltext = lgnd.get_texts()
  plt.setp(ltext,fontsize=9)
  fig.hold(False)
  plt.savefig(figName)
  #sys.exit()
  #plt.show()
  return

def getSmpDb(prjName):
    mySciFiles = SCI.Files(prjName)
    smpDb = '%s.smp.db'%(prjName)
    print '%%%%%%%%%%%%', smpDb
    # Create database for calculated data 
    ## print 'Create smpDb ',smpDb,' in ',os.getcwd()
    (smpDbConn,smpDbCur,smpCreateDb) = utilDb.Smp2Db(smpDb,mySciFiles)
    return (smpDbConn,smpDbCur)

            
# Main program
if __name__ == '__main__':

  if compName == 'sm-bnc':
    #runDir='d:\\SCIPUFF\\runs\\EPRI\\Nash99'
    #runDir='d:\\SCICHEM-2012\\TVA_990715'
    runDir = 'd:\\scipuff\\runs\EPRI\\tva_980825'
  if compName == 'pj-linux4':
    #runDir = '/home/user/bnc/scipuff/runs/EPRI/tva/tva_980825'
    runDir = '/home/user/bnc/scipuff/EPRI_121001/runs/tva/tva_980826'
  if compName == 'sage-d600':
    runDir = 'D:\\SCICHEM-2012\\TVA_980825' 
  os.chdir(runDir)

  print 'runDir = ',runDir

  # Observed data 
  #obsPfx = os.path.join('OBS','tva_071599_')
  obsPfx = os.path.join('OBS','cumb2_')
  print obsPfx

  # Predicted SCICHEM-2012 data
  prjName1 = os.path.join('SCICHEM-2012','tva_980826_10km')
  print '**********' , 
  prjName1
  preConn1,preCur1 = getSmpDb(prjName1)

  # Predicted SCICHEM-01 data
  #prjName2 = 'SCICHEM-01\\071599_vo3_lin_intel'
  #prjName2 = os.path.join('SCICHEM-01','TVA_082598')
  #print prjName2
  #preConn2,preCur2 = getSmpDb(prjName2)
  
  # Use prePfx2 + '_' + str(dist) + 'km' + '.csv.db'

  #prePfx2 = os.path.join('SCICHEM-01','TVA_082598')
  prePfx2 = os.path.join('SCICHEM-01','cumb2')
  
  mainProg(prjName=prjName1,obsPfx=obsPfx,preCur1=preCur1,preCur2=None,prePfx2=prePfx2)

  #preConn1.close()
  #preConn2.close()
