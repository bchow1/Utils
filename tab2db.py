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
def makeDb(fName,separator=None,colTypes=None):
  initDb = True
  for line in fileinput.input(fName):
    if fileinput.lineno() == 1:
      if separator is None:
        colNames = line.replace('#','').strip().split()
      else:
        colNames = line.replace('#','').strip().replace('"','').split(separator)
        for i,colName in enumerate(colNames):
         colNames[i] = colName.strip().replace(' ','')
         if colName.startswith('_'):
           colNames[i] = colName[1:] 
      print 'Column names = ',colNames
      if colTypes is not None:
        if len(colTypes) != len(colNames):
          print 'Error: Column types does not match number of column names = ',colTypes
          sys.exit()
    else:
      line = line.split('#')[0].strip().replace('"','')
      if len(line) > 0 :
        if separator is None:
          colValues = line.split()
        else:
          colValues = line.split(separator)
        if initDb:
          print 'colValues = ',colValues
          if not colTypes:
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
          # end if not colTypes
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
          initDb = False
        # end if initDb
        insertStr = 'INSERT into dataTable VALUES('
        for i in range(len(colNames)):
          if colTypes[i] == 'string':
            insertStr += "'" + colValues[i] + "'"
          else:
            if len(colValues[i]) < 1:
              colValues[i] = '-9999'
            insertStr += colValues[i]
          if i == len(colNames)-1:
            insertStr += ')'
          else:
            insertStr += ', '
        print insertStr
        dbCur.execute(insertStr)
      else:   # skip blank lines
       continue
  # end file input from fName
  fileinput.close()
  if colTypes:
    dbConn.commit()
    dbConn.close()
    print 'Created db file ',dbFile
  return

if __name__ == '__main__':

  import optparse

  # local modules
  import utilDb

  if sys.argv.__len__() < 2:
    print 'Usage: tab2db.py table1.txt [ table2.txt ... ]'
    sys.exit()
  arg = optparse.OptionParser()
  arg.add_option("-s",action="store",type="string",dest="separator")
  arg.add_option("-t",action="store",type="string",dest="coltype")
  arg.set_defaults(separator=None)
  arg.set_defaults(coltype=None)
  opt,args = arg.parse_args()
  print 'Using Separator = ',opt.separator
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
    makeDb(fName,separator=opt.separator,colTypes=colTypes)
    dbFile = fName + '.db'
    #dataArray = utilDb.db2Array(dbFile,'.schema')
    #print dataArray
