#!/usr/bin/python
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('/home/user/bnc/python')
import utilPlot

#Script to compare sampler output from instantaneous and time averaged sampler files

smpFile1 = 'so2.2005.st.smp'
smpFile2 = 'so2.2005.st_noTavg.smp'

nSmp = 44

colNos1 = []
for i in range(nSmp):
  colNos1.append(1 + i*2)

colNos2 = []
for i in range(nSmp):
  colNos2.append(1 + i*3)

t1       = np.loadtxt(smpFile1,skiprows=47,usecols=[0])
conc1    = np.loadtxt(smpFile1,skiprows=47,usecols=colNos1)
nt1,nSmp = np.shape(conc1)
print t1,nt1,nSmp

t2       = np.loadtxt(smpFile2,skiprows=47,usecols=[0])
conc2    = np.loadtxt(smpFile2,skiprows=47,usecols=colNos2)
nt2,nSmp = np.shape(conc2)
print t2,nt2,nSmp

iHr    = int(3600./t2[0])
print 'Average over %d time steps'%iHr 

cHrAvg = np.zeros((nt2/iHr,nSmp),float)
for j in range(nSmp):
  for hr in range(0,nt2-iHr+1,iHr):
    cHrAvg[hr/iHr,j] = np.mean(conc2[hr:hr+iHr,j])

print conc1.max(),conc1.mean()
print conc2.max(),conc2.mean()
print cHrAvg.max(),cHrAvg.mean()

cMax = max(conc1.max(),conc2.max(),cHrAvg.max())

nSub = 1
iFig = -1
fList = []
for smpNo in range(nSmp):
  if smpNo%nSub == 0:
    iFig += 1 
    iSub  = 0
    fName = 'plt%02d.pdf'%iFig
    fig = plt.figure()
    plt.clf()
    plt.hold(True)
  iSub += 1 
  ax = fig.add_subplot(1,1,iSub)
  print smpNo,conc1[:,smpNo].max(),conc1[:,smpNo].mean()
  #lh1 = ax.semilogy(t1,conc1[:,smpNo],color='red',marker='+',markersize=3,linestyle='None')
  #lh2 = ax.semilogy(t2,conc2[:,smpNo],color='black',marker='+',markersize=3,linestyle='None')
  print smpNo,cHrAvg[:,smpNo].max(),cHrAvg[:,smpNo].mean()
  #lh3 = ax.semilogy(t1,cHrAvg[:,smpNo],color='green',marker='x',markersize=3,linestyle='None')
  lh3 = ax.plot(conc1[:,smpNo],cHrAvg[:,smpNo],color='green',marker='o',markersize=3,linestyle='None')
  #plt.legend([lh1,lh2,lh3],['Tavg','Inst','Inst(Avg)'])
  plt.title('Sampler %d'%smpNo)
  #ax.set_xlabel('Hr')
  #ax.set_ylabel('Conc')
  ax.set_xscale('log')
  ax.set_yscale('log')
  #ax.set_xlim([cMax*1e-7,cMax*10.])
  #ax.set_ylim([cMax*1e-7,cMax*10.])
  ax.set_xlabel('Time Avg. Conc')
  ax.set_ylabel('Avg. Inst Conc')
  ax.set_xlim([1e-28,cMax*10.])
  ax.set_ylim([1e-28,cMax*10.])
  #plt.savefig(fName + '%d.pdf'%iSub)
  if iSub == nSub:
     plt.hold(False)
     plt.savefig(fName)
     fList.append(fName)
     print fName
utilPlot.joinPDF(fList,'So2_2005.pdf')

#for smpNo in range(nSmp):
  #print smpNo,conc1[:,smpNo].mean(),cHrAvg[:,smpNo].mean()

#for smpNo in range(nSmp):
#  print smpNo,conc2[0,smpNo],conc2[1,smpNo],conc2[2,smpNo],conc2[3,smpNo],cHrAvg[0,smpNo]

'''
maxconc1 = np.sort(conc1.flatten())[::-1]
maxconc2 = np.sort(cHrAvg.flatten())[::-1]

for i in range(25):
  print i+1,maxconc1[i],maxconc2[i]
'''
