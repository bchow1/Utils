#!/bin/python
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

fig = plt.figure(1)
plt.clf()
plt.hold(True)

def hms(s):
  hr,mn,sc = map(float,s.split(':'))
  hms = (hr*60. + mn)*60. + sc
  return hms

def ms(s):
  mn,sc = map(float,s.split(':'))
  ms = mn*60. + sc
  return ms
 
width = 0.25
fig = plt.figure(1)
plt.clf()
plt.hold(True)
plt.setp(plt.gca(), frame_on=False, xticks=(), yticks=())
plt.title('CPU Load for ETEX using different number of CPUs')

for sp,ncpu in enumerate([1,2,4,8,16]):
  cpu,time = np.loadtxt('cpuload_%d.txt'%ncpu,usecols=(6,0),converters={0:ms},unpack=True)
  ax = fig.add_subplot(5,1,'%d'%(sp+1))
  if sp == 0:
    maxt = time.max()
    ax.text(.02,.8,'%d CPUs'%ncpu,fontsize=9,transform=ax.transAxes)
    print maxt
  else:
    ax.text(.92,.8,'%d CPUs'%ncpu,fontsize=9,transform=ax.transAxes)
  if sp == 4:
    ax.set_xlabel('Secs',fontsize=9)
  else:
    ax.set_xticklabels([])
  print sp,ncpu
  print time,cpu
  ax.bar(time,cpu,width)
  plt.setp(ax.get_xticklabels(),fontsize=9)
  plt.setp(ax.get_yticklabels(),fontsize=9)
  ax.set_ylabel('CPU %',fontsize=9)
  #ax.set_title('No of CPUs = %d'%ncpu,fontsize=9)
  ax.set_xlim(0,maxt)
  ax.set_ylim(0,ncpu*100.)
  ax.yaxis.set_major_locator(MaxNLocator(4))
plt.hold(False)
#plt.show()
plt.savefig('cpuLoad.png')

speedup = np.loadtxt('speedup.txt')
speedup[:,1] = speedup[0,1]/speedup[:,1]
fig = plt.figure(1)
plt.clf()
plt.hold(True)
plt.title('Speedup for ETEX using different number of CPUs')
plt.plot(speedup[:,0],speedup[:,1],marker='o')
plt.xlabel('# CPUs')
plt.xlim([1,16])
plt.ylabel('Speedup')
plt.ylim([0,6])
plt.hold(False)
#plt.show()
plt.savefig('speedup.png')
