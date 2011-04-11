#!/usr/bin/env /usr/bin/python
#
# Converts filename.sam for OLD(HPAC32) style to NEW(HPAC40) or viceversa
# Usage: chngSam.py [-f (NEW|OLD)] [-t (NEW|OLD)] filename.sam
#
import os
import sys
import optparse
import shutil
import re
import fileinput

if sys.platform == 'win32':
  tail = '\r\n'
else:
  tail = '\n'

arg = optparse.OptionParser()
arg.add_option("-f",action="store",type="choice",
                choices=["OLD","NEW"],dest="fromType")
arg.add_option("-t",action="store",type="choice",
                choices=["OLD","NEW"],dest="toType")
arg.set_defaults(fromType="OLD",toType="NEW")
opt,args = arg.parse_args()

fromType = opt.fromType
toType   = opt.toType

outFile = open('TempSam.tmp',"w",0)
for samFile in args:
  print "Converting sam file %s from %s to %s style"%(samFile,fromType,toType)
  for line in fileinput.input(samFile):
     if fileinput.isfirstline():
       (matName,matGrp) = line.split()
       outFile.write('HPAC SENSOR %s'%tail)
     else:
       (xsmp , ysmp , zsmp) = line.split()
       #(xsmp , ysmp, zsmp) = (line.split()[0],line.split()[1])i,10.
       outFile.write('%s %s %s CONC %s:%s Sensor%d %s'%(xsmp,ysmp,zsmp,matName,matGrp,fileinput.lineno()-1,tail))
fileinput.close()
        
try:
  shutil.move('TempSam.tmp',samFile)
  print 'Move %s to %s'% ('TempSam.tmp',samFile)
except EnvironmentError:
  raise
