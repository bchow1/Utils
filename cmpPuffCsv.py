#!/bin/python

import os
import sys
import fileinput

def my_split(s, seps):
  res = [s]
  for sep in seps:
    s, res = res, []
    for seq in s:
      res += seq.split(sep)
  return res

def eqn_split(strng, seps, vnames):
  for sep in seps:
    strng = strng.replace(sep,',%s,'%sep)
  strng = strng.split(',')
  res = ''
  for str in strng:
    try:
      indx = vnames.index(str.upper())
      res += 'colvals[%d]'%indx
    except ValueError:
      res += str
  return res

#os.chdir('d:\\SCIPUFF\\runs\\HPAC\\omp\\simple\\lomp')

csvFile  = sys.argv[1]
nameList = sys.argv[2].split(',')

print 'nameList = ',nameList

if not os.path.exists(csvFile):
  print 'Error: cannot find csvFile = ',csvFile
print 'csvFile = ',csvFile

for line in fileinput.input(csvFile):

  if fileinput.lineno() == 1:
    title,tvalue = line.split(',')
    npuf = int(tvalue.split('=')[-1].split('"')[0])
    print 'npuf = ',npuf

  if fileinput.lineno() == 2:
    nvar = int(line.split(',')[1])
    print 'nvar = ',nvar

  if fileinput.lineno() == 3:
    varNames = line.split(',')
    for vNo, varName in enumerate(varNames):
      varNames[vNo] = varName.replace('"','').upper()
    print varNames
    
    colnos  = []
    opStrs  = []
    opNames = []
    opers   = [ '+','-','*','/']
    for varName in nameList:
      if any(oper in varName for oper in opers):
        rStrng =  eqn_split(varName, opers, varNames)
        opNames.append(varName)
        opStrs.append(rStrng)
        colnos.append(-len(opStrs))
      else:
        colnos.append(varNames.index(varName.upper()))
    print colnos 
    
    break

fileinput.close()

print 

for colno in colnos:
  if colno < 0:
    sys.stdout.write('%14s '%opNames[-colno-1])    
  else:    
    sys.stdout.write('%14s '%varNames[colno])
sys.stdout.write('\n')

for line in fileinput.input(csvFile):
  if fileinput.lineno() < 4:
    continue
  if line.strip()[-1] == ',':
    line = line.strip()[:-1]
  colvals = map(float,line.split(','))
  for colno in colnos:
    if colno < 0:  
      sys.stdout.write('%14.4e '%eval(opStrs[-colno-1]))
    else:
      sys.stdout.write('%14.4e '%colvals[colno])
  sys.stdout.write('\n')

fileinput.close()


