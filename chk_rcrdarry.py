#!/bin/python
import sys
from numpy import *
import DataSampler

vnames       = ('time','conc','var')
mySampler    = DataSampler.Sampler(vnames)
mySampler.id = 1
mySampler.x  = 0.
mySampler.y  = 0.

smpType = [('time',float),('conc',float),('var',float)]

line = '1.0 0.01 0.02'

tmpList = line.split()
print 'tmpList = ',tmpList

tmpArray = array(tmpList,dtype=float)
print 'tmpArray= ',tmpArray

srcValue = []
srcValue.append((tmpArray[0],tmpArray[1],tmpArray[2]))
print '\nWorking srcValue = ',srcValue
smpData = array(srcValue,dtype=smpType)
print 'smpData from srcValue= ',smpData, smpData['time'], smpData['conc']

srcValue = tuple(tmpList)
print '\nTrying srcValue = ',srcValue
smpData = array(srcValue,dtype=smpType)
print 'smpData from srcValue= ',smpData, smpData['time'], smpData['conc']

#mySampler.addData((tmpArray[0],tmpArray[1],tmpArray[2]))
print mySampler.Data
mySampler.addData(line.split())
print mySampler.Data
line = '2.0 0.02 0.04'
mySampler.addData(line.split())
print mySampler.Data
mySampler.typeData()
print mySampler.Data
print mySampler.Data['time']
print mySampler.Data['conc']
print mySampler.Data['var']
