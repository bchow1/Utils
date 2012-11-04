#!/bin/env python
import os
import sys
import re
import fileinput
import numpy as np
import matplotlib.pyplot as plt

class tstSuite:
  
  def __init__(self,name):
    print 'Create mySuite ',name
    self.name    = name
    self.inpDir  = []
    self.outDir  = []
    self.prjList = []
    self.pltList = []

  def addInpDir(self,inpDir):
    self.inpDir.append(inpDir)
  
  def addOutDir(self,outDir):
    self.outDir.append(outDir)
  
  def addPrj(self,prjName):
    self.prjList.append(prjName)
    
  def addPlt(self,pltName):
    self.prjList.append(pltName)

os.chdir('D:\\TestHPAC\\Scripts')
suiteList = []
mySuite   = None
isCase    = False
for line in fileinput.input('runlist.sh'):
  if "case" in line:
    isCase = True
    prjDir = None
    continue
  if "esac" in line:
    isCase = False
    break
  if isCase:
    if line.rstrip().endswith('")'):
      if mySuite is not None:
        suiteList.append(mySuite)
      mySuite = tstSuite(line.strip().replace(')','').replace('"',''))
    if "DIR=" in line:
      line  = line.strip().replace('"','').replace(';','')
      dName = line.split('=')[1].replace('${RUN}',mySuite.name)
      if "INPDIR=" in line:
        mySuite.addInpDir(dName)
      elif "OUTDIR=" in line:
        mySuite.addOutDir(dName)
      else:
        prjDir = dName
        print prjDir
    if "PrjList" in line:
      prjNames = line.split('=')[1].replace('${PrjList[@]}','').replace(';','').replace('(','').replace(')','').split()
      for prjName in prjNames:
        if prjDir is not None:
          prjName = prjName.replace('${DIR}',prjDir)
        mySuite.addPrj(prjName)
fileinput.close()

pattNpuff = re.compile('.*\s+t\s*=\s*(\d*\.\d*)\s*.*\s+NPUFF\s*=\s*(\d+).*',re.I)
pattCmplt = re.compile('.*\s+Time\s*=\s*(\d*\.\d*)\s*.*',re.I)
outDir = '120727.1900'
os.chdir('D:\\TestHPAC\\Outputs')      
for suite in suiteList: 
  print suite.name
  print suite.inpDir
  print suite.outDir
  prjDir = suite.outDir[0].replace('$OUTPUTS',outDir)
  print prjDir
  if os.path.exists(prjDir):
    for prjNo,prjName in enumerate(suite.prjList):
      prjLog = os.path.join(prjDir,prjName+'.log')
      if os.path.exists(prjLog):
        print 'Found :',prjLog
        puffNos = []
        for line in fileinput.input(prjLog):
          if line.startswith("Output completed at"):
            matchNpuff = pattNpuff.match(line.strip())
            if matchNpuff:
              puffNos.append(map(float,(matchNpuff.group(1),matchNpuff.group(2))))
          if line.startswith('Normal termination'):
            matchCmplt = pattCmplt.match(line.strip())              
            print 'Normal',float(matchCmplt.group(1))
      else:
        print 'Missing :',prjLog
      if len(puffNos) > 0:
        puffNos = np.array(puffNos)
        plt.clf()
        plt.plot(puffNos[:,0],puffNos[:,1])
        figName = suite.name+'%02d'%prjNo+'.png'
        print os.getcwd(),figName
        plt.savefig(figName)
      print puffNos
      sys.exit()
      
  
      
      
    