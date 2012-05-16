#
import os
import sys
import ast
import fileinput
import sqlite3
import numpy as np
#

if __name__ == '__main__':

  env = os.environ.copy()
  if sys.platform == 'win32':
    runDir = "D:\hpac\\gitEPRI\\runs\\stepAmbwFlx"
    file1 = 'x1_777.dat'
    file2 = 'x2_777.dat'
    tail = '\r\n'
  else:
    SCIPUFF_BASEDIR = "/home/user/bnc/hpac/fromSCIPUFF/Repository/UNIX/FULL/bin/linux/lahey"
    tail = '\n'

  os.chdir(runDir)

  f1 = open(file1,'r')
  f2 = open(file2,'r')

  isDiff = False 
  for line1,line2 in zip(f1,f2):
    list1 = line1.strip().split(',')
    list2 = line2.strip().split(',')
    nlist1 = map(float,list1[:-1])
    nlist2 = map(float,list2[:-1])
    print 'time = ',nlist1[0],nlist2[0]
    for n1,n2 in zip(nlist1,nlist2):
      if abs(n1-n2) > 1e-16:
        print 'Found diff: ',n1,n2
        print nlist1.index(n1)
        print nlist2.index(n2)
        isDiff = True
        break
    if isDiff:
      print nlist1
      print nlist2
      break
  
  
