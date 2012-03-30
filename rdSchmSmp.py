#
import os
import sys
import fileinput
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mpl as mpl

import utilPlot

if os.system == 'NT':
  os.chdir('d:\\EPRI\\git\\runs\\tva')
else:
  os.chdir('/usr/pc/biswanath/EPRI/git/runs/tva')

samList = []
for line in fileinput.input('tva_990706.sam'):
  if fileinput.lineno() != 1:
    samList.append(map(float,line.split()))
nSampler = len(samList)

'''
fig = plt.figure()
fig.hold(True)
for sNo in range(1,len(samList)+1):
  sLoc = [samList[sNo-1][0],samList[sNo-1][1]]
  #print sNo,sLoc
  plt.scatter(sLoc[0],sLoc[1])
  if sNo%100 == 0:
    plt.text(sLoc[0],sLoc[1]+5,'%03d'%sNo)

fig.hold(False)
plt.savefig('sampLoc.png')
'''

iVar = 0
varList = []
for line in fileinput.input('gas_aero_hg_4TVA1_WRF_1a.smp'):
  if fileinput.lineno() == 1:
    nVar = int(line.strip())
  else:
    vList = line.strip().split()
    for vName in vList:
      varList.append(vName)
    iVar = iVar + len(vList)
    if iVar >= nVar:
      dataStart = fileinput.lineno() + 2
      break
fileinput.close()
print varList[:10]
print varList[-10:]

spNames = []
for varName in varList:
  if varName.endswith('001'):
    spNames.append(varName[:-3])

nSpecies = len(spNames)

print nSpecies,spNames
print nVar,1+nSpecies*nSampler

spList = ['O3','NO2','C']
spLog  = [ False,True,True]

# Create data files for individual species 
if not os.path.exists('Sampler_%s.dat'%spList[0]):

  colNos = [[] for sp in spList]
  fileNos = []
  for spNo,sp in enumerate(spList):
    fileNos.append(open('Sampler_%s.dat'%sp,'w'))

  for spNo,sp in enumerate(spList):
    print spNo,sp
    for isp, spName in enumerate(spNames):
      if spName == sp:  
        for ismp in range(nSampler):
          colNos[spNo].append(1+nSpecies*ismp+isp)
        continue

  for line in fileinput.input('tva_990706.smp'):
    if fileinput.lineno() == dataStart-1:
      print line
    if fileinput.lineno() >= dataStart:
        dataList = []
        for dataValue in line.strip().split():
          try:
            dataList.append(np.float(dataValue.lstrip()))
          except ValueError:
            continue
        print dataList[0]
        for spNo,sp in enumerate(spList):
          fileNos[spNo].write('%15.5e '%dataList[0])
          for colNo in colNos[spNo]:
            #print colNo,varList[colNo]
            fileNos[spNo].write('%15.5e '%dataList[colNo])
          fileNos[spNo].write('\n')
  fileinput.close() 
  for spNo,sp in enumerate(spList):
    fileNos[spNo].close()

# Plot species concentration for each species for all times
samArray = np.array(samList)
xSmp = np.array(samArray[:,0])
ySmp = np.array(samArray[:,1])
print 'xSmp min max = ',xSmp.min(),xSmp.max(),len(xSmp)
print 'ySmp min max = ',ySmp.min(),ySmp.max(),len(ySmp)

myPlot = utilPlot.Plot(clrLev=-1)
cax = myPlot.plt.axes([0.9,0.1,0.03,0.8])

for spNo,sp in enumerate(spList):
  
  print sp
  spDat = np.loadtxt('Sampler_%s.dat'%sp)
  tArray = spDat[:,0]
  print 'First time = %10.3f, nSmp = %d'%(tArray[0],np.size(spDat[0,1:]))
  print 'Concs = ',spDat[0,1:],'\n'
  print 'Last time = %10.3f, nSmp = %d'%(tArray[-1],np.size(spDat[-1,1:]))
  print 'Concs = ',spDat[-1,1:],'\n'

  if spLog[spNo]:
    clrMax = int(np.ceil(np.log(spDat[:,1:].max())))
    clrMin = max(int(np.ceil(np.log(max(spDat[:,1:].min(),1e-20)))),clrMax-7)
    clrLev = clrMax-clrMin
  else:
    clrMax = spDat[:,1:].max()
    clrMin = max(0.,spDat[:,1:].min())
    clrLev = 8

  print spDat[:,1:].min(),spDat[:,1:].max(),clrMin,clrMax,clrLev

  #negIndx = np.where(spDat[:,1:] < 0)
  #print negIndx
  #for i,indx in enumerate(negIndx[:][0]):
  #  print tArray[indx],xSmp[negIndx[1][i]],ySmp[negIndx[1][i]],spDat[indx,negIndx[1][i]]
    
  myPlot.setClrLev(clrLev=clrLev,clrMin=clrMin,clrMax=clrMax,logScale=spLog[spNo])

  fList = []
  for tNo,tVal in enumerate(tArray):
    print 'plotting for time %10.3f'%tVal
    fig = myPlot.plt.figure()
    fig.hold(True)
    myPlot.plt.title('%s at time %g'%(sp,tVal))
    cDat = spDat[tNo,1:]
    cbar = myPlot.plt.scatter(xSmp[::30],ySmp[::30],c=cDat[::30],edgecolors='none',marker='o',\
                              vmin=myPlot.vmin,vmax=myPlot.vmax,cmap=myPlot.clrMap,norm=myPlot.lnorm)
    #cbl = mpl.colorbar.ColorbarBase(cax,cmap=myPlot.clrMap,norm=myPlot.lnorm,ticks=myPlot.levels)
    #cbl.set_ticklabels(myPlot.levels)
    fig.colorbar(cbar)
    fig.hold(False)
    fName = '%s_%03d.pdf'%(sp,tNo)
    fList.append(fName) 
    myPlot.plt.savefig(fName)
  utilPlot.joinPDF(fList,'%s.pdf'%sp)
