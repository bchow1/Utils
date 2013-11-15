#
# Read section name from imc file
# and save the species data in spList
# 
import os
import sys
import sqlite3
import numpy as np

MAX_MC = 250

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
        spList.append(line.strip().split())
  imcFile.close()
  print len(spList),spList[0],spList[-1]
  return spList

def wrtImcSpList(spList,fromSpList,skpSpList=None):
  
  # This function writes species section of an imc file using the 
  # background concentrations from fromSpList
   
  # Get names and ambient concentrations from from spList 
  spNames = [spVal[0] for spVal in spList]
  spConcs = [spVal[2] for spVal in spList]

  fromSpNames = [spVal[0] for spVal in fromSpList]
  fromSpConcs = [spVal[2] for spVal in fromSpList]
  
  fmtList = ['10s','12s','18s','13s','9s','3s','6s']  
  sfmt = '' 
  for idx,fmt in enumerate(fmtList):
    sfmt = sfmt + '{0[%d]:%s} '%(idx,fmt)
  sfmt = sfmt + '\n'

  for spNo,spName in enumerate(spNames):
    try:
      indx = fromSpNames.index(spName)
      if abs(float(spConcs[spNo]) - float(fromSpConcs[indx])) > 1.e-10:
        if float(fromSpConcs[indx]) < 1.e-10:
          print 'Skipping ',spName,' as from conc = ',float(fromSpConcs[indx]),' keeping conc = ',float(spConcs[spNo])
          continue
        if skpSpList is not None:
          if spName in skpSpList:
            print 'Skipping ',spName,' from skSpList as conc = ',float(fromSpConcs[indx]),' keeping conc = ',float(spConcs[spNo])
            continue 
        spList[spNo][2] = fromSpConcs[indx]
        print 'For %s replacing amb = %s with %s'%(spName,spConcs[spNo],fromSpConcs[indx])
    except ValueError:
      print 'Note: Cannot find %s in from species list. Using conc = %s'%(spName,spConcs[spNo])

  imcFile = open('temp.imc','w')
  imcFile.write('#Species,Type,Ambient,Tolerance,deposition vel,wet scav,mw\n')
  for line in spList:
    imcFile.write(sfmt.format(line))
  imcFile.close()   
  
  return                                                    
        
# Main Program

if __name__ == '__main__':
  
  # Get new species background from input imc file 
  
  inpDir = 'D:\\TestSCICHEM\\Outputs\\130327.HiISOPF\\Chemistry\\tva_980825'
  if inpDir is None:
    inpDir = os.getcwd()
  fromImc = 'SCICHEM-2012\\ae5_romebg_eq.imc'
  toImc   = 'FixEmis_CBL_LMET_noLSV_hiVOC\\ae5_noamb.imc'
  os.chdir(inpDir)
  fromSpList = rdImc(os.path.join(inpDir,fromImc))    
  toSpList   = rdImc(os.path.join(inpDir,toImc))
  #
  print 'Using background concentation from ',fromImc,' to ',toImc
  wrtImcSpList(toSpList,fromSpList,skpSpList=['OH','HO2','XO2','XO2N'])
  

