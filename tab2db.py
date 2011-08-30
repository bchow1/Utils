#!/usr/bin/python
import os
import sys
import ast
import sqlite3
import fileinput
import numpy as np
'''
Convert data table from ASCII to db. Use the column names
from first line which may or may not start with '#'.
Ignores all blank lines.
'''
def getColValues(line,separator):
  line = line.split('#')[0].strip().replace('"','')
  if len(line) > 0 :
    if separator is None:
      colValues = line.split()
    else:
      colValues = line.split(separator)
  return colValues

def setColNames(line,separator):
  if separator is None:
    colNames = line.replace('#','').strip().split()
  else:
    colNames = line.replace('#','').strip().replace('"','').split(separator)
  for i,colName in enumerate(colNames):
   colNames[i] = colName.strip().replace(' ','')
   if colName.startswith('_'):
     colNames[i] = colName[1:] 
  print 'Column names = ',colNames
  return colNames

def setColTypes(colValues):
  colTypes = []
  for colValue in colValues: 
    try:
      colValue = ast.literal_eval(colValue)
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
  print '\n',createStr
  dbCur.execute(createStr)
  return (dbCur,dbConn)

def insertDb(dbCur,nCol,colValues):
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
  print insertStr
  dbCur.execute(insertStr)
  return

def makeDb(fName,separator=None,headLineNo=1,colNames=None,colTypes=None):
  dbCur = None
  lWarn = True
  for line in fileinput.input(fName):
    if fileinput.lineno() < headLineNo:
      continue
    if colNames is None:
      if fileinput.lineno() == headLineNo:
        colNames = setColNames(line,separator)
    nCol = len(colNames)
    if colTypes is not None:
      if len(colTypes) != nCol:
        print 'Error: \n Number of column types in \n %s\n does not match number of column names in \n %s'%(colTypes,colNames)
        sys.exit()
    if fileinput.lineno() == headLineNo:
      continue
    if len(line) > 0:
      colValues = getColValues(line,separator)
      if len(colValues) != nCol and lWarn:
        print 'Warning: \n Number of values in \n %s\n does not match number of \n column names in %s'%(colValues,colNames)
        colValues = colValues[:nCol]
        print ' Using only %d columns '%(nCol)
        lWarn = False
      if colTypes is None:
        colTypes = setColTypes(colValues)
      if dbCur is None:
        dbCur,dbConn = initDb(fName,colNames,colTypes)
      insertDb(dbCur,nCol,colValues)
    else:   # skip blank lines
      continue
  # end file input from fName
  fileinput.close()
  if colTypes is not None:
    dbConn.commit()
    dbConn.close()
    print 'Created db file for ',fName
  return

if __name__ == '__main__':

  import optparse

  # local modules
  import utilDb

  if sys.argv.__len__() < 2:
    print 'Usage: tab2db.py [-s separator] [-n colname] [-t coltype] table1.txt [table2.txt ... ]'
    sys.exit()
  arg = optparse.OptionParser()
  arg.add_option("-s",action="store",type="string",dest="separator")
  arg.add_option("-n",action="store",type="string",dest="colname")
  arg.add_option("-t",action="store",type="string",dest="coltype")
  arg.set_defaults(separator=None)
  arg.set_defaults(colname=None)
  arg.set_defaults(coltype=None)
  opt,args = arg.parse_args()

  # Get column separator 
  print 'Using Separator = ',opt.separator

  # Get column names 
  if opt.colname is None:
    colNames = None
  else:
    if opt.separator is None:
      colNames = opt.colname.strip().split(',')
    else:
      colNames = opt.colname.strip().split(opt.separator)
  
  # Get column types 
  if opt.coltype is None:
    colTypes = None
  else:
    colTypes = []
    for cType in list(opt.coltype.strip()):
      if cType == 'i':
        colTypes.append('integer')
      elif cType == 'r':
        colTypes.append('real')
      else:
        colTypes.append('string')
  print 'Using Column types = ',colTypes
  for fName in args:
    print '\nRunning makeDb for file ',fName
    makeDb(fName,separator=opt.separator,colNames=colNames,colTypes=colTypes)
    dbFile = fName + '.db'
    print str(utilDb.db2List(dbFile,'select sql from sqlite_master where type="table"')[0][0])
