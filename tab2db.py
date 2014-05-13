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

def setColNames(line,separator,comment=None,collist=None):
  if comment is None:
    comment = '#'
  lStrip = line.replace(comment,'').strip()  
  if separator is None: # Use default of blank spaces
    colNames = lStrip.split()
  else:
    if lStrip.endswith(separator):
      line = lStrip[:-len(separator)]
    colNames = lStrip.replace('"','').split(separator)
  for i,colName in enumerate(colNames):
    colNames[i] = colName.strip().replace(' ','')
    if colName.startswith('_'):
      colNames[i] = colName[1:]
    colNames[i] = colNames[i].replace('/','') 
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
  print '\n',createStr
  dbCur.execute(createStr)
  return (dbCur,dbConn)

def insertDb(dbCur,nCol,colTypes,colValues):
  nv = len(colValues)
  nt = len(colTypes)
  if nv < nt :
    for i in range(nv+1,nt+1):
      colValues.extend(['-9999'])
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

def checkNcol(colNames,colTypes=None,colValues=None,lWarn=False):
  nName  = len(colNames) 
  nCol   = nName
  colLab = ['types','values']
  for colN,colI in enumerate([colTypes,colValues]):
    if colI is not None:
      nI = len(colI) 
      if nName != nI:
        if lWarn:
          nCol = min(nName,nI)
          print 'Warning: \n Number of %s %d in \n %s\n does not match %d number of column names in \n %s'\
                             %(colLab[colN],len(colI),colI,len(colNames),colNames)
          print ' Using only %d columns '%(nCol)
        else:
          print 'Error: \n Number of column %s in \n %s\n   does not match number of column names in \n %s'\
                            %(colLab[colN],colI,colNames)
          sys.exit()
  return nCol
 
def makeDb(fName,separator=None,comment=None,hdrlno=0,colname=None,coltype=None,collist=None):

  # Get column separator 
  #print 'Using Separator = ',separator

  # Get column names 
  if colname is None:
    colNames = None
    nCol     = -1  
  else:
    if separator is None:
      colNames = colname.strip().split(',')
    else:
      colNames = colname.strip().split(separator)
    nCol = len(colNames)
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
    cList = collist.split(',')
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
    
    # Set colnames from header line no if not set
    if colNames is None:
      if fileinput.lineno() == hdrlno:
        colNames = setColNames(line,separator,comment=comment,collist=colList)
        nCol = checkNcol(colNames,colTypes=colTypes)
        
    if fileinput.lineno() <= hdrlno:
      continue
    if comment is not None:
      try:
        indx = line.index(comment)
        line = line[:indx].strip()
      except ValueError:
        pass
    if len(line) > 0:
      colValues = getColValues(line,separator,collist=colList)
      if lWarn:
        nCol = checkNcol(colNames,colValues=colValues,lWarn=lWarn)
        lWarn = False        
      colValues = colValues[:nCol]
      print colValues
      # set col types from colValues if not set earlier
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
  
  os.chdir("d:\\SCIPUFF\\runs\\EPRI\\DoletHills")
  #['date','time','lat','lon','alt_ft','o3','no','no2','noy','SO2','co']
  sys.argv = ["","-s,","-t","ssrrrrrrrrr","aztec_20050908_some.csv"]
  
  '''
  os.chdir("D:\\SCIPUFF\\EPRI\\runs\\tva\\tva_990715")
  sys.argv = ["","-s,","negO3_puff.dat"]

  
  # Args for PST files
  os.chdir("D:\\Aermod\\v12345\\runs\\pgrass\\AERMOD")
  args    = ["","-m","*","-n","x,y,Cavg,zElev,zHill,zFlag,Ave,Grp,Date","-t","rrrrrrsss","-c","1-9"]
  prjName = 'PGRASS'
  for fName in [prjName+"01.PST"]: #,prjName+"03.PST",prjName+"24.PST"]:
    sys.argv = args
    sys.argv.extend([fName])
  '''
  
  '''
  # Args for KINSF6 files
  os.chdir("D:\\Aermod\\v12345\\runs\\KINSF6\\Obs_Conc")
  #args    = ["","-m","*","-n","YY,MM,DD,HH,ARC,RECNAM,RECX,RECY,RECZ     DIST  DIR     Q     CHI      CHI/Q","-t","rrrrrrsss","-c","1-9"]
  obsName = 'KINSF6.SUM'
  headLineNo = 3
  args    = ["","-m","*","-d","3"]
  sys.argv = args
  sys.argv.extend([obsName])
  '''
     
  if sys.argv.__len__() < 2:
    print 'Usage: tab2db.py [-s separator] [-m comment ] [-d headerlineno ] [-n colname] [-t coltype] [-c collist] table1.txt [table2.txt ... ]'
    print 'Example: python ~/python/tab2db.py -s "," -n "hrs,mrate,lat,lon" -t rrrr -c "1,2,5" RT970925.DAT'
    print '   Note: Col numbers start from 1'
    sys.exit()
  arg = optparse.OptionParser()
  arg.add_option("-s",action="store",type="string",dest="separator")
  arg.add_option("-m",action="store",type="string",dest="comment")
  arg.add_option("-d",action="store",type="int"   ,dest="hdrlno")
  arg.add_option("-n",action="store",type="string",dest="colname")
  arg.add_option("-t",action="store",type="string",dest="coltype")
  arg.add_option("-c",action="store",type="string",dest="collist")
  arg.set_defaults(separator=None)
  arg.set_defaults(comment=None)
  arg.set_defaults(hdrlno=1)
  arg.set_defaults(colname=None)
  arg.set_defaults(coltype=None)
  arg.set_defaults(collist=None)
  opt,args = arg.parse_args()
  print args

  for fName in args:
    print '\nRunning makeDb for file ',fName
    #print opt.separator,opt.colname,opt.coltype,opt.collist
    makeDb(fName,separator=opt.separator,comment=opt.comment,hdrlno=opt.hdrlno,colname=opt.colname,coltype=opt.coltype,collist=opt.collist)
    dbFile = fName + '.db'
    print '\nCheck:'
    print str(utilDb.db2List(dbFile,'select sql from sqlite_master where type="table"')[0][0])
  print "Done :-)"
