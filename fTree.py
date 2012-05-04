# -*- coding: cp1252 -*-
#
# system modules
import os
import sys
import re
import fileinput
import sqlite3

# local modules
import utilDb

# patterns
commPatt = re.compile('(.*?)!(.*)')
startIfacePatt = re.compile('\s*interface\s*$',re.I)
endIfacePatt   = re.compile('\s*end\s+interface\s*$',re.I)
#
subPatt     = re.compile(r'.*\bsubroutine\s+(\w+)\b.*',re.I)
endSubPatt  = re.compile(r'\s*end\s+subroutine\s+.*',re.I)
#
fncPatt     = re.compile(r'.*\bfunction\s+(\w+)\b.*',re.I)
endFncPatt  = re.compile(r'\s*end\s+function\s+.*',re.I)
#
extPatt  = re.compile(r'.*\bexternal\s*.*::\s*(.*)',re.I)
callPatt = re.compile(r'.*\bcall\s+(\w+)\b.*',re.I)
#
endPatt  = re.compile(r'\s*end\s*$',re.I)

def getFnames(baseDir='./',skipDirs=None):
  fList = []
  for root,dirs,files in os.walk(baseDir):
    if skipDirs is not None:
      for skipDir in skipDirs:
        if skipDir in dirs:
          dirs.remove(skipDir)
    for fName in files:
      if fName.lower().endswith('.f') or fName.lower().endswith('.f90'):
        fList.append(os.path.join(root,fName))
  return fList

def getCalledNames(fName):

  # initialize lists
  subList    = []
  fncList    = []
  extList    = []
  calledList = []

  # initialize logicals and names
  mainName  = fName.split(os.sep)[-1] + '::Main' 
  startMain = True
  startSub  = False
  startFnc  = False
  isInterFace = False

  for line in fileinput.input(fName):
    
    # remove comments
    commMatch = commPatt.match(line)
    if commMatch:
      line = commMatch.group(1)
      
    # check interface start
    if startIfacePatt.match(line):
      isInterFace = True

    # check interface end
    if endIfacePatt.match(line):
      isInterFace = False

    # skip interface lines
    if isInterFace: continue

   
    # Check for subroutines
    subMatch = subPatt.match(line)
    if subMatch:
      subName = fName.split(os.sep)[-1] + '::' + subMatch.group(1).lower()
      subList.append(subName)
      #print '< start subroutine ',subName
      startSub = True

    # Check for declared functions
    fncMatch = fncPatt.match(line)
    if fncMatch:
      fncName = fName.split(os.sep)[-1] + '::' + fncMatch.group(1).lower()
      fncList.append(fncName)
      startFnc = True

    # Check for external functions
    extMatch = extPatt.match(line)
    if extMatch:
      extNames = extMatch.group(1).lower().split(',')
      if startSub:
        prefix = subName + '::'
      elif startFnc:
        prefix = fncName + '::'
      else:
        prefix = mainName + '::'      
      for extName in extNames:
        if prefix + extName not in extList:
          extList.append(prefix + extName)
      
    # Check for called subroutines
    callMatch = callPatt.match(line)
    if callMatch:
      calledSubName = callMatch.group(1).lower()
      #print calledSubName
      if startSub:
        prefix = subName + '::'
      elif startFnc:
        prefix = fncName + '::'
      else:
        prefix = mainName + '::'

      if prefix + calledSubName not in calledList:
        calledList.append(prefix + calledSubName)

    # match  end statements
    endMatch = endPatt.match(line)    
    endSubMatch = endSubPatt.match(line)
    endFncMatch = endFncPatt.match(line)
    
    if startSub:
      if endMatch or endSubMatch:
        startSub = False
        #print 'end subroutine ',subName,'>'
    elif startFnc:
      if endMatch or endFncMatch:
        startFnc = False
    elif endMatch:
      startMain = False
      
  return subList,fncList,extList,calledList

def openDb(dbName):
  dbConn = sqlite3.connect(dbName)
  dbConn.row_factory = sqlite3.Row
  dbCur  = dbConn.cursor()
  return (dbConn,dbCur)

def closeDb(dbConn,dbCur):
  dbCur.close()
  dbConn.close()
  return  

def createDb(fList,dbName):
  # initialize db
  dbConn,dbCur = openDb(dbName)
  dbCur.execute('DROP table if exists fileTable')
  dbCur.execute('CREATE table fileTable (fileNo integer, fullName string)')
  dbCur.execute('DROP table if exists subTable')
  dbCur.execute('CREATE table subTable (fileNo integer, fileName string, subId integer, subName string)')
  dbCur.execute('DROP table if exists callTable')
  dbCur.execute('CREATE table callTable (subName string, calledSub string)')

  # Add values to tables
  subNo = 0 
  #fList = ['Source1.f90']
  for fileNo,fName in enumerate(fList):
    print '-------------------\n',fName,'\n-------------------\n'
    fNamel = fName.lower()
    insertStr = "INSERT into fileTable VALUES(%d,'%s')"%(fileNo,fName)
    #print insertStr
    dbCur.execute(insertStr)
    subList,fncList,extList,calledList = getCalledNames(fName)
    #print '\n Subroutines =\n',subList,'\n'
    #print '\n Functions =\n',fncList,'\n'
    #print '\n Externals =\n',extList,'\n'
    #print '\n called subroutines =\n',calledList,'\n'
    for fullSubName in subList+fncList:
      subName = fullSubName.split('::')[-1].lower().strip()
      insertStr = "INSERT into subTable VALUES(%d, '%s', %d,'%s')"%(fileNo,fullSubName.split('::')[0],subNo,subName)
      #print '\n',insertStr
      dbCur.execute(insertStr)
      subNo += 1
      for calledSub in calledList+extList:
        callingSubName = calledSub.split('::')[1].lower()
        if subName == callingSubName:
          insertStr = "INSERT into callTable VALUES('%s','%s')"%(subName,calledSub.split('::')[-1].lower().strip())
          #print '   ',insertStr
          dbCur.execute(insertStr)
    dbConn.commit()
  closeDb(dbConn,dbCur)

  return

def getCallers(dbCur,subName,subList,lastSubList):
  selectStr = 'SELECT subName from callTable where calledSub="%s"'%subName.lower().strip()
  callingSubs = utilDb.db2List(dbCur,selectStr)
  if len(callingSubs) == 0:
    print '*******************\n'
  for callingSub in callingSubs:
    subSubName = str(callingSub[0])
    subString = subName + ':' + subSubName
    if subName != subSubName and subString not in subList:
      if len(subList) > 0:
        if subList[-1] != lastSubList and subList[-1].split(':')[1] == subName:
          print '            |<- ',subSubName
        else:
          print subName,'<-',subSubName
        lastSubList = subList[-1]
      else:
        print subName,'<-',subSubName
      subList.append(subString)
      getCallers(dbCur,subSubName,subList,lastSubList)
  return subList

def getCalled(dbCur,subName,subList,indent):
  selectStr = 'SELECT DISTINCT calledSub from callTable where subName="%s"'%subName.lower().strip()
  calledSubs = utilDb.db2List(dbCur,selectStr)
  
  if len(calledSubs) > 0:
    indent += "|--"
    for calledSub in calledSubs:
      subSubName = str(calledSub[0]) 
      print '%s->%s'%(indent,subSubName)
      if subSubName not in subList:
        subList.append(subSubName)
        getCalled(dbCur,subSubName,subList,indent)
  else:
    indent = indent[:-2]
  return

def getTree(subName,dbName):
  #
  print os.getcwd()
  dbConn,dbCur = openDb(dbName)

  print '\n=========================='
  print 'called from ',subName
  print '============================'
  subList = []
  indent = ""
  getCalled(dbCur,subName,subList,indent)
  
  print '\n=========================='
  print 'callers to ',subName
  print '==========================\n'

  subList = []
  lSub = ''
  getCallers(dbCur,subName,subList,lSub)
  closeDb(dbConn,dbCur)

if __name__ == '__main__':

  #ver,subName = raw_input('Version [f|m], subroutine ? ').split(' ')
  ver = 'f'
  subName = 'InitChemSubMPI'
  if ver == 'f':
    dbFile = 'SciEpri.db'
  elif ver == 'm':
    dbFile = 'scichem_v1900.db'
  else:
    dbFile = None
    
  if dbFile is not None:
    skipDirs = ['CVS']
    #
    if dbFile == 'SciEpri.db':
      baseDir = 'd:\\hpac\\gitEPRI\\UNIX\\EPRI\\src'
    if dbFile == 'scichem_v1900.db':
      baseDir = 'd:\\EPRI\\SCICHEM_MADRID\\V1900\\src'
      skipDirs = ['pcscipuf','contri','ncar','noDll','ntinc','util','CVS']
    #
    os.chdir(baseDir)
    if not os.path.exists(dbFile):
      fList = getFnames(baseDir,skipDirs=skipDirs)
      createDb(fList,dbFile)
    getTree(subName,dbFile)
