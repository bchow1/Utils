#!/bin/python
import sys
import os
import fileinput
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import socket

compName = socket.gethostname()

# Local modules
if compName == 'sm-bnc' or compName == 'sage-d600':
  sys.path.append('C:\\Users\\sid\\python')
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')


if compName == 'Durga':
  sys.path.append('C:\\Users\\Bishusunita\\BNC\\python')
  sys.path.append('C:\\Users\\Bishusunita\\BNC\\TestSCICHEM\\Scripts')
  sys.path.append('C:\\Users\\Bishusunita\\BNC\\TestSCICHEM\\Scripts\\Chemistry')
  sys.path.append('C:\\Users\\Bishusunita\\BNC\\TestSCICHEM\\Scripts\\AERMOD')

  
import measure
import utilDb
import setSCIparams as SCI
'''^^^^^^^^^^^^
Leave first 4 columns of asmp
Leave fistr column of smp
Create diff as data Frame
plot the diff
#^^^^^^^^^^^^^^^^^^
'''
class smp(object):
    
  def __init__(self,fSmp,fSam=None):
    self.fsmp     = fSmp
    self.fsam     = fSam
    self.fasmp    = None
    self.wrap     = False
    self.splist   = []
    self.spDict   = {}
    self.nspc     = 0
    self.spClStrt = 9999
    self.hdr      = False
    self.nsmp     = 1
    self.smpNos   = [] 
    self.ncols    = 3
    self.colNames = ["T","C001","V001"]
    self.varNames = ["T","C","V"]
    self.pltNames = ["Time","Concentration","Variance"]
    self.varCols  = []
    self.nTime    = 1
    self.Times    = [0.,]
    self.skiprows = 1
  
    
    print smpFile
    self.fasmp = smpFile.replace('.smp','') + '.asmp'

    print self.fasmp
    print os.getcwd()
    
    
    if os.path.isfile(self.fasmp):
      print 'asmp file exists'
    else:
      self.fasmp = None
      print '*****asmp file does not exist'
    
  def getColNames(self,line):
    colNames   = line.split()
    self.colNames = colNames
    self.ncols = len(colNames)
    varNames = ['T']
    print "\n==============="
    print "colNo  colNames"
    print "==============="
    for colNo,colName in enumerate(colNames):
      if colName.endswith('_001'):
        if self.spClStrt == 9999:
          self.spClStrt = colNo
        varNames.append(colName.replace('_001',''))
      if len(colName) == 4 and colName.endswith('001'):
        varNames.append(colName.replace('001',''))
      if len(colName) == 4 and colName.endswith('002'):
        break
      if self.nspc > 0 and colNo >= self.spClStrt:        
        print '%3d   %s   %s'%(colNo,varNames[colNo],self.splist[colNo-self.spClStrt])
        self.spDict.update({varNames[colNo]:self.splist[colNo-self.spClStrt]})
      else:
        print '%3d   %s'%(colNo,varNames[colNo])
    self.varNames = varNames
    self.nsmp = (self.ncols - 1)/(len(varNames) - 1) 
    
  def getVarCols(self,varNames=None,smpNos=[]):
    # Find col numbers for variable names requested by user
     
    if varNames is None:
      varNames = self.varNames
    
    varCols = []
    addSmp  = True
    print self.colNames
    for varName in varNames:
      if varName in self.colNames:
        varCols.append(self.colNames.index(varName))
        addSmp = False
      elif varName in self.varNames:
        varCols.append(self.varNames.index(varName))
      elif self.nspc > 0 and varName in self.splist:
        varCols.append(self.splist.index(varName) + self.spClStrt)
      else:
        print 'Warning cannot find variable ',varName
        return
      print 'varName,varCol = ',varName,varCols[-1]

    if 'T' not in varNames:
      self.varCols = [0]            # Always add time as first user variable
      varNames.insert(0, 'T')
    nVar = len(self.varNames) - 1

    if len(smpNos) == 0 and addSmp:
      smpNos = [i for i in range(1,self.nsmp+1)]
    else:
      self.varCols = copy.copy(varCols)
      self.varCols.insert(0,0)

    for smpNo in smpNos:
      if int(smpNo) > self.nsmp:
        print 'smpNo(%d) > nsmp(%d)'%(int(smpNo),self.nsmp)
        return
      for varCol in varCols:
        self.varCols.append((int(smpNo)-1)*nVar + varCol)

    self.smpNos = smpNos
    
    return
    
  def setSpList(self,line):
    if '(' in line:
      self.splist = line.split('(')[1].split(')')[0].split(',')
      self.nspc   = len(self.splist)
      print 'nSp,spList = ',self.nspc,self.splist
    
  def setType(self):
    for line in fileinput.input(self.fsmp):
      #print 'Line no: ',fileinput.lineno(),line[:50]
      # Check first line to see if version is present
      if fileinput.lineno() == 1:
        if 'Version' in line:
          self.hdr = True
          continue
        else:
          self.hdr = False
          hdrLine  = line.strip()    # Check if the output is wrapped by 
          try:                       # checking if hdrLine is an integer
            self.ncols = int(hdrLine)
            self.wrap  = True
            self.varNames = []
            continue
          except ValueError:         # Does have integer so read col names
            self.skiprows = 1
            self.getColNames(line)
            break
      if self.hdr:
        # 
        # Section for SCICHEM 3.0 format
        #
        # If header is present then read smp from second line
        if fileinput.lineno() == 2:
          self.nsmp = int(line.split()[1])
          continue
        if fileinput.lineno() == 3:
          self.setSpList(line) 
          continue
        if fileinput.lineno() < self.nsmp + 3:
          continue
        if fileinput.lineno() == self.nsmp + 3:
          self.getColNames(line)
          self.skiprows = self.nsmp + 3
          break
      else:
        # 
        # Section for reading wrapped colNames from smp with no headers
        #      
        if len(self.varNames) < self.ncols:
          self.varNames.extend(line.strip().split())
          if len(self.varNames) == self.ncols:
            self.skiprows = fileinput.lineno() + 1
            self.getColNames(' '.join(self.varNames))
            break
          else:
            continue
      fileinput.close()
      
# Main program
      
if sys.argv.__len__() < 3:
  print 'Usage: printSmpCols.py smpFile varNames [smpNos]'
  sys.exit()

smpFile = sys.argv[1]

print 'smpFile = ',os.path.join(os.getcwd(),smpFile)

#Create DB for testing
prjName= smpFile.replace('.smp','')
mySciFiles = SCI.Files(prjName)

smpDb = '%s.smp.db'%(prjName)
print '%%%%%%%%%%%%', smpDb
    # Create database for calculated data 
    ## print 'Create smpDb ',smpDb,' in ',os.getcwd()
(smpDbConn,smpDbCur,smpCreateDb) = utilDb.Smp2Db(smpDb,mySciFiles)

outFile = open(smpFile.replace('.','_') + '.out','w')

varNames = sys.argv[2].split(',')
print 'varNames = ',varNames

smpNos = []
if sys.argv.__len__() == 4:
  smpNos = map(int,sys.argv[3].split(','))

mySmp = smp(smpFile)
mySmp.setType()

mySmp.getVarCols(varNames=varNames,smpNos=smpNos)

if len(mySmp.splist) > 0:
  for k,v in mySmp.spDict.items():
    for icol,colName in enumerate(mySmp.colNames):
      mySmp.colNames[icol] = colName.replace(k + '_',v + '_')
  
# Load sampler data
isFirst = True
chSize = 10000

if not mySmp.wrap:
  if isFirst:
    df  = pd.read_table(mySmp.fsmp,skiprows=mySmp.skiprows,sep=r'\s*',names=mySmp.colNames,iterator=True,chunksize=chSize)
    if mySmp.fasmp!=None:
      adf  = pd.read_table(mySmp.fasmp,skiprows=mySmp.skiprows,sep=r'\s*',names=mySmp.colNames,iterator=True,chunksize=chSize)
    isFirst = False
  else:
    df  = pd.read_table(mySmp.fsmp,sep=r'\s*',names=mySmp.colNames,chunksize=chSize)
    if mySmp.fasmp!=None:
      adf  = pd.read_table(mySmp.fasmp,sep=r'\s*',names=mySmp.colNames,chunksize=chSize)
smpDat = pd.concat(list(df), ignore_index=True) 
if mySmp.fasmp!=None: 
  asmpDat = pd.concat(list(adf), ignore_index=True) 

#for chunk in smpDat:
#  print 'chunk1 ',chunk

outFile.write("\n===================================\n")
outFile.write(" varName       Tmax(Days)         CMax(ug/m3)\n")  
outFile.write("====================================\n")

for colNo in mySmp.varCols:
  colName = smpDat.columns[colNo]
  
  cMax = smpDat[colName].max()
  iMax = smpDat[colName].idxmax()
  
  if colName == 'T':
    outFile.write('%8s %13.4e\n'%(colName,smpDat['T'][iMax]/(3600.*24.)))
  elif '_' in colName:
    outFile.write('%8s %13.4e %13.4e\n'%(colName,smpDat['T'][iMax]/(3600.*24.),cMax))
  else:
    outFile.write('%8s %13.4e %13.4e\n'%(colName,smpDat['T'][iMax]/(3600.*24.),cMax*1e+9))
  
outFile.write('\n')

if sys.argv.__len__() == 4 or len(mySmp.smpNos) == 0:
  colList = []
  for colNo in mySmp.varCols:
    if smpDat.columns[colNo] not in colList:
      colList.append(smpDat.columns[colNo])
  for colName in colList:
    outFile.write('%8s '%colName)
  outFile.write('\n')
  
  for row in range(len(smpDat['T'])):
    for colName in colList:
      #outFile.write('%13.4e'%(smpDat[colName][row]))
      outFile.write('%-10s' %(smpDat[colName][row]))

    outFile.write('\n')
  outFile.write('\n')
  myMaxConc = []  
  for cName in colList:
    #print smpDat[cName]
    if cName !='T':
      maxVal = max(smpDat[cName])
      print 'Max value for ', cName, maxVal, '\n'
      myMaxConc.append(maxVal)
      outFile.write('Max value for  %s, %-10s \n' %(cName, max(smpDat[cName])))
  #print max(myMaxConc)
  print myMaxConc  
  print 'Maximum conc is', max(myMaxConc) 
  maxVal = max(myMaxConc) 
  outFile.write('Maximum conc is %13.4e' %(maxVal) )

  
  #print myMaxConc.max()
# Create Plots

if True:
  plt.figure()
  plt.hold(True)
  plt.clf()
  for colNo in mySmp.varCols:
    colName = smpDat.columns[colNo]
    if colName == 'T':
      continue
    if mySmp.fasmp!=None:
      plt.plot(smpDat['T'],smpDat[colName]-asmpDat[colName], label="%s"%colName)
    else:
      plt.plot(smpDat['T'],smpDat[colName], label="%s"%colName)
  plt.title('Plot from %s'%colName)
  plt.legend(bbox_to_anchor=(0.9,0.96),ncol=1)
  plt.hold(False)
  plt.savefig('%s.png'%colName)
  print 'Created %s.png\n'%colName
    
