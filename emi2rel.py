#!/bin/python

import os
import sys
import fileinput
import datetime

if sys.argv.__len__() < 2:
  print 'Usage: emi2rel.py emiFile startTime'
  print '       startTime format "%Y-%m-%d;%H:%M:%S"'
  sys.exit()

emiName = sys.argv[1] 
ymd     = sys.argv[2]
#YYYY,MM,DD,hh,mm,ss = map(int,[ymd[0:5],ymd[5:7],ymd[7:9],ymd[9:11]

strStart = datetime.datetime.strptime(ymd,'%Y-%m-%d;%H:%M:%S')
print 'Start time = ',strStart

sList = {}
for line in fileinput.input(emiName):
  #SO HOUREMIS 92  5  1  1 MC12          386.91     389.8     11.45
  values = line.split() # SO HOUREMIS Year(2), Month(3), Day(4), Hour(5), Source ID, rate, tempK, vel 
  yy,mm,dd = map(int,values[2:5])
  if yy > 1900:
    pass
  elif yy < 50:
    yy = yy + 2000
  elif yy > 50 and yy < 99:
    yy = yy + 1900

  hr,rate,temp,vel = map(float,[values[5],values[7],values[8],values[9]])
  hh = int(hr)
  mins = (hr - hh)*60.
  mn = int(mins)
  ss = int((mins - mn)*60)
  print values
  if ss == 60:
    ss = 0
    mn = mn + 1
  if mn > 59:
    mn = mn - 60
    hh = hh + 1
  if hh > 23:
    hh = hh - 24
    addDay = 1
  else:
    addDay = 0
  tstr = datetime.datetime(yy,mm,dd,hh,mn,ss)
  if addDay == 1:
    print 'Before: ',tstr
    tstr = tstr + datetime.timedelta(days=1)
    print 'After: ',tstr
  hr = (tstr - strStart).total_seconds()/3600.
  sId = values[6]
  relName = '%s.rel'%sId
  if sId not in sList:
    sList.update({sId:open(relName,'w')})
    sList[sId].write('!time rate exitTemp  exitUvel\n')
  # time rate exitTemp  exitUvel, exitVvel, exitWvel
  sList[sId].write('%g %g %g %g\n'%(hr,rate,max(temp-273.15,0.),vel))
  if fileinput.lineno() > 5:
    print sId,hr,rate,temp,vel
  
for k,v in sList.items():
  sList[k].close()
print sList