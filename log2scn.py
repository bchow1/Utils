import os
import sys
import re
import fileinput

trelPatt = re.compile('\s*TREL\s*=\s*(.+),')
relSPatt = re.compile('\s*RELSTATUS\s*=\s*(.+),')

def rdLog(fName,tStart,tEnd):
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
        sys.exit()
  fileinput.close()
  scnFile.close()

def wrtScn(scnFile,scnLines,relTime,tStart):
  for line in scnLines:
    tRelMatch = trelPatt.match(line)
    relSMatch = relSPatt.match(line)
    if tRelMatch is not None:
      line = ' TREL    =  ' + str(float(relTime) -tStart)  + ',\n'
    if relSMatch is not None:
      line = ' RELSTATUS       =           1,\n'
    scnFile.write('%s'%line) 
  return

if __name__ == "__main__":
  os.chdir('d:\\Aermod\\v12345\\runs\\kinsf6\\SCICHEM')
  logFile = 'KSF6-424_80I.log'
  tStart  = 0.
  tEnd    = 1e+10
  #logFile = 'ww_1yr.log'
  rdLog(logFile,tStart,tEnd)
