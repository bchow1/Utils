#
# Read section name from imc file
# and save the species data in spList
# 
import os
import sys
import sqlite3
import numpy as np

def rdSpSec(line,spList):
  spList.append(line.strip().split())
  return spList

def rdImc(imcName):
  imcFile  = open(imcName,'r')
  sctnName = None

  # Initialize spList
  spList   = []

  # Read section name and data from each line
  for line in imcFile:
    if len(line.strip()) > 0: 
      if line.startswith('#'):
        sctnName = line.strip().split()[0].replace('#','').split(',')[0]
        print 'Section = ',sctnName
        continue
      if sctnName == 'Species':
        rdSpSec(line,spList)
  imcFile.close()
  print len(spList),spList[0],spList[-1]
  return spList

def rdMCScn(scnName):
  
  scnFile = open(scnName,'r')
  scnList = []
  
  inScn = False
  for line in scnFile:
    lStrip = line.strip()
    if len(lStrip) > 0: 
      if lStrip.startswith('&SCN'):
        print 'Start Scn ',len(scnList)+1
        inScn = True
        scnLines = []
        relList  = []
      if lStrip.startswith('/'):
        scnList.append([scnLines,relList])
        inScn = False
        print 'End Scn ',len(scnList)
      # Reads SCICHEM-99 type MC release
      if inScn:
        if 'REL_MC' in line:
          if lStrip.endswith(','):
            lStrip = lStrip[:-1]
          relList = map(float,lStrip.split('=')[1].strip().split(','))
          print len(relList)
        else:
          scnLines.append(line)
  scnFile.close()

  return scnList

def wrtMCScn(spList,scnList,newRel=None):

  # Get names and ambient concentrations from new spList 
  if newRel is not None:
    spNames = [spVal[0] for spVal in spList]
    spConcs = [spVal[2] for spVal in spList]

  scnFile = open('temp.scn','w')
  for scnNo,scnVal in enumerate(scnList):
    print '\n#START_MC ',scnNo+1
    for line in scnVal[0]:
      scnFile.write('%s'%line)
    for spNo in range(len(spList)):
      if scnVal[1][spNo] != 0.:
        print '     ',spList[spNo][0],scnVal[1][spNo]
    if newRel is not None:
      print '#NEW_MC ',scnNo+1
    else:
      print '#END_MC ',scnNo+1
    
    # Replace relList with newRel values 
    if newRel is not None:
      for spNo in range(len(scnVal[1])):
        scnVal[1][spNo] = 0.
      for spName,spConc in newRel.iteritems():
        spIndx = spNames.index(spName) 
        scnVal[1][spIndx] = spConc
      for spNo in range(len(spList)):
        if scnVal[1][spNo] != 0.:
          print '     ',spList[spNo][0],scnVal[1][spNo]
      print '#END_MC ',scnNo+1
               
    scnFile.write(' REL_MC = ')
    for spRel in scnVal[1]:
      scnFile.write('%13.5e,'%spRel)
    scnFile.write('\n/\n')
  return
  
def openDb(dbName):
  dbConn = sqlite3.connect(dbName)
  dbConn.row_factory = sqlite3.Row
  dbCur  = dbConn.cursor()
  return (dbConn,dbCur)

def dbExecuteStmts(dbName):
  dbConn,dbCur = openDb(dbName)
  dbCur.execute('DROP table if exists concTable')
  dbCur.execute('CREATE table concTable ( speciesName varChar(8), speciesType varChar(2), ambConc real , tolerence real)')
  return (dbConn,dbCur)

def insertData(dbConn,dbCur,spList):
  for i in range(0, len(spList)-1):
    #print spList[i][0], spList[i][1], spList[i][2]
    insertStr = "INSERT into concTable VALUES('%s', '%s', %13.5e, %13.5e)"%(spList[i][0],spList[i][1],float(spList[i][2]),float(spList[i][3]))
    #print insertStr
    dbCur.execute(insertStr)
  dbConn.commit()
    
def createDB(spList):
  dbName = 'scichem99_amb_vals.db'
  dbConn,dbCur = dbExecuteStmts(dbName)  
  insertData(dbConn,dbCur,spList)
  
# Main Program

if __name__ == '__main__':
  runDir = 'D:\\SCIPUFF\\EPRI\\runs\\negativeO3'
  imcName = 'scichem-99\\negO3_1hr_fix.imc'
  scnName = 'scichem-99\\negO3_1hr_fix.scn'
  #runDir = 'D:\\negativeO3\\' 

  os.chdir(runDir)
  spList = rdImc(imcName)
  #createDB(spList)
  scnList = rdMCScn(scnName)
  
  #
  newRel = {'NO2':3.21E+04,'NO':2.885E+05,'SO2':5.76E+02} 
  wrtMCScn(spList,scnList,newRel=newRel)
  

