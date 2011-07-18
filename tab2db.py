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
def makeDb(fName):
  colTypes = None
  for line in fileinput.input(fName):
    if fileinput.lineno() == 1:
      colNames = line.replace('#','').strip().split()
      #print 'Column names = ',colNames
    else:
      line = line.split('#')[0]
      if len(line.strip()) > 0 :
        colValues = line.split()
        if not colTypes:
          colTypes = []
          for colValue in colValues: 
            try:
              colValue = ast.literal_eval(colValue)
              if isinstance(colValue,int):
                colTypes.append('integer')
              elif isinstance(colValue,float):
                colTypes.append('real')
              else:
                print 'Error: unknown type for ',colValue
                sys.exit()
            except ValueError:
              colTypes.append('string')
          #print 'colValues = ',colValues
          #print 'colTypes = ',colTypes
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
          print createStr
          dbCur.execute(createStr)
        # end if not colTypes
        insertStr = 'INSERT into dataTable VALUES('
        for i in range(len(colNames)):
          insertStr += colValues[i]
          if i == len(colNames)-1:
            insertStr += ')'
          else:
            insertStr += ', '
        #print insertStr
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
  # local modules
  import utilDb
  if sys.argv.__len__() < 2:
    print 'Usage: tab2db.py table1.txt [ table2.txt ... ]'
    sys.exit()
  for i in range(1, sys.argv.__len__()):
    print 'Running makeDb for file ',i,':',sys.argv[i]
    fName = sys.argv[i]
    makeDb(fName)
    dbFile = fName + '.db'
    dataArray = utilDb.db2Array(dbFile,'select * from dataTable')
    print dataArray
