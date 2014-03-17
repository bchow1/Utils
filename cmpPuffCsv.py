#!/bin/python

import os
import sys
import fileinput

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
    
    colnos   = []
    for varName in nameList:
      colnos.append(varNames.index(varName.upper()))
    print colnos 
    
    break

fileinput.close()

print 

for colno in colnos:
  sys.stdout.write('%14s '%varNames[colno])
sys.stdout.write('\n')


for line in fileinput.input(csvFile):
  if fileinput.lineno() < 4:
    continue
  colvals = line.strip().split(',')
  for colno in colnos:
    sys.stdout.write('%14s '%colvals[colno])
  sys.stdout.write('\n')

fileinput.close()

