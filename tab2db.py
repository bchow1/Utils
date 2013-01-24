#!/usr/bin/python
import os
import sys
import ast
import sqlite3
import fileinput
'''
Convert data table from ASCII to db. Use the column names
from first line which may or may not start with '#'.
Ignores all blank lines.
'''
def getColValues(line,separator,collist=None):
  line = line.split('#')[0].strip().replace('"','')
  if len(line) > 0 :
    if separator is None:
      colValues = line.split()
    else:
      if line.strip().endswith(separator):
        line = line.strip()[:-len(separator)]      
      colValues = line.split(separator)
    if collist is not None:
      cValues = []
      for i,colValue in enumerate(colValues):
        if i+1 in collist:
          cValues.append(colValue)
      colValues = cValues
  return colValues

def setColNames(line,separator,collist=None):
  if separator is None:
    colNames = line.replace('#','').strip().split()
  else:
    if line.strip().endswith(separator):
      line = line.strip()[:-len(separator)]
    colNames = line.replace('#','').strip().replace('"','').split(separator)
  for i,colName in enumerate(colNames):
    colNames[i] = colName.strip().replace(' ','')
    if colName.startswith('_'):
      colNames[i] = colName[1:] 
  if collist is not None:
    cNames = []
    for i,colName in enumerate(colNames):
      if i+1 in collist:
        cNames.append(colName)
    colNames = cNames
 
  # Rename duplicates
  for colNo in range(len(colNames)-1):
    if colNames[colNo] == colNames[colNo-1]:
      colNames[colNo-1] = colNames[colNo] + '1'
      colNames[colNo]   = colNames[colNo] + '2'
  return colNames

def setColTypes(colValues):
  colTypes = []
  for colValue in colValues:
    if len(colValue.strip()) == 0:
      colTypes.append('string')
      continue       
    try:
      colValue = ast.literal_eval(colValue.strip())
      if isinstance(colValue,int):
        colTypes.append('integer')
      elif isinstance(colValue,float):
        colTypes.append('real')
      #else:
      #  print 'Error: unknown type for ',colValue
      #  sys.exit()
    except ValueError:
      colTypes.append('string')
  return colTypes

def initDb(fName,colNames,colTypes):
  #print len(colNames),colNames
  dbFile = fName + '.db'
  dbConn = sqlite3.connect(dbFile)
  dbCur = dbConn.cursor() 
  dbCur.execute('DROP table if exists dataTable')
  createStr = 'CREATE table dataTable ('
  for i in range(len(colNames)):
    createStr += colNames[i] + ' ' + colTypes[i]
    if i == len(colNames)-1:
      createStr += ')'
    else:
      createStr += ', '
  #print '\n',createStr
  dbCur.execute(createStr)
  return (dbCur,dbConn)

def insertDb(dbCur,nCol,colTypes,colValues):
  insertStr = 'INSERT into dataTable VALUES('
  for i in range(nCol):
    if colTypes[i] == 'string':
      insertStr += "'" + colValues[i] + "'"
    else:     
      if len(colValues[i]) < 1:
        colValues[i] = '-9999'
      else:
        try:
          colValue = ast.literal_eval(colValues[i].strip())
          if (not isinstance(colValue,int) and \
              not isinstance(colValue,float)):
            colValues[i] = '-9999'
        except ValueError:
          colValues[i] = '-9999'
        except SyntaxError:
          colValues[i] = '-9999'
      insertStr += colValues[i]
    if i == nCol-1:
      insertStr += ')'
    else:
      insertStr += ', '
  #print insertStr
  dbCur.execute(insertStr)
  return

def makeDb(fName,separator=None,comment=None,headLineNo=1,colname=None,coltype=None,collist=None):

  # Get column separator 
  #print 'Using Separator = ',separator

  # Get column names 
  if colname is None:
      colNames = None
  else:
    if separator is None:
      colNames = colname.strip().split(',')
    else:
      colNames = colname.strip().split(separator)
  #print 'Using Column names = ',colNames

  # Get column types 
  if coltype is None:
    colTypes = None
  else:
    colTypes = []
    for cType in list(coltype.strip()):
      if cType == 'i':
        colTypes.append('integer')
      elif cType == 'r':
        colTypes.append('real')
      elif cType == 's':
        colTypes.append('string')
      else:
        colTypes.append('string')
  #print 'Using Column types = ',colTypes

  if collist is None:
    colList = None
  else:
    if separator is None:
      cList = collist.split(',')
    else:
      cList = collist.split(separator)
    colList = []
    for colNo in cList:
      if '-' in colNo:
        cstart,cend = map(int,colNo.split('-'))
        for icol in range(cstart,cend+1):
          colList.append(icol) 
      else:
        colList.append(int(colNo)) 
    #print 'Using only columns from column list = ',colList

  dbCur = None
  lWarn = True
  fileinput.close()
  for line in fileinput.input(fName):
    if comment is not None:
      if line.strip().startswith(comment):
        continue
    if fileinput.lineno() < headLineNo:
      continue
    if colNames is None:
      if fileinput.lineno() == headLineNo:
        colNames = setColNames(line,separator,collist=colList)
    nCol = len(colNames)
    if colTypes is not None:
      if len(colTypes) != nCol:
        print 'Error: \n Number of column types in \n %s\n   does not match number of column names in \n %s'%(colTypes,colNames)
        sys.exit()
    if fileinput.lineno() == headLineNo:
      continue
    if len(line) > 0:
      colValues = getColValues(line,separator,collist=colList)
      if len(colValues) != nCol and lWarn:
        print 'Warning: \n Number of values %d in \n %s\n does not match %d number of column names in \n %s'\
               %(len(colValues),colValues,len(colNames),colNames)
        colValues = colValues[:nCol]
        print ' Using only %d columns '%(nCol)
        lWarn = False
      if colTypes is None:
        colTypes = setColTypes(colValues)
      if dbCur is None:
        dbCur,dbConn = initDb(fName,colNames,colTypes)
      insertDb(dbCur,nCol,colTypes,colValues)
    else:   # skip blank lines
      continue
  # end file input from fName
  fileinput.close()
  if colTypes is not None:
    dbConn.commit()
    dbConn.close()
    #print 'Created db file for ',fName
  return 

if __name__ == '__main__':

  import optparse
  # local modules
  import utilDb
  
  #os.chdir("D:\\SCIPUFF\\EPRI\\runs\\tva\\tva_990715")
  #sys.argv = ["","-s,","negO3_puff.dat"]

  os.chdir("D:\\Aermod\\v12345\\runs\\pgrass\\AERMOD")
  
  # Args for PST files
  args    = ["","-m","*","-n","x,y,Cavg,zElev,zHill,zFlag,Ave,Grp,Date","-t","rrrrrrsss","-c","1-9"]
  prjName = 'PGRASS'
  for fName in [prjName+"01.PST"]: #,prjName+"03.PST",prjName+"24.PST"]:
    sys.argv = args
    sys.argv.extend([fName])
  
  if sys.argv.__len__() < 2:
    print 'Usage: tab2db.py [-s separator] [-m comment ] [-n colname] [-t coltype] [-c collist] table1.txt [table2.txt ... ]'
    print 'Example: python ~/python/tab2db.py -s "," -n "hrs,mrate,lat,lon" -t rrrr -c "1,2,5" RT970925.DAT'
    sys.exit()
  arg = optparse.OptionParser()
  arg.add_option("-s",action="store",type="string",dest="separator")
  arg.add_option("-m",action="store",type="string",dest="comment")
  arg.add_option("-n",action="store",type="string",dest="colname")
  arg.add_option("-t",action="store",type="string",dest="coltype")
  arg.add_option("-c",action="store",type="string",dest="collist")
  arg.set_defaults(separator=None)
  arg.set_defaults(comment=None)
  arg.set_defaults(colname=None)
  arg.set_defaults(coltype=None)
  arg.set_defaults(collist=None)
  opt,args = arg.parse_args()
  print args

  for fName in args:
    print '\nRunning makeDb for file ',fName
    #print opt.separator,opt.colname,opt.coltype,opt.collist
    makeDb(fName,separator=opt.separator,comment=opt.comment,colname=opt.colname,coltype=opt.coltype,collist=opt.collist)
    dbFile = fName + '.db'
    print str(utilDb.db2List(dbFile,'select sql from sqlite_master where type="table"')[0][0])
  print "Done :-)"
