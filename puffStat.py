#!/bin/python

import os
import sys
import socket
import numpy as np
import pandas as pd

compName = socket.gethostname()
env      = os.environ.copy()
 
if sys.platform == 'win32':
  if compName == 'sm-bnc':
    SCIPUFF_BASEDIR="D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\"
    binDir = os.path.join(SCIPUFF_BASEDIR,"workspace","EPRI","bin",compiler,"Win32",version)
    iniFile = "D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\workspace\\EPRI\\scipuff.ini"
    env["PATH"] = "%s" % (binDir)
    print env["PATH"]
    readpuf  = ["%s\\scipp.exe"%binDir,"-I:%s"%iniFile,"-R:RP"]
else:
  SCIPUFF_BASEDIR = "/home/user/bnc/scipuff/Repository/UNIX/EPRIx64/bin/linux/ifort"
  readpuf = ["%s/scipp"%SCIPUFF_BASEDIR,"-I:scipuff.ini","-R:RP"]
  env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH"] + ':' + SCIPUFF_BASEDIR
  sys.path.append('/home/user/bnc/python')

import readPuf as rp

if sys.argv.__len__() > 1:
  prjName = sys.argv[1]
else:
  print 'Usage: puffStat.py prjName'
  sys.exit()

vNames,hrDat = rp.getHrDat(readpuf,env,prjName,-1,rmOut=False)

sys.exit()

hrList = ['hr1','hr464','hr465']

df = [[] for i in hrList]

for fNo,fName in enumerate(hrList):
  df[fNo] = pd.read_csv(fName + '.csv',skiprows=[0,1])
  dpList = []
  for indx in df[fNo].columns:
    if 'Unnamed' in indx:
      dpList.append(indx)
  for indx in dpList:
    df[fNo] = df[fNo].drop(indx,1)
  print fNo, df[fNo]['IPUF'].count(), len(df[fNo].columns)

for indx in df[0].columns:
  print
  print indx
  print 'MIN = ',df[0][indx].min(),df[1][indx].min(),df[2][indx].min()
  print 'MAX = ',df[0][indx].max(),df[1][indx].max(),df[2][indx].max()
