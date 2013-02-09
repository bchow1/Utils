
#
# Read section name from imc file
# and save the species data in spList
# 
import os
import sys
import sqlite3

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

def rdMCScn(scnName,form=None):
  print scnName
  scnFile = open(scnName,'r')
  scnList = []
  
  for line in scnFile:
    if len(line.strip()) > 0: 
      if line.strip().startswith('&SCN'):
        print 'Start Scn'
      if line.strip().startswith('/'):
        print 'Start Scn'
  scnFile.close()

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
  runDir = 'D:\\negativeO3\\' 
  os.chdir(runDir)
  imcName = 'scichem-99\\negO3_1hr_fix.imc'
  spList = rdImc(imcName)

  scnName = 'scichem-99\\negO3_1hr_fix.scn'
  rdMCScn(scnName)
  
  createDB(spList)
  
