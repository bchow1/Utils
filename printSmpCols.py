#!/bin/python
import sys
import fileinput

print sys.argv.__len__() 

if sys.argv.__len__() < 3:
  print 'Usage: printSmpCols.py smpFile spNames [smpNos]'
  sys.exit()

smpFile = sys.argv[1]
print 'smpFile = ',smpFile

spNames = sys.argv[2].split(',')
#print 'spNames = ',spNames

smpNos = []
if sys.argv.__len__() == 4:
  smpNos = sys.argv[3].split(',')

for line in fileinput.input(smpFile):
  #print fileinput.lineno()
  if fileinput.lineno() == 1:
    if 'Version' in line:
      lHeader = True
    else:
      lHeader = False
    continue
  if lHeader:
    if fileinput.lineno() == 2:
      nSmp = int(line.split()[1])
      #print 'nSmp = ',nSmp
      if len(smpNos) == 0:
        smpNos = [ i+1 for i in range(nSmp) ]
      #print 'smpNos = ',smpNos
      continue
    if fileinput.lineno() == 3:
      spList = line.split('(')[1].split(')')[0].split(',')
      nSp = len(spList)
      print 'nSp,spList = ',nSp,spList
      spCol = []
      for spName in spNames:
        spCol.append(spList.index(spName))
      #print 'spCol = ',spCol 
      continue
    if fileinput.lineno() < nSmp + 3:
      continue
    if fileinput.lineno() == nSmp + 3:
      colNames = line.split()
      print 'colNames = ',colNames
      spColStart = 0
      for colNo,colName in enumerate(colNames):
        if colName.endswith('_001'):
          spColStart = colNo
          break
      #print 'spColStart = ',spColStart
      print 'spNames = ',spNames
      for smpNo in smpNos:
        for spNo,spName in enumerate(spNames):
          icol = spColStart + (spColStart - 1 + nSp)*(smpNo-1) + spCol[spNo]
          sys.stdout.write('%3d:%s '%(icol+1,colNames[icol]))
      sys.stdout.write('\n')
      lHeader = False
      continue
  else:
    pass
  #print fileinput.lineno(),': ',line[:50]
  colVals =map(float,line.split())
  sys.stdout.write('%13.4e %13.4e '%(colVals[0]/3600.,colVals[1]))
  for spNo,spName in enumerate(spNames):
    for smpNo in smpNos:
      icol = spColStart + (spColStart - 1 + nSp)*(smpNo-1) + spCol[spNo]
      sys.stdout.write('%13.4e'%colVals[icol])
  sys.stdout.write('\n')
