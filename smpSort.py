#!/bin/python
import sys
import numpy as np

if sys.argv.__len__() < 2:
  print 'Usage: smpSort.py csvFile [colNo]'
  sys.exit()

print sys.argv.__len__(), sys.argv
csvFile = sys.argv[1]
if sys.argv.__len__() == 3:
  colNo = sys.argv[2]
else:
  colNo = 3

'''
# srf2smp output
cUnits = '[kg/(m3.hr) to ug/(m3.s)]'
cFac   = 1.e9/3600. # ug/kg * hr/sec 

tUnits = 'hr/days'
tFac   = 1./24 

#cDat = np.loadtxt(csvFile,skiprows=1,delimiter=',')
'''

# smp file
cUnits = '[kg/m3 to ug/m3]'
cFac   = 1.e9 # ug/kg

tUnits = 'hr/secs'
tFac   = 1./(24.*3600.)

cDat = np.loadtxt(csvFile,skiprows=7)

print 'Conc factor = ',cFac,cUnits
print 'Time factor = ',tFac,tUnits

cDat[:,colNo] = cDat[:,colNo]*cFac
cDat[:,0]     = cDat[:,0]*tFac

cSort = np.sort(cDat[:,colNo])[::-1]

for i in range(10): 
   print cDat[np.where(cDat[:,colNo]==cSort[i])[0][0],:]
