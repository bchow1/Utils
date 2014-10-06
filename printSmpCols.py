#!/bin/python
import sys
import fileinput
import numpy as np
import pandas as pd

class smp(object):
    
  def __init__(self,fSmp,fSam=None):
    self.fsmp     = fSmp
    self.fsam     = fSam
    self.wrap     = False
    self.splist   = []
    self.nspc     = 0
    self.spClStrt = 9999
    self.hdr      = False
    self.nsmp     = 1
    self.smpNo    = [1] 
    self.ncols    = 3
    self.colNames = ["T","C001","V001"]
    self.varNames = ["T","C","V"]
    self.pltNames = ["Time","Concentration","Variance"]
    self.varCols  = []
    self.nTime    = 1
    self.Times    = [0.,]
    self.skiprows = 1
    
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
      if colName.endswith('C002') or colName.endswith('D002'):
        break
      if self.nspc > 0 and colNo >= self.spClStrt:        
        print '%3d   %s   %s'%(colNo,varNames[colNo],self.splist[colNo-self.spClStrt])
      else:
        print '%3d   %s'%(colNo,varNames[colNo])
    self.varNames = varNames
    self.nsmp = (self.ncols - 1)/(len(varNames) - 1) 
    
  def getVarCols(self,varNames=None,smpNos=[]):
    # Find col numbers for variable names requested by user
     
    if varNames is None:
      varNames = self.varNames
    
    varCols = []
    for varName in varNames:
      if varName in self.varNames:
        varCols.append(self.varNames.index(varName))
        #print 'varName,varCol = ',varName,varCols[-1]
      elif self.nspc > 0 and varName in self.splist:
        varCols.append(self.splist.index(varName) + self.spClStrt)
        #print 'varName,varCol = ',varName,varCols[-1]
      else:
        print 'Warning cannot find variable ',varName
        return
      
    if len(smpNos) == 0:
      smpNos = [i for i in range(1,self.nsmp+1)]

    if 'T' not in varNames:
      self.varCols = [0]            # Always add time as first user variable
      varNames.insert(0, 'T')
    nVar = len(self.varNames) - 1
    for smpNo in smpNos:
      if int(smpNo) > self.nsmp:
        print 'smpNo(%d) > nsmp(%d)'%(int(smpNo),self.nsmp)
        return
      for varCol in varCols:
        self.varCols.append((int(smpNo)-1)*nVar + varCol)
    
    return
    
  def setSpList(self,line):
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
print 'smpFile = ',smpFile

varNames = sys.argv[2].split(',')
print 'varNames = ',varNames

smpNos = []
if sys.argv.__len__() == 4:
  smpNos = map(int,sys.argv[3].split(','))

mySmp = smp(smpFile)
mySmp.setType()

mySmp.getVarCols(varNames=varNames,smpNos=smpNos)

# Load sampler data

if not mySmp.wrap:
  smpDat = pd.read_table(mySmp.fsmp,skiprows=mySmp.skiprows,sep=r'\s*',names=mySmp.colNames)

print "\n==================================="
print ' varName       Min           Max'  
print "===================================="
for colNo in mySmp.varCols:
  colName = smpDat.columns[colNo]
  print '%8s %13.4e %13.4e'%(colName,smpDat[colName].min(),smpDat[colName].max())
print '\n'

'''

for line in fileinput.input(smpFile):
 
  if lHeader:
    if fileinput.lineno() == nSmp + 3:
      spColStart,varNames,colNames = getColStart(line,getColNames=True)
      print 'spNames = ',spNames
      for smpNo in smpNos:
        for spNo,spName in enumerate(spNames):
          icol = spColStart + (spColStart - 1 + nSp)*(smpNo-1) + spCol[spNo]
          sys.stdout.write('%3d:%s '%(icol+1,colNames[icol]))
      sys.stdout.write('\n')
      lHeader = False
      continue
  if not lHeader and spColStart < 0:
    spColStart,varNames = getColStart(' '.join(colNames))
    nVar = len(varNames)
    print nVar,varNames #,colNames
    colNos = []
    for smpNo in smpNos:
      for varNo,varName in enumerate(spNames):
        icol = 2 + varNames.index(varName)+ (smpNo-1)*nVar
        colNos.append(icol)
        # Verify
        print 'Variable Name: ',varName,' ,Sampler No. = ',smpNo,' , ColNo = ',icol,'  ColName = ',colNames[icol-1]
  try:
    colVals = map(float,line.split())
    if lWrap:
      if len(wrapColVals) < len(colNames):
        wrapColVals.extend(colVals)
      if len(wrapColVals) < len(colNames):
        continue
  except ValueError:
    print 'Skip line ',line.strip()
    continue
  #print fileinput.lineno(),': ',line[:50]
  if lHeader:
    sys.stdout.write('%13.4e %13.4e '%(colVals[0]/3600.,colVals[1]))
    for spNo,spName in enumerate(spNames):
      for smpNo in smpNos:
        icol = spColStart + (spColStart - 1 + nSp)*(smpNo-1) + spCol[spNo]
        sys.stdout.write('%13.4e'%colVals[icol])
    sys.stdout.write('\n')
  else:
    if lWrap:
      colVals = wrapColVals
      wrapColVals = []   
    sys.stdout.write('%13.4e  '%(colVals[0]/3600.))
    for colNo in colNos:
      sys.stdout.write('%13.4e'%colVals[colNo])
    sys.stdout.write('\n')
'''