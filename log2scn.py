import os
import sys
import re
import fileinput

trelPatt = re.compile('\s*TREL\s*=\s*(.+),')
relSPatt = re.compile('\s*RELSTATUS\s*=\s*(.+),')

def wrtScn(scnFile,scnLines,relTime,tStart):
# Writes the scnLines to scnFile after setting trel and relstatus
# Called from rdLog
  for line in scnLines:
    tRelMatch = trelPatt.match(line)
    relSMatch = relSPatt.match(line)
    if tRelMatch is not None:
      line = ' TREL    =  ' + str(float(relTime) -tStart)  + ',\n'
    if relSMatch is not None:
      line = ' RELSTATUS       =           1,\n'
    scnFile.write('%s'%line) 
  return


def rdLog(fName,tStart,tEnd):
# Read log file fName and write out temp.scn 
# Optional tStart and tEnd can be used for limiting the
# release times. 
  scnFile = open('temp.scn','w')
  isSCN = False
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
        continue
      if 'CMASS' in line:
        cMass = float(line.strip().split('=')[1].replace(',',''))
    elif 'Update Release' in line:
      relTime = line.split("'")[2].strip()
      print 'Rel Time = ',relTime
      if float(relTime) > tStart and cMass > 0.:
        wrtScn(scnFile,scnLines,relTime,tStart)
      scnLines = []
      if float(relTime) > tEnd:
        break
  fileinput.close()
  scnFile.close()

def reWriteScn(fName,tStart=0.0,tEnd=1.e+20):
# Read scn file fName and write out modified namelist 
# to new file temp.scn 
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
  os.chdir('d:\\Aermod\\v12345\\runs\\kinsf6\\SCICHEM')
  logFile = 'KSF6-724_80I.log'
  tStart  = 0.
  tEnd    = 1e+10
  #logFile = 'ww_1yr.log'
  #rdLog(logFile,tStart,tEnd)
  reWriteScn('072480.scn')
