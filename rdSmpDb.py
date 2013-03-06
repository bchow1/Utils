#!/usr/bin/python
#
# Create a sqlite database name filename.smp.db from filename.smp 
# Usage: dbUtil.py -p prjName1[:prjName2...] [-a prj1.sam[:prj2.sam...]]
#
import os
import sys
import numpy as np
import sqlite3
import fileinput
import optparse
import time
import math
# User Local modules
import utilDb
    
def getNOy(prjName,tHr,zSmp):
# Function reads multicomponent sampler db
# and writes the value of NOy species at the
# max SO2 location at given Time and Height 
  print '\nProject :%s\n'%prjName
  dbName = prjName + '.smp.db'
  
  utilDb.createSmpDb([prjName,]) 
  smpConn = sqlite3.connect(dbName)
  smpConn.row_factory = sqlite3.Row
  dbCur = smpConn.cursor()
  
  # Find smpId for max SO2 value 
  selectStr  = 'select smpId, max(Value) maxVal from samTable a,smpTable p where a.colNo=p.colNo '
  selectStr += 'and varName in ( "SO2") and time = %10.3f and zSmp = %7.2f group by smpId '%(tHr,zSmp)
  selectStr += 'order by maxVal desc limit 1'
  smpId,maxSO2 = utilDb.db2List(dbCur,selectStr)[0]    
  print 'Maximum SO2 value = %g at smpId = %d for project %s at time %10.3f hr and height %7.2f '%\
         (maxSO2,int(smpId),prjName,tHr,zSmp)
  
  for varName in ['C','NO','NO2','NO3','N2O5','HNO3','HONO','PAN','NOx','NOy','OH'] :

    #print '\n',varName

    # Prediction query
    if varName == "NOx":
      qryStr  = 'select Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo '
      qryStr += 'and varName in ( "NO","NO2" ) '
      qryStr += 'and time=%10.3f and smpId=%d'%(tHr,smpId)
    elif varName == 'NOy':
      qryStr  = 'select Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo '
      qryStr += 'and varName in ( "NO","NO2","NO3","N2O5","HNO3","HONO","PAN" ) '
      qryStr += 'and time=%10.3f and smpId=%d'%(tHr,smpId)
    else:  
      qryStr  = 'select Value from samTable a,smpTable p where a.colNo=p.colNo '
      qryStr += 'and varName="%s" and time=%10.3f and smpId=%d'%(varName,tHr,smpId)
    #print qryStr
    maxVal = utilDb.db2Array(dbCur,qryStr,dim=0)
    print '%s   %13.5e   %8.3f'%(varName,maxVal,maxVal*100./maxSO2) 
      
    
# function to create calculated db
def readSmpDb(prjNames,cScale):
     
  #samTable (colNo integer, varName string, smpID string, xSmp real, ySmp real, matName string)
  #smpTable (time real, EpTime real, colNo integer, value real)

  smpConn = []
  sCur = []
  for prjNo,prjName in enumerate(prjNames):
    print '\nProject :%s\n'%prjName
    dbName = prjName + '.smp.db'
    utilDb.createSmpDb([prjName,]) 
    smpConn.append(sqlite3.connect(dbName))
    smpConn[prjNo].row_factory = sqlite3.Row
    sCur.append(smpConn[prjNo].cursor())
    dbCur = sCur[prjNo]

    # Get domain min max
    xyArray = utilDb.db2Array(dbCur,'SELECT DISTINCT xSmp,ySmp from samTable')
    nSmp = len(xyArray)
    print 'No. of samplers = ',nSmp
    (yMin,yMax) = (min(xyArray[:,0]),max(xyArray[:,0]))
    print 'yMin = ',yMin,', yMax = ',yMax
    (xMin,xMax) = (min(xyArray[:,1]),max(xyArray[:,1]))
    print 'xMin = ',xMin,', xMax = ',xMax

    # Get start and end times
    timeArray = utilDb.db2Array(dbCur,'SELECT DISTINCT time,EpTime from smpTable')
    (timeMin,timeMax) = (min(timeArray[:,0]),max(timeArray[:,0]))
    if len(timeArray) > 1:
      dtCol = np.diff(timeArray[:,1])
    else:
      dtCol = np.array([0])
    print 'tMin = ',timeMin,', tMax = ',timeMax,', dt = ',dtCol[0],'(s)'
    (epTimeMin,epTimeMax) = (min(timeArray[:,1]),max(timeArray[:,1]))
    print 'epTMin = ',epTimeMin,', epTMax = ',epTimeMax
    EpStartTime = epTimeMin - timeMin
    EpEndTime   = epTimeMax
    print '\nSampler start %s(%d)'%(time.ctime(EpStartTime),EpStartTime)
    print 'Sampler end %s(%d)'%(time.ctime(EpEndTime),EpEndTime)

    varNameList = utilDb.db2List(dbCur,'SELECT DISTINCT varName from samTable')
    vNames = []
    for vName in varNameList:
      vName = str(vName[0])
      vNames.append(vName)
    print '\nVariable names = ',vNames
      
    for vName in vNames:
      dbCur.execute('select max(value) from smpTable d,samTable c where d.colNo = c.colNo and varName=?',(vName,))
      if vName == 'C' or vName == 'D':
        vScale = cScale
      elif vName == 'V':
        vScale = cScale*cScale
      else:
        vScale = 1.
      print 'Max %s = %15.5e'%(vName,float(dbCur.fetchone()[0])*vScale)
  
    print '\n#  Var    Max            Avg          Dose'
    #for vName in vNames:
    for vName in ['C']:
      for iSmp in range(1,nSmp+1):
        dbCur.execute('select time,value from smpTable d,samTable a where d.colNo = a.colNo\
                       and smpID = ? and varName=?',(iSmp,vName))
        Rows = dbCur.fetchall()
        rSum = 0.
        for rNo,row in enumerate(Rows):
          if rNo == 0:
            dt = dtCol[0]
          else:
            dt = dtCol[rNo-1] 
          rSum += float(row[1])*dt
          print row[0],cScale*float(row[1]),dt,rSum*cScale
        print rSum*cScale
        dbCur.execute('select max(value),count(value),sum(value) from smpTable d,samTable a where d.colNo = a.colNo\
                       and smpID = ? and varName=?',(iSmp,vName))
        vMax,nSum,vSum = dbCur.fetchone() 
        if vName == 'C' or vName == 'D':
          vScale = cScale
        elif vName == 'V':
          vScale = cScale*cScale
        else:
          vScale = 1.
        print '%s     %s   %15.5e %15.5e %15.5e'%(str(iSmp),vName,vMax*vScale,vSum*vScale/float(nSum),vSum*vScale*dt)

  return

# Call main program
if __name__ == '__main__':
  # Parse arguments
  arg = optparse.OptionParser()
  arg.add_option("-p",action="store",type="string",dest="prjNames")
  arg.add_option("-s",action="store",type="float",dest="cScale")
  arg.set_defaults(prjNames=None,cScale=1.)
  opt,args = arg.parse_args()
  # Check arguments
  if not opt.prjNames:
    print 'Error: prjNames must be specified'
    print 'Usage: smp2db.py -p prjName1[:prjName2...]'
    #sys.exit()
    # Inputs for getNOy
    runDir = 'v:\\scipuff\\Repository\\export\\EPRI\\archives\\runs\\JAWMA-2012\\tva\\tva_990706'
    os.chdir(runDir)#('d:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\runs\\JAWMA_CMAS_2012\\tva\\tva_980826')
    prjNames = []
    tHrs     = []
    zSmps    = []
    #
    prjNames.append('SCICHEM-2012\\tva_990706')
    tHrs.append(16.0)
    zSmps.append(448.0)
    #
    '''
    prjNames.append('SCICHEM-ROME\\070699_vo3')
    tHrs.append(16.0)
    zSmps.append(500.0)
    #
    prjNames.append('SCICHEM-99\\tva_990706_romebg_fixed')
    tHrs.append(16.0)
    zSmps.append(500.0)
    '''
    #Loop
    for prjNo,prjName in enumerate(prjNames):
      getNOy(prjName,tHrs[prjNo],zSmps[prjNo])
  else:
    prjNames = opt.prjNames.split(':')
  #readSmpDb(prjNames,cScale=opt.cScale)
 
