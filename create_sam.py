#!/bin/env /opt/ActivePython-2.6/bin/python
import os, sys, fileinput, re

if sys.platform == 'win32':
  env = os.environ.copy()
  OldPath = env["PATH"]
  env["PATH"] = "%s;%s" % (OldPath,'D:\SourceEstimation\runs\FFT07\script')
  #tail = '\r\n'
  tail = '\n'
else:
  sys.path.append('/usr/pc/biswanath/SourceEstimation/runs/FFT07/script')
  tail = '\n'

mname = 'SF6'
xmin = -116.16
xmax = -116.00
ymin = 37.00
ymax = 37.20
z    = 6.
nx = 10 
ny = 5
SenInp=open("x.sam","w",0)
SenInp.write("HPAC SENSOR%s"%tail)
dx = (xmax - xmin)/float(nx)
dy = (ymax - ymin)/float(ny)
x = xmin
while x <= xmax:
  y = ymin
  while y <= ymax:
    SenInp.write("%8.4f %8.4f %8.4f %s %s %s" % (x, y, z, 'CONC', mname, tail))
    y = y + dy
  print x,dx
  x = x + dx
SenInp.close()
