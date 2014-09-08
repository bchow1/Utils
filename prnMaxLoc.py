#!/usr/bin/python

import os
import sys
import setSCIparams as SCI


for arg in sys.argv[1:]:

  dName = os.path.dirname(arg)
  fName = os.path.basename(arg)
  
  if '.' in fName:
    slfFile = os.path.join(dName,fName)   
    ntvFile = os.path.join(dName,fName.split('.')[0] + '.ntv')
  else:
    slfFile = os.path.join(dName,fName) + '.out'   
    ntvFile = os.path.join(dName,fName) + '.ntv'
       
  mySCIFiles = SCI.Files(slfFile)
  
  print 'Reading files ',slfFile,' and ',ntvFile
  tMax,maxList      = mySCIFiles.readSumFile(slfFile,showDate=True)
  relTime,relX,relY = mySCIFiles.readNtvFile(ntvFile)
  
  print '\n  Time              = ',tMax[0],', ',tMax[1],', ',relTime
  print '  Location Function = ',maxList[0][0]
  print '  Location          = ',relX,', ',relY
  print '  Release Mass      = ',maxList[1][0],maxList[1][1]
  if maxList[2][0] is not None:
    print '  Duration          = ',maxList[2][0],maxList[2][1],'\n'



