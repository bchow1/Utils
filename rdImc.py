#!/bin/python

import os
import sys
import fileinput

def readImc(fName):
  rdMode = 'Unknown'
  spList = []
  eqList = []
  for line in fileinput.input(fName):
    if line.startswith('#'):
      fChar = line[1:2].upper()
      if fChar == 'C':
        rdMode = 'Ctrl'
      elif fChar == 'Q':
        rdMode = 'AqAer'
      elif fChar == 'S':
        rdMode = 'Sps'
      elif fChar == 'T':
        rdMode = 'Tbl'
      elif fChar == 'B':
        rdMode = 'Bal'
      elif fChar == 'E':
        rdMode = 'Eqn'
      else:
        rdMode = 'Unknown'
      continue
    if len(line) > 1:
      if rdMode == 'Sps':
        spList.append(line.strip().split())
      if rdMode == 'Eqn':
        eqList.append(line.strip().split())
  # print species type
  nFast = 0
  nSlow = 0 
  nPart = 0 
  nEqul = 0 
  nAmbt = 0 
  for spVal in spList:
    spNam = '['+spVal[0].strip()+']'
    spTyp = spVal[1]
    if spTyp == 'F':
      nFast += 1
    elif spTyp == 'S':
      nSlow += 1
    elif spTyp == 'P':
      nPart += 1
    elif spTyp == 'E':
      nEqul += 1
    elif spTyp == 'A':
      nAmbt += 1
    #print '\n=========='
    #print 'Species = ',spNam
    #print '=========='
    nEqn = 0
    for eqVal in eqList:
      indx = eqVal.index(';')
      eqn = eqVal[:indx]
      if spNam in eqn:
        #print eqn
        nEqn += 1
    print spNam,spTyp,nEqn
  print nFast,nSlow,nPart,nEqul,nAmbt, nFast+nSlow+nPart+nEqul+nAmbt
  
  return
    
if __name__ == "__main__":
    fName = raw_input('Enter imc file name :')
    if len(fName) > 1:
      if not fName.endswith('.imc'):
        fName = fName + '.imc'
    readImc(fName)
