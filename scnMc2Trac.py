#
# Read a multicomponent scn file and write out a tracer scn
# 
import os
import sys

def rdMCScn(scnName):
  
  scnFile = open(scnName,'r')
  scnList = []
  
  inScn = False
  inMC  = False
  for line in scnFile:
    lStrip = line.strip()
    if len(lStrip) > 0: 
      if lStrip.startswith('&SCN'):
        print 'Start Scn ',len(scnList)+1
        inScn = True
        scnLines = []
      if lStrip.startswith('/'):
        scnLines.append(line)
        scnList.append(scnLines)
        inScn = False
        print 'End Scn ',len(scnList)
        print
      # Reads scn file
      if inScn:
        if '#START_MC' in line:
          inMC = True
        if not inMC:
          scnLines.append(line)
        if '#END_MC' in line:
          inMC = False
  scnFile.close()

  return scnList

def wrtMCScn(scnList):
          
  scnFile = open('temp.scn','w')
  for scnLines in scnList:
    for line in scnLines:
      scnFile.write('%s'%line)
  scnFile.close()
  
  return

def rdWrtInp(InpName):
  
  inpFile  = open(InpName,'r')
  tmpFile = open('temp.inp','w')
  inpLines = []
  
  for line in inpFile:
    isSMP = False
    isIMC = True
    if 'SMPFILE' in line:
      tmpFile.write(" SMPFILE = '',\n")
    elif 'FILE_NAME' in line:
      tmpFile.write(" FILE_NAME = '',\n")
    elif line.strip() == "'," or len(line.strip()) == 0:
      pass
    else:
      tmpFile.write("%s"%line)
        
  inpFile.close()
  tmpFile.close()

# Main Program

if __name__ == '__main__':
  
  runDir = None
  if sys.argv.__len__() > 1:
    prjName = sys.argv[1]
    if sys.argv.__len__() > 2:
      runDir = sys.argv[2]
  else:
    print 'Usage: scnMc2Trac.py prjName [runDir]'
    sys.exit()

  curDir = os.getcwd()  
  if runDir is not None:
    os.chdir(runDir)
 
  scnList = rdMCScn(prjName + '.scn')
  wrtMCScn(scnList)
  
  rdWrtInp(prjName + '.inp')
  

  

