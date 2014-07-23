#!/bin/python

import os
import sys
import fileinput
import numpy as np
import matplotlib.pyplot as plt

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

os.chdir('d:\\SCIPUFF\\runs\\EPRI\\AECOM\\Gibson\\SCICHEM\\Gibson_090423')
 
'''
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
'''
csvFiles = ['blr5_fix_nosplit_puf.csv','blr5_fix_puf.csv']
nFiles   = len(csvFiles)

#for i in range(1,nFiles):
#  csvFiles.append(sys.argv[i])

pDat = [[] for i in range(nFiles)]
#print 'csvFiles = ',csvFiles

#nameList = sys.argv[2].split(',')
#nameList = 'ipuf,x,y,z,sxx,sxy,sxz,syy,syz,szz,c'.split(',')
nameList = 'y,szz,zwc,c,z,wc'.split(',')


#print 'nameList = ',nameList

opers   = [ '+','-','*','/']

csvFile = csvFiles[0]

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
    
    colNos  = []
    opStrs  = []
    opNames = []
    
    for varName in nameList:
      
      if any(oper in varName for oper in opers):
        rStrng =  eqn_split(varName, opers, varNames)
        opNames.append(varName)
        opStrs.append(rStrng)
        colNos.append(-len(opStrs))
      else:
        print varName.upper(),varNames.index(varName.upper())
        colNos.append(varNames.index(varName.upper()))
              
    for colno in colNos:
      if colno < 0:
        sys.stdout.write('%14s '%opNames[-colno-1])    
      else:    
        sys.stdout.write('%14s '%varNames[colno])
    sys.stdout.write('\n')
                     
    break
    
fileinput.close()

for fNo,csvFile in enumerate(csvFiles):
        
  for line in fileinput.input(csvFile):
      
    if fileinput.lineno() < 4:
      continue

    if line.strip()[-1] == ',':
      line = line.strip()[:-1]
    colVals = map(float,line.split(','))
    
    for colno in colNos:
      if colno < 0:  
        sys.stdout.write('%14.4e '%eval(opStrs[-colno-1]))
      else:
        sys.stdout.write('%14.4e '%colVals[colno])
    sys.stdout.write('\n')
      
    nameVals = {}
    for varNo,colNo in enumerate(colNos):
      nameVals.update({nameList[varNo]:colVals[colNo]})
 
    colVals  = []        
    for vName in nameList: 
      if vName == 'ipuf':
        colVals.append(int(nameVals[vName]))
      else:
        colVals.append(nameVals[vName])
        
    #if fileinput.lineno() == 4:
    #  sys.stdout.write('\n')
    #  print colVals

    pDat[fNo].append(tuple(colVals))
  
  fileinput.close()
  
  print 'File ',fNo+1
  print pDat[fNo][0]
  print pDat[fNo][-1]
  print 

#if nFiles == 1:
for fNo,csvFile in enumerate(csvFiles):
  
  p1 = np.array(pDat[fNo])
  print p1.shape
  
  # Y distance from source 
  p1[:,0] = (p1[:,0] - 4247.423)*1000.

  #p2 = np.array(pDat[1])
  #print p2.shape

  fig = plt.figure(1)
  plt.clf()
  plt.hold(True)
  plt.setp(plt.gca(),frame_on=False,xticks=(),yticks=())

  sub1 = fig.add_subplot(2,2,1)
  sub1.scatter(p1[:,0],np.sqrt(p1[:,1]),marker='+',color='g')
  sub1.set_xlim([0,3000.])
  #sub1.set_xscale('log')
  sub1.set_xlabel('x')
  #sub1.set_ylabel('sxz/sqrt(sxx*szz) syz/sqrt(syy*szz)')
  sub1.set_ylabel('sz')
  #sub1.set_yscale('log')
  #sub1.set_ylim([1e-4,1e2])

  sub2 = fig.add_subplot(2,2,2)
  sub2.scatter(p1[:,0],p1[:,2]/p1[:,3],marker='+',color='g')
  sub2.set_xlim([0.,3000.])
  #sub2.set_xscale('log')
  sub2.set_xlabel('x')
  sub2.set_ylabel('zwc')
  sub2.yaxis.tick_right()
  #sub2.yaxis.set_label_position("right")
  #sub2.set_yscale('log')
  #sub2.set_ylim([1e-4,1e2])
  
  sub2 = fig.add_subplot(2,2,3)
  sub2.scatter(p1[:,0],p1[:,4],marker='+',color='g')
  sub2.set_xlim([0.,3000.])
  #sub2.set_xscale('log')
  sub2.set_xlabel('x')
  sub2.set_ylabel('z')
  
  sub2 = fig.add_subplot(2,2,4)
  sub2.scatter(p1[:,0],p1[:,5]/p1[:,3],marker='+',color='g')
  sub2.set_xlim([0.,3000.])
  #sub2.set_xscale('log')
  sub2.set_xlabel('x')
  sub2.set_ylabel('wc')
  sub2.yaxis.tick_right()
  #sub2.yaxis.set_label_position("right")

  plt.hold(False)
  figName = csvFile.replace('.csv','') + '_zwc' + '.png'
  print figName
  plt.savefig(figName)
