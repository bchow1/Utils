#!/bin/env /opt/ActivePython-2.6/bin/python
import os
import sys
import fileinput

def wrtPrf(prfName,x,y,thr,mol,obsData):
  prfFile=open(prfName,"w",0)
  prfFile.write("PROFILE\n")
  prfFile.write("   5   3\n")
  #SenInp.write("%8.4f %8.4f %8.4f %s %s %s" % (x, y, z, 'CONC', mname, tail))
  prfFile.write("ID      X       Y       TIME    MOL\n")
  prfFile.write("NONE    M       M       HRS     M\n")
  prfFile.write("Z       WSPD    DIR\n")
  prfFile.write("M       M/S     NONE\n")
  prfFile.write("-999.99\n")
  prfFile.write("ID: NONE %s %s %s %s\n"%(x,y,thr,mol))
  hts = [2,4,8,16,32,61]
  for ih,ht in enumerate(hts):
    print obsData[ih]
    prfFile.write("%8.4f %8.2f 270.\n"%(float(ht),float(obsData[ih])))
  prfFile.close()
  
os.chdir('D:\\SCIPUFF\\runs\\LowWindSpeeds\\IdahoFalls')
TestNames = {4:'020774',5:'020874',6:'020974',7:'021274',8:'022174',9:'032174',\
             10:'041774',11:'043074a',12:'043074b',13:'050374',14:'052274'}
csvFile = 'IdahoFalls.csv'
obsList = [[] for i in range(15)]
for line in fileinput.input(csvFile):
  if len(line.strip()) > 0:
    if line.startswith('#'):
      continue
    else:
      lData = line.strip().split(',') 
      tNo = int(lData[0])
      if lData[1].strip() == 'vv':
        obsList[tNo].append(lData[2:])
#print obsList
fileinput.close()

for tNo in TestNames.keys():
  sfcFile = 'if%s.sfc'%TestNames[tNo][:6]
  idLNo = None 
  for line in fileinput.input(sfcFile):
    if len(line.strip()) > 0:
      if line.strip().startswith('ID'):
        idLNo = fileinput.lineno()
      if idLNo is not None:
        if fileinput.lineno() == idLNo + 3:
          pid,x,y,z,tHr,wspd,wdir,mol = line.split()
          break
  fileinput.close()
  prfFile = 'if%s.prf'%TestNames[tNo]
  wrtPrf(prfFile,x,y,tHr,mol,obsList[tNo][0])
