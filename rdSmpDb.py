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
from utilDb import *
    
# function to create calculated db
def readSmpDb(prjNames,cScale):
     
  #samTable (colNo integer, varName string, smpID string, xSmp real, ySmp real, matName string)
  #smpTable (time real, EpTime real, colNo integer, value real)

  smpConn = []
  sCur = []
  for prjNo,prjName in enumerate(prjNames):
    print '\nProject :%s\n'%prjName
    dbName = prjName + '.smp.db'
    if not os.path.exists(dbName):
      createSmpDb([prjName,]) 
    smpConn.append(sqlite3.connect(dbName))
    smpConn[prjNo].row_factory = sqlite3.Row
    sCur.append(smpConn[prjNo].cursor())
    dbCur = sCur[prjNo]

    # Get domain min max
    xyArray = db2Array(dbCur,'SELECT DISTINCT xSmp,ySmp from samTable')
    nSmp = len(xyArray)
    print 'No. of samplers = ',nSmp
    (yMin,yMax) = (min(xyArray[:,0]),max(xyArray[:,0]))
    print 'yMin = ',yMin,', yMax = ',yMax
    (xMin,xMax) = (min(xyArray[:,1]),max(xyArray[:,1]))
    print 'xMin = ',xMin,', xMax = ',xMax

    # Get start and end times
    timeArray = db2Array(dbCur,'SELECT DISTINCT time,EpTime from smpTable')
    (timeMin,timeMax) = (min(timeArray[:,0]),max(timeArray[:,0]))
    dtCol = np.diff(timeArray[:,1])
    print 'tMin = ',timeMin,', tMax = ',timeMax,', dt = ',dtCol[0],'(s)'
    (epTimeMin,epTimeMax) = (min(timeArray[:,1]),max(timeArray[:,1]))
    print 'epTMin = ',epTimeMin,', epTMax = ',epTimeMax
    EpStartTime = epTimeMin - timeMin
    EpEndTime   = epTimeMax
    print '\nSampler start %s(%d)'%(time.ctime(EpStartTime),EpStartTime)
    print 'Sampler end %s(%d)'%(time.ctime(EpEndTime),EpEndTime)

    varNameList = db2List(dbCur,'SELECT DISTINCT varName from samTable')
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
    sys.exit()
  else:
    prjNames = opt.prjNames.split(':')
  readSmpDb(prjNames,cScale=opt.cScale)
