#!/bin/python

import os
import sys
import re
import fileinput

eqTyPatt = re.compile(';\s*(\d+).*')

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
  print 'F: ',nFast,', S: ',nSlow,', P: ',nPart,', E: ',nEqul,', A: ',nAmbt,\
        'Total: ',nFast+nSlow+nPart+nEqul+nAmbt
  return(spList,eqList)

def getEqns(spNam,eqList):
  print spNam
  nEqn = 0
  for eqVal in eqList:
    indx = eqVal.index(';')
    eqn = eqVal[:indx]
    if spNam in eqn:
      nEqn += 1
      print nEqn,':',eqn
  return

def getEqTypes(eqTyp,eqList):
  for eqVal in eqList:
    indx = eqVal.index(';')
    typNo = eqVal[indx+1]
    if typNo == eqTyp:
      print eqVal
  return
    
if __name__ == "__main__":
  if sys.platform == 'win32':
    os.chdir('d:\\EPRI\\git\\runs\\cumberland')
  #fName = '071599_vo3.imc'
  fName = 'tva_990706_ae5.imc'
  #fName = raw_input('Enter imc file name :')
  #if len(fName) > 1:
  #  if not fName.endswith('.imc'):
  #    fName = fName + '.imc'
  spList,eqList = readImc(fName)
  #print spList
  '''
  ambList = []
  for spVal in spList:
    spTyp = spVal[1]
    if spTyp != 'E':
      ambList.append(spVal[0])
  nsp = len(ambList)+1
  print nsp
  newAmbFile = open('newAmb.dat','w')
  for line in fileinput.input('ambient.dat'):
    if fileinput.lineno() == 1:
      newAmbFile.write('%s'%line)
      newAmbFile.write('%d\n'%(nsp-1))
      for ambName in ambList:
        newAmbFile.write('%8s\n'%ambName)
    else :
      newAmbFile.write('%s'%line)
    spNo = (fileinput.lineno()-3)%nsp
    #if spNo >= 0 and spNo < 36:
    #  print spNo+1,ambList[spNo],line.strip()
    #if fileinput.lineno()/nsp == 2:
    #  break
  #spNam = raw_input('Enter species name :')
  #spNam = '['+spNam.strip()+']'
  #getEqns(spNam,eqList)
  '''
  eqTyp = raw_input('Enter equation type :')
  eqTyp = eqTyp.strip()
  getEqTypes(eqTyp,eqList)
