#
# Read section name from imc file
# and save the species data in spList
# 
import os
import sys

def rdSpSec(line,spList):
  spList.append(line.strip().split())
  return spList

def rdImc(imcName):
  imcFile  = open(imcName,'r')
  sctnName = None

  # Initialize spList
  spList   = []

  # Read section name and data from each line
  for line in imcFile:
    if len(line.strip()) > 0: 
      if line.startswith('#'):
        sctnName = line.strip().split()[0].replace('#','').split(',')[0]
        print 'Section = ',sctnName
        continue
      if sctnName == 'Species':
        rdSpSec(line,spList)
  imcFile.close()

  print len(spList),spList[0],spList[-1]
  return

def rdMCScn(scnName,form=None):
  scnFile = open(scnName,'r')
  scnList = []
  
  for line in scnFile:
    if len(line.strip()) > 0: 
      if line.strip().startswith('&SCN'):
        print 'Start Scn'
      if line.strip().startswith('/'):
        print 'Start Scn'
  scnFile.close()

  return

# Main Program

if __name__ == '__main__':

  imcName = 'test2.imc'
  rdImc(imcName)

  scnName = 'test2.scn'
  rdMCScn(scnName)

