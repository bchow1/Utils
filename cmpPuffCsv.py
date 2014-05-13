#!/bin/python

import os
import sys
import fileinput
import numpy as np
import matplotlib.pyplot as plt

#os.chdir('d:\\SCIPUFF\\runs\\HPAC\\omp\\simple\\lomp')

csvFiles = []
nFiles   = sys.argv.__len__()
if nFiles < 2:
  print 'For Plotting: '
  print 'Usage: cmpPuffCsv.py csvFile1 csvFile2'
  print
  print 'Else: '
  print 'Usage: cmpPuffCsv.py csvFile'
  print
  sys.exit()
elif nFiles == 1:
  print
  print 'Skipping Plotting'
  print

for i in range(1,nFiles):
  csvFiles.append(sys.argv[i])

pDat = [[] for i in range(1,nFiles)]
#print 'csvFiles = ',csvFiles
  
#nameList = sys.argv[2].split(',')
nameList = 'ipuf,x,y,z,sxx,sxy,sxz,syy,syz,szz,c'.split(',')

#print 'nameList = ',nameList

for fNo,csvFile in enumerate(csvFiles):

  if not os.path.exists(csvFile):
    print 'Error: cannot find csvFile = ',csvFile
  print 'csvFile = ',csvFile

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
      
      colNos = []
      for varName in nameList:
        colNo = varNames.index(varName.upper())
        colNos.append(colNo)
        #print colNo,varName
      
      #for colno in colNos:
      #  sys.stdout.write('%14s'%varNames[colno])
      #sys.stdout.write('\n')


    if fileinput.lineno() < 4:
      continue

    colVals = map(float,line.strip().split(',')[0:-1])

    nameVals = {}
    for varNo,colNo in enumerate(colNos):
      nameVals.update({nameList[varNo]:colVals[colNo]})
   
    '''
    if fileinput.lineno() == 4:
      for varName in ['ipuf','x','y','z','c','sxz','szz','sxx','syz','syy']:
        colNo = varNames.index(varName.upper())
        sys.stdout.write('%7s(%2d) '%(varName,colNo))
      sys.stdout.write('\n')
    #colVals = [int(nameVals['ipuf']),nameVals['x'],nameVals['y'],nameVals['z'],nameVals['c'],\
    #             nameVals['sxz']/np.sqrt(nameVals['szz']*nameVals['sxx']), nameVals['syz']/np.sqrt(nameVals['szz']*nameVals['syy'])]
    '''

    colVals  = []
    # Variables names required for printing or plotting
    varNames = ['ipuf','x','y','z','c','sxx','sxy','sxz','syy','syz','szz']
    for varName in varNames 
      if varName == 'ipuf':
        colVals.append(int(nameVals[varName]))
      else:
        colVals.append(nameVals[varName])
      if fileinput.lineno() == 4:
        sys.stdout.write('%7s(%2d) '%(varName,colNo))
    if fileinput.lineno() == 4:
      sys.stdout.write('\n')
      print colVals

    pDat[fNo].append(tuple(colVals))
  
    # ipuf 
    maxLine = 100
    if  fileinput.lineno() < maxLine:
      for colVal in colVals:
        sys.stdout.write(' %10.3e '%colVal)
      sys.stdout.write('\n')
    elif fileinput.lineno() == maxLine: 
      sys.stdout.write('\n')
      break

  fileinput.close()
  print pDat[fNo][0],pDat[fNo][-1]

if nFiles < 2:
  p1 = np.array(pDat[0])
  print p1.shape

  p2 = np.array(pDat[1])
  print p2.shape

  fig = plt.figure(1)
  plt.clf()
  plt.hold(True)
  plt.setp(plt.gca(),frame_on=False,xticks=(),yticks=())

  sub1 = fig.add_subplot(2,1,1)
  sub1.scatter(p1[:,4],p1[:,5],marker='+',color='g')
  sub1.scatter(p2[:,4],p2[:,5],marker='x',color='b')
  sub1.set_xlim([1e-6,1.])
  sub1.set_xscale('log')
  sub1.set_xlabel('C')
  #sub1.set_ylabel('sxz/sqrt(sxx*szz) syz/sqrt(syy*szz)')
  sub1.set_ylabel('sxz/sxx_szz')
  sub1.set_yscale('log')
  sub1.set_ylim([1e-4,1e2])

  sub2 = fig.add_subplot(2,1,2)
  sub2.scatter(p1[:,4],p1[:,6],marker='+',color='g')
  sub2.scatter(p2[:,4],p2[:,6],marker='x',color='b')
  sub2.set_xlim([1e-6,1.])
  sub2.set_xscale('log')
  sub2.set_xlabel('C')
  sub2.set_ylabel('syz/syy_szz')
  sub2.set_yscale('log')
  sub2.set_ylim([1e-4,1e2])

  plt.hold(False)
  figName = csvFile[0].replace('.csv','') + csvFile[0].replace('.csv','') + '.png'
  print figName
  plt.savefig(figName)
