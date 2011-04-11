#!/usr/bin/python
import sys
import time
sys.path.append('/home/user/bnc/python')
import smp2db

#(Yr,Mo,Day,Hr,Min,Sec) = smp2db.
for i in range(1,sys.argv.__len__()):
  #print 'From ctime = ',time.ctime(float(sys.argv[i]))
  timeTuple = time.localtime(float(sys.argv[i]))
  #print 'Time tuple = ',timeTuple
  timeString = time.strftime('%Y/%m/%d %H:%M:%S',timeTuple)
  print 'From strftime = ',timeString
  #timeTuple = time.strptime(timeString,'%Y/%m/%d %H:%M:%S')
  #print 'Time tuple = ',timeTuple
  #epTime = time.mktime(timeTuple)
  #print 'From mktime, epTime = ',epTime
