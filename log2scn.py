import os
import sys
import re
import fileinput

trelPatt = re.compile('\s*TREL\s*=\s*(.+),')
relSPatt = re.compile('\s*RELSTATUS\s*=\s*(.+),')

def rdLog(fName):
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
    elif 'Update Release' in line:
        relTime = line.split("'")[2].strip()
        print 'Rel Time = ',relTime
        wrtScn(scnFile,scnLines,relTime)
        scnLines = []
        if float(relTime) > 23.75:
          sys.exit()
  fileinput.close()
  scnFile.close()


def wrtScn(scnFile,scnLines,relTime):
  for line in scnLines:
    tRelMatch = trelPatt.match(line)
    relSMatch = relSPatt.match(line)
    if tRelMatch is not None:
      line = ' TREL    =  ' + relTime + ',\n'
    if relSMatch is not None:
      line = ' RELSTATUS       =           1,\n'
    scnFile.write('%s'%line) 
  return

if __name__ == "__main__":
  logFile = 'kinso2.log'
  rdLog(logFile)
