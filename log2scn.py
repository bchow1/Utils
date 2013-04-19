import os
import sys
import re
import fileinput

trelPatt = re.compile('\s*TREL\s*=\s*(.+),')
tdurPatt = re.compile('\s*TDUR\s*=\s*(.+),')
relSPatt = re.compile('\s*RELSTATUS\s*=\s*(.+),')

def wrtScn(scnFile,tStart,cMass,relTime,relDur,scnLines):
# Writes the scnLines to scnFile after setting trel and relstatus
# Called from rdLog
  tRel = float(relTime) - tStart 
  if tRel >= 0. and cMass > 0.:
    print 'Writing release for time = %g  for duration %g and mass = %g'%(relTime,relDur,cMass)
    for line in scnLines:
      tRelMatch = trelPatt.match(line)
      tDurMatch = tdurPatt.match(line)
      relSMatch = relSPatt.match(line)
      if tRelMatch is not None:
        line = ' TREL    =  ' + str(float(relTime) - tStart)  + ',\n'
      if tDurMatch is not None:
        line = ' TDUR    =  ' + str(relDur)  + ',\n'
      if relSMatch is not None:
        line = ' RELSTATUS       =           1,\n'
      scnFile.write('%s'%line) 
  prvRelList = [0.,-9999.,[]] 
  return prvRelList


def rdLog(fName,tStart,tEnd):
# Read log file fName and write out temp.scn 
# Optional tStart and tEnd can be used for limiting the
# release times.
  scnLines   = []
  relTime    = -9999.0
  cMass      = 0.
  scnFile = open('temp.scn','w')
  isSCN = False
  for line in fileinput.input(fName):
    #print fileinput.lineno(),':',line.strip()
    if line.strip().startswith("&SCN"):
      isSCN      = True
      prvRelList = [cMass,relTime,scnLines]
      scnLines   = []
      scnLines.append(line)
      continue
    if isSCN:
      scnLines.append(line)
      if line.strip().startswith('/'):
        isSCN = False
        continue
      if 'CMASS' in line:
        cMass = float(line.strip().split('=')[1].replace(',',''))
    elif 'Update Release' in line:
      relTime = float(line.split("'")[2].strip())
      print 'Read release for time = ',relTime
      # Write out the previous release list using the current relTime for duration
      if prvRelList[1] >= 0.:
        tDur = relTime - prvRelList[1]
        prvRelList = wrtScn(scnFile,tStart,prvRelList[0],prvRelList[1],tDur,prvRelList[2])
      if float(relTime) > tEnd:
        break
  wrtScn(scnFile,tStart,cMass,relTime,tDur,scnLines)
  fileinput.close()
  scnFile.close()

def reWriteScn(fName,tStart=0.0,tEnd=1.e+20):
# Read scn file fName and write out modified namelist 
# to new file temp.scn. 
# Optional tStart and tEnd can be used for limiting the
# release times.   
  scnFile = open('temp.scn','w')
  isSCN   = False
  cMass   = 0.
  for line in fileinput.input(fName):
    #print fileinput.lineno(),':',line.strip()
    if line.strip().startswith("&SCN"):
      isSCN = True
      scnLines = []
      scnLines.append(line)
      continue
    if isSCN:
      scnLines.append(line)
      if line.strip().startswith('/'):
        isSCN = False
        # Write out the scnLines at end of namelist for non-zero releases 
        if cMass > 0.:
          for line in scnLines:
            # Hard coded for TestHPAC EPRI 072480.scn to correct emi rate
            # emi rates are wrong in scn files when using kg/sec. Must have been kg/hr.
            if 'CMASS' in line:
              line = ' CMASS   =  %13.3e,\n'%(cMass/3600.)
            scnFile.write('%s'%line)
        scnLines = []
        cMass    = 0. 
        continue
      # Find the release rate in scn namelist
      if 'CMASS' in line:
        cMass = float(line.strip().split('=')[1].replace(',',''))
  fileinput.close()
  scnFile.close()  

if __name__ == "__main__":
  #os.chdir('d:\\Aermod\\v12345\\runs\\kinsf6\\SCICHEM_Select')
  #logFile = 'KSF6-528_81I.log'
  os.chdir('d:\\TestSCICHEM\\Outputs\\130407_CALCBL\\AERMOD\\pgrass\\SCICHEM')
  logFile = 'pgrass.log'
  tStart  = 0.
  tEnd    = 1e+10
  #logFile = 'ww_1yr.log'
  rdLog(logFile,tStart,tEnd)
  #reWriteScn('..\\SCIPUFF\\052881.scn')
  print 'Done'
