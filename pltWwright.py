
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

def mainProg():
  db = [ "ww_dec_lso.smp.db",  "ww_dec_ynb.smp.db" , "ww_dec_ynb_rdc.smp.db","ww_dec_amd_rdc.smp.db" ]
  myprjName    = ["LSO",  "YNB" , "YNB_RDC", "AMD_RDC" ]
  figName     = [415, 584, 582]
  print len(db)
  for i in range(len(db)):
    print db[i], myprjName[i]
    prjName = myprjName[i]
    pre2DbName =  db[i]
    
        
    preConn2 = sqlite3.connect(pre2DbName)
    preConn2.row_factory = sqlite3.Row
    preCur2 = preConn2.cursor()
    print preConn2

    varNames = [ 'O3', 'NOx']

    for varName in varNames:
      print varName
      preQry1 = preQry2 = ''
      preArray1 = preArray2 = []
      plt.clf()
      if (varName == 'NOx'):
          print varName
          preQry1 = 'select time,Value from samTable a,smpTable p where a.colNo=p.colNo'
          preQry1 += " and varName in ('NO2' ) "
          preQry1 += " order by time"
          preArray1 = utilDb.db2Array(preCur2,preQry1)
          

          preQry2 = 'select time,Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo'
          preQry2 += " and varName in ('NO2', 'NO' ) "
          preQry2 += "  group by time"
          print preQry2
          print varName
          preArray2 = utilDb.db2Array(preCur2,preQry2)
          plt.plot(preArray2[:,0],preArray1[:,1]/preArray2[:,1],'gs')
          plt.ylabel('NO2/NOx ratio')
          print '1'
      if (varName == 'O3'):
          print varName
          preQry1 = 'select time,Value from samTable a,smpTable p where a.colNo=p.colNo'
          preQry1 += " and varName in ('O3' ) "
          preQry1 += " order by time"
          preArray1 = utilDb.db2Array(preCur2,preQry1)
          plt.plot(preArray1[:,0],preArray1[:,1],'gs')
          plt.ylabel('Ozone Concentration (ppm)')
          print '2'
      print '3'
      figName = myprjName[i] + varName
      figTitle = myprjName[i] + "   " + varName
      
      plt.xlabel('time')
      plt.title(figTitle)
      #plt.show()
      plt.savefig(figTitle)


          
def pltCmpConc(dist, varName, obsData, preData1, preData2, figTitle, figName):
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
  if dist < 21:
    plt.xlim([-20,20])
  else:
    plt.xlim([-50,50])
  if varName == 'O3':
    plt.ylim([0,0.1])
  plt.legend([LkO,LkP1,LkP2],bbox_to_anchor=(0.02,0.98),loc=2,borderaxespad=0.)
  lgnd  = plt.gca().get_legend()
  ltext = lgnd.get_texts()
  plt.setp(ltext,fontsize=9)
  fig.hold(False)
  plt.savefig(figName)
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

  
  runDir = 'D:\\SCICHEM-2012\\wwright' 
  os.chdir(runDir)

  print 'runDir = ',runDir

  mainProg()
  #mainProg(prjName=prjName1,obsPfx=obsPfx,preCur1=preCur1,preCur2=None,prePfx2=prePfx2)

  #preConn1.close()
  #preConn2.close()
