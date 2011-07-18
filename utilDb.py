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
# modules from $HOME/python 
import run_cmd
import setSCIparams as SCI

class prj():

  def __init__(self):
    self.xyArray  = np.zeros(2,float)
    self.sourceLoc    = np.array([-999.,-999.],dtype=float)
    self.timeArray    = np.zeros(1,float)
    self.EpStartTime  = 0.
    self.EpEndTime    = 0.
    self.createCaldb  = False

  def setDb(self,prjName,samFile=None):
    self.prjName  = prjName
    self.sciFiles = SCI.Files(self.prjName,mySCIpattern)
    if samFile:
      self.sciFiles.samFile = samFile
    self.calDb = '%s.db'%(self.sciFiles.smpFile)
    # Create database for calculated data 
    print 'Create smpDb ',self.calDb
    (self.sCur,self.createCaldb) = Smp2Db(self.calDb,self.sciFiles,mySCIpattern,self.createCaldb)
    return

global allPrj

allPrj = prj()

def createSmpDb(prjNames,samFiles=None):

  global mySCIpattern
 
  mySCIpattern = SCI.Pattern()
  
  print 'In dbUtil.createSmpDb, prjNames(must be a list) = ',prjNames
 
  # Set calculated data file and create database
  myPrj = [[] for i in range(len(prjNames))]
  for i in range(len(prjNames)):
    myPrj[i] = prj()
    myPrj[i].createCaldb = True
    if samFiles:
      myPrj[i].setDb(prjNames[i],samFile=samFiles[i])
    else:
      myPrj[i].setDb(prjNames[i])
    
  dbCur = myPrj[0].sCur

  # Get domain min max
  allPrj.xyArray = db2Array(dbCur,'SELECT DISTINCT xSmp,ySmp from samTable')
  (yMin,yMax) = (min(allPrj.xyArray[:,0]),max(allPrj.xyArray[:,0]))
  print 'yMin = ',yMin,', yMax = ',yMax
  (xMin,xMax) = (min(allPrj.xyArray[:,1]),max(allPrj.xyArray[:,1]))
  print 'xMin = ',xMin,', xMax = ',xMax

  # Get start and end times
  allPrj.timeArray = db2Array(dbCur,'SELECT DISTINCT time,EpTime from smpTable')
  (timeMin,timeMax) = (min(allPrj.timeArray[:,0]),max(allPrj.timeArray[:,0]))
  print 'tMin = ',timeMin,', tMax = ',timeMax
  (epTimeMin,epTimeMax) = (min(allPrj.timeArray[:,1]),max(allPrj.timeArray[:,1]))
  print 'epTMin = ',epTimeMin,', epTMax = ',epTimeMax
  allPrj.EpStartTime = epTimeMin - timeMin
  allPrj.EpEndTime   = epTimeMax
  print '\nSampler start %s(%d)'%(time.ctime(allPrj.EpStartTime),allPrj.EpStartTime)
  print 'Sampler end %s(%d)'%(time.ctime(allPrj.EpEndTime),allPrj.EpEndTime)

def db2Array(cur,selectStr,dim=None):
  if dim == 1:
    dbList = db2List(cur,selectStr)
    Array = []
    for v in dbList:
      Array.append(v[0]) 
    Array = np.array(Array)
  else:
    Array = np.array(db2List(cur,selectStr),dtype=float)
  return Array

def db2List(cur,selectStr):
  dbCur = None
  dbConn = None
  if isinstance(cur,sqlite3.Cursor):
    dbCur = cur
  else:
    if os.path.exists(cur):
      dbConn = sqlite3.connect(cur)
      dbCur = dbConn.cursor() 
    else:
      raise RuntimeError('Error: First argument not a cursor or db file')
  dbCur.execute(selectStr)
  Rows  = dbCur.fetchall()
  dbList = []
  for Row in Rows: 
    dbList.append(list(Row))
  if dbConn:
    dbConn.close() 
  return dbList

def getEpTime(*args):
  if len(args) == 1:
    timeString = args[0]
  else:
    (Yr,Mo,Day,tHr) = (args[0],args[1],args[2],args[3])
    timeString = '%04d%02d%02d'%(Yr,Mo,Day)
    if len(args) == 4:
      hms = run_cmd.hr2hms(tHr).replace(':','')
      timeString += hms 
    elif len(args) == 6:
      (Mn,Sec) = (args[4],args[5])
      timeString += '%02d%02d%02d'%(int(tHr),Mn,Sec)
  timeTuple = time.strptime(timeString,"%Y%m%d%H%M%S")
  epTime = time.mktime(timeTuple)
  return epTime

def getYMD(epTime):
  timeTuple = time.localtime(epTime)
  timeString = time.strftime('%Y %m %d %H %M %S',timeTuple)
  return (timeString.split())

def str2ymdhms(timeString):
  (Yr, Mo, Day) = map(int,(timeString[0:4],timeString[4:6],timeString[6:8]))
  (Hr, Mn, Sec) = map(int,(timeString[8:10],timeString[10:12],timeString[12:14]))
  return(Yr,Mo,Day,Hr,Mn,Sec)

def hpacSenHead(line,sCur):  
  tmpHead = line.split()[1:]
  vnames=[]
  for vname in tmpHead:
    if vname[-3:] != '001':
      break
    vnames.append(vname[:-3])
  nvar = len(vnames)
  print ('No. of variables = %d, Names = %s\n' % (nvar,vnames))
  return(len(tmpHead),vnames) 
 
# insert sam data in samTable for nDat samplers and variables in vnames
def createSam(nDat,vnames,sCur,smpLoc):
  nvar = len(vnames)
  i = 1
  while i < nDat: 
    for vname in vnames:
      insertStr = "INSERT into samTable VALUES"
      smpID = (i-1)/nvar+1
      (xSmp,ySmp) = map(float,(smpLoc[smpID-1][0:2]))
      insertStr = insertStr + "(%d, '%s', '%03d',%15.5f,%15.5f,'%s')"%(i,vname,smpID,xSmp,ySmp,smpLoc[smpID-1][3])
      sCur.execute(insertStr)
      i += 1 
  
# Create smpTable if required and add data for time break nt
def addData(line,nDat,sCur,nt,isReverse=1.):
  global allPrj
  print 'nt = ',nt
  if nt == 0:
    sCur.execute('DROP table if exists smpTable')
    createStr = 'CREATE table smpTable (time real, EpTime real, colNo integer, value real)'
    print createStr
    sCur.execute(createStr)    
  nt += 1
  tmpData = map(float,line.split())
  rtime = tmpData[0]
  #print 'Inserting into smpTable for time = ',rtime/3600.,' hr, max = ',max(tmpData[1:])
  initStr = "INSERT into smpTable VALUES (%13.5e, %16.5f, "%(rtime/3600.,allPrj.EpStartTime + isReverse*rtime)
  for i in range(1,nDat+1):
    insertStr = initStr + "%d, %13.5e)"%(i,tmpData[i])
    sCur.execute(insertStr)
    i += 1 
  return(nt)
    
# function to create calculated db
def Smp2Db(dbName,mySciFiles,mySCIpattern,createTable):
  global allPrj
  
  #print '\n In utilDb.Smp2Db: prjName = ',mySciFiles.prjName
  (nmlNames,nmlValues) = mySCIpattern.readNml(mySciFiles.inpFile)
  i = nmlNames.index('time1')
  startYr  = int(nmlValues[i]['year_start'])
  if startYr < 0: startYr = 1970
  startMon = int(nmlValues[i]['month_start'])
  if startMon < 0: startMon = 1
  startDay = int(nmlValues[i]['day_start'])
  if startDay < 0: startDay = 1
  startHr  = float(nmlValues[i]['tstart'])

  i = nmlNames.index('time2')
  endYr  = int(nmlValues[i]['year_end'])
  if endYr < 0: endYr = 1970
  endMon = int(nmlValues[i]['month_end'])
  if endMon < 0: endMon = 1
  endDay = int(nmlValues[i]['day_end'])
  if endDay < 0: endDay= 1
  endHr  = float(nmlValues[i]['tend'])
  runHr  = float(nmlValues[i]['tend_hr'])

  # Get run mode from inp file
  i = nmlNames.index('flags')
  runMode = int(nmlValues[i]['run_mode'])
  if runMode == 128:
    isReverse = -1
  else:
    isReverse = 1
  print '\n run mode = ',isReverse
  
  allPrj.EpStartTime = getEpTime(startYr,startMon,startDay,startHr)
  print 'Sampler start %02d/%02d/%02d %13.3f hr(%s)'%(startYr,startMon,startDay,startHr,allPrj.EpStartTime)
  
  if int(endHr) > 0. :
    allPrj.EpEndTime = getEpTime(endYr,endMon,endDay,endHr)
    print 'Sampler end from inp file %02d/%02d/%02d %13.3f hr(%s)'%(endYr,endMon,endDay,endHr,allPrj.EpEndTime)
    if abs((allPrj.EpEndTime - allPrj.EpStartTime)/3600. - runHr) > 1.e-6:
      print 'Warning: Runtime ',(allPrj.EpEndTime - allPrj.EpStartTime)/3600.,' does not match tend_hr = ',runHr
      allPrj.EpEndTime = allPrj.EpStartTime + isReverse*runHr*3600.
    elif isReverse < 0:
      allPrj.EpEndTime = 2.*allPrj.EpStartTime - allPrj.EpEndTime
  else:
    allPrj.EpEndTime = allPrj.EpStartTime + isReverse*runHr*3600.
  (endYr,endMon,endDay,endHr,endMn,endSec)  = getYMD(allPrj.EpEndTime)
  print 'Sampler end %s/%s/%s %s:%s:%s(%15.2f)'%(endYr,endMon,endDay,endHr,endMn,endSec,allPrj.EpEndTime)

  #
  (nmlNames,nmlValues) = mySCIpattern.readNml(mySciFiles.scnFile)
  i = nmlNames.index('scn')
  xrel  = float(nmlValues[i]['xrel'])
  yrel  = float(nmlValues[i]['yrel'])
  sourceLoc = np.array([xrel,yrel],dtype=float)
  if allPrj.sourceLoc[0] == -999. :
    allPrj.sourceLoc = sourceLoc
  print 'Source location = ',allPrj.sourceLoc
    
  # Create database for calculated data 
  if not createTable:
    if not os.path.exists(dbName):
      createTable =  True
  print 'Create smp data table = ',createTable,' in database file ',dbName
    
  smpConn = sqlite3.connect(dbName)
  smpConn.row_factory = sqlite3.Row
  sCur = smpConn.cursor()

  if createTable:
 
    # Read and save sampler locations
    smpLoc = []
    print 'From inp file samFile = ',mySciFiles.samFile
    if not mySciFiles.samFile:
      mySciFiles.samFile = raw_input('Enter name of samFile ')
    if len(mySciFiles.samFile) > 0:
      for line in fileinput.input( mySciFiles.samFile ):
        #print fileinput.lineno(),': ',line
        if fileinput.isfirstline():
          matchSen = mySCIpattern.pattSmpT.match(line)
          if not matchSen:
            matName = line.strip().split()[0]
        else:
          if len(line) < 3: break
          if matchSen:
            matName = line.split()[4].split(':')[0]
          tmpList = line.split()[0:3]
          tmpList.extend([matName])
          smpLoc.append(tmpList)
      fileinput.close()
      #print 'sampler locations and matName from samfile = ',smpLoc[0]
    else:
      print 'samFile must be defined. Try again'
      sys.exit()

    # Read sampler output data
    sCur.execute('DROP table if exists samTable')
    sCur.execute('CREATE table samTable (colNo integer, varName string, smpID string, xSmp real, ySmp real, matName string)')
    nt = 0
    for line in fileinput.input( mySciFiles.smpFile ):
      #print fileinput.lineno(),': ',line
      # HPAC or SCIPUFF sensor type
      if matchSen:
        if fileinput.isfirstline():
          (nDat,vnames) = hpacSenHead(line,sCur)
          createSam(nDat,vnames,sCur,smpLoc)
        else:
          nt = addData(line,nDat,sCur,nt,isReverse=isReverse)          
      else:
        # old sensor file  
        if fileinput.isfirstline():
          nDat = int(line) -1
          vnames = []
          nNames = 0
        else: 
          if nNames < nDat:
            if not vnames:
              tmpHead = line.split()[1:]
            else:
              tmpHead = line.split()
            nNames += len(tmpHead)
            for vname in tmpHead:
              if vname[-3:] != '001':
                break
              vnames.append(vname[:-3])
          elif nNames == nDat:
             print ('No. of variables = %d, Names = %s\n' % (len(vnames),vnames))
             createSam(nDat,vnames,sCur,smpLoc)
             nNames += 1
          elif nNames > nDat:
             nt = addData(line,nDat,sCur,nt,isReverse=isReverse)
    print 'No. of time breaks = ',nt  
    smpConn.commit()   
    sCur.execute('select max(value) from smpTable d,samTable c where d.colNo = c.colNo and varName=?',(vnames[0],))
    #c.execute('SELECT DISTINCT itime,timeString FROM indr WHERE itime_local = ?',(it,))
    print 'Max %s = %15.5e'%(vnames[0],float(sCur.fetchone()[0]))
    fileinput.close()
    return(sCur,createTable)

def sen2db(startTimeString,senFile,samList=None):

  (Yr,Mo,Day,Hr,Mn,Sec) = str2ymdhms(startTimeString)
  startEpTime = getEpTime(Yr,Mo,Day,Hr,Mn,Sec)

  dbFile = senFile + '.db'
  senConn = sqlite3.connect(dbFile)
  senConn.row_factory = sqlite3.Row
  senCur = senConn.cursor()

  senCur.execute('DROP table if exists senTable')
  senCur.execute('CREATE table senTable (matName string, matType string, timeString string,\
                  epTime real,tHr real, tDur real, xSen real, ySen real, cSen real)')

  if samList:
    matList = []

  rdNext = False
  for line in fileinput.input( senFile ):
    #print fileinput.lineno(),':',line  
    if line.rstrip().endswith('Type2Sensor'):
      rdNext = True
    else:
      if rdNext:
        insertStr = "INSERT into senTable VALUES"
        senList = line.split(';')
        (matName,matType,timeString) = (senList[0],senList[5],senList[4])
        (Yr,Mo,Day,Hr,Mn,Sec) = str2ymdhms(timeString)
        epTime = getEpTime(Yr,Mo,Day,Hr,Mn,Sec)
        tHr = (epTime - startEpTime)/3600. 
        (xSen,ySen,cSen,tDur) = map(float,(senList[1],senList[2],senList[7],senList[10]))
        if matType.strip() == 'N':
          cSen = 0.
        insertStr += "('%s','%s','%s',%13.2f,%16.5f,%10.3f,%10.3f,%10.3f,%13.5e)"% \
                      (matName,matType,timeString,epTime,tHr,tDur,xSen,ySen,cSen)
        #print insertStr
        senCur.execute(insertStr)
        if samList:
          matList.append(matName)
      rdNext = False
  senConn.commit()
  senConn.close()
  if samList:
    samList.createSam(matList=matList)
  senConn.close()

def db2sen(startTimeString,dbName,senFile,cFactor=1,cCut=1.):

  senOut = open(senFile,"w",0)
  #
  obsConn = sqlite3.connect(dbName)
  obsConn.row_factory = sqlite3.Row
  obsCur = obsConn.cursor()

  obsCur.execute('SELECT min(xStn),max(xStn),min(yStn),max(yStn) from obsTable')
  print 'db2sen:minmax x,y = ',obsCur.fetchall()[0]

  obsXy = db2Array(obsCur,'SELECT distinct xstn,ystn from obsTable where \
                             conc >= 0. order by xstn,ystn')
  obsThr = db2Array(obsCur,'SELECT distinct tHr from obsTable where conc >= 0.')
  obsThr = obsThr.tolist()

  obsConc = db2Array(obsCur,'SELECT xStn,yStn,stnId,tHr,conc from obsTable where \
                             conc >= 0. order by tHr,xStn,yStn')

  (startYr,startMo,startDay,startHr,startMin,startSec) = str2ymdhms(startTimeString)
  startEpTime = getEpTime(startYr,startMo,startDay,startHr,startMin,startSec)
  print 'db2sen: startEpTime = ',startEpTime,'(',startYr,startMo,startDay,startHr,startMin,startSec,')'
 
  cCut     = max(obsConc[:,4])*cCut
  print 'db2sen:Max Obs and cCut Conc = ',max(obsConc[:,4]), cCut

  for cO in obsConc:
    for ip,xy in enumerate(obsXy,1):
      if abs(cO[0]-xy[0]) + abs(cO[1]-xy[1]) < 0.001:
        cO[2] = ip*1.
        break
    epTime = cO[3]*3600. + startEpTime
    (Yr,Mo,DD,HH,mm,ss) = getYMD(epTime)
    # 
    if cO[4] > cCut:
      cO[4] = cO[4]/cFactor       # convert to kg/m3
      mType = 'T'
    else:
      cO[4] = 0. #cCut
      mType = 'NT'

    try:
      hrId = obsThr.index(cO[3]) + 1
    except IndexError:
      print 'Error: cannot find hr = ',cO[3]
      sys.exit()
    
    senOut.write('mil.dtra.hpac.models.sensor.CAcomp.data.Type2Sensor\n')
    senOut.write('%s%03d.%03d;%8.4f;%8.4f;%8.4f;%s%s%s%s%s%s;%s;%13.5e;%13.5e;%8.4f;%s;%13.5f\n'%(\
           mType[0],cO[2],hrId,cO[0],cO[1],10.,Yr,Mo,DD,HH,mm,ss,mType, 1.e-19, cO[4], 1.,'NS',10800))
    #T011.024;      2.65000;     51.08330;     10.00000;19941024113000; T;  1.25700E-19;  1.00000E-02;     10.00000; NS;  10800.00000
  senOut.close()
  obsConn.close()

# Call main program
if __name__ == '__main__':
  # Parse arguments
  arg = optparse.OptionParser()
  arg.add_option("-p",action="store",type="string",dest="prjNames")
  arg.add_option("-a",action="store",type="string",dest="samFiles")
  arg.set_defaults(prjNames=None,samFiles=None)
  opt,args = arg.parse_args()
  # Check arguments
  if not opt.prjNames:
    print 'Error: prjNames must be specified'
    print 'Usage: smp2db.py -p prjName1[:prjName2...] [-a prj1.sam[:prj2.sam...]]'
    sys.exit()
  else:
    prjNames = opt.prjNames.split(':')
  if opt.samFiles:
    samFiles = opt.samFiles.split(':')
    print 'samFiles from command line will be used'
  else:
    samFiles = None
  createSmpDb(prjNames,samFiles=samFiles)
