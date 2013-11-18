import os
import sys
import socket
import fileinput

os.chdir("d:\\EPRI\\SCICHEM_STE\\runs\\Dxl")
inSenFile  = 'TestSENfile2.sen'
outSenFile = open('x.sen','w')

for line in fileinput.input(inSenFile):
  if len(line) <= 2: continue
  if line.rstrip().endswith('Type2Sensor'):
    rdNext = True
    outSenFile.write(line)
    continue
  if rdNext:
    try:
      (matName, xSen, ySen, zSen, timeString, matType, cMin, cSen, sSig, sSat, tDur) = line.split(';')
      (xSen,ySen,zSen,cMin,cSen,sSig,tDur)  = map(float,(xSen,ySen,zSen,cMin,cSen,sSig,tDur))
      zSen = max(0.,zSen-250.)
      if matType.strip() == 'N':
        cSen = 0.0
        matName = matName.replace('T','N')
      #cMin = 1.0e-19
      #sSig = 10.
      outSenFile.write('%s; %8.2f; %8.2f; %8.2f; %s; %s; %10.3e; %10.3e; %4.1f; %s; %4.1f\n'%\
                      (matName, xSen, ySen, zSen, timeString, matType, cMin, cSen, sSig, sSat, tDur))      
    except ValueError:
      print 'Error reading line from %s-\n%d:%s'%(inSenFile,fileinput.lineno(),line)
      rdNext = False
      continue
fileinput.close()
outSenFile.close()