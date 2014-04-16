#!/bin/python

import os
import sys
import fileinput
import numpy as np
import matplotlib.pyplot as plt

#os.chdir('d:\\SCIPUFF\\runs\\HPAC\\omp\\simple\\lomp')

csvFile  = sys.argv[1]
nameList = sys.argv[2].split(',')

#print 'nameList = ',nameList

if not os.path.exists(csvFile):
  print 'Error: cannot find csvFile = ',csvFile
#print 'csvFile = ',csvFile

for line in fileinput.input(csvFile):

  if fileinput.lineno() == 1:
    title,tvalue = line.split(',')
    npuf = int(tvalue.split('=')[-1].split('"')[0])
    #print 'npuf = ',npuf

  if fileinput.lineno() == 2:
    nvar = int(line.split(',')[1])
    #print 'nvar = ',nvar

  if fileinput.lineno() == 3:
    varNames = line.split(',')
    for vNo, varName in enumerate(varNames):
      varNames[vNo] = varName.replace('"','').upper()
    #print varNames
    
    colnos   = []
    for varName in nameList:
      colnos.append(varNames.index(varName.upper()))
    #print colnos 
    
    break

fileinput.close()
#print 

#for colno in colnos:
#  sys.stdout.write('%14s'%varNames[colno])
for varName in ['ipuf','x','y','z','c','sqrt(szz/sxx)','sqrt(szz/syy)']:
  sys.stdout.write('%14s '%varName)
sys.stdout.write('\n')

pDat = []

for line in fileinput.input(csvFile):
  if fileinput.lineno() < 4:
    continue
  colVals = map(float,line.strip().split(',')[0:-1])
  nameVals = {}
  for varNo,colNo in enumerate(colnos):
    nameVals.update({nameList[varNo]:colVals[colNo]})

  colVals = [int(nameVals['ipuf']),nameVals['x'],nameVals['y'],nameVals['z'],nameVals['c'],np.sqrt(nameVals['szz']/nameVals['sxx']),np.sqrt(nameVals['szz']/nameVals['syy'])]
  pDat.append(colVals) 
  
  # ipuf 
  #for colVal in colVals:
  #  sys.stdout.write(' %13.5e '%colVal)
  #sys.stdout.write('\n')

  #if  fileinput.lineno() > 100:
  #  break

fig = plt.figure(1)
plt.clf()
plt.hold(True)
plt.setp(plt.gca(),frame_on=False,xticks=(),yticks=())

pDat = np.array(pDat)
sub1 = fig.add_subplot(2,1,1)
sub1.scatter(pDat[:,5],pDat[:,3]/1000.,marker='o',color='g')
sub1.scatter(pDat[:,6],pDat[:,3]/1000.,marker='s',color='b')
sub1.set_xlim([1e-4,1e2])
sub1.set_xscale('log')
sub1.set_xlabel('sz/sx')
sub1.set_ylim([0,8])
sub1.set_ylabel('Z')

sub2 = fig.add_subplot(2,1,2)
sub2.scatter(pDat[:,4],pDat[:,5],marker='o',color='g')
sub2.scatter(pDat[:,4],pDat[:,6],marker='o',color='b')
sub2.set_xlim([1e-6,1.])
sub2.set_xscale('log')
sub2.set_xlabel('C')
sub2.set_ylim([1e-4,1e2])
sub2.set_yscale('log')
sub2.set_ylabel('sz/sx')

plt.hold(False)
figName = csvFile
figName = figName.replace('.csv','.png')
print figName
plt.savefig(figName)
fileinput.close()
